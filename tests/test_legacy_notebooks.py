"""Development-only notebook checks; notebooks are excluded from submission archives."""
import ast
import csv
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class LegacyNotebookTests(unittest.TestCase):
    def test_notebooks_parse_and_have_no_stale_outputs(self):
        for path in ROOT.glob("*.ipynb"):
            notebook = json.loads(path.read_text(encoding="utf-8"))
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    ast.parse("".join(cell["source"]))
                    self.assertEqual(cell.get("outputs"), [], path.name)
                    self.assertIsNone(cell.get("execution_count"), path.name)

    def test_foldchange_notebook_runs_with_small_grid_and_rectangular_csvs(self):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        notebook = json.loads((ROOT / "new_foldchange.ipynb").read_text(encoding="utf-8"))
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                namespace = {}
                with patch.object(plt, "show", side_effect=lambda: plt.close("all")):
                    for cell in notebook["cells"]:
                        if cell["cell_type"] == "code":
                            source = "".join(cell["source"]).replace("np.linspace(0.3, 10, 2000)", "np.linspace(0.3, 10, 20)")
                            exec(compile(source, "new_foldchange.ipynb", "exec"), namespace)
                for path in Path(directory).glob("*.csv"):
                    with path.open(newline="") as stream:
                        rows = list(csv.reader(stream))
                    self.assertTrue(all(len(row) == len(rows[0]) for row in rows), path.name)
            finally:
                os.chdir(previous)
                plt.close("all")

