"""
app_safety_dashboard.py — HSE Safety Dashboard

Built directly on data/safety_incidents_kenya.csv — a real HSE incident export
(445 records, Jan-Jun 2026, 7 depot sites across Kenya) with severity, potential
serious-injury-or-fatality (SIF) flags, critical-control-verification status,
and per-site lat/lon already included. No synthetic data involved.

Run:
    streamlit run app_safety_dashboard.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
DATA_PATH = "data/safety_incidents_kenya.csv"
CRITICAL_SEVERITY_THRESHOLD = 4   # severity >= this counts as "critical" (scale is 0-5)

st.set_page_config(page_title="HSE Safety Dashboard", layout="wide")


# ----------------------------------------------------------------------------
# 1. Data loading
# ----------------------------------------------------------------------------
# @st.cache_data means the CSV is parsed once per session instead of on every
# widget interaction — sidebar filters below never touch this function, so
# every filter change is a cheap re-run against the already-parsed DataFrame.
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["incident_date"])
    # Combine date + time once at load time (not per-render) for the time-series chart.
    df["incident_datetime"] = pd.to_datetime(
        df["incident_date"].dt.strftime("%Y-%m-%d") + " " + df["incident_time"],
        errors="coerce",
    )
    return df


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Couldn't find `{DATA_PATH}`. Place `safety_incidents_kenya.csv` in the "
        f"`data/` folder next to this script, or update DATA_PATH above."
    )
    st.stop()

st.title("⚠️ HSE Safety Incident Dashboard")
st.caption(
    "Kenya depot network incident tracking across 7 sites, Jan-Jun 2026. "
    "Severity scale: 0 (near miss) to 5 (most severe)."
)


# ----------------------------------------------------------------------------
# 2. Sidebar controls
# ----------------------------------------------------------------------------
# Grouped filters in the sidebar so the main panel stays chart-focused. Defaults
# are "everything selected" so the dashboard is never empty on first load.
st.sidebar.header("")

sites = sorted(df["site"].unique())
selected_sites = st.sidebar.multiselect("Site / Location", sites, default=sites)

min_date, max_date = df["incident_date"].min().date(), df["incident_date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
# date_input returns a single date if the user hasn't finished picking a range yet —
# guard against that so the app doesn't crash mid-selection.
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

incident_types = sorted(df["incident_type"].unique())
selected_types = st.sidebar.multiselect("Incident Type", incident_types, default=incident_types)

st.sidebar.markdown("---")
critical_threshold = st.sidebar.slider(
    "Critical-count alert threshold", min_value=1, max_value=30, value=10,
    help="Trigger the warning banner when the number of critical-severity "
         "incidents in the filtered view exceeds this.",
)

# ----------------------------------------------------------------------------
# 3. Apply filters — everything below reads from `filtered`, so every chart
#    and metric updates automatically whenever a sidebar control changes.
# ----------------------------------------------------------------------------
filtered = df[
    df["site"].isin(selected_sites)
    & df["incident_type"].isin(selected_types)
    & (df["incident_date"].dt.date >= start_date)
    & (df["incident_date"].dt.date <= end_date)
].copy()

if filtered.empty:
    st.warning("No incidents match the current filters. Widen the date range or reselect sites/types.")
    st.stop()

filtered["is_critical"] = filtered["severity"] >= CRITICAL_SEVERITY_THRESHOLD


# ----------------------------------------------------------------------------
# 4. KPI metrics with conditional coloring
# ----------------------------------------------------------------------------
# st.metric's built-in delta coloring only handles up/down arrows, not arbitrary
# "is this bad" logic, so KPI cards are hand-built with a small color helper —
# gives full control over red/green thresholds per metric, tuned to real fields
# in this dataset (potential_sif, critical_control_verified).
def kpi_card(label: str, value: str, is_bad: bool, subtext: str = ""):
    color = "#d32f2f" if is_bad else "#2e7d32"  # red / green
    bg = "#fdecea" if is_bad else "#eaf6ec"
    st.markdown(
        f"""
        <div style="background-color:{bg}; border-radius:10px; padding:14px 18px; border:1px solid {color}33;">
            <div style="font-size:13px; color:#555;">{label}</div>
            <div style="font-size:28px; font-weight:700; color:{color};">{value}</div>
            <div style="font-size:12px; color:#777;">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


total_incidents = len(filtered)
avg_severity = filtered["severity"].mean()
critical_count = int(filtered["is_critical"].sum())
# potential_sif: "credible worst case could be life-altering" per the dataset's
# own descriptions — this is the single highest-signal HSE field available,
# distinct from severity (an SIF-potential event can still score low on realized harm).
sif_count = int(filtered["potential_sif"].sum())
avg_control_verification = filtered["critical_control_verified"].mean() * 100

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi_card("Total Incidents", f"{total_incidents}", is_bad=total_incidents > 100,
              subtext=f"{start_date} → {end_date}")
