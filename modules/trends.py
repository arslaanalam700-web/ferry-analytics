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

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12, color="#1A2940"),
    margin=dict(l=8, r=8, t=35, b=8),
)


def render(df_raw, kpis):
    st.markdown('<div class="section-header">10-Year Trend Analysis (2015–2025)</div>',
                unsafe_allow_html=True)
    annual = (df_raw.groupby("year").agg(
        avg_oli=("oli","mean"),
        peak_oli=("oli","max"),
        idle_pct=("oli", lambda x:(x<0.20).mean()*100),
        cong_pct=("oli", lambda x:(x>0.75).mean()*100),
        total_sales=("sales_count","sum"),
        total_redemptions=("redemption_count","sum"),
        variability=("oli","std"),
    ).reset_index())
    annual["total_tickets"] = annual["total_sales"] + annual["total_redemptions"]

    tab1, tab2, tab3 = st.tabs(["📈 OLI Trends","🎟️ Ticket Volume","📊 KPI Evolution"])
    with tab1:
        _oli_trends(annual)
    with tab2:
        _ticket_volume(annual)
    with tab3:
        _kpi_evolution(annual, df_raw)


def _oli_trends(annual):
    col_l, col_r = st.columns([3,2])
    with col_l:
        st.markdown("**Annual OLI: average, idle %, and congestion % (2015–2025)**")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annual["year"],y=(annual["avg_oli"]*100).round(1),
            name="Avg OLI %",line=dict(color=TEAL,width=3),mode="lines+markers",
            marker=dict(size=7,color=TEAL),fill="tozeroy",fillcolor="rgba(29,158,117,0.08)"))
        fig.add_trace(go.Scatter(x=annual["year"],y=annual["idle_pct"].round(1),
            name="Idle %",line=dict(color=GRAY,width=2,dash="dot"),
            mode="lines+markers",marker=dict(size=5,color=GRAY)))
        fig.add_trace(go.Scatter(x=annual["year"],y=annual["cong_pct"].round(1),
            name="Congested %",line=dict(color=RED,width=2.5),
            mode="lines+markers",marker=dict(size=6,color=RED)))
        fig.add_vline(x=2020,line_dash="dot",line_color=AMBER,
                      annotation_text="COVID-19",annotation_font_color=AMBER)
        fig.update_layout(**BASE, height=340,
                          xaxis=dict(title="Year",dtick=1,showgrid=False),
                          yaxis=dict(title="%",range=[0,80],
                                     showgrid=True,gridcolor="#EEF1F5"),
                          legend=dict(orientation="h",y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("**Annual variability score**")
        bar_c = [RED if y==2020 else AMBER if y==2021 else TEAL for y in annual["year"]]
        fig2 = go.Figure(go.Bar(x=annual["year"],y=(annual["variability"]*100).round(2),
                                marker_color=bar_c))
        fig2.update_layout(**BASE, height=200,
                           xaxis=dict(dtick=1,tickangle=45,showgrid=False),
                           yaxis=dict(title="Std dev of OLI (×100)",
                                      showgrid=True,gridcolor="#EEF1F5"))
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("**Annual summary table**")
        tbl = annual[["year","avg_oli","idle_pct","cong_pct","variability"]].copy()
        tbl["avg_oli"]     = (tbl["avg_oli"]*100).round(1).astype(str)+"%"
        tbl["idle_pct"]    = tbl["idle_pct"].round(1).astype(str)+"%"
        tbl["cong_pct"]    = tbl["cong_pct"].round(1).astype(str)+"%"
        tbl["variability"] = tbl["variability"].round(4)
        tbl.columns = ["Year","Avg OLI","Idle","Congested","Variability"]
        st.dataframe(tbl.set_index("Year"), use_container_width=True)


def _ticket_volume(annual):
    st.markdown("**Annual ticket volume (millions)**")
    bar_c = ["#F09595" if y==2020 else "#FAC775" if y==2021 else TEAL for y in annual["year"]]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=annual["year"],y=(annual["total_tickets"]/1e6).round(2),
        marker_color=bar_c,name="Total tickets",
        text=(annual["total_tickets"]/1e6).round(2).astype(str)+"M",
        textposition="outside"))
    fig.add_trace(go.Scatter(x=annual["year"],y=(annual["total_sales"]/1e6).round(2),
        name="Sales only",line=dict(color=BLUE,width=2,dash="dot"),
        mode="lines+markers",marker=dict(size=5)))
    fig.add_vline(x=2020,line_dash="dot",line_color=AMBER,
                  annotation_text="COVID-19 (−73% YoY)",annotation_font_color=AMBER)
    fig.update_layout(**BASE, height=360,
                      xaxis=dict(title="Year",dtick=1,showgrid=False),
                      yaxis=dict(title="Millions of tickets",
                                 showgrid=True,gridcolor="#EEF1F5"),
                      legend=dict(orientation="h",y=1.08))
    st.plotly_chart(fig, use_container_width=True)

    annual2 = annual.copy()
    annual2["yoy"] = annual2["total_tickets"].pct_change()*100
    st.markdown("**Year-over-year ticket growth**")
    fig2 = go.Figure(go.Bar(
        x=annual2["year"][1:], y=annual2["yoy"][1:].round(1),
        marker_color=[RED if v<0 else TEAL for v in annual2["yoy"][1:]],
        text=annual2["yoy"][1:].round(1).astype(str)+"%",textposition="outside"))
    fig2.update_layout(**BASE, height=260,
                       xaxis=dict(title="Year",dtick=1,showgrid=False),
                       yaxis=dict(title="YoY Growth %",showgrid=True,gridcolor="#EEF1F5"))
    st.plotly_chart(fig2, use_container_width=True)


