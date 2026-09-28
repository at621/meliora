"""Generate fixed datasets and provenance-stamped independent R outputs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


if __name__ == '__main__':
    y = np.random.default_rng(812).normal(size=80)+np.linspace(0, 2, 80)
    pd.DataFrame({'y': y, 'x': np.linspace(-1, 1, 80)}).to_csv(HERE/'regression.csv', index=False)
    pd.DataFrame(np.cumsum(np.random.default_rng(921).normal(size=(80, 2)), axis=0), columns=['a','b']).to_csv(HERE/'walk.csv', index=False)
    subprocess.run(['Rscript', str(HERE/'oracle.R')], cwd=ROOT, check=True)
    session = HERE/'r_session.txt'
    session.write_text('\n'.join(line.rstrip() for line in session.read_text().splitlines())+'\n')
    files = ['regression.csv', 'walk.csv', 'oracle.R', 'r_results.csv', 'r_session.txt', 'regenerate.py']
    (HERE/'provenance.json').write_text(json.dumps({
        'generator': 'R, independent of Meliora and Python statistical backends',
        'files': {f: digest(HERE/f) for f in files},
    }, indent=2)+'\n')
