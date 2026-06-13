import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_generator import filter_data

DAYS  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
TEAL  = "#1D9E75"
BLUE  = "#185FA5"
RED   = "#D85A30"
AMBER = "#EF9F27"

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12, color="#1A2940"),
    margin=dict(l=8, r=8, t=30, b=8),
)


def render(df_raw, kpis, year_filter, season_filter):
    fd = filter_data(df_raw, year_filter, season_filter)
    st.markdown('<div class="section-header">Congestion & Idle Period Heatmaps</div>',
                unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🗓️ Weekly Heatmap","📆 Monthly Heatmap","⏱️ Hour-by-Hour"])
    with tab1:
        _weekly_heatmap(fd)
    with tab2:
        _monthly_heatmap(fd)
    with tab3:
        _hourly_comparison(fd)


def _weekly_heatmap(fd):
    pivot = (fd.groupby(["day_of_week","hour"])["oli"]
               .mean().reset_index()
               .pivot(index="day_of_week",columns="hour",values="oli"))
    pivot.index = [DAYS[i] for i in pivot.index]
    cscale = [[0.00,"#E1F5EE"],[0.20,"#9FE1CB"],[0.40,"#1D9E75"],
              [0.60,"#EF9F27"],[0.80,"#D85A30"],[1.00,"#7F1D1D"]]
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=cscale, zmin=0, zmax=1,
        hovertemplate="<b>%{y}</b> at %{x}<br>OLI: %{z:.1%}<extra></extra>",
        colorbar=dict(title="OLI",tickformat=".0%",len=0.8)
    ))
    fig.update_layout(**BASE, height=320,
                      xaxis=dict(title="Hour of Day",tickangle=45),
                      yaxis=dict(title=""))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Peak congestion windows (avg OLI > 60%)**")
    high = (fd.groupby(["day_of_week","hour"])["oli"]
              .mean().reset_index()
              .rename(columns={"day_of_week":"Day","hour":"Hour","oli":"Avg OLI"}))
    high["Day"] = high["Day"].apply(lambda x: DAYS[x])
    high = high[high["Avg OLI"]>0.60].sort_values("Avg OLI",ascending=False).head(10)
    high["Avg OLI"] = high["Avg OLI"].apply(lambda v: f"{v:.1%}")
    st.dataframe(high.reset_index(drop=True), use_container_width=True, hide_index=True)


def _monthly_heatmap(fd):
    mnames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot = (fd.groupby(["month","hour"])["oli"]
               .mean().reset_index()
               .pivot(index="month",columns="hour",values="oli"))
    pivot.index = [mnames[i-1] for i in pivot.index]
    cscale = [[0.00,"#E1F5EE"],[0.25,"#9FE1CB"],[0.50,"#1D9E75"],
              [0.70,"#EF9F27"],[0.85,"#D85A30"],[1.00,"#7F1D1D"]]
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=cscale, zmin=0, zmax=1,
        hovertemplate="<b>%{y}</b> at %{x}<br>OLI: %{z:.1%}<extra></extra>",
        colorbar=dict(title="OLI",tickformat=".0%",len=0.8)
    ))
    fig.update_layout(**BASE, height=420,
                      xaxis=dict(title="Hour of Day",tickangle=45),
                      yaxis=dict(title=""))
    st.plotly_chart(fig, use_container_width=True)


def _hourly_comparison(fd):
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Weekday vs Weekend OLI by hour**")
        wd = fd[~fd["is_weekend"]].groupby("hour")["oli"].mean()
        we = fd[ fd["is_weekend"]].groupby("hour")["oli"].mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=wd.index,y=wd.values,name="Weekday",
            line=dict(color=BLUE,width=2.5),fill="tozeroy",
            fillcolor="rgba(24,95,165,0.07)"))
        fig.add_trace(go.Scatter(x=we.index,y=we.values,name="Weekend",
            line=dict(color=RED,width=2.5,dash="dot"),fill="tozeroy",
            fillcolor="rgba(216,90,48,0.07)"))
        fig.update_layout(**BASE, height=280,
                          xaxis=dict(title="Hour",tickmode="linear",dtick=2,showgrid=False),
                          yaxis=dict(title="Avg OLI",tickformat=".0%",
                                     showgrid=True,gridcolor="#EEF1F5"),
                          legend=dict(orientation="h",y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("**OLI distribution by day of week**")
        fd2 = fd.copy()
        fd2["Day"] = fd2["day_of_week"].apply(lambda x: DAYS[x])
        fig2 = px.box(fd2,x="Day",y="oli",category_orders={"Day":DAYS},
                      color="Day",
                      color_discrete_sequence=[TEAL,TEAL,TEAL,TEAL,TEAL,RED,RED])
        fig2.update_layout(**BASE, height=280, showlegend=False,
                           xaxis=dict(title="",showgrid=False),
                           yaxis=dict(title="OLI",tickformat=".0%",
                                      showgrid=True,gridcolor="#EEF1F5"))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Operational efficiency bands**")
    bins = pd.cut(fd["oli"],bins=[0,0.2,0.45,0.75,1.0],
                  labels=["Idle (<20%)","Normal (20–45%)","High (45–75%)","Congested (>75%)"])
    band_counts = bins.value_counts().sort_index()
    band_pct    = (band_counts/len(fd)*100).round(1)
    colors_b = ["#9FE1CB","#1D9E75","#EF9F27","#D85A30"]
    icons_b  = ["😴","✅","⚡","🚨"]
    cols = st.columns(4)
    for i,(col,label) in enumerate(zip(cols,band_counts.index)):
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid {colors_b[i]}">
              <div class="metric-label">{icons_b[i]} {label}</div>
              <div class="metric-value">{band_pct.iloc[i]:.1f}%</div>
              <div class="metric-sub">{band_counts.iloc[i]:,} intervals</div>
            </div>""", unsafe_allow_html=True)
