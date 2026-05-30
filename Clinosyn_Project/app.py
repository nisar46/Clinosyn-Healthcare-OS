import streamlit as st
import os

# Import our refactored modules
from modules.db_utils import fetch_data, DB_PATH
from modules.analytics import render_analytics
from modules.intelligence import render_intelligence
from modules.governance import render_governance

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="CLINOSYN OS",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    h1, h2, h3 { color: #00d2ff; font-family: 'Inter', sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 2rem; color: #00d2ff; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.markdown(
    """
    <div style="text-align: center; padding-bottom: 10px;">
        <img src="https://img.icons8.com/nolan/256/artificial-intelligence.png" width="130" style="filter: drop-shadow(0px 0px 15px rgba(0, 210, 255, 0.6)); margin-bottom: 5px;">
        <h2 style="color: #00d2ff; margin-top: 0; font-family: 'Inter', sans-serif; font-weight: 800; letter-spacing: 1px;">CLINOSYN OS</h2>
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🧠 Intelligence (GenAI)", "📊 Analytics (Real-Time)", "🛡️ Governance (DPDP)"]
)

st.sidebar.markdown("---")

# Live record count in sidebar
if st.sidebar.button("🔄 Sync Live Data"):
    st.cache_data.clear()
    st.rerun()

df_count = fetch_data("SELECT COUNT(*) as total FROM patients")
total = df_count['total'].iloc[0] if not df_count.empty else 0
st.sidebar.metric("Live Records (OmniIngest)", f"{total:,}")
st.sidebar.caption("🟢 Bridge Status: CONNECTED")
st.sidebar.caption(f"📂 Source: omniingest_FINAL.db")

# ============================================================
# ROUTING
# ============================================================
if page == "📊 Analytics (Real-Time)":
    render_analytics()

elif page == "🧠 Intelligence (GenAI)":
    render_intelligence()

elif page == "🛡️ Governance (DPDP)":
    render_governance()
