import streamlit as st

st.set_page_config(
    page_title="⛴️ Ferry Analytics · Toronto",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Page background ── */
.stApp {
    background: linear-gradient(135deg, #0A0F1E 0%, #0D1B2A 40%, #0A1628 70%, #050D18 100%);
    background-attachment: fixed;
}

/* Starfield overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(1px 1px at 20% 30%, rgba(100,200,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 80% 10%, rgba(100,200,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 50% 60%, rgba(150,220,255,0.15) 0%, transparent 100%),
        radial-gradient(1px 1px at 10% 80%, rgba(100,200,255,0.2) 0%, transparent 100%),
        radial-gradient(1px 1px at 90% 70%, rgba(120,210,255,0.2) 0%, transparent 100%),
        radial-gradient(2px 2px at 35% 15%, rgba(100,180,255,0.25) 0%, transparent 100%),
        radial-gradient(1px 1px at 65% 85%, rgba(100,200,255,0.15) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 55%, rgba(150,220,255,0.1) 0%, transparent 100%),
        radial-gradient(2px 2px at 75% 40%, rgba(100,180,255,0.2) 0%, transparent 100%);
    pointer-events: none;
    z-index: 0;
}

/* Glowing orbs */
.stApp::after {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse 600px 400px at 20% 20%, rgba(0,120,200,0.06) 0%, transparent 70%),
        radial-gradient(ellipse 500px 350px at 80% 80%, rgba(0,80,160,0.07) 0%, transparent 70%),
        radial-gradient(ellipse 400px 300px at 60% 30%, rgba(0,180,150,0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Glass cards */
.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(100,200,255,0.15);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,120,255,0.15), inset 0 1px 0 rgba(255,255,255,0.1);
}
.metric-label {
    font-size: 10px;
    color: rgba(150,210,255,0.7);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 24px;
    font-weight: 700;
    color: #E8F4FF;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}
.metric-sub { font-size: 11px; color: rgba(150,200,255,0.5); }

.badge-up {
    background: rgba(0,220,130,0.15);
    color: #00DC82;
    border: 1px solid rgba(0,220,130,0.3);
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
}
.badge-warn {
    background: rgba(255,170,0,0.15);
    color: #FFAA00;
    border: 1px solid rgba(255,170,0,0.3);
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
}
.badge-danger {
    background: rgba(255,70,70,0.15);
    color: #FF6B6B;
    border: 1px solid rgba(255,70,70,0.3);
    padding: 3px 10px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
}

/* Section headers */
.section-header {
    font-size: 11px;
    font-weight: 600;
    color: rgba(100,200,255,0.8);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 1rem;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(100,200,255,0.2);
}

/* Alert banners */
.alert-warn {
    background: rgba(255,170,0,0.08);
    border: 1px solid rgba(255,170,0,0.3);
    border-left: 3px solid #FFAA00;
    padding: 10px 16px; border-radius: 10px;
    font-size: 13px; color: #FFD080; margin-bottom: 10px;
}
.alert-danger {
    background: rgba(255,70,70,0.08);
    border: 1px solid rgba(255,70,70,0.3);
    border-left: 3px solid #FF6B6B;
    padding: 10px 16px; border-radius: 10px;
    font-size: 13px; color: #FF9999; margin-bottom: 10px;
}
.alert-ok {
    background: rgba(0,220,130,0.07);
    border: 1px solid rgba(0,220,130,0.25);
    border-left: 3px solid #00DC82;
    padding: 10px 16px; border-radius: 10px;
    font-size: 13px; color: #80FFD0; margin-bottom: 10px;
}

/* Insight boxes */
.insight-box {
    background: linear-gradient(135deg, rgba(0,120,255,0.08) 0%, rgba(0,80,200,0.04) 100%);
    border: 1px solid rgba(100,180,255,0.15);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 8px;
}
.insight-title { font-size: 13px; font-weight: 600; color: #64C8FF; margin-bottom: 5px; }
.insight-text  { font-size: 12px; color: rgba(180,210,255,0.7); line-height: 1.5; }

/* Sidebar */
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060C18 0%, #0A1628 100%) !important;
    border-right: 1px solid rgba(100,200,255,0.1);
}
div[data-testid="stSidebar"] * { color: rgba(180,220,255,0.85) !important; }
div[data-testid="stSidebar"] .stSelectbox label,
div[data-testid="stSidebar"] .stRadio label,
div[data-testid="stSidebar"] .stSlider label {
    color: rgba(100,200,255,0.6) !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(100,200,255,0.1);
    border-radius: 12px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    color: rgba(150,200,255,0.6);
    font-weight: 500;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,120,255,0.25) !important;
    color: #64C8FF !important;
    border: 1px solid rgba(100,200,255,0.3);
}

/* Charts background */
.js-plotly-plot { background: transparent !important; }

/* DataFrames */
.stDataFrame { border-radius: 12px; overflow: hidden; }

header[data-testid="stHeader"] { background: transparent; }

/* Main content area */
.block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)

from utils.data_generator import generate_data
from utils.kpis import compute_kpis
import modules.overview as overview
import modules.heatmap as heatmap
import modules.seasonal as seasonal
import modules.trends as trends
import modules.raw_data as raw_data

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <div style="font-size:36px">⛴️</div>
      <div style="font-size:15px;font-weight:700;color:#64C8FF;margin-top:6px">Ferry Analytics</div>
      <div style="font-size:11px;color:rgba(150,200,255,0.5);margin-top:3px">Jack Layton Terminal · Toronto</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    year_options = ["All years (2015–2025)"] + [str(y) for y in range(2025, 2014, -1)]
    selected_year = st.selectbox("📅  Year", year_options)

    season_options = ["All seasons", "Summer (Jun–Aug)", "Off-season (Nov–Mar)", "Shoulder (Apr–May, Sep–Oct)"]
    selected_season = st.selectbox("🌿  Season", season_options)

    granularity = st.radio("📊  Granularity", ["15-minute", "Hourly", "Daily"])

    st.markdown("---")
    st.markdown('<div style="font-size:11px;color:rgba(100,200,255,0.6);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px">Thresholds</div>', unsafe_allow_html=True)
    congestion_thresh = st.slider("Congestion OLI", 0.5, 1.0, 0.75, 0.05)
    idle_thresh       = st.slider("Idle OLI",       0.0, 0.5, 0.20, 0.05)

    st.markdown("---")
    page = st.radio("🗺️  Navigation", [
        "📊 Overview", "🔥 Congestion Heatmap",
        "🌿 Seasonal Efficiency", "📈 10-Year Trends", "🗃️ Raw Data"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-size:10px;color:rgba(100,180,255,0.35);text-align:center;line-height:1.6">Real data · 261,537 intervals<br>May 2015 – Dec 2025<br>Toronto Parks & Recreation</div>', unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
year_filter = None if selected_year.startswith("All") else int(selected_year)
season_filter = None if selected_season.startswith("All") else selected_season.split(" ")[0]
gran_map = {"15-minute": "15min", "Hourly": "H", "Daily": "D"}
gran = gran_map[granularity]

with st.spinner("Loading ferry data..."):
    df_raw = generate_data()

kpis = compute_kpis(df_raw, year_filter=year_filter, season_filter=season_filter, congestion_thresh=congestion_thresh, idle_thresh=idle_thresh)

# ── Header ────────────────────────────────────────────────────────────────────
filter_label = f"{selected_year}  ·  {selected_season}  ·  {granularity}"
st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,80,160,0.5) 0%,rgba(0,40,100,0.3) 50%,rgba(0,120,100,0.2) 100%);
     border:1px solid rgba(100,200,255,0.2);
     border-radius:20px;padding:1.4rem 2rem;margin-bottom:1.2rem;
     backdrop-filter:blur(20px);
     box-shadow:0 8px 40px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.08)">
  <div style="display:flex;align-items:center;gap:16px">
    <div style="font-size:44px;filter:drop-shadow(0 0 12px rgba(100,200,255,0.5))">⛴️</div>
    <div>
      <div style="font-size:20px;font-weight:700;color:#E8F4FF;letter-spacing:-0.02em">
        Ferry Capacity Utilization &amp; Operational Efficiency
      </div>
      <div style="font-size:12px;color:rgba(150,210,255,0.6);margin-top:5px">
        Jack Layton Ferry Terminal &nbsp;·&nbsp; Centre Island &nbsp;·&nbsp; Hanlan's Point &nbsp;·&nbsp; Ward's Island
        &nbsp;&nbsp;|&nbsp;&nbsp; {filter_label}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Alerts ────────────────────────────────────────────────────────────────────
