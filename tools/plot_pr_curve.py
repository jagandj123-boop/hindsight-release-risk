"""Redraws reports/figures/pr_curve.png from data/pr_curve.csv: the random forest's precision-recall curves
on the 16 test releases (fixed test and walk-forward).

Walking down the priority list from the riskiest row: recall so far = share of the real hotspots found,
precision so far = share of the rows checked so far that were real hotspots. PR-AUC (average precision) =
the average of the precision at each real hotspot. Guessing scores the share of rows that are hotspots.

Usage (from the repository folder):  python tools/plot_pr_curve.py
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
pc = pd.read_csv(ROOT / 'data' / 'pr_curve.csv')

fig, ax = plt.subplots(figsize=(9, 5.2))
guess = None
for test, color in [('Fixed test', '#2a6fdb'), ('Walk-forward', '#e07b28')]:
    g = pc[pc.test == test].sort_values('position')
    hot = g.real_hotspot == 'Yes'
    pr_auc = g.loc[hot, 'precision_so_far'].mean()          # average precision
    guess = hot.mean()
    ax.plot(g.recall_so_far, g.precision_so_far, color=color, linewidth=1.8, label=f'{test}: PR-AUC {pr_auc:.2f}')
    top = round(len(g) * 0.2)
    print(f'{test}: PR-AUC {pr_auc:.4f}; top 20% ({top} rows) holds {int(hot[:top].sum())} of {int(hot.sum())} hotspots; '
          f'last hotspot at row {int(g.position[hot].max())} of {len(g)}')
ax.axhline(guess, color='#8c8c8c', linestyle='--', linewidth=1.2, label=f'Guessing: {guess:.2f}')
ax.set_xlim(0, 1.02)
ax.set_ylim(0, 1.05)
ax.set_xlabel('Recall so far: share of the real hotspots found, walking down the priority list')
ax.set_ylabel('Precision so far: share of rows\nchecked that were real hotspots')
ax.set_title('Precision-recall curve of the random forest on the 16 test releases', loc='left', fontsize=10)
ax.legend(frameon=False, loc='upper right', fontsize=9)
for side in ['top', 'right']:
    ax.spines[side].set_visible(False)
plt.tight_layout()
out = ROOT / 'reports' / 'figures' / 'pr_curve.png'
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, dpi=150)
print('saved', out.relative_to(ROOT))
