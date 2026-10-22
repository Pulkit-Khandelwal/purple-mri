"""Exercise installed-style native helper dispatch without neuroimaging tools."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class LegacyShellTests(unittest.TestCase):
    def test_helper_failure_stops_pipeline_from_unrelated_cwd(self):
        source = Path(__file__).resolve().parents[1] / "pkg_src/purple_mri/scripts/run_surface_pipeline.sh"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copy(source, scripts / source.name)
            for name in ("fs", "mri", "seg", "atlas", "elsewhere"):
                (root / name).mkdir()
            (root / "mri/subject.nii.gz").write_bytes(b"x")
            (root / "seg/subject.nii.gz").write_bytes(b"x")
            (root / "stats.dat").write_bytes(b"x")
            (scripts / "prepare_segm_files.sh").write_text("#!/bin/bash\nexit 17\n")
            # Later helpers are deliberately absent: a continued run would fail differently.
            args = [str(root / name) for name in ("fs", "output", "mri", "seg", "atlas")]
            result = subprocess.run(["bash", str(scripts / source.name), *args, "8", str(root / "stats.dat")],
                                    cwd=root / "elsewhere", capture_output=True, text=True)
            self.assertEqual(result.returncode, 17, result.stderr)

    def test_no_arguments_exits_with_usage(self):
        source = Path(__file__).resolve().parents[1] / "pkg_src/purple_mri/scripts/run_surface_pipeline.sh"
        result = subprocess.run(["bash", str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)


if __name__ == "__main__":
    unittest.main()
