import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from purple_mri import lifecycle

CID = 'c' * 64
IMAGE = 'sha256:' + 'a' * 64


class LifecycleTests(unittest.TestCase):
    def exercise(self, final_status='exited', actual_exit=0, client_exit=0,
                 interrupt=False, mismatch=False, stop_fails=False):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'purple_run.json'
            record = {'image_id': IMAGE, 'exit_code': None}
            calls = []
            inspections = 0
            process = Mock()
            process.wait.side_effect = KeyboardInterrupt() if interrupt else None
            process.wait.return_value = client_exit
            process.poll.return_value = client_exit

            def run(argv, **kwargs):
                nonlocal inspections
                calls.append(argv)
                if argv[1] == 'create':
                    self.assertNotIn('--rm', argv)
                    return subprocess.CompletedProcess(argv, 0, CID + '\n')
                if argv[1:3] == ['container', 'inspect']:
                    inspections += 1
                    status = 'created' if inspections == 1 else final_status
                    if interrupt and inspections == 2 and final_status == 'exited':
                        status = 'running'
                    data = {'Id': CID, 'Image': IMAGE,
                            'Config': {'Labels': {lifecycle.RUN_LABEL: 'wrong' if mismatch else record['run_id']}},
                            'State': {'Status': status, 'Running': status == 'running',
                                      'ExitCode': actual_exit, 'OOMKilled': False,
                                      'FinishedAt': '2026-10-21T18:00:00Z'}}
                    return subprocess.CompletedProcess(argv, 0, json.dumps([data]))
                if argv[1] == 'stop' and stop_fails:
                    raise subprocess.CalledProcessError(1, argv)
                return subprocess.CompletedProcess(argv, 0, '')

            with patch.object(lifecycle.subprocess, 'run', side_effect=run), \
                 patch.object(lifecycle.subprocess, 'Popen', return_value=process) as start, \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = lifecycle.execute_container(['docker', 'run', '--rm', IMAGE, '/bin/true'], path, record)
            return rc, json.loads(path.read_text()), calls, start

    def test_success_uses_actual_state_and_removes_only_owned_container(self):
        rc, record, calls, start = self.exercise()
        self.assertEqual(rc, 0)
        self.assertEqual(record['status'], 'succeeded')
        self.assertEqual(record['exit_code'], 0)
        self.assertTrue(record['container_removed'])
        self.assertIn(['docker', 'rm', CID], calls)
        self.assertTrue(start.call_args.kwargs['start_new_session'])

    def test_container_failure_overrides_successful_attach_client(self):
        rc, record, calls, _ = self.exercise(actual_exit=7)
        self.assertEqual(rc, 7)
        self.assertEqual(record['exit_code'], 7)
        self.assertEqual(record['status'], 'failed')
        self.assertFalse(any(c[1] == 'rm' for c in calls))

    def test_interrupt_stops_owned_container_and_records_real_exit(self):
        rc, record, calls, _ = self.exercise(actual_exit=137, interrupt=True)
        self.assertEqual(rc, 130)
        self.assertEqual(record['cli_exit_code'], 130)
        self.assertEqual(record['exit_code'], 137)
        self.assertEqual(record['status'], 'cancelled')
        self.assertIn(['docker', 'stop', '--time', '30', CID], calls)
        self.assertFalse(any(c[1] == 'rm' for c in calls))

    def test_identity_mismatch_never_starts_stops_or_removes(self):
        rc, record, calls, start = self.exercise(mismatch=True)
        self.assertNotEqual(rc, 0)
        self.assertEqual(record['status'], 'unknown')
        self.assertIsNone(record['exit_code'])
        start.assert_not_called()
        self.assertFalse(any(c[1] in ('stop', 'rm') for c in calls))

    def test_failed_stop_keeps_running_state_unconfirmed(self):
        rc, record, calls, _ = self.exercise(final_status='running', interrupt=True, stop_fails=True)
        self.assertEqual(rc, 130)
        self.assertEqual(record['status'], 'running_after_client_exit')
        self.assertIsNone(record['exit_code'])
        self.assertNotIn('finished_utc', record)
        self.assertIn('errors', record)
        self.assertFalse(any(c[1] == 'rm' for c in calls))

    def test_client_exit_is_not_container_completion(self):
        rc, record, _, _ = self.exercise(final_status='running')
        self.assertNotEqual(rc, 0)
        self.assertEqual(record['status'], 'running_after_client_exit')
        self.assertIsNone(record['exit_code'])

    def test_cancel_before_start_has_no_fictional_processing_exit(self):
        rc, record, calls, _ = self.exercise(final_status='created', interrupt=True)
        self.assertEqual(rc, 130)
        self.assertEqual(record['status'], 'cancelled_before_start')
        self.assertIsNone(record['exit_code'])
        self.assertFalse(any(c[1] in ('stop', 'rm') for c in calls))
