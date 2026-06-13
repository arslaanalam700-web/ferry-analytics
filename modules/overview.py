import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from utils.data_generator import filter_data, resample_df

TEAL  = "#1D9E75"
BLUE  = "#185FA5"
AMBER = "#EF9F27"
RED   = "#D85A30"

BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", size=12, color="#1A2940"),
    margin=dict(l=8, r=8, t=30, b=8),
)


def _badge(val, good_fn, warn_fn, good_txt, warn_txt, bad_txt):
    if good_fn(val):   return f'<span class="badge-up">{good_txt}</span>'
    elif warn_fn(val): return f'<span class="badge-warn">{warn_txt}</span>'
    return f'<span class="badge-danger">{bad_txt}</span>'


def render(df_raw, kpis, year_filter, season_filter, gran, cong_thresh, idle_thresh):
    st.markdown('<div class="section-header">Key Performance Indicators</div>',
                unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    cards = [
        (c1,"Capacity utilization ratio",f"{kpis['avg_oli']*100:.1f}%","Avg. OLI across period",
         _badge(kpis['avg_oli'],lambda v:0.45<=v<=0.75,lambda v:v<0.45,"✓ Optimal","↓ Under-utilized","⚠ Over-capacity")),
        (c2,"Congestion pressure index",f"{kpis['congestion_pct']:.1f}%",f"Intervals >{cong_thresh:.0%} OLI",
         _badge(kpis['congestion_pct'],lambda v:v<15,lambda v:v<25,"✓ Low","⚠ Moderate","🚨 High")),
        (c3,"Idle capacity",f"{kpis['idle_pct']:.1f}%",f"Intervals <{idle_thresh:.0%} OLI",
         _badge(kpis['idle_pct'],lambda v:v<25,lambda v:v<40,"✓ Low","⚠ Elevated","⚠ High idle")),
        (c4,"Peak OLI",f"{kpis['peak_oli']*100:.1f}%","Max recorded load",
         _badge(kpis['peak_oli'],lambda v:v<0.80,lambda v:v<0.92,"✓ Safe","⚠ Near capacity","🚨 Over capacity")),
        (c5,"Variability score",f"{kpis['variability']:.3f}","Std. dev. of OLI",
         _badge(kpis['variability'],lambda v:v<0.25,lambda v:v<0.35,"✓ Stable","⚠ Moderate","⚠ Volatile")),
        (c6,"Ticket activity",f"{kpis['total_activity']:,}","Sales + redemptions",
         '<span class="badge-up">↑ Period total</span>'),
    ]
    for col,label,val,sub,badge in cards:
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{val}</div>
              <div class="metric-sub">{sub}</div>
              <div style="margin-top:8px">{badge}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    fd = filter_data(df_raw, year_filter, season_filter)
    rd = resample_df(fd, gran)
    if len(rd) > 2000:
        rd = rd.iloc[::max(1,len(rd)//2000)].reset_index(drop=True)

    tab1, tab2, tab3 = st.tabs(["📊 Activity & OLI","📉 Redemption Pressure","🔍 Interval Distribution"])

    with tab1:
        col_l, col_r = st.columns([3,2])
        with col_l:
            st.markdown("**Sales vs Redemptions over time**")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=rd["timestamp"],y=rd["sales_count"],
                                 name="Sales",marker_color=TEAL,opacity=0.85))
            fig.add_trace(go.Bar(x=rd["timestamp"],y=rd["redemption_count"],
                                 name="Redemptions",marker_color=BLUE,opacity=0.85))
            fig.update_layout(**BASE, barmode="stack", height=300,
                              xaxis=dict(showgrid=False),
                              yaxis=dict(showgrid=True,gridcolor="#EEF1F5"),
                              legend=dict(orientation="h",y=1.08,x=0))
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            st.markdown("**Operational Load Index (OLI)**")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=rd["timestamp"],y=rd["oli"],fill="tozeroy",
                fillcolor="rgba(29,158,117,0.15)",line=dict(color=TEAL,width=2),name="OLI"))
            fig2.add_hline(y=cong_thresh,line_dash="dot",line_color=RED,
                annotation_text=f"Congestion ({cong_thresh:.0%})",annotation_font_color=RED)
            fig2.add_hline(y=idle_thresh,line_dash="dot",line_color=AMBER,
                annotation_text=f"Idle ({idle_thresh:.0%})",annotation_font_color=AMBER)
            fig2.update_layout(**BASE, height=300,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True,gridcolor="#EEF1F5",
                                          tickformat=".0%",range=[0,1]))
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.markdown("**Redemption Pressure Ratio (RPR = redemptions / (sales + 1))**")
        colors = rd["rpr"].apply(lambda v: RED if v>0.85 else (AMBER if v>0.55 else TEAL))
        fig3 = go.Figure(go.Bar(x=rd["timestamp"],y=rd["rpr"],
                                marker_color=colors,name="RPR"))
        fig3.add_hline(y=0.85,line_dash="dot",line_color=RED,
                       annotation_text="High pressure (0.85)")
        fig3.add_hline(y=0.55,line_dash="dot",line_color=AMBER,
                       annotation_text="Moderate (0.55)")
        fig3.update_layout(**BASE, height=300,
                           xaxis=dict(showgrid=False),
                           yaxis=dict(showgrid=True,gridcolor="#EEF1F5",range=[0,1.2]))
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**OLI distribution**")
            fig4 = px.histogram(fd,x="oli",nbins=50,color_discrete_sequence=[TEAL],
                                labels={"oli":"OLI","count":"Intervals"})
            fig4.add_vline(x=cong_thresh,line_dash="dot",line_color=RED)
            fig4.add_vline(x=idle_thresh,line_dash="dot",line_color=AMBER)
            fig4.update_layout(**BASE, height=280,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True,gridcolor="#EEF1F5"))
            st.plotly_chart(fig4, use_container_width=True)
        with col_b:
            st.markdown("**Sales vs Redemptions scatter (sampled)**")
            sample = fd.sample(min(3000,len(fd)),random_state=1)
            fig5 = px.scatter(sample,x="sales_count",y="redemption_count",
                              color="oli",color_continuous_scale="Tealgrn",opacity=0.5,
                              labels={"sales_count":"Sales","redemption_count":"Redemptions","oli":"OLI"})
            fig5.update_layout(**BASE, height=280,
                               xaxis=dict(showgrid=False),
                               yaxis=dict(showgrid=True,gridcolor="#EEF1F5"))
            st.plotly_chart(fig5, use_container_width=True)

    st.markdown('<div class="section-header">Operational Insights</div>',
                unsafe_allow_html=True)
    peak_hr  = int(fd.groupby("hour")["oli"].mean().idxmax())
    idle_hr  = int(fd.groupby("hour")["oli"].mean().idxmin())
    best_dow = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][
        int(fd.groupby("day_of_week")["oli"].mean().idxmin())]
    i1,i2,i3 = st.columns(3)
    with i1:
        st.markdown(f"""<div class="insight-box">
          <div class="insight-title">🏖️ Peak demand hour: {peak_hr:02d}:00</div>
          <div class="insight-text">OLI peaks at {peak_hr}:00.
          Additional ferry runs would reduce wait times and prevent over-capacity incidents.</div>
        </div>""", unsafe_allow_html=True)
    with i2:
        st.markdown(f"""<div class="insight-box">
          <div class="insight-title">😴 Lowest utilization: {idle_hr:02d}:00</div>
          <div class="insight-text">Operations at {idle_hr}:00 show the lowest average load.
          Vessel stand-down here can recover fuel and crew costs.</div>
        </div>""", unsafe_allow_html=True)
    with i3:
        st.markdown(f"""<div class="insight-box">
          <div class="insight-title">📅 Most efficient day: {best_dow}</div>
          <div class="insight-text">{best_dow} shows the most balanced OLI.
          Use this day's schedule as a benchmark for efficient operations.</div>
        </div>""", unsafe_allow_html=True)
