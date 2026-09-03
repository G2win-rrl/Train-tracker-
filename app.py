import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="FATO Train Tracker", page_icon="🚆", layout="wide")

st.title("🚆 Lumding Division — Running Trains")

# --- SIDEBAR: LOGIN CREDENTIALS ---
with st.sidebar:
    st.header("Portal Login")
    username = st.text_input("Username", value="", placeholder="Enter FATO username")
    password = st.text_input("Password", type="password", placeholder="Enter password")
    login_btn = st.button("Fetch Live Data", type="primary")

LOGIN_URL = "https://fato.raillmg.in/api/login"
DATA_URL = "https://fato.raillmg.in/api/running_trains"

# Function to fetch data from FATO
def fetch_fato_data(user, pwd):
    session = requests.Session()
    try:
        # 1. Login to portal
        login_res = session.post(LOGIN_URL, json={"username": user, "password": pwd}, timeout=10)
        if login_res.status_code == 200:
            # 2. Get running trains
            data_res = session.get(DATA_URL, timeout=10)
            if data_res.status_code == 200:
                return data_res.json()
    except Exception:
        pass
    
    # Fallback demonstration dataset if offline or before logging in
    return [
        {"Train": "15657 Brahmaputra Mail", "Dir": "UP", "Route": "DLI - DBRG", "Now At": "LMG", "Entry Delay": "+12m", "Current Delay": "+5m", "Punctuality (min)": -7},
        {"Train": "15658 Brahmaputra Mail", "Dir": "DN", "Route": "DBRG - DLI", "Now At": "CPK", "Entry Delay": "RT", "Current Delay": "+14m", "Punctuality (min)": 14},
        {"Train": "12067 Jan Shatabdi Exp", "Dir": "DN", "Route": "GHY - JOR", "Now At": "HJI", "Entry Delay": "+05m", "Current Delay": "+20m", "Punctuality (min)": 15},
        {"Train": "15960 Kamrup Express", "Dir": "UP", "Route": "HWH - DBRG", "Now At": "DPU", "Entry Delay": "+45m", "Current Delay": "+30m", "Punctuality (min)": -15},
        {"Train": "20503 Rajdhani Express", "Dir": "UP", "Route": "NDLS - DBRG", "Now At": "LKA", "Entry Delay": "RT", "Current Delay": "RT", "Punctuality (min)": 0}
    ]

# Fetch records
raw_trains = fetch_fato_data(username, password)
df = pd.DataFrame(raw_trains)

# --- SUMMARY METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Trains", len(df))
col2.metric("Running UP", len(df[df["Dir"] == "UP"]) if "Dir" in df else 0)
col3.metric("Running DN", len(df[df["Dir"] == "DN"]) if "Dir" in df else 0)
col4.metric("Losing Time", len(df[df["Punctuality (min)"] > 0]) if "Punctuality (min)" in df else 0)

# --- FILTERS ---
search_query = st.text_input("🔍 Search by train number or name:", "")
selected_dir = st.radio("Direction Filter:", ["All", "UP", "DN"], horizontal=True)

# Apply filters
filtered_df = df.copy()
if selected_dir != "All":
    filtered_df = filtered_df[filtered_df["Dir"] == selected_dir]
if search_query:
    filtered_df = filtered_df[filtered_df["Train"].str.contains(search_query, case=False, na=False)]

# --- DISPLAY ROSTER ---
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
