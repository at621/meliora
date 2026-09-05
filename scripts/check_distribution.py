"""Inspect release artifacts for accidental research/data payloads or missing files."""

import argparse
import re
import tarfile
import zipfile
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

from readme_renderer.markdown import render

import meliora

ROOT = Path(__file__).resolve().parents[1]


class ReadmeLinks(HTMLParser):
    """Collect links from the same Markdown renderer used by PyPI."""

    def __init__(self):
        """Initialize the HTML parser and its collected links."""
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        """Collect navigation and image URLs from rendered HTML elements."""
        self.links.extend(value for key, value in attrs if key in {"href", "src"})


def check_metadata(content):
    """Validate release metadata, the packaged README and its permanent links."""
    metadata = BytesParser(policy=policy.default).parsebytes(content)
    assert metadata["Name"] == "meliora"
    assert metadata["Version"] == meliora.__version__
    assert metadata["Requires-Python"] == ">=3.11"
    assert metadata["License-Expression"] == "MIT"
    assert metadata["Description-Content-Type"] == "text/markdown"
    readme = metadata.get_payload(decode=True).decode("utf-8")
    assert readme.rstrip() == (ROOT / "README.md").read_text(encoding="utf-8").rstrip()
    rendered = render(readme)
    assert rendered, "README failed to render for PyPI"
    parser = ReadmeLinks()
    parser.feed(rendered)
    prefix = f"https://github.com/at621/meliora/blob/v{meliora.__version__}/"
    for link in parser.links:
        assert link.startswith(("https://", "mailto:", "#")), f"Non-absolute README URL: {link}"
        if link.startswith("https://github.com/at621/meliora/blob/"):
            assert link.startswith(prefix), f"README link must use the release tag: {link}"
            relative = unquote(urlparse(link[len(prefix) :]).path)
            target = (ROOT / relative).resolve()
            assert target.is_relative_to(ROOT) and target.is_file(), f"Missing README target: {link}"


def main():
    """Validate one wheel and source archive without uploading either artifact.

    Both must be below 2 MB. The wheel must contain the package; the source
    archive must also include tests, the method catalogue, docs and examples.
    Research, CSV data, local environments and publishing config are forbidden.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="Require this release tag to match the built package version")
    args = parser.parse_args()
    if args.tag:
        assert re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", meliora.__version__), (
            "Expected a final release version"
        )
        assert args.tag == f"v{meliora.__version__}", "Release tag and package version differ"
    wheels = list((ROOT / "dist").glob("*.whl"))
    sources = list((ROOT / "dist").glob("*.tar.gz"))
    assert len(wheels) == len(sources) == 1, "Build into an empty dist directory"
    for path in [*wheels, *sources]:
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as archive:
                names = archive.namelist()
                metadata = [name for name in names if name.endswith(".dist-info/METADATA")]
                assert len(metadata) == 1
                check_metadata(archive.read(metadata[0]))
            assert "meliora/core.py" in names and "meliora/_validation.py" in names
        else:
            with tarfile.open(path) as archive:
                metadata = [
                    member
                    for member in archive.getmembers()
                    if member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
                ]
                assert len(metadata) == 1
                check_metadata(archive.extractfile(metadata[0]).read())
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
