"""
Instagram Performance Analytics - Sugar Cosmetics
Streamlit dashboard (Labmentrix project)

Run:  streamlit run app.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from data_prep import WEEKDAYS, prepare  # noqa: E402

# ------------------------------------------------------------------
# Page + design tokens
# ------------------------------------------------------------------
st.set_page_config(page_title="Sugar Cosmetics | Instagram Insights",
                   page_icon="📊", layout="wide")

INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"
ACCENT = "#2a78d6"          # single-series colour
ACCENT_DARK = "#1c5cab"     # highlight (best bar)
MUTED = "#b7d3f6"           # de-emphasised bars
TYPE_COLORS = {"Image": "#2a78d6", "Reel": "#eb6834",
               "Story": "#1baf7a", "Video": "#eda100"}
FUNNEL_RAMP = ["#104281", "#184f95", "#1c5cab", "#256abf", "#3987e5", "#6da7ec"]

st.markdown(f"""
<style>
  .block-container {{padding-top: 1.6rem; padding-bottom: 2rem;}}
  h1, h2, h3 {{color: {INK}; letter-spacing: -0.01em;}}
  .kpi {{background: {SURFACE}; border: 1px solid {GRID}; border-radius: 10px;
         padding: 14px 16px; height: 100%;}}
  .kpi .lbl {{color: {INK_2}; font-size: 0.82rem; margin-bottom: 4px;}}
  .kpi .val {{color: {INK}; font-size: 1.65rem; font-weight: 700; line-height: 1.1;}}
  .kpi .sub {{color: {INK_2}; font-size: 0.75rem; margin-top: 4px;}}
  .note {{color: {INK_2}; font-size: 0.85rem;}}
  .insight {{background: #eef4fc; border-left: 4px solid {ACCENT};
             padding: 10px 14px; border-radius: 6px; margin: 6px 0 14px 0;
             color: {INK}; font-size: 0.92rem;}}
  div[data-testid="stTabs"] button p {{font-size: 0.9rem;}}
