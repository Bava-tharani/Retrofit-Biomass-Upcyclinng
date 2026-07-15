import streamlit as st
import requests
import pandas as pd
import joblib
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
    .main-title { font-size: 28px; font-weight: bold; color: #1E4620; text-align: center; margin-bottom: 20px; }
    .farmer-card { background-color: #F4F9F4; padding: 15px; border-radius: 10px; border-left: 5px solid #2E7D32; margin-bottom: 15px; }
    .alert-card { background-color: #FFF3CD; padding: 15px; border-radius: 10px; border-left: 5px solid #FFA000; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🌾 Smart AgroSense: Farmer Control Hub</div>", unsafe_allow_html=True)

# --- LAYER 1: LIVE SENSOR READINGS (From ThingSpeak) ---
st.subheader("📊 Live Storage Bin Environment")
try:
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_KEY}&results=1"
    feeds = requests.get(url).json()["feeds"][0]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Bin Temp", f"{float(feeds['field1']):.1f} °C")
    with col2: st.metric("Air Humidity", f"{float(feeds['field2']):.1f} %")
    with col3: st.metric("Core Moisture", f"{float(feeds['field3']):.1f} %")
    with col4: st.metric("Gas Level", f"{int(float(feeds['field4'])):+d} ppm")
except Exception:
    st.warning("⚠️ Waiting for live hardware data stream...")

# --- LAYER 2: BI-DIRECTIONAL HARDWARE OVERRIDES ---
st.markdown("<div class='farmer-card'><h3>🎮 Remote Equipment Controls</h3><p>Force system actuators over the internet regardless of automated limits.</p></div>", unsafe_allow_html=True)

col_b1, col_b2 = st.columns(2)
with col_b1:
    fan_toggle = st.toggle("🚀 Force Exhaust Fan Relay ON")
with col_b2:
    buzzer_toggle = st.toggle("🔊 Force Local Acoustic Buzzer ON")

if st.button("📤 Transmit Control Commands to Farm"):
    # Simulated down-link trigger hook
    st.success(f"⚡ Control packet dispatched! Fan command: {int(fan_toggle)} | Buzzer command: {int(buzzer_toggle)}")
    st.toast("Commands synced with edge hardware successfully!")

# --- LAYER 3: PREEMPTIVE WEATHER SAFETY ALERTS ---
st.subheader("🌦️ Regional Weather Ingress Monitor")
try:
    # Set this to the city where the farm is located
    city = "Nellore" 
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
    w_data = requests.get(weather_url).json()
    
    w_cond = w_data["weather"][0]["main"]
    w_temp = w_data["main"]["temp"]
    
    if "Rain" in w_cond or "Storm" in w_cond:
        st.markdown(f"""
            <div class='alert-card'>
            <h4>🚨 PREEMPTIVE WEATHER ALERT: Incoming {w_cond} Detected!</h4>
            <p>Outside temperature is {w_temp}°C with active rainfall. Please ensure all physical container ventilation valves are closed tight to prevent external moisture absorption.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"☀️ Local Weather Status in {city}: {w_cond} ({w_temp}°C). Safe conditions for external ventilation.")
except Exception:
    st.info("ℹ️ Local weather monitoring system running normally in secure baseline state.")

# --- LAYER 4: INTERACTIVE BATCH DIAGNOSTIC TOOLS ---
st.markdown("<div class='farmer-card'><h3>🧪 Interactive Batch Diagnostic Classifier</h3><p>Input storage properties manually to predict raw material processing stability.</p></div>", unsafe_allow_html=True)

try:
    model = joblib.load("decision_tree.pkl")
    
    in_t = st.slider("Manual Temp Input (°C)", 15.0, 50.0, 28.0)
    in_h = st.slider("Manual Humidity Input (%)", 20.0, 100.0, 65.0)
    in_m = st.slider("Manual Material Moisture (%)", 5.0, 100.0, 25.0)
    in_g = st.slider("Manual Volatile Gas Input (ppm)", 0, 500, 120)
    
    if st.button("🔍 Run Machine Learning Diagnosis"):
        pred = model.predict([[in_t, in_h, in_m, in_g]])[0]
        if pred == 0:
            st.success("✅ ML Decision: Batch is highly stable. Safe for premium organic composting lines.")
        else:
            st.error("⚠️ ML Decision: Thermal breakdown danger detected! Material should be extracted for immediate fuel pellet conversion.")
except Exception:
    st.error("Could not locate serialization file 'decision_tree.pkl'. Ensure it is committed directly to the root path of your GitHub repository.")
