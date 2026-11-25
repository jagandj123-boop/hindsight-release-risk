"""Rebuilds the web dashboard's data files (docs/data/*.json) from the anonymised CSV files in data/.

Each JSON file is one array with one record per line: the first line holds the column names, every later
line one row in the same order. Column names are the same as in the CSV files and data/README.txt.

Usage (from the repository folder):  python tools/build_dashboard_data.py
"""
import json
import math
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / 'data', ROOT / 'docs' / 'data'
TEXT_COLUMNS = {'release': str, 'next_release': str, 'defect': str, 'name': str}   # "1.50" must stay text
SKIP = {'defect_components.csv', 'defect_detail_tags.csv'}     # Tableau helpers; the page reads defect_tags


def clean(value):
    if value is None:
        return None
    if isinstance(value, float):
        if math.isnan(value):
            return None
        return int(value) if value.is_integer() else round(value, 4)
    if hasattr(value, 'item'):
        return clean(value.item())
    return value


OUT.mkdir(parents=True, exist_ok=True)
for path in sorted(p for p in SRC.glob('*.csv') if p.name not in SKIP):
    df = pd.read_csv(path, dtype=TEXT_COLUMNS)
    rows = [list(df.columns)] + [[clean(v) for v in row] for row in df.itertuples(index=False, name=None)]
    text = '[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in rows) + '\n]\n'
    (OUT / f'{path.stem}.json').write_text(text, encoding='utf-8')
    print(f'{path.stem + ".json":24} {len(rows) - 1:5} rows')
