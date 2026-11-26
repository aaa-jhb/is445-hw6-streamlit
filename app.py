
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="IS445 HW6 - UFO Explorer",
    page_icon="🛸",
    layout="wide"
)

st.title("UFO Sightings: Time and Geography")
st.write(
    "IS445 Homework 6 | Interactive Data Visualization"
)

st.markdown("""
This dashboard explores reported UFO sightings from two
perspectives: when sightings occur and how different UFO
shapes are reported across U.S. states.
""")

# --------------------------------------------------
# Load and clean data
# --------------------------------------------------

DATA_URL = (
    "https://raw.githubusercontent.com/UIUC-iSchool-DataViz/"
    "is445_data/main/"
    "ufo-scrubbed-geocoded-time-standardized-00.csv"
)

COLUMNS = [
    "datetime", "city", "state", "country", "shape",
    "duration_seconds", "duration_hours_min", "comments",
    "date_posted", "latitude", "longitude"
]

@st.cache_data
def load_data():
    df = pd.read_csv(
        DATA_URL,
        header=None,
        names=COLUMNS,
        dtype=str,
        low_memory=False,
        on_bad_lines="skip"
    )

    df["month"] = pd.to_numeric(
        df["datetime"].str.extract(
            r"^\s*(\d{1,2})/",
            expand=False
        ),
        errors="coerce"
    )

    df["hour"] = pd.to_numeric(
        df["datetime"].str.extract(
            r"^\s*\d{1,2}/\d{1,2}/\d{4}\s+(\d{1,2}):",
            expand=False
        ),
        errors="coerce"
    )

    df["shape"] = df["shape"].str.strip().str.lower()
    df["country"] = df["country"].str.strip().str.lower()
    df["state"] = df["state"].str.strip().str.lower()

    df = df[
        df["month"].between(1, 12) &
        df["hour"].between(0, 23)
    ].copy()

    df["month"] = df["month"].astype(int)
    df["hour"] = df["hour"].astype(int)

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Data loading failed: {e}")
    st.stop()

st.caption(f"Loaded {len(df):,} UFO reports with valid time fields.")

# --------------------------------------------------
# Visualization 1: Heatmap
# --------------------------------------------------

st.header("1. When Are UFO Sightings Reported?")

heatmap_data = (
    df.groupby(["month", "hour"])
    .size()
    .reset_index(name="reports")
)

months = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

heatmap_data["month_name"] = heatmap_data["month"].map(
    dict(enumerate(months, start=1))
)

chart1 = (
    alt.Chart(heatmap_data)
    .mark_rect()
    .encode(
        x=alt.X(
            "hour:O",
            title="Hour of Day",
            sort=list(range(24))
        ),
        y=alt.Y(
            "month_name:N",
            title="Month",
            sort=months
        ),
        color=alt.Color(
            "reports:Q",
            title="Number of Reports",
            scale=alt.Scale(scheme="viridis")
        ),
        tooltip=[
            alt.Tooltip("month_name:N", title="Month"),
            alt.Tooltip("hour:O", title="Hour"),
            alt.Tooltip("reports:Q", title="Reports")
        ]
    )
    .properties(height=400)
)

st.altair_chart(chart1, use_container_width=True)

st.markdown("""
**Visualization 1 — Design choices and interpretation**

This visualization examines how UFO sighting reports vary
by month and hour of the day. I chose a heatmap because it
allows two temporal dimensions to be compared in a single
view. Month and hour are treated as ordered categorical
variables, while the number of reports is quantitative and
encoded through color intensity. I used the Viridis color
scheme because its sequential colors make differences in
reporting frequency easier to distinguish. To prepare the
data, I extracted month and hour from the original date
strings, removed invalid observations, and aggregated
the number of reports for each combination. With more time,
I would incorporate regional differences in daylight
hours and population to examine whether reporting patterns
are influenced by observation opportunities.
""")

st.divider()

# --------------------------------------------------
# Visualization 2: Interactive Bar Chart
# --------------------------------------------------

st.header("2. UFO Shapes Across U.S. States")

us_df = df[
    (df["country"] == "us") &
    df["state"].notna() &
    df["shape"].notna() &
    (df["state"] != "") &
    (df["shape"] != "")
].copy()

top_shapes = (
    us_df["shape"]
    .value_counts()
    .head(12)
    .index.tolist()
)

col1, col2 = st.columns(2)

with col1:
    selected_shape = st.selectbox(
        "Select UFO Shape",
        options=["All shapes"] + top_shapes
    )

with col2:
    top_n = st.slider(
        "Number of States",
        min_value=5,
        max_value=30,
        value=15,
        step=5
    )

if selected_shape == "All shapes":
    filtered_df = us_df
else:
    filtered_df = us_df[
        us_df["shape"] == selected_shape
    ]

state_counts = (
    filtered_df.groupby("state")
    .size()
    .reset_index(name="reports")
    .sort_values("reports", ascending=False)
    .head(top_n)
)

chart2 = (
    alt.Chart(state_counts)
    .mark_bar(color="#3274A1")
    .encode(
        x=alt.X(
            "reports:Q",
            title="Number of Reports"
        ),
        y=alt.Y(
            "state:N",
            title="U.S. State",
            sort="-x"
        ),
        tooltip=[
            alt.Tooltip("state:N", title="State"),
            alt.Tooltip("reports:Q", title="Reports")
        ]
    )
    .properties(height=500)
)

st.altair_chart(chart2, use_container_width=True)

st.markdown("""
**Visualization 2 — Design choices and interpretation**

The second visualization compares UFO report counts across
U.S. states and allows users to examine different reported
shapes. A horizontal bar chart was selected because it
makes state labels readable and supports direct comparisons
of reporting frequency. State is encoded as a nominal
variable, while the number of reports is quantitative.
I used a single blue color because the primary comparison
is between bar lengths rather than between color categories.
The data were filtered to U.S. reports, cleaned to standardize
state and shape labels, and aggregated by state after the
user's filter was applied. With more time, I would normalize
the counts by state population and add a geographic map
to explore regional reporting patterns.
""")

st.subheader("Interactivity")

st.markdown("""
The second visualization includes two interactive controls:
a dropdown menu to select a UFO shape and a slider to
change the number of states displayed. Both controls
directly update the chart, allowing viewers to focus
on different subsets of the data. This interaction goes
beyond basic zooming or tooltips because it changes
the records and categories included in the visualization.
""")

st.divider()

st.subheader("Relationship to Homework 5")

st.markdown("""
This project uses the same UFO dataset as Homework 5,
but the visualizations and written explanations are new.

Homework 5 focused on annual sighting trends and the
distribution of UFO shapes by year. Homework 6 instead
explores reporting patterns by month and hour and
compares reports across U.S. states using interactive
filters. The new visualizations address different
questions and use different chart designs.
""")

st.markdown(
    f"[Original UFO Dataset]({DATA_URL})"
)

st.caption(
    "These data represent reported sightings, not verified "
    "observations of extraterrestrial activity."
)
# put streamlit code here as needed