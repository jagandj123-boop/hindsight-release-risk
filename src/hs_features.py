"""History features for the Hindsight fact table.

Rule: a release's features use only releases of the same vendor stream that had FINISHED before it started,
so the model never sees the future. Used by notebook 07 (fact table) and the model notebook (scoring the next release).

Inputs chosen by Jagan (24 Nov 2026):
- priority weights Critical 8, High 4, Medium 2, Low 1 (priority works as severity in this team)
- recency half-life: try 2 and 4 releases, keep whichever predicts better (decided in the model step)
"""
from types import SimpleNamespace

import numpy as np
import pandas as pd

NOT_PRODUCT = ['Unknown', 'Not a product defect', 'Out of scope (perf)']
PRIORITY_WEIGHTS = {'Critical': 8, 'High': 4, 'Medium': 2, 'Low': 1}
HALF_LIVES = (2, 4)

FEATURES_NUM = ['hist_rate_per_10pd', 'prev_density_per_10pd', 'recent_rate_hl2', 'recent_rate_hl4',
                'hist_sev_rate_per_10pd', 'spread_releases', 'spread_share', 'hist_reopened', 'hist_share',
                'recent_90d', 'n_prev_releases', 'gap_days', 'n_concurrent', 'shared_vendor_work']
FEATURES_CAT = ['vendor', 'component']


def load_context(cc):
    """Read the cleaned tables once and prepare everything the feature function needs."""
    x = SimpleNamespace()
    x.timeline = pd.read_sql('select * from release_timeline', cc, parse_dates=['window_start', 'window_end', 'last_run_end'])
    x.timeline['in_model'] = x.timeline.in_model.astype(bool)          # stored as 0/1 in SQLite
    x.timeline['effort_estimated'] = x.timeline.effort_estimated.fillna(0).astype(bool)
    x.final = pd.read_sql('select f.key, f.release_key, f.vendor, f.also_vendor, f.work_type, f.final_confidence, '
                          'd.created, d.priority, d.counts_for_risk, d.reopen_events_strict '
                          'from defect_release_final f join defects d using(key)', cc)
    x.final['created'] = pd.to_datetime(x.final.created).dt.tz_localize(None)
    comps = pd.read_sql("select key, name from defect_components where kind in ('main component', 'component')", cc)
    x.comps = comps[~comps.name.isin(NOT_PRODUCT)]
    x.primary = pd.read_sql('select key, primary_component from defect_primary_component', cc)
    x.tracker = pd.read_sql('select release_key, top_group, ptf from tracker_items', cc)

    # Defects that count: release testing (not upgrade work), counted for risk (notebooks 01 and 04)
    x.counted = x.final[(x.final.work_type == 'release testing') & (x.final.counts_for_risk == 1)]
    x.in_release = x.counted[x.counted.release_key.notna()]

    # One line per defect and component, for every release in the timeline (model and history-only releases)
    links = x.in_release.merge(x.comps, on='key')
    links = links.merge(x.timeline[['release_key', 'in_model', 'split']], on='release_key', how='left')
    links['main'] = links.key.map(x.primary.set_index('key').primary_component) == links.name
    links['critical_high'] = links.priority.isin(['Critical', 'High'])
    links['priority_weight'] = links.priority.map(PRIORITY_WEIGHTS).fillna(1)
    links['reopened'] = links.reopen_events_strict.fillna(0) > 0
    links['date_only'] = links.final_confidence == 'date only'
    x.links = links

    by = links.groupby(['release_key', 'name'])
    x.count_of = by.key.nunique()                       # component defects per release
    x.weight_of = by.priority_weight.sum()              # priority-weighted defects per release
    x.reopen_of = by.reopened.sum()                     # reopened defects per release
    x.total_of = x.in_release.groupby('release_key').key.nunique()      # release totals (each defect once)
    x.done = x.timeline[['release_key', 'vendor', 'window_start', 'window_end', 'person_days', 'in_model']].copy()
    x.comp_dates = links[['name', 'created']]
    # Shared work with another vendor in the tracker (a scope fact known at planning time)
    x.shared = set(x.tracker[x.tracker.release_key.notna() & x.tracker.top_group.str.count('Vendor').ge(2)].release_key)
    return x


def history(x, vendor, start, component, release_key=None):
    """Features for one component in one release of a vendor stream that starts on `start`."""
    c = component
    past = x.done[(x.done.vendor == vendor) & (x.done.window_end < start)].sort_values('window_end')
    pm = past[past.in_model]                         # finished releases with effort data, oldest first
    out = {'n_prev_releases': len(past)}

    # Density: defects per 10 person-days in earlier releases (the component's usual rate)
    counts_pm = np.array([x.count_of.get((k, c), 0) for k in pm.release_key], dtype=float)
    effort_pm = pm.person_days.to_numpy(dtype=float)
    dens = counts_pm / effort_pm * 10 if len(pm) else np.array([])
    out['hist_rate_per_10pd'] = counts_pm.sum() / effort_pm.sum() * 10 if len(pm) else np.nan
    out['prev_density_per_10pd'] = dens[-1] if len(dens) else np.nan

    # Recency: average density with recent releases counting more (weight halves every `h` releases)
    for h in HALF_LIVES:
        if len(dens):
            age = np.arange(len(dens))[::-1]              # 0 = most recent finished release
            w = 0.5 ** (age / h)
            out[f'recent_rate_hl{h}'] = float((dens * w).sum() / w.sum())
        else:
            out[f'recent_rate_hl{h}'] = np.nan

    # Severity: priority-weighted defects (Critical 8, High 4, Medium 2, Low 1) per 10 person-days
    weights_pm = sum(x.weight_of.get((k, c), 0) for k in pm.release_key)
    out['hist_sev_rate_per_10pd'] = weights_pm / effort_pm.sum() * 10 if len(pm) else np.nan

    # Spread: in how many earlier releases the component had defects (all earlier releases, history-only included)
    counts_all = [x.count_of.get((k, c), 0) for k in past.release_key]
    out['spread_releases'] = int(sum(n > 0 for n in counts_all))
    out['spread_share'] = out['spread_releases'] / len(past) if len(past) else np.nan

    # Fix churn: reopened defects in earlier releases
    out['hist_reopened'] = int(sum(x.reopen_of.get((k, c), 0) for k in past.release_key))

    # Context
    stream_total = sum(x.total_of.get(k, 0) for k in past.release_key)
    out['hist_share'] = sum(counts_all) / stream_total if stream_total else np.nan
    recent = x.comp_dates[(x.comp_dates.name == c) & (x.comp_dates.created >= start - pd.Timedelta(days=90))
                          & (x.comp_dates.created < start)]
    out['recent_90d'] = len(recent)
    out['gap_days'] = (start - past.window_end.max()).days if len(past) else np.nan
    out['n_concurrent'] = int(((x.done.window_start <= start) & (x.done.window_end >= start)
                               & (x.done.release_key != release_key)).sum())
    out['shared_vendor_work'] = int(release_key in x.shared) if release_key else 0
    return out