if kpis["congestion_pct"] > 25:
    st.markdown(f'<div class="alert-danger">🚨 <b>Congestion Alert:</b> {kpis["congestion_pct"]:.1f}% of intervals exceed OLI threshold ({congestion_thresh:.0%}). Fleet redeployment recommended for peak windows.</div>', unsafe_allow_html=True)
elif kpis["congestion_pct"] > 10:
    st.markdown(f'<div class="alert-warn">⚠️ <b>Elevated Congestion:</b> {kpis["congestion_pct"]:.1f}% of intervals above threshold. Monitor peak windows closely.</div>', unsafe_allow_html=True)

if kpis["idle_pct"] > 60:
    st.markdown(f'<div class="alert-warn">⚠️ <b>High Idle Capacity:</b> {kpis["idle_pct"]:.1f}% of intervals below idle threshold. Significant cost-saving opportunities available.</div>', unsafe_allow_html=True)

if kpis["congestion_pct"] <= 10 and kpis["idle_pct"] <= 60:
    st.markdown('<div class="alert-ok">✅ <b>Operations within thresholds</b> for the selected period. No immediate intervention required.</div>', unsafe_allow_html=True)

# ── Route ─────────────────────────────────────────────────────────────────────
if page == "📊 Overview":
    overview.render(df_raw, kpis, year_filter, season_filter, gran, congestion_thresh, idle_thresh)
elif page == "🔥 Congestion Heatmap":
    heatmap.render(df_raw, kpis, year_filter, season_filter)
elif page == "🌿 Seasonal Efficiency":
    seasonal.render(df_raw, kpis)
elif page == "📈 10-Year Trends":
    trends.render(df_raw, kpis)
elif page == "🗃️ Raw Data":
    raw_data.render(df_raw, year_filter, season_filter, gran)
