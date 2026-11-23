"""Synthetic regression tests; no external thickness executable is run."""
import argparse
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import nibabel as nib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dots_common import HERE, load_volume, read_labels, read_manifest, safe_name
from prepare_pancakes import prepare
from thickness import (BINARIES, Runner, binary_paths, compute, exact_file,
                       parse_radius, run_subject, segmentation_path)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dots test ")
        self.root = Path(self.temp.name)
        self.affine = np.diag([0.3, 0.4, 0.5, 1.0])
        self.affine[:3, 3] = [4, -3, 8]
        self.seg = np.zeros((12, 13, 14), dtype=np.uint16)
        self.seg[0:10, 0:11, 0:12] = 2
        self.seg[4:7, 4:7, 4:7] = 3
        self.dots = np.zeros_like(self.seg)
        self.dots[1, 1, 1] = 1
        self.dots[3, 3, 3] = 2
        self.seg_path = self.write("seg.nii.gz", self.seg)
        self.dots_path = self.write("dots.nii.gz", self.dots)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, filename, data, affine=None, units="mm"):
        path = self.root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        image = nib.Nifti1Image(data, self.affine if affine is None else affine)
        image.set_qform(image.affine, 1)
        image.set_sform(image.affine, 2)
        image.header.set_xyzt_units(units)
        nib.save(image, path)
        return path

    def prep(self, **kwargs):
        options = dict(specimen="SUBJECT001", dots_file=self.dots_path,
                       segmentation_file=self.seg_path, output_dir=self.root / "prepared",
                       labels=[(1, "vis"), (2, "Mot")], tissue_labels=[2], half_width=3)
        options.update(kwargs)
        return prepare(**options)

    def test_labels_match_itksnap(self):
        labels = read_labels()
        self.assertEqual(len(labels), 18)
        self.assertEqual(labels[14], (15, "BA35"))
        import shlex
        snap = {}
        for line in (HERE / "PMdots_Labels.txt").read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                fields = shlex.split(line)
                if int(fields[0]):
                    snap[int(fields[0])] = fields[-1]
        self.assertEqual(dict(labels), snap)

    def test_label_map_rejects_case_duplicates_and_prefix_names_work(self):
        path = self.root / "map.txt"
        path.write_text("1 region\n2 REGION\n")
        with self.assertRaises(ValueError):
            read_labels(path)
        path.write_text("1 region\n2 region_more\n")
        self.assertEqual(len(read_labels(path)), 2)

    def test_identifiers_cannot_escape_output_root(self):
        for name in ("../private", "a/b", "a b", "x;cmd"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_name(name)

    def test_edge_box_is_clipped_and_geometry_preserved(self):
        rows = self.prep()
        result = nib.load(rows[0]["output_file"])
        expected = np.zeros_like(self.seg)
        expected[0:4, 0:4, 0:4] = self.seg[0:4, 0:4, 0:4] == 2
        np.testing.assert_array_equal(result.get_fdata(), expected)
        np.testing.assert_allclose(result.affine, nib.load(self.seg_path).affine)
        self.assertEqual(result.header.get_xyzt_units()[0], "mm")
        self.assertEqual(int(result.header["qform_code"]), 1)
        self.assertEqual(int(result.header["sform_code"]), 2)
        self.assertEqual(result.get_data_dtype(), np.dtype("uint16"))
        self.assertIn("box_clipped_at_image_edge", rows[0]["notes"])

    def test_selected_tissue_and_overlapping_regions_remain_separate(self):
        rows = self.prep(half_width=5)
        first = nib.load(rows[0]["output_file"]).get_fdata()
        second = nib.load(rows[1]["output_file"]).get_fdata()
        self.assertTrue(np.any((first > 0) & (second > 0)))
        self.assertEqual(set(np.unique(first)), {0, 1})
        self.assertEqual(set(np.unique(second)), {0, 2})
        self.assertTrue(np.all(second[self.seg == 3] == 0))
        self.assertFalse(list((self.root / "prepared").rglob("*all_dots*")))

    def test_missing_dot_has_no_output_and_outside_tissue_is_explicit(self):
        rows = self.prep(labels=[(1, "vis"), (9, "absent")], tissue_labels=[3])
        self.assertEqual(rows[0]["status"], "dot_outside_tissue")
        self.assertEqual(rows[1]["status"], "missing_dot")
        self.assertEqual(rows[0]["output_file"], "")
        self.assertEqual(rows[1]["output_file"], "")

    def test_partial_overlap_is_flagged(self):
        self.dots[10, 1, 1] = 1
        self.write("dots.nii.gz", self.dots)
        rows = self.prep(half_width=20)
        self.assertIn("partial_dot_overlap", rows[0]["notes"])

    def test_centroid_is_opt_in_and_uses_an_existing_dot_voxel(self):
        self.dots[:] = 0
        self.dots[1:5, 1, 1] = 1
        self.write("dots.nii.gz", self.dots)
        self.prep(center="centroid", labels=[(1, "vis")])
        record = json.loads((self.root / "prepared/SUBJECT001/preparation.json").read_text())
        center = record["boxes"]["vis"]["center_voxel"]
        self.assertEqual(center, [2, 1, 1])
        self.assertEqual(self.dots[tuple(center)], 1)

    def test_unknown_units_require_explicit_assumption(self):
        path = self.write("unknown.nii.gz", self.dots, units="unknown")
        with self.assertRaises(ValueError):
            load_volume(path)
        _, _, notes = load_volume(path, assume_mm=True)
        self.assertEqual(notes, ["unknown_units_assumed_mm"])
        path = self.write("meters.nii.gz", self.dots, units="meter")
        with self.assertRaises(ValueError):
            load_volume(path, assume_mm=True)

    def test_grid_mismatch_is_rejected_before_writing_masks(self):
        affine = self.affine.copy()
        affine[0, 3] += 0.3
        other = self.write("other.nii.gz", self.dots, affine)
        with self.assertRaisesRegex(ValueError, "same shape and affine"):
            self.prep(dots_file=other)
        self.assertFalse((self.root / "prepared").exists())

    def test_continuous_labels_nan_and_empty_tissue_are_rejected(self):
        data = self.seg.astype(float)
        data[1, 1, 1] = 2.5
        path = self.write("fractional.nii.gz", data)
        with self.assertRaises(ValueError):
            self.prep(segmentation_file=path)
        data[1, 1, 1] = np.nan
        path = self.write("nan.nii.gz", data)
        with self.assertRaises(ValueError):
            load_volume(path)
        with self.assertRaises(ValueError):
            self.prep(tissue_labels=[99])

    def test_existing_preparation_is_not_overwritten(self):
        self.prep()
        with self.assertRaises(FileExistsError):
            self.prep()

    def test_manifest_paths_resolve_from_manifest_parent(self):
        manifest = self.root / "config" / "batch.tsv"
        manifest.parent.mkdir()
        manifest.write_text("specimen_id\tdots_file\tsegmentation_file\ttissue_labels\n"
                            "SUBJECT001\t../dots.nii.gz\t../seg.nii.gz\t2,3\n")
        row = read_manifest(manifest, ["specimen_id", "dots_file", "segmentation_file", "tissue_labels"])[0]
        self.assertEqual(Path(row["dots_file"]), self.dots_path)
        manifest.write_text(manifest.read_text() + "SUBJECT001\t../dots.nii.gz\t../seg.nii.gz\t2\n")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            read_manifest(manifest, ["specimen_id"])

    def test_matching_is_exact_prioritized_and_rejects_ambiguity(self):
        root = self.root / "regional"
        root.mkdir()
        pancake = root / "SUBJECT001_pancake_vis.nii.gz"
        pancake.touch()
        self.assertEqual(segmentation_path(root, "SUBJECT001", "vis"), (pancake, "levelset"))
        manual = root / "SUBJECT001_manualedit_vis.nii.gz"
        manual.touch()
        self.assertEqual(segmentation_path(root, "SUBJECT001", "vis"), (manual, "label"))
        self.assertIsNone(exact_file(root, "SUBJECT00_manualedit_vis.nii.gz"))
        (root / "duplicate").mkdir()
        (root / "duplicate" / manual.name).touch()
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            segmentation_path(root, "SUBJECT001", "vis")

    def test_radius_parsing_rejects_invalid_and_ambiguous_output(self):
        self.assertEqual(parse_radius("Maximal sphere Radius: 1.25\n"), 1.25)
        for text in ("", "Radius: 1.25", "Maximal sphere Radius: nan", "Maximal sphere Radius: 0",
                     "Maximal sphere Radius: -1", "Maximal sphere Radius: 1\nMaximal sphere Radius: 2"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_radius(text)

    def test_command_sequence_and_radius_to_diameter(self):
        class RecordingRunner:
            binaries = {"qvoronoi": Path("/example binaries/qvoronoi")}
            def __init__(self):
                self.calls = []
            def run(self, tool, *args, stdout_file=None, outputs=()):
                self.calls.append((tool, tuple(map(str, args))))
                if stdout_file:
                    Path(stdout_file).write_text("Maximal sphere Radius: 1.25\n")
        runner = RecordingRunner()
        radius, diameter = compute(runner, "my mask.nii.gz", "label", 15,
                                   "my dots.nii.gz", 15, self.root / "example")
        self.assertEqual((radius, diameter), (1.25, 2.5))
        self.assertEqual([tool for tool, _ in runner.calls],
                         ["c3d", "vtklevelset", "mesh_smooth_curv", "cmrep_vskel", "tetfill",
                          "tetfill", "c3d", "vtklevelset", "c3d", "c3d", "skel_tetra_max_thick_sphere"])
        self.assertEqual(runner.calls[2][1][:6], ("-mu", "-0.51", "-lambda", "0.5", "-iter", "200"))
        self.assertIn("VoronoiRadius", runner.calls[4][1])
        self.assertIn("VoronoiCenter", runner.calls[5][1])
        self.assertIn("1x1x1", runner.calls[8][1])
        self.assertIn("1x1x1", runner.calls[9][1])
        self.assertEqual(runner.calls[0][1][2:4], ("15", "15"))
        runner = RecordingRunner()
        compute(runner, "levelset.nii.gz", "levelset", 1, "dots.nii.gz", 1, self.root / "levelset")
        self.assertEqual(runner.calls[0][1][2:4], ("-inf", "0"))
        self.assertEqual(runner.calls[1][1][-1], "0.0")

    def test_runner_keeps_paths_as_arguments_and_stops_on_command_failure(self):
        binaries = {name: self.root / "bin tools" / name for name in BINARIES}
        runner = Runner(binaries, io.StringIO())
        with patch("thickness.subprocess.run") as invoke:
            runner.run("c3d", "path with spaces;literal.nii.gz", "-info")
            command = invoke.call_args.args[0]
            self.assertEqual(command[1], "path with spaces;literal.nii.gz")
            self.assertNotIn("shell", invoke.call_args.kwargs)
        with patch("thickness.subprocess.run", side_effect=subprocess.CalledProcessError(1, ["c3d"])):
            with self.assertRaises(subprocess.CalledProcessError):
                runner.run("c3d", "test")

    def test_missing_binaries_report_the_actual_paths(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "Missing or non-executable"):
                binary_paths(self.root / "empty binaries")

    def subject_args(self):
        return argparse.Namespace(specimen="SUBJECT001", root_dir=self.root,
                                  work_root=self.root / "work", dot_file=self.dots_path,
                                  dots_dir=None, assume_mm=False, anatomical_level="", layer="",
                                  seg_file=None, seg_kind="label", seg_label=None)

    def test_missing_rows_are_blank_and_old_results_are_not_reused(self):
        args = self.subject_args()
        rows = run_subject(args, [(1, "vis"), (9, "absent")], {}, {})
        self.assertEqual([row["status"] for row in rows], ["missing_segmentation", "missing_dot"])
        self.assertTrue(all(row["thickness_mm"] == "" for row in rows))
        with self.assertRaises(FileExistsError):
            run_subject(args, [(1, "vis")], {}, {})
        result = json.loads((args.work_root / "thickness/SUBJECT001/vis/result.json").read_text())
        self.assertEqual(result["qc_status"], "unavailable")

    def test_success_is_needs_review_and_command_failure_stays_missing(self):
        args = self.subject_args()
        self.write("SUBJECT001_manualedit_vis.nii.gz", (self.seg == 2).astype(np.uint16))
        binaries = {name: self.root / name for name in BINARIES}
        with patch("thickness.compute", return_value=(1.25, 2.5)):
            rows = run_subject(args, [(1, "vis")], binaries, {})
        self.assertEqual(rows[0]["thickness_mm"], 2.5)
        self.assertEqual(rows[0]["qc_status"], "needs_review")
        args.work_root = self.root / "failed work"
        with patch("thickness.compute", side_effect=subprocess.CalledProcessError(1, ["tetfill"])):
            rows = run_subject(args, [(1, "vis")], binaries, {})
        self.assertEqual(rows[0]["status"], "error")
        self.assertEqual(rows[0]["thickness_mm"], "")

    def test_dot_only_mask_cannot_produce_a_thickness(self):
        args = self.subject_args()
        self.write("SUBJECT001_manualedit_vis.nii.gz", (self.dots == 1).astype(np.uint16))
        with patch("thickness.compute") as invoke:
            rows = run_subject(args, [(1, "vis")], {}, {})
        invoke.assert_not_called()
        self.assertEqual(rows[0]["status"], "error")
        self.assertEqual(rows[0]["thickness_mm"], "")
        self.assertIn("only the dot voxels", rows[0]["notes"])

    def test_cli_help_and_batch_preparation_with_spaces(self):
        script = HERE / "runme.sh"
        result = subprocess.run(["bash", str(script), "--help"], cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        manifest = self.root / "batch.tsv"
        manifest.write_text("specimen_id\tdots_file\tsegmentation_file\ttissue_labels\n"
                            "SUBJECT001\tdots.nii.gz\tseg.nii.gz\t2\n")
        result = subprocess.run([sys.executable, str(HERE / "prepare_pancakes.py"),
                                 "--manifest", str(manifest), "--output-dir", str(self.root / "batch output"),
                                 "--regions", "vis", "Mot"], cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        with (self.root / "batch output/preparation.csv").open() as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 2)

    def test_manual_edits_folder_without_spaces(self):
        args = self.subject_args()
        args.root_dir = self.root / "manual_edits"
        self.write("manual_edits/SUBJECT001_manualedit_vis.nii.gz",
                   (self.seg == 2).astype(np.uint16))
        binaries = {name: self.root / name for name in BINARIES}
        with patch("thickness.compute", return_value=(1.25, 2.5)) as invoke:
            rows = run_subject(args, [(1, "vis")], binaries, {})
        self.assertEqual(rows[0]["status"], "ok")
        self.assertEqual(invoke.call_args.args[1].parent.name, "manual_edits")

    def test_runme_prepare_single_and_batch(self):
        command = ["bash", str(HERE / "runme.sh"), "prepare"]
        output = self.root / "automated_pancakes"
        result = subprocess.run(command + ["--specimen", "SUBJECT001", "--dots", str(self.dots_path),
                               "--segmentation", str(self.seg_path), "--tissue-labels", "2",
                               "--regions", "vis", "--output-dir", str(output)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        single = nib.load(output / "SUBJECT001/SUBJECT001_manualedit_vis.nii.gz").get_fdata()
        manifest = self.root / "prepare.tsv"
        manifest.write_text("specimen_id\tdots_file\tsegmentation_file\ttissue_labels\n"
                            "SUBJECT001\tdots.nii.gz\tseg.nii.gz\t2\n")
        output = self.root / "batch pancakes"
        result = subprocess.run(command + ["--manifest", str(manifest), "--regions", "vis",
                               "--output-dir", str(output)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        batch = nib.load(output / "SUBJECT001/SUBJECT001_manualedit_vis.nii.gz").get_fdata()
        np.testing.assert_array_equal(single, batch)

    def test_prepare_rejects_incomplete_or_conflicting_cli_inputs(self):
        command = ["bash", str(HERE / "runme.sh"), "prepare"]
        for arguments in (["--specimen", "SUBJECT001"],
                          ["--manifest", "unused.tsv", "--tissue-labels", "1"]):
            result = subprocess.run(command + arguments, capture_output=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
