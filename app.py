import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import joblib

# 1. Page Configuration
st.set_page_config(page_title="Biomass Monitoring Dashboard", layout="wide")
st.title("🌱 Smart Biomass Storage & Predictive Monitoring System")
st.markdown("Real-time telemetry and machine learning predictive analytics pipeline.")

# 2. Configuration Parameters
CHANNEL_ID = "3420644"
READ_API_KEY = "KUTCD4R1BFV20MZ5"
MODEL_PATH = "decision_tree.pkl"

# 3. Load Trained ML Model
@st.cache_resource
def load_model():
    try:
        return joblib.load(MODEL_PATH)
    except FileNotFoundError:
        st.error(f"❌ Error: '{MODEL_PATH}' not found. Please upload it to your GitHub repository.")
        return None

model = load_model()

# 4. Fetch Live Data from ThingSpeak
@st.cache_data(ttl=15) # Refresh cache every 15 seconds
def fetch_thingspeak_data():
    url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={READ_API_KEY}&results=50"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            feeds = response.json().get('feeds', [])
            if feeds:
                df = pd.DataFrame(feeds)
                # Typecast to Float
                df['Temp'] = df['field1'].astype(float)
                df['Humidity'] = df['field2'].astype(float)
                df['Moisture'] = df['field3'].astype(float)
                df['Gas'] = df['field4'].astype(float)
                df['Timestamp'] = pd.to_datetime(df['created_at'])
                return df
    except Exception as e:
        st.sidebar.error(f"API Connection Error: {e}")
    return pd.DataFrame() # Return empty dataframe if it fails

df_live = fetch_thingspeak_data()

if not df_live.empty:
    # Get latest telemetry reading
    latest_reading = df_live.iloc[-1]
    
    # 5. Dashboard Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Temperature", f"{latest_reading['Temp']} °C")
    col2.metric("Humidity", f"{latest_reading['Humidity']} %")
    col3.metric("Moisture content", f"{latest_reading['Moisture']} %")
    col4.metric("Gas Concentration", f"{latest_reading['Gas']} ppm")
    
    st.markdown("---")
    
    # 6. Machine Learning Prediction Engine
    if model:
        # Structure the input exactly like the training feature columns
        input_features = pd.DataFrame([{
            "Temp": latest_reading['Temp'],
            "Humidity": latest_reading['Humidity'],
            "Moisture": latest_reading['Moisture'],
            "Gas": latest_reading['Gas']
        }])
        
        prediction = model.predict(input_features)[0]
        
        st.subheader("🔮 Machine Learning Operational Inference")
        if prediction == 1:
            st.error("🚨 System Status: **PELLET MODE ACTIVATED** (High Temperature/Gas or Critical Low Moisture detected)")
        else:
            st.success("✅ System Status: **COMPOST MODE ACTIVE** (Safe, baseline environmental parameters)")

    st.markdown("---")
    
    # 7. Interactive Visualizations
    st.subheader("📈 Environmental Trend Analysis (Last 50 Readings)")
    fig = px.line(df_live, x='Timestamp', y=['Temp', 'Moisture', 'Gas'], 
                  labels={'value': 'Sensor Magnitude', 'variable': 'Sensors'},
                  title="Multi-Channel Dynamic Telemetry Streams")
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ No telemetry data retrieved from ThingSpeak. Please confirm your hardware tracker is actively broadcasting packets.")
