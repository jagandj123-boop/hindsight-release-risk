# Hindsight: release risk for multi-vendor retail QA

Hindsight scores each software component's risk **before a release starts**, so testers can put the most effort where defects are likely and test lighter where they are not. It learns from eight years of a UK retail organisation's defect and test-effort history, using only releases that had already finished.

Capstone project for the Imperial College Professional Certificate in Data Analytics, 2026, by Jagan. All data is anonymised (see [Anonymisation](#anonymisation)).

**Live dashboard:** [jagandj123-boop.github.io/hindsight-release-risk](https://jagandj123-boop.github.io/hindsight-release-risk/) (11 pages: next-release risk, release history, drill-down to defects, components, vendors, testing effort, and the model and rating checks).

## The result in four lines

| Check | Result |
| --- | --- |
| Ranking score (PR-AUC) on the 16 test releases, walk-forward check | **0.50**, against 0.15 for guessing |
| Real hotspots in the top 20% of the priority list (32 of 161 rows) | **14 of 24** |
| Rows at the bottom of the list with no hotspot | **59 of 161**: a safe zone for lighter testing, with a minimum floor |
| Release rating on the 13 test releases that can be judged | caught 2 of 4 bad releases, 2 false alarms (MCC 0.28) |

## What is in this repository

| Folder | What it holds |
| --- | --- |
| `docs/` | The web dashboard: one HTML page and its data, served by GitHub Pages |
| `data/` | 14 anonymised CSV files; `data/README.txt` defines every column and how the files join |
| `notebooks/` | The 11 steps, 01 to 11, plus a README with the order and the tables each step writes |
| `src/` | `hs_features.py`: the history features, built only from releases finished before each release starts |
| `reports/` | Figures, and `Hindsight_Measures_Check_public.xlsx`, which rebuilds every PR-AUC and MCC with Excel formulas |
| `tools/` | Rebuild the dashboard data from `data/`; redraw the precision-recall figure |

## How the work was done

1. **Load and check** the Jira export: 3,152 defects raised from August 2016 to November 2026; 2,597 count for risk (not withdrawn, not "not a defect", not performance testing).
2. **Release of each defect**, read from the title first, then labels, fix version and other fields.
3. **Test effort** from eight years of tracker workbooks (December 2018 to October 2026): the test window and person-days of every release.
4. **One release per defect**; upgrade and infrastructure work is kept out of releases.
5. **Components and detail tags** per defect, with the author's hand labels for 331 defects always winning.
6. **Time order and split**: 61 releases; 36 training releases started before 1 January 2025, 16 test releases from that date, 9 history only.
7. **Fact table**: one row per component per release (541 rows), with features that only use what was known before the release started.
8. **Label**: a component is a hotspot when its defects per 10 person-days are above its stream's hotspot line (the top quarter of training releases), with at least 2 defects.
9. **Class balance**: balanced class weights, almost a tie with SMOTE-NC and simpler.
10. **Model ladder**: always high, a usual-rate rule, logistic regression, a decision tree and a random forest. The winner was chosen on the training releases only (random forest), then tested once on the 16 test releases, in a fixed test and a walk-forward check.
11. **Release rating**: the component scores roll up to High, Medium or Low (share of High components or weighted average, with cut-offs per stream), checked against what happened.

## Main numbers

| Model | PR-AUC, walk-forward | PR-AUC, fixed test |
| --- | --- | --- |
| Always high (guessing) | 0.15 | 0.15 |
| Usual-rate rule | 0.49 | 0.49 |
| Logistic regression | 0.48 | 0.50 |
| Decision tree | 0.39 | 0.37 |
| **Random forest (chosen)** | **0.50** | **0.56** |

- The fixed test is slightly optimistic: two training releases were still running when the first test releases started. The walk-forward check learns only from releases finished before each test release, so it is the headline.
- Random forest, walk-forward, 161 test rows: flagged 37; caught 16 of the 24 hotspots; 21 false alarms; 8 missed; 116 correctly left alone.
- Release rating, all 38 releases that can be judged: caught 8 of 12 bad releases, 10 false alarms, MCC 0.26.
- Critical and High defects per 10 person-days of release testing fell from 4.84 in 2019 to 1.33 in 2026.

## Anonymisation

- Vendors appear only as Vendor A to E, and each vendor's release stream has the same name.
- Releases have public numbers: Vendor A 1.28 to 1.56 (next 1.57), Vendor B CI 2 to CI 11.4, Vendor C 3.0 to 5.4 and Vendor E 6.0 to 8.2 (numbered in date order), Vendor D v2.24 to v2.29.
- Components and detail tags that named a product, system or company have generic names or codes such as "System tag 3". Defects are codes, D-0001 onwards.
- Not published: defect titles, descriptions, comments, labels, environment notes, build names, people, the Jira export, the tracker workbooks and the project database.
- Every notebook keeps its outputs (counts, tables and charts) from the original run on the private data: 01 to 05 read the raw Jira export and the test trackers, and 06 to 11 build and test the model. Names in the code, text and tables were replaced with the public codes after that run, so every number is exactly as computed. The notebooks are for reading: they do not run without the private database, which is not published. No notebook output shows a defect title, description, comment or person.
- Every file passed an automatic scan for the organisation's, vendors', products' and people's names before it was published.

## Run it yourself

```
pip install -r requirements.txt
cd docs && python -m http.server 8000        # then open http://localhost:8000
python tools/build_dashboard_data.py           # rebuild docs/data from data/
python tools/plot_pr_curve.py                  # redraw reports/figures/pr_curve.png
```

The dashboard needs a web server (GitHub Pages or the command above), because the browser will not load its data files from a double-clicked file.

## Limitations

- Effort is recorded per release, not per component, so component rates share the release's person-days.
- The label is defects found in testing per person-day; no production incidents or hotfix data were available.
- Priority stands in for severity, as it does in this team.
- No planned release dates exist, so delay is shown only through signs (long test windows, repeat test runs, fix drops).
- The data is small (541 component rows, 120 hotspots), and Vendors D and E have few releases.
