HINDSIGHT: ANONYMISED DATA FOR THE DASHBOARD
Built on 25 Nov 2026 from the project's cleaned database. Every name is anonymised.

WHAT IS IN THIS FOLDER
Fourteen CSV files (comma-separated, UTF-8). Dates are written YYYY-MM-DD.
- Defects: all 3,152 defects in the Jira export of 20 Nov 2026 (raised Aug 2016 to Nov 2026).
- Test effort: tracker work items from Dec 2018 to Oct 2026.
- Release, component and model numbers are the same as in notebooks 06 to 11.

NAMES
- Vendors appear as Vendor A to E, and each vendor's release stream has the same name.
- Releases have public numbers. Vendor A: 1.28 to 1.56 (next 1.57). Vendor B: CI 2 to CI 11.4.
  Vendor C: 3.0 to 5.4 and Vendor E: 6.0 to 8.2, numbered in date order. Vendor D: v2.24, v2.25,
  v2.29 and regression 2023.
- Defects are codes D-0001 onwards, oldest first. No titles, descriptions, people, labels or comments.
- A few components and detail tags have generic names or codes, for example "System tag 3".

WORDS USED
- Person-day: one tester working for one day. "Per 10 person-days" puts big and small releases
  on the same scale.
- Counts for risk: a defect that is not withdrawn, not "not a defect", and not from performance testing.
- Hotspot: a component whose defects per 10 person-days in a release were above its stream's hotspot
  line (the top quarter of training releases), with at least 2 defects.
- Score made before: the random forest's risk score (0 to 1) for a component, made before the release
  started, using only releases that had finished by then.
- Band: High (score 0.56 or more), Medium (0.24 to under 0.56), Low (under 0.24).
- Rating made before: the release rating built from its component scores (final rule: the mix of
  threshold and weighted average, with cut-offs per stream).
- Outcome: Bad = defects per 10 person-days above the stream's average training release;
  Clean = below it; Not judged = no average to compare with (Vendor D and history-only releases).
- Period: Training = releases that started before 1 Jan 2025; Test = from 1 Jan 2025;
  History only = releases outside the model (before the trackers, or left out).

FILES AND COLUMNS
releases.csv - one row per release (61)
  release, stream, vendor, period, in_model (Yes/No), test_start, test_end (the test window),
  window_days, usual_window_days (median window of the stream's model releases), person_days,
  effort_estimated (Yes for the 2 releases whose effort was estimated), test_runs, ptf_drops (fix drops
  during testing, Vendor A only), defects (counted for risk, from release testing), critical_high,
  defects_per_10pd, stream_average, times_stream_average, outcome, rating_before (High, Medium, Low or
  Not scored), rating_first_version (one cut-off for all streams), components, high_components,
  high_share, weighted_avg_score, rating_reason.

component_release.csv - one row per component in a model release (541)
  release, stream, vendor, period, test_start, person_days, component, defects, critical_high,
  priority_weighted (Critical 8, High 4, Medium 2, Low 1), reopened, defects_per_10pd, hotspot (Yes/No),
  score_before, band (High, Medium, Low or Not scored), usual_rate (defects per 10 person-days in
  earlier releases).

defects.csv - one row per defect (3,152)
  defect, created, year, month, priority, status (Done, In progress, Open), resolution_group,
  root_cause, root_cause_group, days_to_resolve (done defects only, deferred left out), reopened,
  accepted_as_is, counts_for_risk, reason_not_counted, work_type (Release testing or Upgrade and
  infrastructure), release ("No release" if none was found), stream, vendor, main_component,
  critical_or_high.

defect_tags.csv - one row per defect and component or detail tag (8,073)
  defect, name, kind (Main component, Other component, Detail tag).

defect_components.csv - the component rows of defect_tags.csv (4,876), for Tableau
  defect, component, component_role (Main or Other). A defect can name more than one component;
  counting defects per component this way gives the same numbers as component_release.csv.

defect_detail_tags.csv - the detail-tag rows of defect_tags.csv (3,197), for Tableau
  defect, detail_tag.

next_release.csv - one row per component in each stream's next release (33)
  next_release, stream, component, score, band, usual_rate, recent_rate, severity_weighted_rate,
  earlier_reopens, share_of_releases_with_defects, earlier_releases, stream_rating, rating_reason.

year_summary.csv - one row per year, for all vendors (All) and for each vendor
  vendor, year, effort_coverage, release_testing_person_days, defects_counted, critical_high,
  critical_high_share, defects_per_10pd, critical_high_per_10pd, reopen_share, median_days_to_resolve.

vendor_scorecard.csv - one row per vendor (5)
  vendor, stream, releases_in_model, releases_judged, clean_releases, clean_share, defects_per_10pd,
  defects_counted, critical_high_share, reopen_share, median_days_to_resolve,
  accepted_or_wont_fix_share, avg_test_runs, ptf_drops_per_release, note.

effort.csv - one row per tracker work item (1,532)
  year, month, work_group (Release work, Release and upgrade work, Upgrade and infrastructure, Other,
  Programme work, Out of scope), group_detail, testing_type, phase, person_days, test_cases_planned,
  test_cases_run, defects_reported, release, stream.

model_results.csv - one row per model and check (15)
  model, check (Training checks, Fixed test, Walk-forward), pr_auc, recall, precision, mcc,
  share_of_hotspots_in_top_20pct, flagged, caught, false_alarms, missed, correctly_left_alone,
  model_order, final_model.

pr_curve.csv - one row per position in the random forest's priority list (161 per test)
  test, position, recall_so_far, precision_so_far, real_hotspot.

drivers.csv - one row per model input (15)
  rank, driver, drop_in_pr_auc (how much worse the ranking gets when this input is shuffled).

data_funnel.csv - one row per step from all defects to the defects the model uses (5)
  step_order, step, defects, left_out_at_this_step, reason_left_out.

HOW THE FILES JOIN
- release: releases, component_release, defects and effort.
- component: component_release.component = defect_components.component = defect_tags.name
  (defects.main_component holds only the main one).
- defect: defects, defect_tags, defect_components and defect_detail_tags.
- In Tableau, keep each file as its own data source, except one: defects + defect_components +
  defect_detail_tags, related on defect, for the drill-down.

READ WITH CARE
- 2018 effort covers December only, and 2026 effort runs to October. Yearly per-10-person-day
  figures are left blank where effort is missing (2016 to 2018). The 2026 rates use defects raised
  January to October, to match the effort; the 2026 counts include every defect raised in 2026.
- year_summary counts defects by the year they were raised and effort by the tracker month.
- Vendor D and Vendor E have few releases and defects.
- Window days, test runs and PTF drops are signs of a long release, not proof of delay:
  no planned dates exist.
