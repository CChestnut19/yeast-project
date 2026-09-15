"""Remove saved execution output and imports unused anywhere in each notebook.

Model variants and parameter values are retained. Shared functions in
new_foldchange.ipynb are imported from yeast_analysis.
"""

import ast
import io
import json
from pathlib import Path
import re
import tokenize

ROOT = Path(__file__).resolve().parents[1]


def normalize_windows_paths(source):
    """Use forward slashes in drive paths, including formerly invalid \u005c\u005cD escapes."""
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.STRING and re.match(r"(?i)^[rubf]*['\"]+[a-z]:", token.string):
            token = token._replace(string=re.sub(r"\\+", "/", token.string))
        tokens.append(token)
    return tokenize.untokenize(tokens)


def clean_notebook(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code = "\n".join(normalize_windows_paths("".join(c.get("source", []))) for c in notebook["cells"]
                     if c["cell_type"] == "code")
    used = {node.id for node in ast.walk(ast.parse(code))
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    removed_imports = replaced_functions = 0
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = normalize_windows_paths("".join(cell.get("source", [])))
        lines = source.splitlines(keepends=True)
        edits = []
        for node in ast.parse(source).body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                    continue
                names = [a for a in node.names if a.name == "*" or
                         (a.asname or (a.name.split(".")[0] if isinstance(node, ast.Import) else a.name)) in used]
                if len(names) != len(node.names):
                    removed_imports += len(node.names) - len(names)
                    node.names = names
                    edits.append((node.lineno - 1, node.end_lineno,
                                  ast.unparse(node) + "\n" if names else ""))
            if path.name == "new_foldchange.ipynb" and isinstance(node, ast.FunctionDef):
                if node.name in {"foldchange1", "foldchange2", "foldchange3", "fast_pareto_2d"}:
                    nuclear = any(a.arg == "kx1" for a in node.args.args)
                    imported = "nuclear_" + node.name if nuclear else node.name
                    alias = f" as {node.name}" if nuclear else ""
                    edits.append((node.lineno - 1, node.end_lineno,
                                  f"from yeast_analysis import {imported}{alias}\n"))
                    replaced_functions += 1
        for start, end, text in sorted(edits, reverse=True):
            lines[start:end] = [text]
        source = "".join(lines)
        if path.name == "parameters_fitting.ipynb":
            source = source.replace("data_all = pd.concat(data)\n", 'data_all = pd.concat(data).dropna(subset=["LBD", "inducer", "RPU"])\n')
            source = source.replace("pd.read_csv(os.path.join(folder_path, filename))\n", 'pd.read_csv(os.path.join(folder_path, filename)).dropna(subset=["LBD", "inducer", "RPU"])\n')
            # All three arrays must retain the same rows, even when missing entries differ by column.
            if "class MyModel" in source:
                source = source.replace(".dropna().values", ".values")
        if path.name == "new_foldchange.ipynb":
            # These exports contain two values per DBD, so they need two headers.
            source = source.replace(
                "writer.writerow(['LBD_name'] + kd_labels)\n    for i, params in enumerate(LBD_parameters):\n        writer.writerow([params['LBD_name']] + max_f1[i].tolist()+max_f2[i].tolist())",
                "writer.writerow(['LBD_name'] + [f'{x}_log10_f1' for x in kd_labels] + [f'{x}_log10_f2' for x in kd_labels])\n    for i, params in enumerate(LBD_parameters):\n        writer.writerow([params['LBD_name']] + max_f1[i].tolist()+max_f2[i].tolist())")
        cell["source"] = source.splitlines(keepends=True)
        cell["outputs"] = []
        cell["execution_count"] = None
        cell.get("metadata", {}).pop("execution", None)
    notebook["cells"] = [c for c in notebook["cells"] if "".join(c.get("source", [])).strip()]
    path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return {"notebook": path.name, "unused_imports_removed": removed_imports,
            "shared_functions_replaced": replaced_functions}


if __name__ == "__main__":
    for path in sorted(ROOT.glob("*.ipynb")):
        print(json.dumps(clean_notebook(path)))
