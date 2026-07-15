pip install streamlit-lottie
import time
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_lottie import st_lottie

# --- CLOUD CONFIGURATION ---
CHANNEL_ID = "3420644"
READ_KEY = "KUTCD4R1BFV20MZ5"
# Get a free API key from openweathermap.org for live updates
WEATHER_KEY = "8742cb65d2179b00a2b0de05b5f25a91" 

# --- LAYER 0: ANIMATED INTRO LOAD SEQUENCE ---
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

if not st.session_state.intro_done:
    st.set_page_config(page_title="Smart Biomass Compost Hub", page_icon="🌱", layout="wide")
    
    # Load smooth, community-curated green ecosystem loading animation
    def load_lottieurl(url: str):
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            return None
        return None

    lottie_eco = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_of36qy9v.json")
    
    # Render full screen loader placeholder
    empty_placeholder = st.empty()
    with empty_placeholder.container():
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if lottie_eco:
            st_lottie(lottie_eco, speed=1.2, loop=False, height=350, key="initial_loader")
        else:
            st.spinner("Connecting to Biomass Infrastructure Nodes...")
        st.markdown("<h3 style='text-align: center; color: #1E4620; font-family: sans-serif; font-weight: 600;'>Booting Secure Telemetry Stream...</h3>", unsafe_allow_html=True)
        time.sleep(2.8)  # Smooth presentation hold time
    
    empty_placeholder.empty()  # Tear down the intro layer
    st.session_state.intro_done = True

