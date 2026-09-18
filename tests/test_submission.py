"""Submission artifacts must be self-contained, traceable and explicitly draft."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load_builder():
    path = ROOT / 'tools/build_submission.py'
    if not path.is_file():
        raise AssertionError('Submission archive builder has not been implemented')
    spec = importlib.util.spec_from_file_location('submission_builder', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SubmissionPackageTests(unittest.TestCase):
    def fixture(self, directory):
        root = Path(directory) / 'source'
        (root / 'submission').mkdir(parents=True)
        (root / 'submission/metadata.json').write_text(json.dumps({
            'version': '0.1.0-draft.1', 'status': 'DRAFT',
            'license': {'status': 'pending_author_confirmation'},
            'manuscript_title': None, 'authors': [], 'doi': None,
        }))
        (root / 'README.md').write_text('# Test source\n')
        (root / 'old.ipynb').write_text('not for release')
        (root / 'figure.pdf').write_text('not for release')
        (root / 'secret.tmp').write_text('not for release')
        (root / 'submission/package_files.json').write_text(json.dumps({
            'files': ['README.md', 'submission/metadata.json', 'submission/package_files.json'],
        }))
        return root

    def test_archive_is_allowlisted_reproducible_and_records_hashes(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            source = {'revision': 'a' * 40, 'dirty': False, 'kind': 'git'}
            one = builder.build_archive(root, Path(directory) / 'one', source)
            two = builder.build_archive(root, Path(directory) / 'two', source)
            self.assertEqual(one.read_bytes(), two.read_bytes())
            self.assertIn('DRAFT', one.name)
            with zipfile.ZipFile(one) as archive:
                names = set(archive.namelist())
                self.assertNotIn('old.ipynb', names)
                self.assertNotIn('secret.tmp', names)
                manifest = json.loads(archive.read('PACKAGE_MANIFEST.json'))
                self.assertEqual(manifest['source']['revision'], 'a' * 40)
                self.assertEqual(manifest['status'], 'DRAFT')
                for name, expected in manifest['sha256'].items():
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)
            checksum = one.with_suffix('.zip.sha256').read_text().split()[0]
            self.assertEqual(checksum, hashlib.sha256(one.read_bytes()).hexdigest())
            with self.assertRaises(FileExistsError):
                builder.build_archive(root, Path(directory) / 'one', source)

    def test_invalid_missing_duplicate_and_outside_paths_are_rejected(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            for files in [['../secret.txt'], ['/absolute'], ['C:/absolute'], ['missing.py'], ['README.md', 'README.md'], ['old.ipynb'], ['figure.pdf']]:
                (root / 'submission/package_files.json').write_text(json.dumps({'files': files}))
                with self.subTest(files=files), self.assertRaises((ValueError, FileNotFoundError)):
                    builder.build_archive(root, Path(directory) / 'out', {'revision':'a'*40, 'dirty':False, 'kind':'git'})

    def test_unconfirmed_metadata_cannot_be_silently_promoted_to_final(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            path = root / 'submission/metadata.json'
            metadata = json.loads(path.read_text())
            metadata['status'] = 'FINAL'
            path.write_text(json.dumps(metadata))
            with self.assertRaises(ValueError):
                builder.build_archive(root, Path(directory) / 'out', {'revision':'a'*40, 'dirty':False, 'kind':'git'})

    def test_extracted_archive_verifies_before_repackaging(self):
        builder = load_builder()
        with tempfile.TemporaryDirectory() as directory:
            root = self.fixture(directory)
            archive = builder.build_archive(root, Path(directory) / 'out', {'revision':'a'*40, 'dirty':False, 'kind':'git'})
            target = Path(directory) / 'extracted'
            with zipfile.ZipFile(archive) as stream:
                stream.extractall(target)
            self.assertEqual(builder.source_info(target)['revision'], 'a'*40)
            (target / 'README.md').write_text('changed')
            with self.assertRaises(ValueError):
                builder.source_info(target)

    def test_submission_inventory_contains_inputs_and_excludes_legacy_notebooks(self):
        builder = load_builder()
        files = builder.selected_files(ROOT)
        for required in ('yeast/repressor/data/experiment_data.csv',
                         'yeast/combinatorial/data/Supplementary_Note_11_plot_data.csv',
                         'mammalian/Scripts/model_core.py', 'tests/test_submission.py',
                         'yeast/analysis.py', 'submission/requirements-lock.txt'):
            self.assertIn(required, files)
        self.assertFalse(any(name.endswith('.ipynb') for name in files))
        self.assertNotIn('tests/test_legacy_notebooks.py', files)
        self.assertFalse(any(name.endswith(('.pdf', '.png', '.svg', '.docx')) for name in files))
        self.assertNotIn('yeast_analysis.py', files)
        self.assertFalse(any('Output/' in name or '.runtime/' in name or '__pycache__' in name for name in files))

    def test_demo_runs_both_supplied_datasets_from_any_working_directory(self):
        script = ROOT / 'tools/run_submission_demo.py'
        self.assertTrue(script.is_file(), 'Submission demo runner must exist')
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'results'
            result = subprocess.run([sys.executable, str(script), '--output-dir', str(target)],
                                    cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            report = json.loads((target / 'demo_report.json').read_text())
            self.assertEqual(report['status'], 'PASS')
            self.assertEqual(report['checks']['note10_observations'], 1141)
            self.assertEqual(report['checks']['note11_observations'], 216)
            self.assertEqual(len(report['checks']['note11_panels']), 12)
            self.assertEqual(set(report['not_run']), {'activator_experimental', 'mammalian_experimental'})
            self.assertGreater(report['elapsed_seconds'], 0)
            spec = importlib.util.spec_from_file_location('submission_demo', script)
            demo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(demo)
            metrics_path = target / 'note11/metrics.json'
            metrics = json.loads(metrics_path.read_text())
            metrics['A2']['R2'] = 0.99
            metrics_path.write_text(json.dumps(metrics))
            with self.assertRaisesRegex(ValueError, 'Note 11 reference mismatch: A2'):
                demo.check_outputs(target)


if __name__ == '__main__':
    unittest.main()