</style>
""", unsafe_allow_html=True)


def style(fig, height=380, legend=False):
    fig.update_layout(
        template="plotly_white", height=height,
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(color=INK, size=12),
        margin=dict(l=10, r=20, t=50, b=10),
        title_font=dict(size=15, color=INK),
        showlegend=legend, bargap=0.25,
        hoverlabel=dict(bgcolor="white", font_color=INK, bordercolor=GRID),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    title_text=""),
    )
    fig.update_xaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False,
                     title_font=dict(color=INK_2), tickfont=dict(color=INK_2))
    fig.update_yaxes(gridcolor=GRID, linecolor=AXIS, zeroline=False,
                     title_font=dict(color=INK_2), tickfont=dict(color=INK_2))
    fig.update_traces(selector=dict(type="bar"),
                      marker_line_width=0, marker_cornerradius=4, cliponaxis=False)
    return fig


def fmt(n, dec=1):
    n = float(n)
    for div, suf in [(1e9, "B"), (1e6, "M"), (1e3, "K")]:
        if abs(n) >= div:
            return f"{n / div:.{dec}f}{suf}"
    return f"{n:,.0f}"


def kpi(col, label, value, sub=""):
    col.markdown(f"<div class='kpi'><div class='lbl'>{label}</div>"
                 f"<div class='val'>{value}</div><div class='sub'>{sub}</div></div>",
                 unsafe_allow_html=True)


def insight(text):
    st.markdown(f"<div class='insight'>💡 {text}</div>", unsafe_allow_html=True)


def highlight_colors(values, best=None, selected=None):
    """Colour list: selected bar(s) dark, others accent; or best bar dark."""
    out = []
    for v in values:
        if selected:
            out.append(ACCENT_DARK if v in selected else MUTED)
        else:
            out.append(ACCENT_DARK if v == best else ACCENT)
    return out


# ------------------------------------------------------------------
# Data
# ------------------------------------------------------------------
@st.cache_data(show_spinner="Loading & preparing data...")
def load():
    return prepare()


posts, tags = load()
ACCOUNT_ER = posts["Engagement Rate (%)"].mean()
MONTHS = posts.sort_values("Month")["Month-Year"].unique().tolist()
HASHTAGS = sorted(tags["Hashtag"].unique())

# ------------------------------------------------------------------
# Sidebar filters (apply to every page)
# ------------------------------------------------------------------
st.sidebar.markdown("## 🎛️ Filters")
st.sidebar.caption("Filters apply to every tab.")
f_type = st.sidebar.multiselect("Post Type", sorted(posts["Post Type"].unique()))
f_month = st.sidebar.multiselect("Month", MONTHS)
f_tag = st.sidebar.multiselect("Hashtag", HASHTAGS)
f_camp = st.sidebar.multiselect("Campaign Type", sorted(posts["Campaign Type"].unique()))
f_src = st.sidebar.multiselect("Engagement Source", sorted(posts["Engagement Source"].unique()))
st.sidebar.caption("Leave a filter empty to include everything.")

df = posts
if f_type:
    df = df[df["Post Type"].isin(f_type)]
if f_month:
    df = df[df["Month-Year"].isin(f_month)]
if f_camp:
    df = df[df["Campaign Type"].isin(f_camp)]
if f_src:
    df = df[df["Engagement Source"].isin(f_src)]
if f_tag:
    df = df[df["Post ID"].isin(tags.loc[tags["Hashtag"].isin(f_tag), "Post ID"])]

dtags = tags[tags["Post ID"].isin(df["Post ID"])]
if f_tag:
    dtags = dtags[dtags["Hashtag"].isin(f_tag)]

st.sidebar.markdown("---")
st.sidebar.caption("Project by **Adarsh Shrikant Tiwari**")
st.sidebar.markdown(f"**Posts in view:** {len(df):,}  \n"
                    f"<span class='note'>{len(df) / len(posts):.0%} of all posts</span>",
                    unsafe_allow_html=True)

# ------------------------------------------------------------------
# Header
# ------------------------------------------------------------------
st.markdown("## 📊 Sugar Cosmetics · Instagram Performance Analytics")
st.markdown(f"<span class='note'>{len(posts):,} posts · "
            f"{posts['Post Date'].min():%d %b %Y} to {posts['Post Date'].max():%d %b %Y} · "
            "Engagement Rate = (Likes + Comments + Shares + Saves) ÷ Reach</span>",
            unsafe_allow_html=True)

if df.empty:
    st.warning("No posts match the selected filters. Clear a filter in the sidebar.")
    st.stop()

tabs = st.tabs([
    "🏠 Dashboard",
    "1 · KPI Overview",
    "2 · Monthly Trend",
    "3 · Top 10 by Likes",
    "4 · Top 10 by ER",
    "5 · Post Type",
    "6 · Day of Week",
    "7 · Engagement Funnel",
    "8 · Hashtags",
    "📈 Campaigns & Growth",
    "10 · Recommendations",
    "🗂️ Data",
])


# ------------------------------------------------------------------
# Chart builders (re-used by dashboard + individual sheets)
# ------------------------------------------------------------------
def kpi_row(d):
    c = st.columns(5)
    kpi(c[0], "Total Posts", f"{len(d):,}", f"{d['Post Date'].nunique()} active days")
    kpi(c[1], "Total Likes", fmt(d["Likes"].sum(), 2), f"avg {d['Likes'].mean():,.0f} / post")
    kpi(c[2], "Total Comments", fmt(d["Comments"].sum(), 2), f"avg {d['Comments'].mean():,.0f} / post")
    kpi(c[3], "Total Reach", fmt(d["Reach"].sum(), 2), f"avg {d['Reach'].mean():,.0f} / post")
    kpi(c[4], "Avg Engagement Rate", f"{d['Engagement Rate (%)'].mean():.2f}%",
        f"median {d['Engagement Rate (%)'].median():.2f}%")


def monthly_posts_fig(d, height=360):
    m = d.groupby("Month").agg(Posts=("Post ID", "size"),
                               ER=("Engagement Rate (%)", "mean")).reset_index()
    fig = go.Figure(go.Scatter(
        x=m["Month"], y=m["Posts"], mode="lines+markers",
        line=dict(color=ACCENT, width=2), marker=dict(size=8, color=ACCENT,
                                                      line=dict(color=SURFACE, width=2)),
        customdata=m["ER"],
        hovertemplate="<b>%{x|%b %Y}</b><br>Posts: %{y:,}<br>Avg ER: %{customdata:.2f}%<extra></extra>"))
    fig.update_layout(title="Posts per Month", hovermode="x unified")
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig.update_yaxes(title="Posts", rangemode="tozero")
    return style(fig, height)


def type_er_fig(d, selected=None, height=360):
    t = d.groupby("Post Type")["Engagement Rate (%)"].agg(["mean", "size"]).reset_index()
    best = t.loc[t["mean"].idxmax(), "Post Type"]
    fig = go.Figure(go.Bar(
        x=t["Post Type"], y=t["mean"], text=t["mean"].map("{:.2f}%".format),
        textposition="outside", marker_color=highlight_colors(t["Post Type"], best, selected),
        customdata=t["size"],
        hovertemplate="<b>%{x}</b><br>Avg ER: %{y:.2f}%<br>Posts: %{customdata:,}<extra></extra>"))
    fig.update_layout(title="Avg Engagement Rate by Post Type")
    fig.update_yaxes(title="Avg ER (%)", range=[0, t["mean"].max() * 1.18])
    return style(fig, height)


def weekday_er_fig(d, selected=None, height=360):
    w = (d.groupby("Weekday", observed=True)["Engagement Rate (%)"]
         .agg(["mean", "size"]).reindex(WEEKDAYS).dropna().reset_index())
    best = w.loc[w["mean"].idxmax(), "Weekday"]
    fig = go.Figure(go.Bar(
        x=w["Weekday"].str[:3], y=w["mean"], text=w["mean"].map("{:.2f}%".format),
        textposition="outside", marker_color=highlight_colors(w["Weekday"], best, selected),
        customdata=w[["Weekday", "size"]],
        hovertemplate="<b>%{customdata[0]}</b><br>Avg ER: %{y:.2f}%<br>Posts: %{customdata[1]:,}<extra></extra>"))
    fig.update_layout(title="Avg Engagement Rate by Weekday")
    fig.update_yaxes(title="Avg ER (%)", range=[0, w["mean"].max() * 1.18])
    return style(fig, height)


def funnel_values(d):
    stages = ["Impressions", "Reach", "Likes", "Comments", "Shares", "Saves"]
    return stages, [d[s].sum() for s in stages]


def funnel_fig(d, height=380):
    """Funnel drawn as horizontal bars on a log scale so small steps stay visible."""
    stages, vals = funnel_values(d)
    pct_impr = [v / vals[0] * 100 for v in vals]
    pct_prev = [100] + [vals[i] / vals[i - 1] * 100 for i in range(1, len(vals))]
    labels = [f"{fmt(v, 2)} · {p:.2f}%" if p < 10 else f"{fmt(v, 2)} · {p:.1f}%"
              for v, p in zip(vals, pct_impr)]
    fig = go.Figure(go.Bar(
        y=stages, x=vals, orientation="h", marker_color=FUNNEL_RAMP,
        text=labels, textposition="outside", textfont=dict(color=INK),
        customdata=list(zip(pct_impr, pct_prev)),
        hovertemplate="<b>%{y}</b><br>Total: %{x:,}<br>% of Impressions: %{customdata[0]:.2f}%"
                      "<br>% of previous step: %{customdata[1]:.1f}%<extra></extra>"))
    fig.update_layout(title="Engagement Funnel (value · % of impressions, log scale)")
    fig.update_xaxes(type="log", range=[np.log10(min(vals)) - 0.3, np.log10(max(vals)) + 0.9],
                     showticklabels=False, showgrid=False)
    fig.update_yaxes(autorange="reversed")
    return style(fig, height)


def hashtag_er_fig(dt, selected=None, height=360):
    h = (dt.groupby("Hashtag").agg(ER=("Engagement Rate (%)", "mean"),
                                   Posts=("Post ID", "size"),
                                   Reach=("Reach", "mean"))
         .sort_values("ER").reset_index())
    best = h.loc[h["ER"].idxmax(), "Hashtag"]
    fig = go.Figure(go.Bar(
        y=h["Hashtag"], x=h["ER"], orientation="h",
        text=h["ER"].map("{:.2f}%".format), textposition="outside",
        marker_color=highlight_colors(h["Hashtag"], best, selected),
        customdata=h[["Posts", "Reach"]],
        hovertemplate="<b>%{y}</b><br>Avg ER: %{x:.2f}%<br>Posts: %{customdata[0]:,}"
                      "<br>Avg Reach: %{customdata[1]:,.0f}<extra></extra>"))
    fig.update_layout(title="Avg Engagement Rate by Hashtag")
    fig.update_xaxes(title="Avg ER (%)", range=[0, h["ER"].max() * 1.2])
    return style(fig, height)


def top10_fig(d, by, title, height=440):
    top = d.nlargest(10, by).iloc[::-1]
    is_er = by == "Engagement Rate (%)"
    text = top[by].map("{:.2f}%".format) if is_er else top[by].map("{:,.0f}".format)
    fig = go.Figure(go.Bar(
        y=top["Post Label"], x=top[by], orientation="h", text=text,
        textposition="outside", marker_color=[TYPE_COLORS.get(t, ACCENT) for t in top["Post Type"]],
        showlegend=False,
        customdata=top[["Likes", "Reach", "Engagement Rate (%)", "Comments", "Saves", "Hashtags"]],
        hovertemplate="<b>%{y}</b><br>Likes: %{customdata[0]:,}<br>Reach: %{customdata[1]:,}"
                      "<br>ER: %{customdata[2]:.2f}%<br>Comments: %{customdata[3]:,}"
                      "<br>Saves: %{customdata[4]:,}<br>%{customdata[5]}<extra></extra>"))
    # legend entries for post type colours
    for t, c in TYPE_COLORS.items():
        if t in top["Post Type"].values:
            fig.add_trace(go.Bar(x=[None], y=[None], name=t, marker_color=c, showlegend=True))
    fig.update_layout(title=title)
    fig.update_xaxes(title=by, range=[0, top[by].max() * 1.18])
    fig.update_yaxes(tickfont=dict(size=11))
    return style(fig, height, legend=True)


XF_FIELDS = {"type": "x", "day": "x", "tag": "y"}


def xf_store():
    return st.session_state.setdefault("xf", {"type": [], "day": [], "tag": []})


def on_chart_select(dim):
    """Callback: copy the clicked bars of a chart into the persistent cross-filter store."""
    def _cb():
        state = st.session_state.get(f"xf_{dim}_{st.session_state.get('xf_nonce', 0)}")
        try:
            pts = state["selection"]["points"]
        except (TypeError, KeyError):
            pts = []
        field = XF_FIELDS[dim]
        xf_store()[dim] = sorted({p.get(field) for p in pts if p.get(field) is not None})
    return _cb


# ------------------------------------------------------------------
# TAB 0 - DASHBOARD (Task 9)
# ------------------------------------------------------------------
with tabs[0]:
    st.markdown("### Instagram Insights Report")
    st.caption("Click a bar in **Post Type**, **Weekday** or **Hashtag** to cross-filter the rest "
               "of the dashboard (filter action). Selections combine across charts "
               "(e.g. Reel + Wednesday). Use the button to reset.")

    nonce = st.session_state.setdefault("xf_nonce", 0)
    xf = xf_store()
    sel_type = xf["type"]
    sel_day = [d for d in WEEKDAYS if d[:3] in xf["day"]]
    sel_tag = xf["tag"]

    def cross(d, skip=None):
        if sel_type and skip != "type":
            d = d[d["Post Type"].isin(sel_type)]
        if sel_day and skip != "day":
            d = d[d["Weekday"].isin(sel_day)]
        if sel_tag and skip != "tag":
            d = d[d["Post ID"].isin(tags.loc[tags["Hashtag"].isin(sel_tag), "Post ID"])]
        return d

    def cross_tags(skip=None):
        return dtags[dtags["Post ID"].isin(cross(df, skip)["Post ID"])]

    active = [f"Post Type = {', '.join(sel_type)}" if sel_type else "",
              f"Weekday = {', '.join(sel_day)}" if sel_day else "",
              f"Hashtag = {', '.join(sel_tag)}" if sel_tag else ""]
    active = [a for a in active if a]
    cc1, cc2 = st.columns([5, 1])
    cc1.markdown("**Active cross-filters:** " + (" · ".join(active) if active else "_none_"))
    if cc2.button("↺ Clear selections", width="stretch"):
        st.session_state["xf_nonce"] = nonce + 1
        st.session_state["xf"] = {"type": [], "day": [], "tag": []}
        st.rerun()

    dd = cross(df)
    if dd.empty:
        st.warning("No posts for this combination of selections.")
    else:
        kpi_row(dd)
        st.write("")
        r1 = st.columns([1.4, 1])
        with r1[0]:
            st.plotly_chart(monthly_posts_fig(dd, 340), width="stretch")
        with r1[1]:
            st.plotly_chart(funnel_fig(dd, 340), width="stretch")

        r2 = st.columns(3)
        with r2[0]:
            st.plotly_chart(type_er_fig(cross(df, "type"), sel_type, 340),
                            width="stretch", key=f"xf_type_{nonce}",
                            on_select=on_chart_select("type"), selection_mode="points")
        with r2[1]:
            st.plotly_chart(weekday_er_fig(cross(df, "day"), sel_day, 340),
                            width="stretch", key=f"xf_day_{nonce}",
                            on_select=on_chart_select("day"), selection_mode="points")
        with r2[2]:
            st.plotly_chart(hashtag_er_fig(cross_tags("tag"), sel_tag, 340),
                            width="stretch", key=f"xf_tag_{nonce}",
                            on_select=on_chart_select("tag"), selection_mode="points")

        r3 = st.columns(2)
        with r3[0]:
            st.plotly_chart(top10_fig(dd, "Likes", "Top 10 Posts by Likes", 420),
                            width="stretch")
        with r3[1]:
            st.plotly_chart(top10_fig(dd, "Engagement Rate (%)",
                                      "Top 10 Posts by Engagement Rate", 420),
                            width="stretch")

# ------------------------------------------------------------------
# TAB 1 - KPI OVERVIEW
# ------------------------------------------------------------------
with tabs[1]:
    st.markdown("### Task 1 · KPI Overview — How is the account performing?")
    kpi_row(df)
    st.write("")
    c = st.columns(5)
    kpi(c[0], "Total Impressions", fmt(df["Impressions"].sum(), 2))
    kpi(c[1], "Total Shares", fmt(df["Shares"].sum(), 2))
    kpi(c[2], "Total Saves", fmt(df["Saves"].sum(), 2))
    kpi(c[3], "Profile Visits", fmt(df["Profile Visits"].sum(), 2))
    kpi(c[4], "New Follows", fmt(df["Follows"].sum(), 2),
        f"{df['Follows'].sum() / df['Reach'].sum() * 100:.2f}% of reach")
    st.write("")

    comp = pd.DataFrame({
        "Action": ["Likes", "Comments", "Saves", "Shares"],
        "Total": [df[x].sum() for x in ["Likes", "Comments", "Saves", "Shares"]]})
    comp["Share"] = comp["Total"] / comp["Total"].sum() * 100
    fig = go.Figure(go.Bar(x=comp["Share"], y=comp["Action"], orientation="h",
                           text=comp["Share"].map("{:.1f}%".format), textposition="outside",
                           marker_color=ACCENT,
                           customdata=comp["Total"],
                           hovertemplate="<b>%{y}</b><br>%{x:.1f}% of engagement<br>Total: %{customdata:,}<extra></extra>"))
    fig.update_layout(title="What makes up total engagement?")
    fig.update_xaxes(title="% of total engagement", range=[0, 100])
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style(fig, 300), width="stretch")

    total_eng = df["Total Engagement"].sum()
    insight(f"Across {len(df):,} posts the account earned <b>{fmt(df['Reach'].sum(), 2)}</b> reach and "
            f"<b>{fmt(total_eng, 2)}</b> engagements. Average engagement rate is "
            f"<b>{df['Engagement Rate (%)'].mean():.2f}%</b> of reach. Likes make up "
            f"<b>{comp.loc[0, 'Share']:.0f}%</b> of all engagement — saves and shares (the actions "
            f"Instagram's algorithm rewards most) are only {comp.loc[2:3, 'Share'].sum():.0f}% combined.")

# ------------------------------------------------------------------
# TAB 2 - MONTHLY TREND
# ------------------------------------------------------------------
with tabs[2]:
    st.markdown("### Task 2 · Monthly Posting Trend")
    st.plotly_chart(monthly_posts_fig(df, 400), width="stretch")

    m = df.groupby("Month").agg(Posts=("Post ID", "size"),
                                ER=("Engagement Rate (%)", "mean"),
                                Reach=("Reach", "sum"),
                                Follows=("Follows", "sum")).reset_index()
    fig = go.Figure(go.Scatter(x=m["Month"], y=m["ER"], mode="lines+markers",
                               line=dict(color=ACCENT, width=2), marker=dict(size=8),
                               hovertemplate="<b>%{x|%b %Y}</b><br>Avg ER: %{y:.2f}%<extra></extra>"))
    fig.add_hline(y=ACCOUNT_ER, line_dash="dot", line_color=INK_2,
                  annotation_text=f"Account avg {ACCOUNT_ER:.2f}%",
                  annotation_font_color=INK_2)
    fig.update_layout(title="Avg Engagement Rate per Month")
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    fig.update_yaxes(title="Avg ER (%)", range=[0, max(m["ER"].max() * 1.15, 1)])
    st.plotly_chart(style(fig, 340), width="stretch")

    full = m.iloc[1:-1] if len(m) > 2 else m
    insight(f"Posting is very consistent: about <b>{full['Posts'].mean():,.0f} posts per full month</b> "
            f"(≈{df.groupby('Post Date').size().mean():.0f} per day). "
            f"{m['Month'].min():%b %Y} and {m['Month'].max():%b %Y} are partial months, so they show fewer posts. "
            f"Monthly engagement rate stays in a narrow band "
            f"({m['ER'].min():.2f}%–{m['ER'].max():.2f}%) — no seasonal spike or decline.")
    with st.expander("Monthly table"):
        mt = m.copy()
        mt["Month"] = mt["Month"].dt.strftime("%b %Y")
        st.dataframe(mt.round(2), width="stretch", hide_index=True)

# ------------------------------------------------------------------
# TAB 3 - TOP 10 BY LIKES
# ------------------------------------------------------------------
TABLE_COLS = ["Post ID", "Post Date", "Post Type", "Campaign Type", "Engagement Source",
              "Hashtags", "Likes", "Comments", "Shares", "Saves", "Reach",
              "Engagement Rate (%)"]

with tabs[3]:
    st.markdown("### Task 3 · Top 10 Posts by Likes")
    st.caption("Dataset has no caption column, so each post is identified by a label: "
               "Post ID | Type | Campaign | Date.")
    st.plotly_chart(top10_fig(df, "Likes", "Top 10 Posts by Likes", 480), width="stretch")
    t = df.nlargest(10, "Likes")[TABLE_COLS].copy()
    t["Post Date"] = t["Post Date"].dt.strftime("%d %b %Y")
    st.dataframe(t.round(2), width="stretch", hide_index=True)
    insight(f"Every top-10 post by likes has very high reach "
            f"(avg {t['Reach'].mean():,.0f} vs account avg {df['Reach'].mean():,.0f}). "
            "Likes mostly follow reach — the biggest posts are the ones that were shown to the most people.")

# ------------------------------------------------------------------
# TAB 4 - TOP 10 BY ENGAGEMENT RATE
# ------------------------------------------------------------------
with tabs[4]:
    st.markdown("### Task 4 · Top 10 Posts by Engagement Rate")
    min_reach = st.slider("Minimum reach (to ignore tiny-reach posts)", 0, 20000, 0, 1000)
    d4 = df[df["Reach"] >= min_reach]
    if d4.empty:
        st.info("No posts above this reach.")
    else:
        st.plotly_chart(top10_fig(d4, "Engagement Rate (%)", "Top 10 Posts by Engagement Rate", 480),
                        width="stretch")
        t = d4.nlargest(10, "Engagement Rate (%)")[TABLE_COLS].copy()
        t["Post Date"] = t["Post Date"].dt.strftime("%d %b %Y")
        med_likes = df["Likes"].median()
        t["Hidden Gem?"] = (t["Likes"] < med_likes).map({True: "💎 Yes", False: ""})
        st.dataframe(t.round(2), width="stretch", hide_index=True)
        gems = (t["Likes"] < med_likes).sum()
        insight(f"<b>{gems} of the top 10</b> posts by engagement rate got fewer likes than the median post "
                f"({med_likes:,.0f}). These are <b>hidden gems</b>: small reach, but the people who saw them "
                "engaged strongly — good candidates to boost or repurpose.")

    fig = px.scatter(df.sample(min(len(df), 4000), random_state=1), x="Reach",
                     y="Engagement Rate (%)", color="Post Type",
                     color_discrete_map=TYPE_COLORS, opacity=0.55,
                     hover_data={"Post Label": True, "Likes": ":,"})
    fig.update_traces(marker=dict(size=8, line=dict(color=SURFACE, width=1)))
    fig.update_layout(title="Reach vs Engagement Rate (sample of 4,000 posts)")
    st.plotly_chart(style(fig, 420, legend=True), width="stretch")
    st.caption("Engagement rate is not driven by reach — high-ER posts exist at every reach level.")

# ------------------------------------------------------------------
# TAB 5 - POST TYPE
# ------------------------------------------------------------------
with tabs[5]:
    st.markdown("### Task 5 · Post Type Performance Comparison")
    pt = (df.groupby("Post Type")
          .agg(Posts=("Post ID", "size"), Likes=("Likes", "mean"), Comments=("Comments", "mean"),
               Saves=("Saves", "mean"), Shares=("Shares", "mean"), Reach=("Reach", "mean"),
               ER=("Engagement Rate (%)", "mean"), Follows=("Follows", "mean"))
          .reset_index())
    metrics = ["Likes", "Comments", "Saves", "Shares"]
    fig = make_subplots(rows=1, cols=4, subplot_titles=[f"Avg {m}" for m in metrics])
    for i, mtr in enumerate(metrics, start=1):
        fig.add_trace(go.Bar(x=pt["Post Type"], y=pt[mtr],
                             marker_color=[TYPE_COLORS[t] for t in pt["Post Type"]],
                             text=pt[mtr].map("{:,.0f}".format), textposition="outside",
                             hovertemplate="<b>%{x}</b><br>Avg " + mtr + ": %{y:,.1f}<extra></extra>"),
                      row=1, col=i)
        fig.update_yaxes(range=[0, pt[mtr].max() * 1.2], row=1, col=i)
    fig.update_layout(title="Average interactions per post, by format (each panel has its own scale)")
    st.plotly_chart(style(fig, 400), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(type_er_fig(df), width="stretch")
    with c2:
        fig = go.Figure(go.Bar(x=pt["Post Type"], y=pt["Posts"],
                               marker_color=[TYPE_COLORS[t] for t in pt["Post Type"]],
                               text=pt["Posts"].map("{:,}".format), textposition="outside"))
        fig.update_layout(title="Number of Posts by Type")
        fig.update_yaxes(range=[0, pt["Posts"].max() * 1.2])
        st.plotly_chart(style(fig, 360), width="stretch")
    st.dataframe(pt.round(2), width="stretch", hide_index=True)
    b = pt.loc[pt["ER"].idxmax()]
    w = pt.loc[pt["ER"].idxmin()]
    insight(f"<b>{b['Post Type']}</b> has the highest average engagement rate ({b['ER']:.2f}%) and "
            f"<b>{w['Post Type']}</b> the lowest ({w['ER']:.2f}%). The gap is small "
            f"({b['ER'] - w['ER']:.2f} percentage points), so format alone is not a big lever — "
            "the content inside the format matters more.")

# ------------------------------------------------------------------
# TAB 6 - DAY OF WEEK
# ------------------------------------------------------------------
with tabs[6]:
    st.markdown("### Task 6 · Day of Week Analysis")
    st.plotly_chart(weekday_er_fig(df, height=380), width="stretch")

    wd = (df.groupby("Weekday", observed=True)
          .agg(Posts=("Post ID", "size"), ER=("Engagement Rate (%)", "mean"),
               Likes=("Likes", "mean"), Reach=("Reach", "mean"))
          .reindex(WEEKDAYS).dropna().reset_index())
    base = df["Engagement Rate (%)"].mean()
    wd["vs avg (pp)"] = wd["ER"] - base
    fig = go.Figure(go.Bar(
        x=wd["Weekday"], y=wd["vs avg (pp)"],
        marker_color=["#2a78d6" if v >= 0 else "#eb6834" for v in wd["vs avg (pp)"]],
        text=wd["vs avg (pp)"].map("{:+.2f}".format), textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y:+.3f} pp vs average<extra></extra>"))
    fig.add_hline(y=0, line_color=AXIS)
    fig.update_layout(title="Difference from average engagement rate (percentage points)")
    fig.update_yaxes(title="pp vs avg")
    st.plotly_chart(style(fig, 340), width="stretch")

    hm = (df.pivot_table(index="Post Type", columns="Weekday", values="Engagement Rate (%)",
                         aggfunc="mean", observed=True).reindex(columns=WEEKDAYS))
    fig = px.imshow(hm.round(2), text_auto=".2f", aspect="auto",
                    color_continuous_scale=["#cde2fb", "#6da7ec", "#256abf", "#104281"])
    fig.update_layout(title="Avg ER heatmap: Post Type × Weekday", coloraxis_colorbar_title="ER %")
    st.plotly_chart(style(fig, 330), width="stretch")

    bd = wd.loc[wd["ER"].idxmax()]
    wo = wd.loc[wd["ER"].idxmin()]
    insight(f"Best day: <b>{bd['Weekday']}</b> ({bd['ER']:.2f}%). Weakest: <b>{wo['Weekday']}</b> "
            f"({wo['ER']:.2f}%). The spread between days is only {bd['ER'] - wo['ER']:.2f} pp, so the "
            "audience engages almost equally all week — keep a steady 7-day schedule and place "
            "the most important launches on the stronger days.")

# ------------------------------------------------------------------
# TAB 7 - FUNNEL
# ------------------------------------------------------------------
with tabs[7]:
    st.markdown("### Task 7 · Engagement Funnel")
    st.plotly_chart(funnel_fig(df, 440), width="stretch")
    stages, vals = funnel_values(df)
    ft = pd.DataFrame({"Stage": stages, "Total": vals})
    ft["% of Impressions"] = ft["Total"] / ft["Total"].iloc[0] * 100
    ft["% of Reach"] = ft["Total"] / ft["Total"].iloc[1] * 100
    ft["% of previous step"] = ft["Total"] / ft["Total"].shift(1) * 100
    st.dataframe(ft.round(2), width="stretch", hide_index=True)

    st.markdown("#### Growth funnel: Reach → Profile Visits → Follows")
    g = pd.DataFrame({"Stage": ["Reach", "Profile Visits", "Follows"],
                      "Total": [df["Reach"].sum(), df["Profile Visits"].sum(), df["Follows"].sum()]})
    g["Prev"] = g["Total"] / g["Total"].shift(1) * 100
    g["Label"] = [fmt(v, 2) + ("" if pd.isna(p) else f" · {p:.1f}% of previous step")
                  for v, p in zip(g["Total"], g["Prev"])]
    fig = go.Figure(go.Bar(y=g["Stage"], x=g["Total"], orientation="h",
                           marker_color=FUNNEL_RAMP[:3], text=g["Label"],
                           textposition="outside", textfont=dict(color=INK),
                           hovertemplate="<b>%{y}</b><br>%{x:,}<extra></extra>"))
    fig.update_layout(title="Follower conversion funnel (log scale)")
    fig.update_xaxes(type="log", showticklabels=False, showgrid=False,
                     range=[np.log10(g["Total"].min()) - 0.3, np.log10(g["Total"].max()) + 1.0])
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(style(fig, 300), width="stretch")

    insight(f"{ft.loc[1, '% of Impressions']:.0f}% of impressions are unique reach. "
            f"Only <b>{ft.loc[2, '% of Reach']:.1f}%</b> of reached users like a post, and deeper actions drop sharply: "
            f"comments {ft.loc[3, '% of Reach']:.2f}%, shares {ft.loc[4, '% of Reach']:.2f}%, "
            f"saves {ft.loc[5, '% of Reach']:.2f}% of reach. "
            f"On the growth side, {g['Total'][1] / g['Total'][0] * 100:.1f}% of reach visits the profile and "
            f"<b>{g['Total'][2] / g['Total'][1] * 100:.0f}%</b> of those visitors follow — the profile converts well; "
            "the bottleneck is getting people to visit it.")

# ------------------------------------------------------------------
# TAB 8 - HASHTAGS
# ------------------------------------------------------------------
with tabs[8]:
    st.markdown("### Task 8 · Hashtag Analysis")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(hashtag_er_fig(dtags, height=360), width="stretch")
    with c2:
        hu = dtags["Hashtag"].value_counts().sort_values().reset_index()
        hu.columns = ["Hashtag", "Posts"]
        fig = go.Figure(go.Bar(y=hu["Hashtag"], x=hu["Posts"], orientation="h", marker_color=ACCENT,
                               text=hu["Posts"].map("{:,}".format), textposition="outside"))
        fig.update_layout(title="Hashtag Usage (number of posts)")
        fig.update_xaxes(range=[0, hu["Posts"].max() * 1.2])
        st.plotly_chart(style(fig, 360), width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        hc = (df.groupby("Hashtag Count").agg(ER=("Engagement Rate (%)", "mean"),
                                               Posts=("Post ID", "size"),
                                               Likes=("Likes", "mean")).reset_index())
        best = hc.loc[hc["ER"].idxmax(), "Hashtag Count"]
        fig = go.Figure(go.Bar(x=hc["Hashtag Count"].astype(str) + " tag(s)", y=hc["ER"],
                               marker_color=highlight_colors(hc["Hashtag Count"], best),
                               text=hc["ER"].map("{:.2f}%".format), textposition="outside",
                               customdata=hc["Posts"],
                               hovertemplate="%{x}<br>Avg ER: %{y:.2f}%<br>Posts: %{customdata:,}<extra></extra>"))
        fig.update_layout(title="Avg ER by number of hashtags used")
        fig.update_yaxes(range=[0, hc["ER"].max() * 1.18])
        st.plotly_chart(style(fig, 340), width="stretch")
    with c4:
        combo = df.copy()
        combo["Combo"] = combo["Hashtags"].str.split(",").apply(
            lambda x: " + ".join(sorted(s.strip() for s in x)))
        cb = (combo.groupby("Combo").agg(ER=("Engagement Rate (%)", "mean"), Posts=("Post ID", "size"))
              .query("Posts >= 100").nlargest(10, "ER").sort_values("ER").reset_index())
        fig = go.Figure(go.Bar(y=cb["Combo"], x=cb["ER"], orientation="h", marker_color=ACCENT,
                               text=cb["ER"].map("{:.2f}%".format), textposition="outside",
                               customdata=cb["Posts"],
                               hovertemplate="%{y}<br>Avg ER: %{x:.2f}%<br>Posts: %{customdata:,}<extra></extra>"))
        fig.update_layout(title="Top 10 hashtag combinations by ER (min 100 posts)")
        fig.update_xaxes(range=[0, cb["ER"].max() * 1.25] if len(cb) else None)
        fig.update_yaxes(tickfont=dict(size=10))
        st.plotly_chart(style(fig, 340), width="stretch")

    hp = (dtags.pivot_table(index="Hashtag", columns="Post Type", values="Engagement Rate (%)",
                            aggfunc="mean"))
    fig = px.imshow(hp.round(2), text_auto=".2f", aspect="auto",
                    color_continuous_scale=["#cde2fb", "#6da7ec", "#256abf", "#104281"])
    fig.update_layout(title="Avg ER heatmap: Hashtag × Post Type", coloraxis_colorbar_title="ER %")
    st.plotly_chart(style(fig, 320), width="stretch")

    hs = dtags.groupby("Hashtag")["Engagement Rate (%)"].mean()
    insight(f"<b>{hs.idxmax()}</b> is the strongest hashtag ({hs.max():.2f}% ER) and <b>{hs.idxmin()}</b> the "
            f"weakest ({hs.min():.2f}%). All five tags are used almost equally, and posts with "
            f"<b>{int(best)} hashtags</b> perform best — use 2–3 focused tags rather than a single tag.")

# ------------------------------------------------------------------
# TAB 9 - CAMPAIGNS & GROWTH (bonus - business use cases)
# ------------------------------------------------------------------
with tabs[9]:
    st.markdown("### Campaigns, Engagement Source & Account Growth")
    st.caption("Extra analysis using the additional columns in the dataset "
               "(Campaign Type, Engagement Source, Audience Emotion, Follows).")
    c1, c2 = st.columns(2)

    def simple_bar(d, col, title):
        g = d.groupby(col)["Engagement Rate (%)"].agg(["mean", "size"]).sort_values("mean").reset_index()
        best = g.loc[g["mean"].idxmax(), col]
        fig = go.Figure(go.Bar(y=g[col], x=g["mean"], orientation="h",
                               marker_color=highlight_colors(g[col], best),
                               text=g["mean"].map("{:.2f}%".format), textposition="outside",
                               customdata=g["size"],
                               hovertemplate="<b>%{y}</b><br>Avg ER: %{x:.2f}%<br>Posts: %{customdata:,}<extra></extra>"))
        fig.update_layout(title=title)
        fig.update_xaxes(range=[0, g["mean"].max() * 1.2], title="Avg ER (%)")
        return style(fig, 320)

    with c1:
        st.plotly_chart(simple_bar(df, "Campaign Type", "Avg ER by Campaign Type"), width="stretch")
    with c2:
        st.plotly_chart(simple_bar(df, "Engagement Source", "Avg ER by Engagement Source"),
                        width="stretch")
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(simple_bar(df, "Audience Emotion", "Avg ER by Audience Emotion"),
                        width="stretch")
    with c4:
        src = df.groupby("Engagement Source").agg(Reach=("Reach", "mean"),
                                                  FollowRate=("Follow Rate (%)", "mean")).reset_index()
        fig = go.Figure(go.Bar(x=src["Engagement Source"], y=src["Reach"], marker_color=ACCENT,
                               text=src["Reach"].map("{:,.0f}".format), textposition="outside"))
        fig.update_layout(title="Avg Reach per Post by Engagement Source")
        fig.update_yaxes(range=[0, src["Reach"].max() * 1.2])
        st.plotly_chart(style(fig, 320), width="stretch")

    gm = df.groupby("Month").agg(Follows=("Follows", "sum")).reset_index()
    gm["Cumulative Follows"] = gm["Follows"].cumsum()
    fig = go.Figure(go.Scatter(x=gm["Month"], y=gm["Cumulative Follows"], mode="lines+markers",
                               fill="tozeroy", fillcolor="rgba(42,120,214,0.10)",
                               line=dict(color=ACCENT, width=2), marker=dict(size=8),
                               customdata=gm["Follows"],
                               hovertemplate="<b>%{x|%b %Y}</b><br>New follows: %{customdata:,}"
                                             "<br>Cumulative: %{y:,}<extra></extra>"))
    fig.update_layout(title="Account growth — cumulative new follows gained from posts")
    fig.update_xaxes(dtick="M1", tickformat="%b\n%Y")
    st.plotly_chart(style(fig, 360), width="stretch")

    sp = df.groupby("Engagement Source")["Engagement Rate (%)"].mean()
    ct = df.groupby("Campaign Type")["Engagement Rate (%)"].mean()
    insight(f"Best campaign type: <b>{ct.idxmax()}</b> ({ct.max():.2f}%). "
            f"Paid posts ({sp.get('Paid', float('nan')):.2f}%) do not clearly beat Organic "
            f"({sp.get('Organic', float('nan')):.2f}%) on engagement rate, and do not get more reach per post — "
            "paid spend should be reviewed for ROI. Follower growth is steady month to month "
            "(no viral spikes, no stagnation).")

# ------------------------------------------------------------------
# TAB 10 - RECOMMENDATIONS (Task 10) - based on full dataset
# ------------------------------------------------------------------
with tabs[10]:
    st.markdown("### Task 10 · Strategic Recommendations")
    st.caption("Based on the full dataset (50,000 posts), independent of the sidebar filters.")
    rec_path = ROOT / "reports" / "insights_summary.md"
    if rec_path.exists():
        text = rec_path.read_text(encoding="utf-8")
        # skip the title line of the markdown file
        st.markdown("\n".join(text.splitlines()[1:]))
    else:
        st.info("reports/insights_summary.md not found.")

# ------------------------------------------------------------------
# TAB 11 - DATA
# ------------------------------------------------------------------
with tabs[11]:
    st.markdown("### Data & Method")
    st.markdown("""
**Cleaning & preparation** (`scripts/data_prep.py`)
- 50,000 rows, 14 columns; no missing values, no duplicates; Reach ≤ Impressions for every post.
- Converted *Post Date* to date; extracted **Month-Year** and **Weekday**.
- Created **Post ID** and **Post Label** (the dataset has no caption column).
- Calculated **Total Engagement**, **Engagement Rate**, Save/Share/Follow rates.
- Split the comma-separated **Hashtags** into one row per hashtag for hashtag analysis.
""")
    show = df.copy()
    show["Post Date"] = show["Post Date"].dt.strftime("%Y-%m-%d")
    show = show.drop(columns=["Month"])
    st.dataframe(show.head(500).round(2), width="stretch", hide_index=True)
    st.caption(f"Showing first 500 of {len(df):,} filtered posts.")
    st.download_button("⬇️ Download filtered data (CSV)", show.round(3).to_csv(index=False).encode(),
                       "sugar_instagram_filtered.csv", "text/csv")