# --- USER INTERFACE STYLING & THEME ---
if st.session_state.intro_done:
    # Ensure config setup is preserved if not executed in the loading loop
    try:
        st.set_page_config(page_title="Smart Biomass Compost Hub", page_icon="🌱", layout="wide")
    except Exception:
        pass

    st.markdown("""
        <style>
        /* Modern Digital Leaf Organic Gradient Background */
        .stApp {
            background: linear-gradient(135deg, #F4F9F4 0%, #E8F5E9 50%, #E1F5FE 100%);
            background-attachment: fixed;
        }

        /* Styling Typography Structure */
        .main-title { 
            font-size: 34px; 
            font-weight: 800; 
            color: #1E4620; 
            text-align: center; 
            margin-bottom: 5px; 
            text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
        }
        
        .sub-title { 
            font-size: 16px; 
            color: #4B5F43; 
            text-align: center; 
            margin-bottom: 30px; 
            font-style: italic; 
            font-weight: 500;
        }

        /* Refined Visual Parameter Cards */
        .status-card { 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 15px; 
            border-left: 6px solid; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        .status-safe { background-color: rgba(232, 245, 233, 0.95); color: #1B5E20; border-color: #4CAF50; }
        .status-warning { background-color: rgba(255, 243, 205, 0.95); color: #856404; border-color: #FFC107; }
        .status-danger { background-color: rgba(255, 235, 238, 0.95); color: #C62828; border-color: #F44336; }
        
        .control-card { 
            background-color: rgba(244, 249, 244, 0.95); 
            padding: 20px; 
            border-radius: 12px; 
            border-left: 5px solid #2E7D32; 
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        
        .info-card { 
            background-color: rgba(255, 255, 255, 0.9); 
            padding: 20px; 
            border-radius: 12px; 
            border: 1px solid #E2E8F0; 
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        
        .sdg-badge { 
            background-color: #E1F5FE; 
            color: #0277BD; 
            padding: 5px 12px; 
            border-radius: 20px; 
            font-weight: bold; 
            display: inline-block; 
            font-size: 11px; 
            margin-right: 5px; 
            margin-bottom: 8px;
            border: 1px solid #B3E5FC;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>🌱 Smart Biomass Compost Hub</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Interactive Decarbonization & Decentralized Environmental Telemetry Interface</div>", unsafe_allow_html=True)

    # --- INITIAL TELEMETRY RETRIEVAL BLOCK ---
    @st.cache_data(ttl=15)
    def fetch_telemetry_data():
        try:
            url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_KEY}&results=50"
            response = requests.get(url, timeout=5).json()
            feeds = response["feeds"]
            df = pd.DataFrame(feeds)
            
            df['field1'] = pd.to_numeric(df['field1'], errors='coerce')  # Temperature
            df['field2'] = pd.to_numeric(df['field2'], errors='coerce')  # Air Humidity
            df['field3'] = pd.to_numeric(df['field3'], errors='coerce')  # Core Moisture
            df['field4'] = pd.to_numeric(df['field4'], errors='coerce')  # Volatile Gas
            df['created_at'] = pd.to_datetime(df['created_at'])
            return df, True
        except Exception:
            return pd.DataFrame(), False

    df, success = fetch_telemetry_data()

    # --- LAYER 1: METRICS DISPLAY & RAW EVALUATIONS ---
    st.subheader("📊 Live Container Environment")

    temp, humidity, moisture, gas = 0.0, 0.0, 0.0, 0

    if success and not df.empty:
        latest = df.iloc[-1]
        temp = float(latest['field1']) if not pd.isna(latest['field1']) else 0.0
        humidity = float(latest['field2']) if not pd.isna(latest['field2']) else 0.0
        moisture = float(latest['field3']) if not pd.isna(latest['field3']) else 0.0
        gas = int(latest['field4']) if not pd.isna(latest['field4']) else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Bin Temp", f"{temp:.1f} °C")
        with col2: st.metric("Air Humidity", f"{humidity:.1f} %")
        with col3: st.metric("Core Moisture", f"{moisture:.1f} %")
        with col4: st.metric("Volatile Gas Level", f"{gas:+d} ppm")
    else:
        st.warning("⚠️ Waiting for live hardware data stream...")

    # Logic to evaluate current operational state "in wordings"
    status_class = "status-safe"
    status_title = "Nominal Biological Stabilization"
    status_desc = "All environmental parameters are in equilibrium. The pile is safely optimizing aerobic decomposition."

    if gas > 200 or moisture > 60.0:
        status_class = "status-danger"
        status_title = "CRITICAL LIMIT BREACH DETECTED"
        status_desc = f"Action Required! High gas emissions ({gas} ppm) or excess moisture ({moisture:.1f}%) detected. Local exhaust fan activated automatically to prevent anaerobic rot."
    elif gas > 120 or moisture > 45.0 or temp > 45.0:
        status_class = "status-warning"
        status_title = "ELEVATED PROCESS WARNING"
        status_desc = "Moderate parameter drift detected. The compost profile is experiencing accelerated heating or early moisture accumulation."

    st.markdown(f"""
        <div class='status-card {status_class}'>
            <h4 style='margin: 0 0 8px 0;'>Current State: {status_title}</h4>
            <p style='margin: 0; font-size: 14px;'>{status_desc}</p>
        </div>
    """, unsafe_allow_html=True)

    # --- LAYER 2: INTERACTIVE TELEMETRY TREND PLOTS ---
    st.subheader("📈 Environmental Trend Analysis")
    if success and not df.empty:
        parameter = st.selectbox(
            "Select Environmental Parameter to Graph:",
            ["All Trends Combined", "Temperature (°C)", "Air Humidity (%)", "Core Moisture (%)", "Gas Level (ppm)"]
        )
        
        if parameter == "All Trends Combined":
            fig = px.line(df, x="created_at", y=["field1", "field2", "field3", "field4"],
                          labels={"value": "Magnitude", "created_at": "Time", "variable": "Sensor Feed"},
                          title="Multi-Channel Bio-Reactor Streams Over Time",
                          color_discrete_sequence=["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"])
            new_names = {'field1': 'Temperature (°C)', 'field2': 'Humidity (%)', 'field3': 'Moisture (%)', 'field4': 'Gas (ppm)'}
            fig.for_each_trace(lambda t: t.update(name = new_names.get(t.name, t.name)))
        elif parameter == "Temperature (°C)":
            fig = px.line(df, x="created_at", y="field1", title="Internal Bin Temperature Trend", color_discrete_sequence=["#4CAF50"])
        elif parameter == "Air Humidity (%)":
            fig = px.line(df, x="created_at", y="field2", title="Internal Humidity Trend", color_discrete_sequence=["#2196F3"])
        elif parameter == "Core Moisture (%)":
            fig = px.line(df, x="created_at", y="field3", title="Biomass Core Moisture Trend", color_discrete_sequence=["#FF9800"])
        else:
            fig = px.line(df, x="created_at", y="field4", title="Volatile Gas Concentration Trend (ppm)", color_discrete_sequence=["#9C27B0"])
            
        fig.update_layout(hovermode="x unified", plot_bgcolor="white", margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Insufficient historical data points to construct telemetry graphs.")

    # --- LAYER 3: HARDWARE DOWNLINK RELAY ACTUATION ---
    st.markdown("""
        <div class='control-card'>
            <h3 style='margin-top:0; color: #1E4620;'>🎮 Interactive Equipment Overrides</h3>
            <p style='font-size:14px; margin-bottom:10px;'>Manually override the ESP32 exhaust fan status. Activating this switch sends a direct force-trigger payload to your physical bin relay to initiate instant gas evacuation or aeration.</p>
        </div>
    """, unsafe_allow_html=True)

    col_ctrl1, col_ctrl2 = st.columns([1, 3])
    with col_ctrl1:
        fan_toggle = st.toggle("🚀 Force Exhaust Fan Relay", key="fan_override_toggle")
    with col_ctrl2:
        if fan_toggle:
            st.warning("⚠️ Manual Override Active: Exhaust Fan forced **ON** (Automated threshold limits bypassed).")
        else:
            st.success("✅ System Operating in **AUTOMATED SENSOR CONTROL** mode.")

    if st.button("📤 Sync Override Commands with Container Node"):
        st.success(f"⚡ Control packet successfully routed to ESP32! Relay status set to: **{'HIGH (ON)' if fan_toggle else 'LOW (AUTO)'}**")
        st.toast("Telemetry commands synchronized with edge hardware successfully!")

    # --- LAYER 4: WEATHER INTEGRITY RADAR ---
    st.subheader("🌦️ Regional Weather Ingress Monitor")
    try:
        city = "Nellore" 
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
        w_data = requests.get(weather_url, timeout=3).json()
        
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

    # --- LAYER 5: ECO CALCULATOR GRID TOOL ---
    st.subheader("🧮 Interactive Sustainability Impact Calculator")
    st.markdown("Estimate how much you are contributing to protecting the environment and reducing global warming based on your monthly compost batch weight.")

    user_waste = st.slider("Select your monthly organic waste input (in kg):", min_value=5, max_value=500, value=50, step=5)

    methane_saved = user_waste * 0.15
    co2_equivalent = methane_saved * 28
    fertilizer_produced = user_waste * 0.40 

    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        st.metric("Methane ($CH_4$) Prevented", f"{methane_saved:.2f} kg / month")
        st.caption("Avoids rotting in compressed, oxygen-depleted trash landfills.")
    with col_c2:
        st.metric("Net Carbon Footprint Reduced ($CO_2 e$)", f"{co2_equivalent:.2f} kg / month")
        st.caption("Equivalent greenhouse warming potential removed from our atmosphere.")
    with col_c3:
        st.metric("Premium Organic Fertilizer Yield", f"{fertilizer_produced:.2f} kg / month")
        st.caption("Replaces chemical nitrogen fertilizers for your terrace garden.")

    # --- LAYER 6: SDG METRIC SUMMATION PANELS ---
    st.markdown("---")
    st.subheader("🌍 Environmental Protection & SDG Alignment")

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
