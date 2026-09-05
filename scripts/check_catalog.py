"""Check that exports, docstrings, tests, Sphinx pages and notebooks stay linked."""

import ast
import inspect
import json
from pathlib import Path

import nbformat
from render_reference import check_reference

import meliora

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Fail on missing method evidence or mismatched signatures and example calls.

    This is a structural gate. Numerical tests, notebook execution and the
    warning-free Sphinx build are separate CI gates; this check does not infer
    mathematical correctness from a file's mere presence.
    """
    catalogue = json.loads((ROOT / "docs/method_catalog.json").read_text(encoding="utf-8"))
    names = [entry["name"] for entry in catalogue]
    assert len(names) == len(set(names))
    assert set(names) == set(meliora.__all__)
    check_reference(catalogue)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notebook = nbformat.read(ROOT / "examples/examples.ipynb", as_version=4)
    cells = {
        cell.metadata["meliora_method"]: cell
        for cell in notebook.cells
        if cell.cell_type == "code" and "meliora_method" in cell.metadata
    }
    assert set(cells) == set(names)
    tree = ast.parse((ROOT / "tests/test_methods.py").read_text(encoding="utf-8-sig"))
    tests = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    for entry in catalogue:
        name = entry["name"]
        function = getattr(meliora, name)
        doc = inspect.getdoc(function)
        assert set(inspect.signature(function).parameters) == set(entry["parameters"]), name
        for section in ["Parameters", "Returns", "Raises", "Notes", "References", "Examples"]:
            assert "\n" + section + "\n" in doc, (name, section)
        for parameter in entry["parameters"]:
            assert "\n" + parameter + " :" in doc, (name, parameter)
        assert all(entry[key] for key in ["notes", "raises", "reference", "interpretation"])
        cell = cells[name]
        assert cell.source.strip() == (entry["example"] + "\nresult").strip(), name
        code = ast.parse(cell.source)
        assert any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "m"
            and node.func.attr == name
            for node in ast.walk(code)
        ), name
        assert any(isinstance(node, ast.Assert) for node in ast.walk(code)), name
        test = tests[entry["test"].split("::")[1]]
        assert ast.get_docstring(test), name
        assert any(isinstance(node, ast.Assert) for node in ast.walk(test)), name
        reference_link = f"[{entry['title']}](docs/source/meliora/{name}.md)"
        assert readme.count(reference_link) == 1, (name, "README reference link")
    for path in (ROOT / "src/meliora").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8-sig"))):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(node)
                assert doc and "Parameters\n" in doc and "Returns\n" in doc, (path.name, node.name)
    print(
        f"{len(names)} methods: exports, signatures, docstrings, tests, notebooks and readable references match"
    )


if __name__ == "__main__":
    main()
