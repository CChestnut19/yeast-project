"""The numerical entry points must run without a graphics installation."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RENDERING = {'matplotlib', 'seaborn', 'plotly', 'palettable', 'pypdf', 'reportlab', 'PIL', 'docx', 'fontTools'}


class AlgorithmsOnlyTests(unittest.TestCase):
    def test_numerical_clis_need_no_rendering_modules_or_flags(self):
        with tempfile.TemporaryDirectory() as directory:
            for module in ('repressor', 'combinatorial'):
                output = Path(directory) / module
                code = (
                    'import importlib.abc, runpy, sys\n'
                    f'blocked = {RENDERING!r}\n'
                    'class NoRendering(importlib.abc.MetaPathFinder):\n'
                    '    def find_spec(self, fullname, path=None, target=None):\n'
                    '        if fullname.split(".")[0] in blocked:\n'
                    '            raise ImportError("Rendering module is unavailable: " + fullname)\n'
                    'sys.meta_path.insert(0, NoRendering())\n'
                    f'sys.argv = ["yeast.{module}", "run", "--output-dir", {str(output)!r}]\n'
                    f'runpy.run_module("yeast.{module}", run_name="__main__")\n'
                )
                result = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(json.loads((output / 'validation.json').read_text())['status'], 'PASS')
                self.assertEqual({p.name for p in output.iterdir()},
                                 {'predictions.csv', 'metrics.json', 'provenance.json', 'validation.json'})

    def test_production_modules_import_no_rendering_libraries(self):
        violations = []
        for folder in ('yeast', 'mammalian', 'tools'):
            for path in (ROOT / folder).rglob('*.py'):
                for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
                    names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
                    violations.extend(f'{path.relative_to(ROOT)}:{node.lineno}: {name}'
                                      for name in names if name.split('.')[0] in RENDERING)
        self.assertEqual(violations, [])

    def test_root_algorithms_have_been_consolidated_into_modules(self):
        self.assertEqual(list(ROOT.glob('*.ipynb')), [])
        self.assertEqual(list(ROOT.glob('*.py')), [])
        self.assertFalse((ROOT / 'yeast/combinatorial/resources').exists())
        self.assertFalse((ROOT / 'yeast/repressor/plotting.py').exists())


if __name__ == '__main__':
    unittest.main()
