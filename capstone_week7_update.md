# Capstone Week 7 Update — MasterMaisha

**Project:** Medical Equipment Utilization & Maintenance Risk Monitoring System for Kenyan County Hospitals
**Submitted by:** Valentine Kerubo (Data Engineer)
**Week:** 7 of 12 (compressed to a 4-week implementation window)

## 1. Did you start building your Capstone dashboard?

Not yet as a standalone deliverable, but the groundwork it depends on is done.
This week I built the unified data schema (`docs/data_architecture.md`) covering
facilities, equipment, usage logs, maintenance logs, and failure events, plus a
working scenario generator (`pipeline/scenario_generator.py`) that produces
labeled Layer 2 data for both documented patterns from the proposal — the
usage-vs-register discrepancy pattern and the maintenance-neglect-to-breakdown
pattern — each traced to a cited case in `docs/scenario_rationale.md`. I also
built an initial proof-of-concept dashboard against scenario-derived incident
data to validate the pipeline → dashboard path end-to-end. The fuller
capstone-specific risk dashboard (facility/equipment risk view, discrepancy
flags, lead-time-to-failure display) is still to be built as its own
deliverable, targeted for Week 11 per the original timeline.

## 2. What library are you using?

**Streamlit** for the app shell and layout (sidebar filters, KPI cards, caching
via `@st.cache_data`), and **Plotly Express** for all charts — line chart for
trends, bar chart for categorical breakdowns, `scatter_map` for facility
locations, and `density_heatmap` for shift/day patterns. Chose this combo over
Dash for faster iteration speed within the 4-week window; Plotly's interactivity
(hover, zoom) came for free without extra callback wiring.

## 3. What is one challenge you faced in visualizing your specific Capstone data?

The two real data sources don't line up spatially. The Kenya Health Facility
Census is published as a PDF report with county-level aggregates, not
facility-level records, and KMHFR's live API (the better facility-level source)
hasn't been confirmed accessible yet — nobody on the team has successfully
pulled a live response from it. That leaves no confirmed source of real
facility-level GPS coordinates, so the map view currently has to fall back to
county-centroid coordinates with random jitter for scenario-only facilities,
which is fine for a demo but isn't something we can present as located data.
Until KMHFR access is confirmed, the facility-risk map stays a placeholder
rather than a real geographic view.

## Next steps
- Confirm KMHFR API access (blocking real facility-level location data)
- Build the capstone risk dashboard as its own file, wired to the
  breakdown-risk model output once trained
- Finalize Layer 2 scenario parameters and lock `scenario_rationale.md` before
  feature engineering begins
