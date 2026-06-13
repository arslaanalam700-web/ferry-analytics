import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_generator import filter_data

TEAL  = "#1D9E75"
BLUE  = "#185FA5"
AMBER = "#EF9F27"
RED   = "#D85A30"
GRAY  = "#888780"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12, color="#1A2940"),
    margin=dict(l=8, r=8, t=35, b=8),
)


def render(df_raw, kpis):
    st.markdown('<div class="section-header">Seasonal Efficiency Comparison</div>',
                unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📅 Monthly OLI", "🌡️ Season Bands", "⚖️ Year Comparison"])
    with tab1:
        _monthly_oli(df_raw)
    with tab2:
        _season_bands(df_raw)
    with tab3:
        _year_comparison(df_raw)


def _monthly_oli(df):
    st.markdown("**Average OLI by month — three era comparison**")
    eras = {"2024–25": (2024,2025), "2020–23": (2020,2023), "2015–19": (2015,2019)}
    era_colors = [TEAL, BLUE, GRAY]
    era_dashes  = ["solid", "dot", "dash"]
    fig = go.Figure()
    for (label,(y0,y1)), color, dash in zip(eras.items(), era_colors, era_dashes):
        sub = df[(df["year"]>=y0)&(df["year"]<=y1)]
        monthly = sub.groupby("month")["oli"].mean()*100
        monthly = monthly.reindex(range(1,13))
        fig.add_trace(go.Scatter(
            x=MONTHS, y=monthly.values, name=label,
            line=dict(color=color, width=2.5, dash=dash),
            mode="lines+markers", marker=dict(size=5),
            fill="tozeroy" if label=="2024–25" else None,
            fillcolor="rgba(29,158,117,0.08)" if label=="2024–25" else None,
        ))
    fig.add_vrect(x0="Jun", x1="Aug", fillcolor="rgba(239,159,39,0.08)",
                  layer="below", line_width=0, annotation_text="Summer",
                  annotation_position="top left")
    fig.add_vrect(x0="Jan", x1="Mar", fillcolor="rgba(136,135,128,0.07)",
                  layer="below", line_width=0, annotation_text="Off-season",
                  annotation_position="top left")
    fig.update_layout(**BASE, height=320, title="",
                      xaxis=dict(showgrid=False),
                      yaxis=dict(title="OLI %", range=[0,105],
                                 showgrid=True, gridcolor="#EEF1F5"),
                      legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig, use_container_width=True)

    seasons = {
        "Summer (Jun–Aug)":         [6,7,8],
        "Shoulder (Apr–May, Sep–Oct)": [4,5,9,10],
        "Off-season (Nov–Mar)":     [11,12,1,2,3],
    }
    cols = st.columns(3)
    palette = [RED, TEAL, GRAY]
    icons   = ["☀️","🍂","❄️"]
    for col,(sname,months),color,icon in zip(cols,seasons.items(),palette,icons):
        sub = df[df["month"].isin(months)]
        avg_oli = sub["oli"].mean()*100
        idle    = (sub["oli"]<0.20).mean()*100
        cong    = (sub["oli"]>0.75).mean()*100
        with col:
            st.markdown(f"""
            <div class="metric-card" style="border-left:4px solid {color}">
              <div class="metric-label">{icon} {sname}</div>
              <div class="metric-value">{avg_oli:.1f}%</div>
              <div class="metric-sub">Avg OLI · Idle {idle:.1f}% · Congested {cong:.1f}%</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def _season_bands(df):
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**OLI by season (violin)**")
        fig = px.violin(df, x="season", y="oli",
                        category_orders={"season":["Summer","Shoulder","Off-season"]},
                        color="season",
                        color_discrete_map={"Summer":RED,"Shoulder":AMBER,"Off-season":BLUE},
                        box=True, points=False)
        fig.update_layout(**BASE, showlegend=False,
                          xaxis=dict(title="", showgrid=False),
                          yaxis=dict(title="OLI", tickformat=".0%",
                                     showgrid=True, gridcolor="#EEF1F5"))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("**Hour-of-day OLI split by season**")
        fig2 = go.Figure()
        for season, color in [("Summer",RED),("Shoulder",AMBER),("Off-season",BLUE)]:
            sub = df[df["season"]==season].groupby("hour")["oli"].mean()*100
            fig2.add_trace(go.Scatter(x=sub.index, y=sub.values,
                                      name=season, line=dict(color=color,width=2)))
        fig2.update_layout(**BASE,
                           xaxis=dict(title="Hour", showgrid=False),
                           yaxis=dict(title="Avg OLI %",
                                      showgrid=True, gridcolor="#EEF1F5"),
                           legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("**Weekend vs weekday OLI by season**")
    pivot = (df.groupby(["season","is_weekend"])["oli"]
               .mean().reset_index()
               .pivot(index="season", columns="is_weekend", values="oli")*100)
    pivot.columns = ["Weekday","Weekend"]
    pivot = pivot.reindex(["Summer","Shoulder","Off-season"])
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name="Weekday",x=pivot.index,y=pivot["Weekday"],
                          marker_color=BLUE,width=0.35))
    fig3.add_trace(go.Bar(name="Weekend",x=pivot.index,y=pivot["Weekend"],
                          marker_color=RED,width=0.35))
    fig3.update_layout(**BASE, barmode="group", height=280,
                       xaxis=dict(showgrid=False),
                       yaxis=dict(title="Avg OLI %",
                                  showgrid=True, gridcolor="#EEF1F5"),
                       legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig3, use_container_width=True)


def _year_comparison(df):
    st.markdown("**Year-over-year average OLI by month**")
    years = sorted(df["year"].unique())
    pivot = (df.groupby(["year","month"])["oli"].mean()*100).unstack(level=0)
    pivot.index = MONTHS
    colorscale = px.colors.sequential.Teal
    n = len(years)
    fig = go.Figure()
    for i, year in enumerate(years):
        if year not in pivot.columns:
            continue
        cidx = int(i/max(n-1,1)*(len(colorscale)-1))
        lw   = 3 if year in (2020,2025) else 1.5
        dash = "dot" if year==2020 else "solid"
        fig.add_trace(go.Scatter(x=MONTHS, y=pivot[year].values, name=str(year),
                                 mode="lines",
                                 line=dict(color=colorscale[cidx],width=lw,dash=dash)))
    fig.update_layout(**BASE, height=350,
                      xaxis=dict(showgrid=False),
                      yaxis=dict(title="Avg OLI %",
                                 showgrid=True, gridcolor="#EEF1F5"),
                      legend=dict(orientation="h", y=-0.2, x=0, traceorder="normal"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div class="insight-box">
      <div class="insight-title">📌 2020 anomaly: COVID-19 impact</div>
      <div class="insight-text">2020 shows a near-zero OLI period Apr–Sep due to pandemic closures.
      Full recovery was achieved by 2023, with 2025 recording the highest utilization on record.</div>
    </div>""", unsafe_allow_html=True)
