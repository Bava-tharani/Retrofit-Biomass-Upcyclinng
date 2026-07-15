import os
import time

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


st.set_page_config(page_title="Smart Biomass Compost Hub", page_icon="🌱", layout="wide")

def config_value(name: str, default: str = "") -> str:
    """Read deployment environment variables first, then Streamlit secrets."""
    if value := os.getenv(name):
        return value
    try:
        return str(st.secrets.get(name, default))
    except FileNotFoundError:
        return default


CHANNEL_ID = config_value("THINGSPEAK_CHANNEL_ID", "3420644")
READ_KEY = config_value("THINGSPEAK_READ_KEY")
WEATHER_KEY = config_value("OPENWEATHER_API_KEY")


def inject_theme() -> None:
    """Add the animated background and the shared visual language."""
    st.markdown(
        """
        <style>
        :root { --ink:#173b2a; --green:#198754; --mint:#dff5e7; }
        .stApp {
            background: #edf9f0;
            color: var(--ink);
            overflow: hidden;
        }
        .stApp::before, .stApp::after {
            content:""; position:fixed; z-index:-1; width:50vmax; height:50vmax;
            border-radius:50%; filter:blur(34px); opacity:.48; pointer-events:none;
        }
        .stApp::before {
            top:-24vmax; left:-18vmax; background:#9ce1ad;
            animation: drift-one 19s ease-in-out infinite alternate;
        }
        .stApp::after {
            right:-20vmax; bottom:-28vmax; background:#a9dcea;
            animation: drift-two 23s ease-in-out infinite alternate;
        }
        @keyframes drift-one { to { transform:translate(15vw, 19vh) scale(1.18); } }
        @keyframes drift-two { to { transform:translate(-16vw, -14vh) scale(1.14); } }
        @keyframes rise-in { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
        @keyframes leaf-float { 50% { transform:translateY(-10px) rotate(5deg); } }
        .block-container { max-width:1200px; padding-top:2.5rem; padding-bottom:3rem; }
        .hero { text-align:center; padding:1rem 1rem 2.2rem; animation:rise-in .7s ease both; }
        .hero-leaf { display:inline-block; font-size:3.5rem; line-height:1; animation:leaf-float 3.2s ease-in-out infinite; }
        .hero h1 { color:#12442a; font-size:clamp(2rem, 5vw, 3.5rem); margin:.25rem 0 .35rem; letter-spacing:-.04em; }
        .hero p { color:#3d6750; font-size:1.05rem; margin:0; }
        .eyebrow { color:#177347; font-size:.77rem; letter-spacing:.13em; font-weight:800; text-transform:uppercase; }
        .glass-card, div[data-testid="stMetric"] {
            background:rgba(255,255,255,.72); border:1px solid rgba(255,255,255,.75);
            box-shadow:0 12px 30px rgba(26,75,45,.08); backdrop-filter:blur(12px);
            border-radius:18px;
        }
        div[data-testid="stMetric"] { padding:1rem; }
        .status-card { padding:1.1rem 1.25rem; border-radius:16px; margin:1rem 0 1.5rem; border-left:6px solid; box-shadow:0 8px 22px rgba(26,75,45,.07); }
        .status-safe { background:rgba(232,245,233,.82); color:#1b5e20; border-color:#43a047; }
        .status-warning { background:rgba(255,248,225,.88); color:#795600; border-color:#f7b928; }
        .status-danger { background:rgba(255,235,238,.9); color:#9f2025; border-color:#e65358; }
        .info-card { padding:1.2rem 1.35rem; min-height:190px; }
        .stButton > button { border-radius:10px; border:0; background:#187b4b; color:white; font-weight:700; padding:.55rem 1rem; }
        .stButton > button:hover { background:#0d6338; color:white; }
        @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_intro() -> None:
    """Show a one-time, dependency-free opening screen."""
    if st.session_state.get("intro_seen", False):
        return
    intro = st.empty()
    with intro.container():
        st.markdown(
            """
            <style>
            .intro { min-height:70vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; }
            .intro-orb { width:112px; height:112px; display:grid; place-items:center; font-size:58px; border-radius:50%; background:radial-gradient(circle at 32% 28%, #fff 0 7%, #c6f1d2 30%, #4aaa70 100%); box-shadow:0 0 0 12px rgba(83,178,109,.12), 0 25px 60px rgba(20,103,58,.22); animation:intro-pop .8s cubic-bezier(.2,.9,.3,1) both, intro-breathe 2.5s 1s ease-in-out infinite; }
            .intro h1 { margin:28px 0 7px; color:#123f28; font-size:clamp(2rem, 5vw, 3.4rem); animation:intro-pop .7s .15s both; }
            .intro p { color:#49705a; animation:intro-pop .7s .3s both; }
            .intro-line { width:145px; height:4px; overflow:hidden; margin-top:25px; border-radius:9px; background:#cfe9d6; }
            .intro-line::after { content:""; display:block; width:45%; height:100%; border-radius:9px; background:#1b8a51; animation:load 1.45s ease-in-out infinite; }
            @keyframes intro-pop { from { opacity:0; transform:translateY(20px) scale(.92); } to { opacity:1; transform:none; } }
            @keyframes intro-breathe { 50% { transform:scale(1.07); } }
            @keyframes load { from { transform:translateX(-120%); } to { transform:translateX(330%); } }
            </style>
            <section class="intro"><div class="intro-orb">🌱</div><h1>Smart Biomass Compost Hub</h1><p>Preparing your live environmental dashboard</p><div class="intro-line"></div></section>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(1.6)
    intro.empty()
    st.session_state.intro_seen = True
    st.rerun()


@st.cache_data(ttl=15, show_spinner=False)
def fetch_telemetry() -> tuple[pd.DataFrame, bool]:
    if not READ_KEY:
        return pd.DataFrame(), False
    try:
        url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
        response = requests.get(url, params={"api_key": READ_KEY, "results": 50}, timeout=6)
        response.raise_for_status()
        df = pd.DataFrame(response.json()["feeds"])
        for field in ("field1", "field2", "field3", "field4"):
            df[field] = pd.to_numeric(df[field], errors="coerce")
        df["created_at"] = pd.to_datetime(df["created_at"])
        return df, not df.empty
    except (requests.RequestException, KeyError, ValueError):
        return pd.DataFrame(), False


def current_status(temp: float, moisture: float, gas: int) -> tuple[str, str, str]:
    if gas > 200 or moisture > 60:
        return "status-danger", "CRITICAL LIMIT BREACH", f"Gas ({gas} ppm) or moisture ({moisture:.1f}%) needs immediate attention."
    if gas > 120 or moisture > 45 or temp > 45:
        return "status-warning", "ELEVATED PROCESS WARNING", "The compost profile is warming or accumulating moisture. Monitor aeration."
    return "status-safe", "NOMINAL BIOLOGICAL STABILIZATION", "Environmental parameters are balanced for aerobic decomposition."


inject_theme()
show_intro()

st.markdown("<section class='hero'><div class='hero-leaf'>🌱</div><div class='eyebrow'>Live environmental telemetry</div><h1>Smart Biomass Compost Hub</h1><p>Monitor, protect, and improve every compost cycle.</p></section>", unsafe_allow_html=True)

df, success = fetch_telemetry()
temp = humidity = moisture = 0.0
gas = 0
st.subheader("📊 Live Container Environment")
if success:
    latest = df.iloc[-1]
    temp = float(latest.field1) if pd.notna(latest.field1) else 0.0
    humidity = float(latest.field2) if pd.notna(latest.field2) else 0.0
    moisture = float(latest.field3) if pd.notna(latest.field3) else 0.0
    gas = int(latest.field4) if pd.notna(latest.field4) else 0
    for col, label, value in zip(st.columns(4), ("Bin temperature", "Air humidity", "Core moisture", "Volatile gas"), (f"{temp:.1f} °C", f"{humidity:.1f}%", f"{moisture:.1f}%", f"{gas} ppm")):
        with col:
            st.metric(label, value)
else:
    st.info("Add your ThingSpeak read key in `.streamlit/secrets.toml` or an environment variable to show live data.")

kind, title, detail = current_status(temp, moisture, gas)
st.markdown(f"<div class='status-card {kind}'><strong>{title}</strong><br>{detail}</div>", unsafe_allow_html=True)

st.subheader("📈 Environmental Trend Analysis")
if success:
    tab_all, tab_temp, tab_humidity, tab_moisture, tab_gas = st.tabs(["All trends", "Temperature", "Humidity", "Moisture", "Gas"])
    charts = ((tab_all, ["field1", "field2", "field3", "field4"], "All sensor streams"), (tab_temp, "field1", "Bin temperature"), (tab_humidity, "field2", "Air humidity"), (tab_moisture, "field3", "Core moisture"), (tab_gas, "field4", "Volatile gas"))
    for tab, y, title in charts:
        with tab:
            fig = px.line(df, x="created_at", y=y, title=title, color_discrete_sequence=["#198754", "#2487bf", "#ed9e25", "#874bb5"])
            fig.update_layout(hovermode="x unified", plot_bgcolor="rgba(255,255,255,.76)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=20, r=20, t=45, b=20))
            st.plotly_chart(fig, use_container_width=True)

st.subheader("🎛️ Equipment Override")
left, right = st.columns([1, 2])
with left:
    fan_on = st.toggle("Force exhaust fan relay")
with right:
    st.warning("Manual override active — fan forced ON.") if fan_on else st.success("Automated sensor control is active.")
if st.button("Sync command with container node"):
    st.toast(f"Command prepared: relay {'HIGH (ON)' if fan_on else 'LOW (AUTO)'}.")

st.subheader("🧮 Sustainability Impact Calculator")
waste = st.slider("Monthly organic waste input (kg)", 5, 500, 50, 5)
for col, label, value in zip(st.columns(3), ("Methane prevented", "Carbon footprint reduced", "Organic fertilizer yield"), (f"{waste * .15:.2f} kg/month", f"{waste * .15 * 28:.2f} kg CO₂e/month", f"{waste * .40:.2f} kg/month")):
    with col:
        st.metric(label, value)

left, right = st.columns(2)
with left:
    st.markdown("<div class='glass-card info-card'><h3>🌍 SDG alignment</h3><p>Supports Climate Action, Sustainable Cities, Responsible Consumption, Life on Land, and Clean Energy through local circular waste management.</p></div>", unsafe_allow_html=True)
with right:
    st.markdown("<div class='glass-card info-card'><h3>🔥 Climate impact</h3><p>Aerobic composting helps avoid methane-producing waste, reduces open burning, and returns stable carbon to local soils.</p></div>", unsafe_allow_html=True)