def _kpi_evolution(annual, df_raw):
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Peak OLI recorded per year**")
        fig = go.Figure(go.Scatter(
            x=annual["year"],y=(annual["peak_oli"]*100).round(1),
            line=dict(color=RED,width=2.5),mode="lines+markers",
            marker=dict(size=7,color=RED),
            fill="tozeroy",fillcolor="rgba(216,90,48,0.07)"))
        fig.add_hline(y=100,line_dash="dot",line_color="#7F1D1D",
                      annotation_text="Max capacity")
        fig.update_layout(**BASE, height=260,
                          xaxis=dict(dtick=1,showgrid=False),
                          yaxis=dict(title="Peak OLI %",range=[0,110],
                                     showgrid=True,gridcolor="#EEF1F5"))
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.markdown("**Seasonal mix over years**")
        pivot = (df_raw.groupby(["year","season"])["oli"]
                   .mean().reset_index()
                   .pivot(index="year",columns="season",values="oli")*100)
        fig2 = go.Figure()
        cmap = {"Summer":RED,"Shoulder":AMBER,"Off-season":BLUE}
        for col in ["Summer","Shoulder","Off-season"]:
            if col in pivot.columns:
                fig2.add_trace(go.Scatter(x=pivot.index,y=pivot[col].round(1),
                    name=col,line=dict(color=cmap[col],width=2),
                    mode="lines+markers",marker=dict(size=5)))
        fig2.update_layout(**BASE, height=260,
                           xaxis=dict(title="Year",dtick=1,showgrid=False),
                           yaxis=dict(title="Avg OLI %",showgrid=True,gridcolor="#EEF1F5"),
                           legend=dict(orientation="h",y=1.12))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Strategic Insights</div>',
                unsafe_allow_html=True)
    cols4 = st.columns(4)
    insights = [
        ("📈","10-yr OLI growth",   "+43%",         "From 44% (2015) to 63% (2025)"),
        ("🚨","Congestion growth",  "+3× since 2015","8% → 24% of intervals"),
        ("😴","Idle rate decline",  "−17 pts",       "From 38% to 21% idle intervals"),
        ("🎟️","Post-COVID rebound","1.31M tickets", "2025 highest on record"),
    ]
    for col,(icon,label,val,sub) in zip(cols4,insights):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{icon} {label}</div>
              <div class="metric-value" style="font-size:20px">{val}</div>
              <div class="metric-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)
