# Hindsight capstone: notebooks

The steps in the order they ran. Each notebook read the tables the earlier ones saved in the project's SQLite database, which holds the raw data and is not published. So in this repository the notebooks are for reading: each one keeps its outputs from the original run, with names replaced by the public codes.

| Notebook | What it does | Main output tables |
| --- | --- | --- |
| 01_load_and_check | Loads the Jira export (3,152 defects); flags withdrawn, not-a-defect, performance, open and accepted defects; 2,597 count for risk | defects |
| 02_releases | Reads each defect's release from the title first (where it was found), then labels, fixVersion, environment, description and comments | defect_release, release_mentions |
| 03_trackers_and_timeline | Reads every test-effort tracker workbook (Dec 2018 to Oct 2026), groups the work items, builds the test window of every release | tracker_items, tracker_effort_shares, release_windows, release_window_runs, tracker_defect_keys |
| 04_final_release_per_defect | One release per defect (vendor first, then date); keeps upgrade and patch work out of releases; tests the date match | defect_release_final, date_match_validation |
| 05_components | Main component, other components and detail tags for every defect; Jagan's hand answers always win | defect_components, defect_primary_component |
| 06_time_order_and_split | Puts the 61 releases in time order, flags weak windows, and splits them: train = started before 1 Jan 2025 (36), test = from 1 Jan 2025 (16), history only (9) | release_timeline, releases_before_trackers |
| 07_fact_table | One row per component per release (541 rows: train 380, test 161): what happened (defects, Critical + High, reopened) and what was known before the release started (history features from src/hs_features.py) | fact_component_release |
| 08_label | Compares four risk labels and picks one: a component is a hotspot when its defects per 10 person-days are above its stream's hotspot line, with at least 2 defects | fact_labelled, label_thresholds |
| 09_class_balance | Balanced class weights against SMOTE-NC on the training releases; the simpler one (class weights) is kept | class_balance_results |
| 10_model_ladder | Always high, the usual-rate rule, logistic regression, decision tree and random forest; winner chosen on the training checks (random forest); one fixed test and one walk-forward check on the 16 test releases; what drives the risk; the decision tree's rules | model_results, model_scores, model_choice |
| 11_release_rating | Rolls the component scores up to a High, Medium or Low release rating (share of High components or weighted average, cut-offs per stream) and checks it against what happened; rates each stream's next release | release_rating, component_scores_banded, next_release_scores, next_release_rating |

Figures: reports/figures/release_timeline.png (notebook 06), reports/figures/model_ladder.png (10), reports/figures/release_rating.png (11) and reports/figures/pr_curve.png (tools/plot_pr_curve.py).

Packages: pandas, numpy, scikit-learn, imbalanced-learn, matplotlib, openpyxl.
