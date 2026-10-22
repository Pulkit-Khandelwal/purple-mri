"""Track the container itself, including when the attached client is interrupted."""
from datetime import datetime, timezone
import json
import re
import shlex
import signal
import subprocess
import sys
import uuid

RUN_LABEL = "org.purple-mri.run-id"
CONTROL_TIMEOUT = 45


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def save_record(path, record):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(path)


def inspect_owned(name, run_id, image_id, expected_id=None):
    result = subprocess.run(["docker", "container", "inspect", name], check=True,
                            capture_output=True, text=True, timeout=CONTROL_TIMEOUT)
    data = json.loads(result.stdout)[0]
    container_id = data.get("Id", "")
    labels = data.get("Config", {}).get("Labels") or {}
    if (not re.fullmatch(r"[0-9a-f]{64}", container_id)
            or labels.get(RUN_LABEL) != run_id
            or data.get("Image") != image_id
            or (expected_id and container_id != expected_id)):
        raise ValueError("Container identity mismatch; refusing to manage it.")
    return data


def execute_container(command, provenance, record):
    """Create first so the container ID is recorded before processing starts."""
    if command[:3] != ["docker", "run", "--rm"]:
        raise ValueError("Unexpected container command.")
    run_id = uuid.uuid4().hex
    name = "purple-mri-" + run_id
    create = ["docker", "create", "--name", name, "--label", RUN_LABEL + "=" + run_id,
              *command[3:]]
    record.update(run_id=run_id, container_name=name, container_id=None,
                  status="creating", exit_code=None, cli_exit_code=None)
    save_record(provenance, record)
    process = None
    interrupted = False
    client_rc = 2
    created_id = None
    state = None
    errors = []
    try:
        print(shlex.join(create), flush=True)
        created = subprocess.run(create, check=True, capture_output=True, text=True,
                                 timeout=CONTROL_TIMEOUT)
        created_id = created.stdout.strip()
        if not re.fullmatch(r"[0-9a-f]{64}", created_id):
            raise ValueError("Docker create did not return a valid container ID.")
        inspect_owned(name, run_id, record["image_id"], created_id)
        record.update(container_id=created_id, status="starting")
        save_record(provenance, record)
        start = ["docker", "start", "--attach", created_id]
        print(shlex.join(start), flush=True)
        # The Python CLI owns terminal Ctrl+C. Stop the actual container below.
        process = subprocess.Popen(start, start_new_session=True)
        record["status"] = "running"
        save_record(provenance, record)
        client_rc = process.wait()
        if client_rc < 0:
            client_rc = 128 - client_rc
    except KeyboardInterrupt:
        interrupted = True
        client_rc = 130
        print("Cancelling this run's container (up to 30 seconds grace)...", file=sys.stderr)
    except (OSError, ValueError, subprocess.SubprocessError, KeyError, IndexError) as exc:
        errors.append(str(exc))
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            errors.append(exc.stderr.strip())
    finally:
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            try:
                data = inspect_owned(name, run_id, record["image_id"], created_id)
                record["container_id"] = data["Id"]
                state = data["State"]
                if interrupted and state.get("Running"):
                    try:
                        subprocess.run(["docker", "stop", "--time", "30", data["Id"]],
                                       check=True, capture_output=True, text=True,
                                       timeout=CONTROL_TIMEOUT)
                    finally:
                        # A failed or timed-out stop must not be called completed.
                        state = None
                        data = inspect_owned(name, run_id, record["image_id"], data["Id"])
                        state = data["State"]
            except (OSError, ValueError, subprocess.SubprocessError, KeyError, IndexError) as exc:
                errors.append("Container state/control: " + str(exc))

            if process is not None and process.poll() is None:
                # Only terminate our attached Docker client, never arbitrary jobs.
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                except OSError as exc:
                    errors.append("Client cleanup: " + str(exc))

            record["client_finished_utc"] = utc_now()
            if state and state.get("Running"):
                record["status"] = "running_after_client_exit"
            elif state and state.get("Status") in ("exited", "dead"):
                record.update(exit_code=int(state["ExitCode"]),
                              finished_utc=state.get("FinishedAt"),
                              oom_killed=bool(state.get("OOMKilled")),
                              status="cancelled" if interrupted else (
                                  "succeeded" if state["ExitCode"] == 0 else "failed"))
            elif state and state.get("Status") == "created":
                record["status"] = "cancelled_before_start" if interrupted else "not_started"
            else:
                record["status"] = "unknown"

            rc = 130 if interrupted else (
                record["exit_code"] if record["exit_code"] is not None else (client_rc or 2))
            record["cli_exit_code"] = rc
            if errors:
                record["errors"] = errors
                for error in errors:
                    print("Warning: " + error, file=sys.stderr)
            save_record(provenance, record)
            if record["status"] == "succeeded":
                try:
                    subprocess.run(["docker", "rm", record["container_id"]], check=True,
                                   capture_output=True, text=True, timeout=CONTROL_TIMEOUT)
                    record["container_removed"] = True
                except (OSError, subprocess.SubprocessError) as exc:
                    record["container_removed"] = False
                    print("Could not remove completed container: " + str(exc), file=sys.stderr)
                save_record(provenance, record)
            else:
                print("Container retained for inspection: " + name, file=sys.stderr)
                if record["status"] in ("unknown", "running_after_client_exit"):
                    print("Processing completion is unconfirmed; check docker ps and docker logs.",
                          file=sys.stderr)
        finally:
            signal.signal(signal.SIGINT, previous_handler)
    return rc
