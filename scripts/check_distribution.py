"""Inspect release artifacts for accidental research/data payloads or missing files."""

import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Validate one wheel and source archive without uploading either artifact.

    Both must be below 2 MB. The wheel must contain the package; the source
    archive must also include tests, the method catalogue, docs and examples.
    Research, CSV data, local environments and publishing config are forbidden.
    """
    wheels = list((ROOT / "dist").glob("*.whl"))
    sources = list((ROOT / "dist").glob("*.tar.gz"))
    assert len(wheels) == len(sources) == 1, "Build into an empty dist directory"
    for path in [*wheels, *sources]:
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
            assert "meliora/core.py" in names and "meliora/_validation.py" in names
        else:
            with tarfile.open(path) as archive:
                names = [name.split("/", 1)[-1] for name in archive.getnames()]
            for required in [
                "tests/test_methods.py",
                "tests/test_contracts.py",
                "docs/method_catalog.json",
                "docs/method_checklist.md",
                "docs/README.md",
                "docs/source/index.rst",
                "examples/examples.ipynb",
                "CHANGELOG.md",
            ]:
                assert required in names, (path.name, required)
            for page in (ROOT / "docs/source/meliora").glob("*.md"):
                assert page.relative_to(ROOT).as_posix() in names, (path.name, page.name)
        for name in names:
            assert not name.endswith((".csv", ".pdf", ".docx")), name
            assert not any(part in name.split("/") for part in [".venv", ".cache", ".pypirc", "research"]), (
                name
            )
            assert "ecb_gdp_forecast_moderation" not in name, name
        assert path.stat().st_size < 2_000_000, (path.name, path.stat().st_size)
        print(f"{path.name}: {path.stat().st_size:,} bytes; content checks passed")


if __name__ == "__main__":
    main()
