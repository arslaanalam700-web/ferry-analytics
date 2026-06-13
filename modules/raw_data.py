import streamlit as st
import pandas as pd
import numpy as np
from utils.data_generator import filter_data, resample_df

BASE_TABLE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12, color="#C8E6FF"),
    margin=dict(l=8, r=8, t=35, b=8),
)


def render(df_raw, year_filter, season_filter, gran):
    st.markdown('<div class="section-header">Raw Data Explorer</div>', unsafe_allow_html=True)

    fd = filter_data(df_raw, year_filter, season_filter)
    rd = resample_df(fd, gran)

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Total rows",        f"{len(rd):,}",                      f"After {gran} resampling"),
        (c2, "Date range",        f"{rd['timestamp'].min().date()}",    f"→ {rd['timestamp'].max().date()}"),
        (c3, "Avg sales/interval",f"{rd['sales_count'].mean():.1f}",   f"Per {gran} interval"),
        (c4, "Avg OLI",           f"{rd['oli'].mean()*100:.1f}%",       "Operational load index"),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        oli_range = st.slider("OLI range", 0.0, 1.0, (0.0, 1.0), 0.01, format="%.2f")
    with col_b:
        sort_col = st.selectbox("Sort by", ["timestamp","sales_count",
                                             "redemption_count","total_activity","rpr","oli"])
    with col_c:
        sort_asc = st.radio("Order", ["Descending","Ascending"], horizontal=True)

    filtered = rd[(rd["oli"] >= oli_range[0]) & (rd["oli"] <= oli_range[1])]
    filtered = filtered.sort_values(sort_col, ascending=(sort_asc == "Ascending"))

    display = filtered.copy()
    display["timestamp"] = display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display["oli"]       = (display["oli"] * 100).round(1).astype(str) + "%"
    display["rpr"]       = display["rpr"].round(3)
    display.columns      = [c.replace("_"," ").title() for c in display.columns]

    st.dataframe(display.reset_index(drop=True), use_container_width=True,
                 height=420, hide_index=True)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️  Download filtered data as CSV", data=csv,
                       file_name="ferry_analytics_export.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("**Descriptive statistics**")
    stats = filtered[["sales_count","redemption_count","total_activity","rpr","oli"]].describe().round(3)
    st.dataframe(stats, use_container_width=True)
