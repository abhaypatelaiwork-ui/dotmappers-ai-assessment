import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from dotenv import load_dotenv
from ui.api_client import health_check
from ui.components import (
    render_health_badge,
    render_query_tab,
    render_anomaly_tab,
    render_data_tab,
)

load_dotenv()

# Page config
st.set_page_config(
    page_title="DOTMappers Ticket AI",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Header
st.title("🎫 DOTMappers Support Ticket AI")
st.caption("Ask questions in plain English · Detect anomalies · Explore data")

# Sidebar
st.sidebar.header("⚙️ System Status")
health = health_check()
render_health_badge(health)

st.sidebar.divider()
st.sidebar.markdown(
    """
    **How to use:**
    1. **Ask** — type any English question
    2. **Anomalies** — see flagged tickets
    3. **Data** — browse raw tickets

    **Stack:** FastAPI + Gemini + SQLite + Streamlit
    """
)

# Tabs
tab1, tab2, tab3 = st.tabs(["💬 Ask", "🚨 Anomalies", "📊 Data"])

with tab1:
    render_query_tab()

with tab2:
    render_anomaly_tab()

with tab3:
    render_data_tab()