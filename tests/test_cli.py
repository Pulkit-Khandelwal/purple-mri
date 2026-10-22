import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from purple_mri import cli
from purple_mri.containers import docker_command, validate_run
from purple_mri.workflows import DEFAULT_IMAGE, MODELS, validate_stages


class CLITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "input with spaces"
        self.source.mkdir()
        (self.source / "subject_0000.nii.gz").write_bytes(b"fixture-not-a-real-volume")
        self.output = self.root / "results"
        self.license = self.root / "license.txt"
        self.license.write_text("fixture")

    def args(self, stages=None, extra=()):
        return cli.parser().parse_args(["run", *(stages or ["exvivo_dl"]),
            "--input", str(self.source), "--output", str(self.output), *extra])

    def quiet(self, argv):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(argv)

    def test_no_arguments_prints_help(self):
        self.assertEqual(self.quiet([]), 0)

    def test_model_selection(self):
        self.assertEqual(MODELS["exvivo_multi_sequence_subcortical"][0], 2732)
        self.assertEqual(self.quiet(["models"]), 0)

    def test_stage_sequences(self):
        for stages in (["exvivo_dl"], ["exvivo_all", "exvivo_surface"]):
            validate_stages(stages)
        for stages in ([], ["exvivo_surface", "exvivo_dl"], ["exvivo_dl_infant"], ["exvivo_dl", "exvivo_dl"]):
            with self.subTest(stages=stages), self.assertRaises(ValueError):
                validate_stages(stages)

    def test_docker_argv_readonly_and_spaces(self):
        cmd = docker_command(self.args())
        self.assertIn(f"type=bind,src={self.source},dst=/inputs,readonly", cmd)
        self.assertIn("EXVIVO_MODEL_OUTPUT_DIR=/outputs/predictions", cmd)
        self.assertIn("--gpus", cmd)
        self.assertEqual(cmd[-3:], [DEFAULT_IMAGE, "/src/commands_nnunet_inference.sh", "exvivo_dl"])

    def test_combined_requires_hemisphere_and_license(self):
        for extra in ((), ("--hemi", "rh"), ("--license", str(self.license))):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                validate_run(self.args(["exvivo_dl", "exvivo_surface"], extra))

    def test_both_hemispheres(self):
        for hemi in ("lh", "rh"):
            cmd = docker_command(self.args(["exvivo_dl", "exvivo_surface"],
                ("--hemi", hemi, "--license", str(self.license))))
            self.assertIn("EXVIVO_HEMI=" + hemi, cmd)
            self.assertIn("FS_LICENSE=/license.txt", cmd)

    def test_surface_only_requires_segmentation(self):
        with self.assertRaises(ValueError):
            validate_run(self.args(["exvivo_surface"], ("--hemi", "rh", "--license", str(self.license))))

    def test_surface_only_matches_filename_and_no_gpu(self):
        seg = self.root / "seg"
        seg.mkdir()
        args = self.args(["exvivo_surface"], ("--hemi", "lh", "--license", str(self.license), "--segmentation", str(seg)))
        with self.assertRaises(ValueError):
            validate_run(args)
        (seg / "subject.nii.gz").write_bytes(b"seg")
        cmd = docker_command(args)
        self.assertNotIn("--gpus", cmd)
        self.assertIn("EXVIVO_SEGM_DIR=/segmentations", cmd)

    def test_no_seg_override_in_combined(self):
        with self.assertRaises(ValueError):
            validate_run(self.args(["exvivo_dl", "exvivo_surface"],
                ("--hemi", "rh", "--license", str(self.license), "--segmentation", str(self.root))))

    def test_nonempty_output_rejected(self):
        self.output.mkdir()
        (self.output / "existing.txt").write_text("do not overwrite")
        with self.assertRaises(ValueError):
            validate_run(self.args())

    def test_nested_output_rejected(self):
        args = self.args(); args.output = str(self.source / "outputs")
        with self.assertRaises(ValueError):
            validate_run(args)

    def test_invalid_filename_rejected(self):
        (self.source / "bad name_0000.nii.gz").write_bytes(b"x")
        with self.assertRaises(ValueError):
            validate_run(self.args())

    def test_external_symlink_rejected(self):
        (self.root / "external.nii.gz").write_bytes(b"x")
        (self.source / "external_0000.nii.gz").symlink_to(self.root / "external.nii.gz")
        with self.assertRaises(ValueError):
            validate_run(self.args())

    def test_invalid_mount_path_rejected(self):
        args = self.args(); args.output = str(self.root / "comma,dir")
        with self.assertRaises(ValueError):
            validate_run(args)

    def test_dry_run_never_calls_subprocess_or_writes(self):
        args = self.args(extra=("--dry-run", "--pull"))
        with patch("purple_mri.cli.subprocess.run") as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.run_container(args), 0)
        run.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_error_propagation_and_immutable_id(self):
        image_id = "sha256:" + "a" * 64
        responses = [subprocess.CompletedProcess([], 0),
            subprocess.CompletedProcess([], 0, json.dumps([{"Id": image_id, "RepoDigests": ["example@sha256:abc"]}]))]
        with patch("purple_mri.cli.shutil.which", return_value="/bin/docker"), \
             patch("purple_mri.cli.subprocess.run", side_effect=responses) as run, \
             patch("purple_mri.cli.execute_container", return_value=7) as execute, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.run_container(self.args(extra=("--pull",))), 7)
        self.assertEqual(run.call_args_list[0].args[0], ["docker", "pull", DEFAULT_IMAGE])
        self.assertIn(image_id, execute.call_args.args[0])
        self.assertNotIn(DEFAULT_IMAGE, execute.call_args.args[0])
        record = json.loads((self.output / "purple_run.json").read_text())
        self.assertIsNone(record["exit_code"])
        self.assertEqual(record["image_id"], image_id)

    def test_pull_failure_stops_before_output(self):
        with patch("purple_mri.cli.shutil.which", return_value="/bin/docker"), \
             patch("purple_mri.cli.subprocess.run", side_effect=subprocess.CalledProcessError(9, ["docker", "pull"])):
            rc = self.quiet(["run", "exvivo_dl", "--input", str(self.source),
                             "--output", str(self.output), "--pull"])
        self.assertEqual(rc, 9)
        self.assertFalse(self.output.exists())

    def test_missing_docker_actionable(self):
        with patch("purple_mri.cli.shutil.which", return_value=None):
            self.assertEqual(self.quiet(["doctor"]), 2)

    def test_positive_threads(self):
        self.assertEqual(cli.positive_int("20"), 20)
        for value in ("0", "-2", "abc"):
            with self.subTest(value=value), self.assertRaises(Exception):
                cli.positive_int(value)

    def test_legacy_seven_args_dispatch_and_exit(self):
        with patch("purple_mri.cli.legacy_surface", return_value=4) as legacy:
            self.assertEqual(self.quiet(["/fs", "/out", "/mri", "/seg", "/atlas", "20", "/stats"]), 4)
            self.assertEqual(legacy.call_args.args[0].stats, "/stats")


class MetadataTests(unittest.TestCase):
    def test_root_and_subdirectory_project_metadata_match(self):
        try:
            import tomllib
        except ImportError:
            self.skipTest("metadata comparison uses Python 3.11+ tomllib")
        root = Path(__file__).resolve().parents[1]
        a = tomllib.loads((root / "pyproject.toml").read_text())["project"]
        b = tomllib.loads((root / "pkg_src/pyproject.toml").read_text())["project"]
        a.pop("readme"); b.pop("readme")
        self.assertEqual(a, b)

    def test_repository_launcher_selects_task2732(self):
        root = Path(__file__).resolve().parents[1]
        script = (root / "docker/docker_files/commands_nnunet_inference.sh").read_text()
        self.assertIn('predict 2732 "$INPUT_DIR"', script)
        self.assertIn('exvivo_multi_sequence_subcortical) task=2732', script)
        checker = (root / "docker/docker_files/check_build_inputs.py").read_text()
        self.assertIn('(101, 269, 2732, 276, 279, 283, 289, 451)', checker)


if __name__ == "__main__":
    unittest.main()
