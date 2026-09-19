"""
Atlantic Recording Corporation
Audience Sensitivity, Content Compliance & Format Preference Analysis
France Top 50 Playlist — Streamlit Dashboard

Run with:  streamlit run streamlit_app.py
Requires:  streamlit, pandas, plotly  (pip install streamlit pandas plotly)
Data file: atlantic_france_clean.csv must sit alongside this script
           (or update DATA_PATH below).
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------
# Page config & theming
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Atlantic | France Top 50 Content Compliance Dashboard",
    page_icon="🇫🇷",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#1c2d5e"
RED = "#c8102e"
GOLD = "#d4a017"
GREY = "#7a7a7a"
BLUE = "#3a6ea5"
PALETTE = [NAVY, RED, GOLD, BLUE, GREY]

DATA_PATH = "atlantic_france_clean.csv"

st.markdown(
    f"""
    <style>
    .main {{ background-color: #f7f8fa; }}
    .stMetric {{ background-color: white; padding: 14px; border-radius: 10px;
                 border: 1px solid #e5e7eb; }}
    h1, h2, h3 {{ color: {NAVY}; }}
    .compliance-box {{ background-color: #fff3f3; border-left: 5px solid {RED};
                        padding: 14px 18px; border-radius: 6px; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# Data loading
# ------------------------------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["date"])
    if "duration_min" not in df.columns:
        df["duration_min"] = df["duration_ms"] / 60000
    return df


try:
    df_raw = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find `{DATA_PATH}`. Place the cleaned dataset in the same "
        "folder as this script, or edit DATA_PATH at the top of the file."
    )
    st.stop()

# ------------------------------------------------------------------
# Sidebar — User Capabilities (filters)
# ------------------------------------------------------------------
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/2/2b/Flag_of_France.svg",
    width=60,
)
st.sidebar.title("Atlantic Recording Corp.")
st.sidebar.caption("France Top 50 — Content Compliance Dashboard")
st.sidebar.markdown("---")

st.sidebar.subheader("Filters")

min_date, max_date = df_raw["date"].min(), df_raw["date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

rank_tier_choice = st.sidebar.radio(
    "Rank tier",
    options=["Top 10", "Top 25", "Top 50"],
    index=2,
    help="Restrict the analysis to a chart depth.",
)
tier_cutoff = {"Top 10": 10, "Top 25": 25, "Top 50": 50}[rank_tier_choice]

explicit_choice = st.sidebar.select_slider(
    "Explicit content toggle",
    options=["Clean only", "Both", "Explicit only"],
    value="Both",
)

album_type_choice = st.sidebar.multiselect(
    "Album type",
    options=sorted(df_raw["album_type"].dropna().unique().tolist()),
    default=sorted(df_raw["album_type"].dropna().unique().tolist()),
)

# ------------------------------------------------------------------
# Apply filters
# ------------------------------------------------------------------
mask = (
    (df_raw["date"] >= pd.to_datetime(start_date))
    & (df_raw["date"] <= pd.to_datetime(end_date))
    & (df_raw["position"] <= tier_cutoff)
    & (df_raw["album_type"].isin(album_type_choice))
)
df = df_raw[mask].copy()

if explicit_choice == "Clean only":
    df = df[~df["is_explicit"]]
elif explicit_choice == "Explicit only":
    df = df[df["is_explicit"]]

if df.empty:
    st.warning("No rows match the current filter selection. Adjust filters in the sidebar.")
    st.stop()

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.title("🇫🇷 France Top 50 — Content Compliance & Format Intelligence")
st.caption(
    "Audience Sensitivity, Content Compliance & Format Preference Analysis "
    "for Atlantic Recording Corporation · Unified Mentor Project"
)

# ------------------------------------------------------------------
# KPI row
# ------------------------------------------------------------------
explicit_share = df["is_explicit"].mean() * 100
clean_share = 100 - explicit_share
single_share = (df["album_type"] == "single").mean() * 100
album_share = (df["album_type"] == "album").mean() * 100
avg_duration = df["duration_min"].mean()
avg_tracks = df["total_tracks"].mean()
clean_dominance_ratio = clean_share / explicit_share if explicit_share > 0 else np.nan
single_album_ratio = single_share / album_share if album_share > 0 else np.nan
acceptance_score = df["popularity"].mean() / 100

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Explicit Content Share", f"{explicit_share:.1f}%")
k2.metric("Clean Dominance Ratio", f"{clean_dominance_ratio:.2f}x")
k3.metric("Single vs Album Ratio", f"{single_album_ratio:.2f}x")
k4.metric("Avg Song Duration", f"{avg_duration:.2f} min")
k5.metric("Avg Album Size", f"{avg_tracks:.1f} tracks")
k6.metric("Content Acceptance Score", f"{acceptance_score:.2f}")

st.markdown("---")

# ------------------------------------------------------------------
# Compliance summary panel
# ------------------------------------------------------------------
with st.container():
    st.markdown(
        f"""
        <div class="compliance-box">
        <b>Content Compliance Summary — {rank_tier_choice}, {start_date} to {end_date}</b><br>
        Clean tracks average <b>{df.loc[~df['is_explicit'],'popularity'].mean():.1f}</b> popularity vs.
        <b>{df.loc[df['is_explicit'],'popularity'].mean():.1f}</b> for explicit tracks —
        clean content {"outperforms" if df.loc[~df['is_explicit'],'popularity'].mean() > df.loc[df['is_explicit'],'popularity'].mean() else "underperforms"} explicit content in this selection.
        Singles represent <b>{single_share:.1f}%</b> and albums <b>{album_share:.1f}%</b> of entries.
        Larger albums (17+ tracks) show a correlation of
        <b>{df['total_tracks'].corr(df['popularity']):.2f}</b> between album size and track popularity,
        {"suggesting a dilution effect" if df['total_tracks'].corr(df['popularity']) < -0.05 else "suggesting no strong dilution effect"}.
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("###")

# ------------------------------------------------------------------
# Tabs — Core Modules
# ------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🔞 Explicit vs Clean",
        "💿 Album Format",
        "⏱️ Song Duration",
        "🏆 Rank-Tier Attributes",
    ]
)

# --- Tab 1: Explicit vs clean content analysis ---
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        counts = df["is_explicit"].value_counts().rename({True: "Explicit", False: "Clean"})
        fig = px.pie(
            values=counts.values,
            names=counts.index,
            hole=0.45,
            color=counts.index,
            color_discrete_map={"Explicit": RED, "Clean": NAVY},
            title="Explicit vs Clean Content Share",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        pop = df.groupby("is_explicit")["popularity"].mean().rename({True: "Explicit", False: "Clean"})
        fig = px.bar(
            x=pop.index, y=pop.values,
            color=pop.index,
            color_discrete_map={"Explicit": RED, "Clean": NAVY},
            labels={"x": "", "y": "Average Popularity"},
            title="Average Popularity: Explicit vs Clean",
        )
        fig.update_layout(showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Explicit Share by Rank Position (rolling by day)")
    daily_explicit = (
        df.groupby("date")["is_explicit"].mean().mul(100).rename("Explicit %").reset_index()
    )
    fig = px.line(daily_explicit, x="date", y="Explicit %", color_discrete_sequence=[RED])
    fig.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Explicit Content Share by Rank Tier")
    tier_order = ["Top 10", "Top 25", "Top 50"]
    tier_explicit = df.groupby("rank_tier")["is_explicit"].mean().mul(100).reindex(
        [t for t in tier_order if t in df["rank_tier"].unique()]
    )
    fig = px.bar(
        x=tier_explicit.index, y=tier_explicit.values,
        color_discrete_sequence=[RED],
        labels={"x": "Rank Tier", "y": "Explicit Share (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Album format distribution charts ---
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        fc = df["album_type"].value_counts()
        fig = px.pie(
            values=fc.values, names=[n.title() for n in fc.index],
            title="Release Format Share", color_discrete_sequence=PALETTE,
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        popf = df.groupby("album_type")["popularity"].mean().sort_values(ascending=False)
        fig = px.bar(
            x=[i.title() for i in popf.index], y=popf.values,
            color_discrete_sequence=[NAVY],
            labels={"x": "Format", "y": "Average Popularity"},
            title="Average Popularity by Format",
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Album Size Distribution & Dilution Effect")
    def size_bucket(n):
        if n <= 1: return "Single (1)"
        elif n <= 8: return "EP (2-8)"
        elif n <= 16: return "Standard (9-16)"
        else: return "Large/Deluxe (17+)"
    df["album_size_bucket"] = df["total_tracks"].apply(size_bucket)
    order = ["Single (1)", "EP (2-8)", "Standard (9-16)", "Large/Deluxe (17+)"]

    c3, c4 = st.columns(2)
    with c3:
        dist = df["album_size_bucket"].value_counts().reindex(order)
        fig = px.bar(
            x=dist.values, y=dist.index, orientation="h",
            color_discrete_sequence=[BLUE],
            labels={"x": "Chart Entries", "y": ""},
            title="Album Size Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        pop_size = df.groupby("album_size_bucket")["popularity"].mean().reindex(order)
        fig = px.bar(
            x=pop_size.index, y=pop_size.values,
            color_discrete_sequence=[GOLD],
            labels={"x": "Album Size", "y": "Average Popularity"},
            title="Album Size vs Popularity",
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    corr = df["total_tracks"].corr(df["popularity"])
    st.info(f"Correlation between album size (total tracks) and popularity: **{corr:.3f}** — "
            f"{'a mild dilution effect (larger albums slightly reduce average track popularity)' if corr < -0.05 else 'no strong relationship'}.")

# --- Tab 3: Song duration histograms ---
with tab3:
    c1, c2 = st.columns([2, 1])
    with c1:
        fig = px.histogram(
            df, x="duration_min", nbins=40, color_discrete_sequence=[NAVY],
            labels={"duration_min": "Duration (minutes)"},
            title="Song Duration Distribution",
        )
        fig.add_vline(x=df["duration_min"].mean(), line_dash="dash", line_color=RED,
                       annotation_text=f"Mean {df['duration_min'].mean():.2f} min")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        def dur_bucket(m):
            if m < 2.5: return "Short (<2.5m)"
            elif m <= 3.5: return "Medium (2.5-3.5m)"
            else: return "Long (>3.5m)"
        df["duration_bucket"] = df["duration_min"].apply(dur_bucket)
        dbo = ["Short (<2.5m)", "Medium (2.5-3.5m)", "Long (>3.5m)"]
        dcounts = df["duration_bucket"].value_counts().reindex(dbo)
        fig = px.pie(values=dcounts.values, names=dcounts.index,
                     title="Duration Buckets", color_discrete_sequence=[GOLD, NAVY, RED])
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        popd = df.groupby("duration_bucket")["popularity"].mean().reindex(dbo)
        fig = px.bar(x=popd.index, y=popd.values, color_discrete_sequence=[BLUE],
                     labels={"x": "Duration Bucket", "y": "Average Popularity"},
                     title="Popularity by Duration Bucket")
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        posd = df.groupby("duration_bucket")["position"].mean().reindex(dbo)
        fig = px.bar(x=posd.index, y=posd.values, color_discrete_sequence=[GREY],
                     labels={"x": "Duration Bucket", "y": "Average Chart Position"},
                     title="Average Rank by Duration Bucket (lower = higher rank)")
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    corr_d = df["duration_min"].corr(df["popularity"])
    st.info(f"Correlation between duration and popularity: **{corr_d:.3f}** — a weak relationship, "
            f"indicating duration alone is not a strong driver of chart popularity in this selection.")

# --- Tab 4: Rank-tier content attribute comparison ---
with tab4:
    st.subheader("Content Attribute Density: Top 10 vs Top 25 vs Top 50")
    rows = []
    for tname, cutoff in [("Top 10", 10), ("Top 25", 25), ("Top 50", 50)]:
        sub = df_raw[
            (df_raw["date"] >= pd.to_datetime(start_date))
            & (df_raw["date"] <= pd.to_datetime(end_date))
            & (df_raw["position"] <= cutoff)
        ]
        if explicit_choice == "Clean only":
            sub = sub[~sub["is_explicit"]]
        elif explicit_choice == "Explicit only":
            sub = sub[sub["is_explicit"]]
        sub = sub[sub["album_type"].isin(album_type_choice)]
        if len(sub) == 0:
            continue
        rows.append({
            "Rank Tier": tname,
            "Explicit %": round(sub["is_explicit"].mean() * 100, 1),
            "Single %": round((sub["album_type"] == "single").mean() * 100, 1),
            "Album %": round((sub["album_type"] == "album").mean() * 100, 1),
            "Avg Duration (min)": round(sub["duration_min"].mean(), 2),
            "Avg Album Size": round(sub["total_tracks"].mean(), 1),
            "Avg Popularity": round(sub["popularity"].mean(), 1),
        })
    concentration_df = pd.DataFrame(rows).set_index("Rank Tier")
    st.dataframe(concentration_df, use_container_width=True)

    fig = go.Figure()
    for col, color in zip(["Explicit %", "Single %"], [RED, NAVY]):
        fig.add_trace(go.Bar(name=col, x=concentration_df.index, y=concentration_df[col], marker_color=color))
    fig.update_layout(barmode="group", title="Explicit % and Single % Across Rank Tiers", yaxis_title="Share (%)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top Artists in Current Selection")
    top_artists = df["artist"].value_counts().head(10)
    fig = px.bar(x=top_artists.values, y=top_artists.index, orientation="h",
                 color_discrete_sequence=[NAVY],
                 labels={"x": "Chart Appearances", "y": ""})
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("View filtered raw data"):
        st.dataframe(
            df[["date", "position", "song", "artist", "popularity", "duration_min",
                "album_type", "total_tracks", "is_explicit"]].sort_values(["date", "position"]),
            use_container_width=True,
        )

st.markdown("---")
st.caption(
    "Data source: Atlantic Recording Corporation daily France Top 50 playlist snapshots · "
    "Dashboard built for Unified Mentor project deliverable."
)