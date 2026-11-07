"""CLI contract and resume regression tests; scientific processing stays in Docker."""
import contextlib
import io
import json
import subprocess
from unittest.mock import patch

import unittest
import test_cli
from purple_mri import cli
from purple_mri.containers import docker_command, validate_run
from purple_mri.runs import ensure_previous_stopped, locked, run_record
from purple_mri.workflows import CONTRASTS, DEFAULT_IMAGE, MODELS


class V120Tests(unittest.TestCase):
    setUp = test_cli.CLITests.setUp
    args = test_cli.CLITests.args

    def dl(self, stages=("11_final_merged", "12_surface_labels")):
        root = self.root / "existing_dl"
        root.mkdir(exist_ok=True)
        for stage in stages:
            (root / stage).mkdir(exist_ok=True)
            (root / stage / "subject.nii.gz").write_bytes(b"labels")
        return root

    def surface(self, hemi="rh"):
        root = self.root / "existing_surface"
        root.mkdir()
        for rel in ("qc/surface_provenance.json", "mri/aseg.mgz", f"surf/{hemi}.white",
                    f"surf/{hemi}.pial", f"label/{hemi}.cortex.label"):
            p = root / "subject" / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("fixture")
        return root

    def test_new_default_and_flash_model(self):
        self.assertEqual(DEFAULT_IMAGE, "pulks/docker_purple_mri:v1.2.0")
        self.assertEqual(MODELS["exvivo_flash_gm_wm"][0], 278)

    def test_all_contrasts_and_hemispheres_full_pipeline(self):
        for contrast in CONTRASTS:
            for hemi in ("lh", "rh"):
                with self.subTest(contrast=contrast, hemi=hemi):
                    a = self.args(["exvivo_dl", "exvivo_surface"],
                        ("--contrast", contrast, "--hemi", hemi, "--license", str(self.license)))
                    cmd = docker_command(a)
                    self.assertEqual(cmd[cmd.index("--contrast") + 1], contrast)
                    self.assertIn("EXVIVO_HEMI=" + hemi, cmd)
                    for env in ("EXVIVO_DL_OUTPUT_DIR=/output/dl", "EXVIVO_SURFACE_OUTPUT_DIR=/output/surface",
                                "EXVIVO_ATLAS_OUTPUT_DIR=/output/atlases"):
                        self.assertIn(env, cmd)
                    self.assertNotIn("EXVIVO_SEGM_DIR=/segmentations", cmd)

    def test_contrast_required_except_individual(self):
        a = self.args(); a.contrast = None
        with self.assertRaisesRegex(ValueError, "--contrast"):
            validate_run(a)
        a.stages = ["exvivo_multi_sequence_subcortical"]
        self.assertNotIn("--contrast", docker_command(a))
        a.stages = ["exvivo_flash_gm_wm"]
        cmd = docker_command(a)
        self.assertEqual(cmd[cmd.index("--contrast") + 1], "flash")
        a.contrast = "ciss"
        with self.assertRaisesRegex(ValueError, "Task278"):
            validate_run(a)

    def test_old_segmentation_flag_has_migration_message(self):
        a = self.args(extra=("--segmentation", str(self.root)))
        with self.assertRaisesRegex(ValueError, "complete DL root"):
            validate_run(a)

    def test_preflight_no_gpu_and_forwards_options(self):
        a = self.args(extra=("--preflight-only", "--save-qc-volumes", "--max-roi-voxels", "1000"))
        cmd = docker_command(a)
        self.assertNotIn("--gpus", cmd)
        self.assertIn("--preflight-only", cmd)
        self.assertIn("--save-qc-volumes", cmd)
        self.assertEqual(cmd[-2:], ["--max-roi-voxels", "1000"])

    def test_atlas_only_mounts_reused_inputs_readonly(self):
        dl, surface = self.dl(), self.surface()
        a = self.args(["exvivo_atlas_merge"], ("--hemi", "rh", "--license", str(self.license),
                 "--dl-dir", str(dl), "--surface-dir", str(surface)))
        cmd = docker_command(a)
        self.assertNotIn("--gpus", cmd)
        self.assertIn(f"type=bind,src={dl},dst=/reuse_dl,readonly", cmd)
        self.assertIn(f"type=bind,src={surface},dst=/reuse_surface,readonly", cmd)
        self.assertIn("EXVIVO_ATLAS_OUTPUT_DIR=/output/atlases", cmd)
        self.assertEqual(cmd[cmd.index("/src/commands_nnunet_inference.sh")+1], "exvivo_atlas_merge")

    def test_missing_atlas_provenance_rejected(self):
        dl, surface = self.dl(), self.surface()
        (surface / "subject/qc/surface_provenance.json").unlink()
        with self.assertRaisesRegex(ValueError, "surface_provenance"):
            validate_run(self.args(["exvivo_atlas_merge"], ("--hemi", "rh", "--license", str(self.license),
                "--dl-dir", str(dl), "--surface-dir", str(surface))))

    def test_merge_only_uses_contrast_specific_existing_predictions(self):
        dl = self.dl(("05_purple_corrected", "06_mtl", "07_subcortical", "13_flash_task278"))
        a = self.args(["exvivo_merge"], ("--dl-dir", str(dl)))
        self.assertNotIn("--gpus", docker_command(a))
        a.contrast = "t2w"
        with self.assertRaisesRegex(ValueError, "03_topology_prediction"):
            validate_run(a)
        self.dl(("03_topology_prediction",))
        self.assertNotIn("--gpus", docker_command(a))

    def test_reuse_paths_must_not_overlap(self):
        dl = self.dl()
        a = self.args(["exvivo_merge"], ("--dl-dir", str(dl)))
        a.output = str(dl / "new")
        with self.assertRaisesRegex(ValueError, "must not overlap"):
            validate_run(a)

    def test_external_label_symlink_rejected(self):
        dl = self.dl()
        p = dl / "12_surface_labels/subject.nii.gz"
        p.unlink(); p.symlink_to(self.source / "subject_0000.nii.gz")
        a = self.args(["exvivo_surface"], ("--dl-dir", str(dl), "--hemi", "rh", "--license", str(self.license)))
        with self.assertRaisesRegex(ValueError, "mounted directory"):
            validate_run(a)

    def test_resume_requires_existing_cli_record(self):
        with self.assertRaisesRegex(ValueError, "existing v1.2.0 CLI run"):
            validate_run(self.args(extra=("--resume",)))

    def test_resume_individual_and_preflight_rejected(self):
        for a in (self.args(["exvivo_flash_gm_wm"], ("--resume",)),
                  self.args(extra=("--resume", "--preflight-only"))):
            with self.assertRaisesRegex(ValueError, "--resume applies"):
                validate_run(a)

    def test_resume_checks_image_inputs_options_and_retains_attempt(self):
        a = self.args(); image = {"Id": "sha256:" + "a" * 64}
        with run_record(a, image) as (p, old):
            old["status"] = "failed"
            p.write_text(json.dumps(old))
        original = p.read_bytes()
        a.resume = True
        for key, value in (("contrast", "ciss"), ("hemi", "lh"), ("threads", 4), ("save_qc_volumes", True)):
            before = getattr(a, key); setattr(a, key, value)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "differ"):
                with run_record(a, image):
                    self.fail("mismatched resume was accepted")
            setattr(a, key, before)
            self.assertEqual(p.read_bytes(), original)
        with self.assertRaisesRegex(ValueError, "differ"):
            with run_record(a, {"Id": "sha256:" + "b" * 64}):
                self.fail("changed image was accepted")
        scan = self.source / "subject_0000.nii.gz"
        previous = scan.read_bytes(); scan.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "differ"):
            with run_record(a, image):
                self.fail("changed input was accepted")
        scan.write_bytes(previous)
        with run_record(a, image) as (_, new):
            self.assertEqual(new["request"], old["request"])
            self.assertEqual((self.output / new["previous_attempt"]).read_bytes(), original)
            self.assertIn("--resume", docker_command(a))

    def test_concurrent_cli_run_rejected(self):
        self.output.mkdir()
        with locked(self.output / ".purple_cli.lock"):
            with self.assertRaisesRegex(ValueError, "run lock"):
                with locked(self.output / ".purple_cli.lock"):
                    self.fail("concurrent writer accepted")

    def test_resume_does_not_restart_active_previous_container(self):
        old = {"run_id": "r", "container_id": "a" * 64, "container_name": "purple-mri-r", "image_id": "img"}
        with patch("purple_mri.runs.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "a" * 64)), \
             patch("purple_mri.runs.inspect_owned", return_value={"State": {"Running": True, "Status": "running"}}):
            with self.assertRaisesRegex(ValueError, "still active"):
                ensure_previous_stopped(old)

    def test_preflight_is_distinguished_in_provenance(self):
        with run_record(self.args(extra=("--preflight-only",)), {"Id": "sha256:" + "a" * 64}) as (_, record):
            self.assertEqual(record["kind"], "preflight")
            self.assertTrue(record["request"]["preflight_only"])
