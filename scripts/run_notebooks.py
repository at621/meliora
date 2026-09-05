"""Execute supported notebooks with this interpreter and no user kernel setup."""

import argparse
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Run all supported examples and save outputs in .cache or the source file.

    The optional --write flag refreshes committed example outputs. Each notebook
    receives a fresh kernel using sys.executable and runs from the repository
    root. Cell errors and timeouts propagate as failures. Supported notebooks
    are the files directly under examples/.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Refresh committed notebook outputs")
    args = parser.parse_args()
    output = ROOT / ".cache" / "executed"
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted((ROOT / "examples").glob("*.ipynb")):
        with TemporaryDirectory(prefix="kernel-", dir=ROOT / ".cache") as temporary:
            kernel_dir = Path(temporary) / "meliora-check"
            kernel_dir.mkdir()
            (kernel_dir / "kernel.json").write_text(
                json.dumps(
                    {
                        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                        "display_name": "Meliora validation",
                        "language": "python",
                    }
                ),
                encoding="utf-8",
            )
            manager = KernelManager(
                kernel_name="meliora-check", kernel_spec_manager=KernelSpecManager(kernel_dirs=[temporary])
            )
            notebook = nbformat.read(path, as_version=4)
            client = NotebookClient(
                notebook, km=manager, timeout=120, resources={"metadata": {"path": str(ROOT)}}
            )
            client.execute()
            nbformat.write(notebook, path if args.write else output / path.name)
            count = sum(cell.cell_type == "code" for cell in notebook.cells)
            print(f"{path.relative_to(ROOT)}: {count} code cells executed with {sys.executable}")


if __name__ == "__main__":
    main()