with col2:
    kpi_card("Avg Severity (0-5)", f"{avg_severity:.2f}", is_bad=avg_severity >= 2.5,
              subtext="Higher = more severe")
with col3:
    kpi_card("Critical Incidents", f"{critical_count}", is_bad=critical_count > critical_threshold,
              subtext=f"severity ≥ {CRITICAL_SEVERITY_THRESHOLD}")
with col4:
    kpi_card("Potential SIF Events", f"{sif_count}", is_bad=sif_count > 0,
              subtext="Credible worst case: life-altering")

st.markdown("")  # spacing


# ----------------------------------------------------------------------------
# 6. Alerting logic — separate, explicit banner beyond the KPI card coloring,
#    since a threshold breach deserves an unmissable message, not just a red number.
# ----------------------------------------------------------------------------
if critical_count > critical_threshold:
    st.warning(
        f"⚠️ **{critical_count} critical incidents** (severity ≥ {CRITICAL_SEVERITY_THRESHOLD}) "
        f"in the current filtered view above your alert threshold of {critical_threshold}. "
        f"Review flagged sites below."
    )
if sif_count > 0:
    st.warning(
        f"🚨 **{sif_count} incident(s) flagged as potential SIF** (serious injury or "
        f"fatality) credible worst case for these events was life-altering, "
        f"regardless of the actual outcome recorded. Review immediately."
    )


# ----------------------------------------------------------------------------
# 5. Visualizations
# ----------------------------------------------------------------------------
st.subheader("Trends")
left, right = st.columns([2, 1])

with left:
    # Time-series: daily incident count, colored by whether the day had any
    # critical incident, so trend + severity signal are visible in one chart.
    daily = (
        filtered.groupby(filtered["incident_date"].dt.date)
        .agg(incident_count=("event_id", "count"), max_severity=("severity", "max"))
        .reset_index()
        .rename(columns={"incident_date": "date"})
    )
    daily["flag"] = daily["max_severity"] >= CRITICAL_SEVERITY_THRESHOLD
    fig_ts = px.line(
        daily, x="date", y="incident_count", markers=True,
        title="Incident trend over time",
    )
    fig_ts.add_scatter(
        x=daily.loc[daily["flag"], "date"],
        y=daily.loc[daily["flag"], "incident_count"],
        mode="markers", marker=dict(color="red", size=10, symbol="x"),
        name="Day had a critical incident",
    )
    st.plotly_chart(fig_ts, use_container_width=True)

with right:
    # Categorical breakdown by incident type — bar over pie because with 8
    # categories and skewed counts, bars compare more honestly than pie slices.
    by_type = filtered["incident_type"].value_counts().reset_index()
    by_type.columns = ["incident_type", "count"]
    fig_bar = px.bar(
        by_type, x="count", y="incident_type", orientation="h",
        title="Incidents by type", color="count", color_continuous_scale="Reds",
    )
    fig_bar.update_layout(yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Where and when")
left2, right2 = st.columns([1, 1])

with left2:
    # Map: real lat/lon per depot already in the dataset — scatter map beats a
    # shift/day heatmap here since site location is exactly the kind of context
    # an HSE manager wants at a glance. Sized by severity, colored by type.
    fig_map = px.scatter_map(
        filtered, lat="latitude", lon="longitude",
        color="incident_type", size="severity", hover_name="site",
        hover_data={"incident_date": True, "severity": True, "latitude": False, "longitude": False},
        zoom=5, height=420, title="Incident locations by site",
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

with right2:
    # Heatmap by shift/day-of-week — included alongside the map (not "or") since
    # it surfaces an operational pattern (e.g. night-shift clustering) the map can't.
    filtered["day_of_week"] = filtered["incident_date"].dt.day_name()
    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heat = (
        filtered.groupby(["day_of_week", "shift"])
        .size()
        .reset_index(name="count")
    )
    fig_heat = px.density_heatmap(
        heat, x="day_of_week", y="shift", z="count",
        category_orders={"day_of_week": dow_order, "shift": ["Day", "Night"]},
        color_continuous_scale="Reds", title="Incidents by shift / day of week",
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ----------------------------------------------------------------------------
# 7. Export
# ----------------------------------------------------------------------------
st.subheader("Data")
st.dataframe(filtered.drop(columns=["is_critical", "day_of_week"], errors="ignore"), use_container_width=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=csv_bytes,
    file_name="filtered_incidents.csv",
    mime="text/csv",
)
