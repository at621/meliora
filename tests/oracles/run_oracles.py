"""Regenerate the cross-language oracle files.

Usage::

    python tests/oracles/run_oracles.py data            # rewrite the CSV datasets and python/results.json
    python tests/oracles/run_oracles.py r matlab        # run the R and MATLAB oracles live
    python tests/oracles/run_oracles.py sas             # run SAS through saspy, if configured
    python tests/oracles/run_oracles.py sas --stamp FILE  # adopt a results file produced by hand in SAS
    python tests/oracles/run_oracles.py restamp        # refresh stamps after a change that cannot alter results

Every oracle file gets a provenance stamp: the SHA-256 of the CSV datasets, of
``cases.py`` and of the oracle script that produced it, so that
``tests/test_cross_language.py`` can refuse a stale file.

Executables are located through the environment variables ``MELIORA_RSCRIPT``
and ``MELIORA_MATLAB`` and otherwise through the PATH and the usual Windows
install folders.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from tests.oracles import cases  # noqa: E402

SCRIPTS = {"r": HERE / "r" / "oracle.R", "sas": HERE / "sas" / "oracle.sas", "matlab": HERE / "matlab" / "oracle.m"}


def find_executable(name: str, env: str, patterns: list[str]) -> str:
    if os.environ.get(env):
        return os.environ[env]
    found = shutil.which(name)
    if found:
        return found
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            return matches[-1]
    raise FileNotFoundError(f"{name} not found; set {env}")


def write_json(target: Path, payload: dict) -> None:
    """Write with LF endings on every platform; the frozen files are committed."""
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=1)
        handle.write("\n")


def stamp(language: str, payload: dict) -> Path:
    """Normalise an oracle payload, add provenance and write results.json."""
    meta = dict(payload.get("meta", {}))
    meta["language"] = language
    meta["data_sha256"] = cases.data_hash()
    meta["cases_sha256"] = cases.file_hash(HERE / "cases.py")
    meta["script_sha256"] = cases.file_hash(SCRIPTS[language])
    target = HERE / language / "results.json"
    write_json(target, {"meta": meta, "results": payload["results"]})
    print(f"{language}: {len(payload['results'])} records -> {target.relative_to(ROOT)}")
    return target


def load_raw(path: Path) -> dict:
    """Read an oracle output, accepting SAS PROC JSON's tagged layout as well."""
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if "results" in raw:
        return raw
    results = next(v for k, v in raw.items() if k.upper().endswith("RESULTS"))
    meta_rows = next((v for k, v in raw.items() if k.upper().endswith("META")), [{}])
    meta = meta_rows[0] if meta_rows else {}
    return {"meta": {str(k).lower(): v for k, v in meta.items()}, "results": results}


def run_r() -> None:
    rscript = find_executable("Rscript", "MELIORA_RSCRIPT", ["C:/Program Files/R/R-*/bin/Rscript.exe"])
    target = HERE / "r" / "results.json"
    subprocess.run([rscript, "--vanilla", str(SCRIPTS["r"]), str(cases.DATA_DIR), str(target)], check=True)
    stamp("r", load_raw(target))


def run_matlab() -> None:
    matlab = find_executable("matlab", "MELIORA_MATLAB", ["C:/Program Files/MATLAB/R20*/bin/matlab.exe"])
    target = HERE / "matlab" / "results.json"
    command = (
        f"cd('{SCRIPTS['matlab'].parent.as_posix()}'); "
        f"oracle('{cases.DATA_DIR.as_posix()}', '{target.as_posix()}')"
    )
    subprocess.run([matlab, "-batch", command], check=True)
    stamp("matlab", load_raw(target))


def run_sas(stamp_file: str | None) -> None:
    target = HERE / "sas" / "results.json"
    if stamp_file:
        stamp("sas", load_raw(Path(stamp_file)))
        return
    try:
        import saspy
    except ImportError:
        sys.exit(
            "saspy is not installed. Either install and configure saspy for a SAS server, or run\n"
            f"  {SCRIPTS['sas'].relative_to(ROOT)}\n"
            "by hand (set &data_dir and &out_path at the top), download the JSON it writes and adopt it with\n"
            "  python tests/oracles/run_oracles.py sas --stamp <downloaded.json>"
        )
    session = saspy.SASsession()
    program = SCRIPTS["sas"].read_text(encoding="utf-8")
    program = program.replace("%let data_dir = ;", f"%let data_dir = {cases.DATA_DIR};")
    program = program.replace("%let out_path = ;", f"%let out_path = {target};")
    result = session.submit(program)
    if "ERROR:" in result["LOG"]:
        sys.exit(result["LOG"])
    stamp("sas", load_raw(target))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("targets", nargs="+", choices=["data", "r", "sas", "matlab", "restamp"])
    parser.add_argument("--stamp", help="existing SAS output to adopt instead of running SAS")
    args = parser.parse_args()
    for target in args.targets:
        if target == "restamp":
            # Refresh the provenance of every existing results file without rerunning
            # the oracles, for changes that cannot alter their output (comments, tooling).
            for language in SCRIPTS:
                path = HERE / language / "results.json"
                if path.exists():
                    stamp(language, load_raw(path))
        elif target == "data":
            cases.generate_data()
            results = cases.compute_all()
            path = HERE / "python" / "results.json"
            path.parent.mkdir(exist_ok=True)
            write_json(path, {"meta": cases.python_meta(), "results": cases.to_records(results)})
            print(f"python: {len(results)} cases -> {path.relative_to(ROOT)}")
        elif target == "r":
            run_r()
        elif target == "matlab":
            run_matlab()
        elif target == "sas":
            run_sas(args.stamp)


if __name__ == "__main__":
    main()
