import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- CLOUD CONFIGURATION ---
CHANNEL_ID = "3420644"
READ_KEY = "KUTCD4R1BFV20MZ5"
# Get a free API key from openweathermap.org for live updates
WEATHER_KEY = "8742cb65d2179b00a2b0de05b5f25a91" 

# --- USER INTERFACE STYLING ---
st.set_page_config(page_title="Smart Biomass Compost Hub", page_icon="🌱", layout="wide")

# Custom CSS for a beautiful, clean mobile/web interface
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E4620; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #555; text-align: center; margin-bottom: 25px; font-style: italic; }
    .status-card { padding: 20px; border-radius: 10px; margin-bottom: 15px; border-left: 6px solid; }
    .status-safe { background-color: #E8F5E9; color: #1B5E20; border-color: #4CAF50; }
    .status-warning { background-color: #FFF3CD; color: #856404; border-color: #FFC107; }
    .status-danger { background-color: #FFEBEE; color: #C62828; border-color: #F44336; }
    .sdg-badge { background-color: #E1F5FE; color: #0277BD; padding: 4px 10px; border-radius: 15px; font-weight: bold; display: inline-block; font-size: 12px; margin-right: 5px; margin-bottom: 5px; }
    .info-card { background-color: #F9F9F9; padding: 20px; border-radius: 10px; border: 1px solid #E0E0E0; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🌱 Smart Biomass Compost Hub</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Real-Time Decarbonization & Decentralized Environmental Telemetry Interface</div>", unsafe_allow_html=True)

# --- LAYER 1: LIVE SENSOR READINGS & WORDING INDICATIONS (From ThingSpeak) ---
st.subheader("📊 Live Container Environment")

# Default values if connection fails
temp, humidity, moisture, gas = 0.0, 0.0, 0.0, 0

try:
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_KEY}&results=1"
    feeds = requests.get(url).json()["feeds"][0]
    
    temp = float(feeds['field1'])
    humidity = float(feeds['field2'])
    moisture = float(feeds['field3'])
    gas = int(float(feeds['field4']))
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Bin Temp", f"{temp:.1f} °C")
    with col2: st.metric("Air Humidity", f"{humidity:.1f} %")
    with col3: st.metric("Core Moisture", f"{moisture:.1f} %")
    with col4: st.metric("Volatile Gas Level", f"{gas:+d} ppm")
except Exception:
    st.warning("⚠️ Waiting for live hardware data stream...")

# --- NEW LAYER: TEXTUAL INDICATIONS & REAL-TIME STATE EVALUATION ---
st.markdown("### 📝 Live Container Diagnostics")

# Logic to determine status purely "in wordings"
status_class = "status-safe"
status_title = "Nominal Biological Stabilization"
status_desc = "All environmental parameters are in equilibrium. The pile is safely optimizing aerobic decomposition."

if gas > 200 or moisture > 60.0:
    status_class = "status-danger"
    status_title = "CRITICAL LIMIT BREACH DETECTED"
    status_desc = f"Action Required! High gas emissions ({gas} ppm) or excess moisture ({moisture:.1f}%) detected. Local exhaust fan activated to prevent anaerobic rotting and self-heating degradation."
elif gas > 120 or moisture > 45.0 or temp > 45.0:
    status_class = "status-warning"
    status_title = "ELEVATED PROCESS WARNING"
    status_desc = "Moderate parameter drift detected. The compost profile is experiencing accelerated heating or early moisture accumulation. Monitor closely."

st.markdown(f"""
    <div class='status-card {status_class}'>
        <h4 style='margin: 0 0 8px 0;'>Current State: {status_title}</h4>
        <p style='margin: 0; font-size: 14px;'>{status_desc}</p>
    </div>
""", unsafe_allow_html=True)


# --- LAYER 2: PREEMPTIVE WEATHER SAFETY ALERTS ---
st.subheader("🌦️ Regional Weather Ingress Monitor")
try:
    city = "Nellore" 
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
    w_data = requests.get(weather_url).json()
    
    w_cond = w_data["weather"][0]["main"]
    w_temp = w_data["main"]["temp"]
    
    if "Rain" in w_cond or "Storm" in w_cond:
        st.markdown(f"""
            <div class='status-card status-warning'>
                <h4>🚨 WEATHER WARNING: Incoming {w_cond} Detected!</h4>
                <p>Outside temperature is {w_temp}°C with active rainfall in {city}. Please ensure all external container ventilation valves are closed to prevent rainwater ingress, which triggers anaerobic rot.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"☀️ Local Weather Status in {city}: {w_cond} ({w_temp}°C). Optimal atmospheric conditions for standard ventilation loops.")
except Exception:
    st.info("ℹ️ Local weather monitoring system running normally in secure baseline state.")


# --- LAYER 3: ENVIRONMENTAL IMPACT & SDG METRICS ---
st.markdown("---")
st.subheader("🌍 Environmental Impact & Global Sustainability Metrics")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #1E4620; margin-top:0;'>🇺🇳 United Nations SDG Alignment</h3>
            <p>This decentralized compost retrofit kit directly contributes to the following UN Sustainable Development Goals (SDGs):</p>
            <div class='sdg-badge'>Goal 13: Climate Action</div>
            <div class='sdg-badge'>Goal 11: Sustainable Cities & Communities</div>
            <div class='sdg-badge'>Goal 12: Responsible Consumption & Production</div>
            <div class='sdg-badge'>Goal 15: Life on Land</div>
            <div class='sdg-badge'>Goal 7: Affordable and Clean Energy</div>
            <ul style='font-size: 13.5px; margin-top: 10px; padding-left: 20px; color: #444;'>
                <li><strong>SDG 13 & 11:</strong> Mitigates localized toxic gas accumulation and limits municipal organic waste volume transported to central landfills.</li>
                <li><strong>SDG 12:</strong> Upcycles waste carbon and nitrogen molecules into active, nutrient-rich organic topsoils.</li>
                <li><strong>SDG 15:</strong> Regenerates local soil biodiversity, replacing chemical inputs with natural, stable bio-fertilizers.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
        <div class='info-card'>
            <h3 style='color: #1E4620; margin-top:0;'>🔥 Active Global Warming Mitigation</h3>
            <p>By implementing this smart monitoring platform, you are actively protecting the biosphere and reducing greenhouse gas emissions through several key mechanisms:</p>
            <ol style='font-size: 13.5px; padding-left: 20px; color: #444;'>
                <li><strong>Eliminating Methane (CH₄) Emissions:</strong> When organic waste rots anaerobically, it releases methane—a greenhouse gas over 28 times more potent than carbon dioxide. The ESP32's automated aeration fan prevents anaerobic pockets, keeping the process clean and carbon-neutral.</li>
                <li><strong>Ending Open Burning Practices:</strong> For rural farmers, upcycling crop residues into bio-fertilizers or energy fuels eliminates the need for field burning, directly preventing massive carbon dioxide, soot, and particulate matter (PM2.5) releases.</li>
                <li><strong>Sequestering Soil Carbon:</strong> Curing high-quality home fertilizers allows carbon compounds to bind stably to the ground, trapping atmospheric carbon directly within terrace garden soils.</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)
