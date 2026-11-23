"""Check the distributed example images without running external executables."""
import argparse
import csv
from pathlib import Path
import sys
import tempfile
import unittest
import re
from unittest.mock import patch

import nibabel as nib
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dots_common import HERE, read_labels, same_grid
from thickness import parse_radius, run_subject, segmentation_path


class ExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.labels = read_labels()
        cls.dot_image = nib.load(HERE / 'dots/EXAMPLE001_PMDots.nii.gz')
        cls.dots = np.asanyarray(cls.dot_image.dataobj)
        cls.coordinates = {number: np.where(cls.dots == number) for number, _ in cls.labels}
        cls.paths = [HERE / 'dots/EXAMPLE001_PMDots.nii.gz',
                     HERE / 'manual_edits/EXAMPLE001_all_dots.nii.gz']
        cls.paths += [HERE / folder / f'EXAMPLE001_manualedit_{code}.nii.gz'
                      for folder in ('manual_edits', 'automated_pancakes')
                      for _, code in cls.labels]

    def test_all_labels_and_clean_headers_preserve_one_grid(self):
        self.assertEqual(set(np.unique(self.dots)), set(range(19)))
        self.assertEqual(len(self.paths), 38)
        for path in self.paths:
            with self.subTest(path=path.name):
                image = nib.load(path)
                same_grid(self.dot_image, image)
                self.assertEqual(image.header.get_xyzt_units()[0], 'mm')
                self.assertEqual(image.get_data_dtype(), np.dtype('uint16'))
                self.assertEqual(len(image.header.extensions), 0)
                self.assertEqual(image.dataobj.slope, 1)
                self.assertEqual(image.dataobj.inter, 0)
                for key in ('descrip', 'aux_file', 'intent_name', 'db_name', 'data_type'):
                    self.assertFalse(image.header[key].tobytes().strip(b'\0'))

    def test_manual_files_exactly_split_the_combined_segmentation(self):
        combined = np.asanyarray(nib.load(HERE / 'manual_edits/EXAMPLE001_all_dots.nii.gz').dataobj)
        for number, code in self.labels:
            with self.subTest(region=code):
                path, kind = segmentation_path(HERE / 'manual_edits', 'EXAMPLE001', code)
                self.assertEqual(kind, 'label')
                data = np.asanyarray(nib.load(path).dataobj)
                np.testing.assert_array_equal(data, np.where(combined == number, number, 0))

    def test_regional_masks_and_qc_report_agree(self):
        with (HERE / 'examples/EXAMPLE001_QC.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 36)
        failures = []
        for row in rows:
            number, code = int(row['dot_label']), row['region']
            with self.subTest(source=row['source'], region=code):
                path, _ = segmentation_path(HERE / row['source'], 'EXAMPLE001', code)
                data = np.asanyarray(nib.load(path).dataobj)
                self.assertTrue(np.isin(data, [0, number]).all())
                count = int(np.count_nonzero(data))
                total = len(self.coordinates[number][0])
                overlap = int(np.count_nonzero(data[self.coordinates[number]] == number))
                self.assertEqual(count, int(row['tissue_voxels']))
                self.assertEqual(total, int(row['dot_voxels']))
                self.assertEqual(overlap, int(row['overlapping_dot_voxels']))
                self.assertEqual(total, overlap)
                if count == total:
                    failures.append((row['source'], code))
                    self.assertEqual(row['qc_status'], 'dot_only_mask')
                else:
                    self.assertEqual(row['qc_status'], 'needs_visual_review')
        self.assertEqual(failures, [('manual_edits', 'ERC')])

    def test_real_manual_erc_is_rejected_before_executables_run(self):
        with tempfile.TemporaryDirectory() as directory:
            args = argparse.Namespace(specimen='EXAMPLE001', root_dir=HERE / 'manual_edits',
                                      work_root=Path(directory), dot_file=None, dots_dir=HERE / 'dots',
                                      assume_mm=False, anatomical_level='', layer='',
                                      seg_file=None, seg_kind='label', seg_label=None)
            with patch('thickness.compute') as invoke:
                rows = run_subject(args, [(14, 'ERC')], {}, {})
            invoke.assert_not_called()
            self.assertEqual(rows[0]['status'], 'error')
            self.assertEqual(rows[0]['thickness_mm'], '')
            self.assertIn('only the dot voxels', rows[0]['notes'])


class ReferenceOutputTests(unittest.TestCase):
    directory = HERE / 'reference_output/thickness/EXAMPLE001/vis'

    def test_reported_radius_agrees_with_sphere_geometry(self):
        report = (self.directory / 'EXAMPLE001_vis_thkmax.txt').read_text()
        radius = parse_radius(report)
        self.assertAlmostEqual(2 * radius, 3.32878)
        center = np.fromstring(re.search(r'Center:\s*\[([^]]+)\]', report)[1], sep=',')
        vtk = (self.directory / 'EXAMPLE001_vis_sphere.vtk').read_text()
        points = re.search(r'POINTS\s+(\d+)\s+\w+\s+', vtk)
        vertices = np.fromstring(vtk[points.end():], sep=' ', count=int(points[1]) * 3).reshape(-1, 3)
        distances = np.linalg.norm(vertices - center, axis=1)
        # The supplied text and mesh coordinates are rounded decimal values.
        np.testing.assert_allclose(distances, radius, atol=1e-4, rtol=0)

    def test_complete_reference_files_have_clean_headers(self):
        self.assertEqual(len(list(self.directory.iterdir())), 13)
        images = list(self.directory.glob('*.nii.gz'))
        self.assertEqual(len(images), 6)
        for path in images:
            image = nib.load(path)
            self.assertEqual(image.shape[:3], (450, 288, 624))
            self.assertEqual(image.header.get_xyzt_units()[0], 'mm')
            self.assertFalse(image.header.extensions)
            for key in ('descrip', 'aux_file', 'intent_name', 'db_name', 'data_type'):
                self.assertFalse(image.header[key].tobytes().strip(b'\0'))


if __name__ == '__main__':
    unittest.main()
