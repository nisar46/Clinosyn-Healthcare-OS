import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = r"D:\Omnigest_ABDM_2.0\Phase_0.3\omniingest_FINAL.db"

@st.cache_data(ttl=1)  # Refresh every 1 second to catch live updates
def fetch_data(query):
    if st.session_state.get('kill_switch_active', False):
        return pd.DataFrame() # 🚨 KILL SWITCH: Return empty dataframe

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()
