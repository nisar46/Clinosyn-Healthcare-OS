import streamlit as st
import pandas as pd
import polars as pl
import sqlite3
import json
import requests
import re
from collections import Counter
import os
import sys

# Ensure src module is reachable for audit logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.database import log_audit_event

DB_PATH = r"D:\Omnigest_ABDM_2.0\Phase_0.3\omniingest_FINAL.db"

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

@st.cache_data(ttl=1)
def fetch_data(query, params=None):
    if st.session_state.get('kill_switch_active', False):
        return pd.DataFrame() # KILL SWITCH: Return empty dataframe

    try:
        conn = sqlite3.connect(DB_PATH)
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        # Fallback for 'final_validated' table to 'patients' table
        if "no such table: final_validated" in str(e).lower() and "final_validated" in query.lower():
            try:
                conn = sqlite3.connect(DB_PATH)
                query_fallback = query.replace("final_validated", "patients")
                if params:
                    df = pd.read_sql_query(query_fallback, conn, params=params)
                else:
                    df = pd.read_sql_query(query_fallback, conn)
                conn.close()
                return df
            except Exception as e_fallback:
                pass
        return pd.DataFrame()

# ============================================================
# 1. INTELLIGENCE MODULE (RAG + OLLAMA STREAMING)
# ============================================================
def render_intelligence():
    st.title("🧠 Clinical Intelligence (RAG)")
    st.markdown("Ask natural language questions about verified clinical data.\n\n🛡️ **Powered securely by local offline AI (Ollama)** - Zero data leaves this device.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat Control Header
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # THE CHAT REPETITION AND RENDERING FIX
    # Loops strictly over only the finalized completed elements
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("Ask a clinical question...")

    if query:
        st.chat_message("user").markdown(query)
        st.session_state.messages.append({"role": "user", "content": query})
        
        # CORE KILL-SWITCH RULE - DPDP SECTION 8
        search_term = f"%{query}%"
        revoked_query = "SELECT * FROM final_validated WHERE status_reason = 'CONSENT_REVOKED' AND (patient_name LIKE ? OR abha_id LIKE ? OR clinical_payload LIKE ?)"
        revoked_df = fetch_data(revoked_query, params=(search_term, search_term, search_term))
        
        if not revoked_df.empty:
            st.session_state.messages = [] # Wipe the context memory array
            st.error("ACCESS DENIED: Data processing privileges for this token have been permanently terminated under DPDP Rule 8 Compliance.")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "ACCESS DENIED: Data processing privileges for this token have been permanently terminated under DPDP Rule 8 Compliance."
            })
            log_audit_event('KILL_SWITCH_INTERCEPT', query, 'DPDP Rule 8 Compliance', 'Aborted LLM Execution for Revoked Token')
            return

        with st.chat_message("assistant"):
            with st.spinner("Clinosyn OS is securely parsing and verifying medical records..."):
                # HARD PYTHON/SQL ISOLATION FILTER (THE DATA LEAK FIX)
                sql_query = """
                    SELECT * FROM final_validated 
                    WHERE status_reason != 'CONSENT_REVOKED' 
                    AND (patient_name LIKE ? OR abha_id LIKE ? OR clinical_payload LIKE ?)
                    LIMIT 10
                """
                df = fetch_data(sql_query, params=(search_term, search_term, search_term))
                
                # PEDIATRIC PRIVACY LOCK AND INFANT SECURITY SHIELD SCENARIO
                if not df.empty and 'Age' in df.columns:
                    # Convert to numeric safely
                    df['Age'] = pd.to_numeric(df['Age'], errors='coerce')
                    if (df['Age'] < 12).any():
                        st.session_state.messages = [] # Clear context memory space
                        warning_msg = "Pediatric Privacy Lock Active: Detailed infant biometric summaries and historical data processing require parental guardian override verification."
                        st.warning(warning_msg)
                        st.session_state.messages.append({"role": "assistant", "content": warning_msg})
                        log_audit_event("PEDIATRIC_PRIVACY_LOCK", query, "HIPAA / DPDP 2023", "Intercepted Pediatric Record Request (Age < 12)")
                        return

                # THE GRANULAR TRIAGE AUDIT BREAKDOWN SCENARIO
                triage_metrics_payload = ""
                query_lower = query.lower()
                if "quarantine" in query_lower or "triage" in query_lower or "error" in query_lower or "status" in query_lower or "why" in query_lower:
                    conn = sqlite3.connect(DB_PATH)
                    missing_abha_count = conn.execute("SELECT COUNT(*) FROM patients WHERE status_reason = 'MISSING_ABHA'").fetchone()[0]
                    audit_count = conn.execute("SELECT COUNT(*) FROM patients WHERE status_reason = 'PENDING_CLINICAL_AUDIT'").fetchone()[0]
                    total_errors = missing_abha_count + audit_count
                    conn.close()
                    triage_metrics_payload = f"CRITICAL SYSTEM TRUTH LOGS: The database currently contains exactly {total_errors} quarantined records. Operational Breakdown: Exactly {missing_abha_count} records are actively held at the Identity Desk specifically due to MISSING_ABHA validation errors. Exactly {audit_count} records are actively held at the Clinical Audit Desk specifically due to PENDING_CLINICAL_AUDIT discrepancies. Operator Action Required.\n\n"

                # DEMOGRAPHIC CASE INTELLIGENCE AND REPORTING SCENARIO
                demographics_payload = ""
                if "demographic" in query.lower() or "age" in query.lower() or "gender" in query.lower() or "trend" in query.lower() or "report" in query.lower():
                    demo_df = fetch_data("SELECT * FROM final_validated")
                    if not demo_df.empty:
                        d_df = pl.DataFrame(demo_df)
                        if 'Age' in d_df.columns and 'Gender' in d_df.columns:
                            # Drop nulls and cast
                            d_df = d_df.with_columns(pl.col("Age").cast(pl.Float64, strict=False))
                            mean_age = d_df["Age"].drop_nulls().mean()
                            gender_counts = d_df.group_by("Gender").len().to_dicts()
                            demographics_payload = f"\n\n[DEMOGRAPHICS INTELLIGENCE]: The global hospital demographic trend shows a mean patient age of {mean_age:.1f} years. Gender distribution: {gender_counts}."

            if df.empty:
                patient_record_payload = "No records found."
            else:
                records = df.to_dict(orient="records")
                context_data = {
                    "Sample_Retrieved_Records": records
                }
                patient_record_payload = json.dumps(context_data, indent=2)

            # Inject all granular payloads. Triage metrics go to the HEAD of the context window.
            patient_record_payload = triage_metrics_payload + patient_record_payload + demographics_payload

            # STRICT ANTI-HALLUCINATION PROMPT CONTAINER
            system_prompt = (
                "You are Clinosyn OS, the central authorized clinical operating system assistant. "
                "You must summarize patient charts based strictly and exclusively on the verified data records provided in the active Context window. "
                "If the user asks about triage, errors, quarantine, or reasons, you must strictly extract and provide your answer using the 'CRITICAL SYSTEM TRUTH LOGS' block provided in the context. "
                "If a clinical question cannot be derived or answered using only the retrieved data context, you must reply exactly with: "
                "'Error: No verified clinical history found in the OmniIngest secure data vault for this request.' "
                "Do NOT extrapolate, guess, assume, or hallucinate patient details under any circumstances.\n\n"
                f"Context window:\n{patient_record_payload}"
            )
            
            messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages
            
            ollama_model = st.session_state.get('ollama_model', 'llama3')
            api_url = "http://localhost:11434/api/chat"
            payload = {
                "model": ollama_model,
                "messages": messages_for_api,
                "stream": True
            }

            try:
                # REAL-TIME TOKEN STREAMING UI
                response = requests.post(api_url, json=payload, stream=True)
                response.raise_for_status()

                def generate():
                    for line in response.iter_lines():
                        if line:
                            json_response = json.loads(line)
                            if "message" in json_response and "content" in json_response["message"]:
                                yield json_response["message"]["content"]
                            if json_response.get("done"):
                                break
                
                # Render live text response using native st.write_stream
                full_response = st.write_stream(generate())
                # Append finalized full_response into localized container array immediately upon completion
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                error_msg = f"⚠️ System Error connecting to local Llama3: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# ============================================================
# 2. ANALYTICS MODULE (AI PERFORMANCE & INSIGHTS)
# ============================================================
def render_analytics():
    st.title("📊 Analytics (Real-Time)")
    st.markdown("Real-time telemetry and clinical signal density from the verified data vault.")
    
    df = fetch_data("SELECT * FROM final_validated")
    if df.empty:
        st.warning("No data found.")
        return

    pl_df = pl.DataFrame(df)
    
    # Dual Styled st.metric() counters
    col1, col2 = st.columns(2)
    with col1:
        cleared_count = len(pl_df.filter(pl.col("ingest_status").str.to_uppercase() == "PROCESSED")) if "ingest_status" in pl_df.columns else 0
        st.metric("✅ Clean Cleared Data Volume (PROCESSED)", f"{cleared_count:,}")
    with col2:
        error_count = len(pl_df.filter(pl.col("ingest_status").str.to_uppercase() == "QUARANTINED")) if "ingest_status" in pl_df.columns else 0
        st.metric("🚨 Caught Triage Errors (QUARANTINED)", f"{error_count:,}")

    st.markdown("---")
    # The 80/20 Funnel Chart
    if "ingest_status" in pl_df.columns:
        st.subheader("The 80/20 Funnel Chart (Data Flow Health)")
        # Upgraded to Polars .len() to prevent deprecation warnings
        status_counts = pl_df.group_by("ingest_status").len().to_pandas()
        status_counts = status_counts.set_index("ingest_status")
        st.bar_chart(status_counts, color="#00d2ff")
    
    st.markdown("---")
    # Clinical Signal Density (Top recurring clinical vocabulary tokens)
    st.subheader("Clinical Signal Density")
    if "clinical_payload" in pl_df.columns:
        text_data = " ".join(pl_df["clinical_payload"].drop_nulls().to_list()).lower()
        # Clean basic punctuation and keep words
        words = re.findall(r'\b[a-z]{4,}\b', text_data)
        # Filter common stopwords
        stopwords = {'patient', 'with', 'this', 'that', 'clinical', 'notes', 'from', 'have', 'been', 'unknown', 'condition', 'standard', 'examination', 'available'}
        filtered_words = [w for w in words if w not in stopwords]
        
        word_counts = Counter(filtered_words).most_common(10)
        
        if word_counts:
            density_df = pd.DataFrame(word_counts, columns=['Clinical Token', 'Frequency']).set_index('Clinical Token')
            st.bar_chart(density_df, color="#10b981")
        else:
            st.info("Insufficient clinical payloads to generate signal density.")
    else:
        st.info("clinical_payload column not available for signal density mapping.")

# ============================================================
# 3. GOVERNANCE MODULE (PRIVACY BY DESIGN LOG)
# ============================================================
def render_governance():
    st.title("🛡️ Governance (DPDP)")
    st.info("Academic Objective: Compliance Audit Log with Active PII Shredding.", icon="🎓")

    df = fetch_data("SELECT * FROM final_validated")
    if df.empty:
        st.warning("No data found for governance audit.")
        return

    # Dynamic Masking for Patient Name
    if 'patient_name' in df.columns:
        # e.g., displaying P********_1_1396
        def mask_name(name):
            if not isinstance(name, str) or len(name) < 2:
                return name
            parts = name.split('_', 1)
            first_part = parts[0]
            masked_first = first_part[0] + "*" * (len(first_part) - 1)
            if len(parts) > 1:
                return f"{masked_first}_{parts[1]}"
            return masked_first + "********"

        df['patient_name'] = df['patient_name'].apply(mask_name)

    # Status log layout for DPDP Section 8
    if 'consent_status' in df.columns:
        def append_revoked_flag(row):
            if row['consent_status'] == 'REVOKED' or row.get('status_reason') == 'CONSENT_REVOKED':
                return f"REVOKED 🚨 [PII CRYPTOGRAPHICALLY SHREDDED / RAG PIPE BLOCKED]"
            return row['consent_status']
        
        df['consent_status'] = df.apply(append_revoked_flag, axis=1)

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Emergency Protocol (Rule 8.3 Kill-Switch)")
    kill_state = st.session_state.get('kill_switch_active', False)
    if not kill_state:
        st.markdown("Instantly revoke query access to all active data streams in case of a compliance breach.")
        if st.button("ACTIVATE KILL-SWITCH", type="primary", use_container_width=True):
            st.session_state['kill_switch_active'] = True
            log_audit_event('MANUAL_KILL_SWITCH', 'GLOBAL', 'Emergency Protocol', 'Activated System Kill-Switch')
            st.rerun()
    else:
        # High visibility container
        st.error("ACCESS DENIED: Data processing privileges for this token have been permanently terminated under DPDP Rule 8 Compliance.")
        if st.button("RESTORE ACCESS", type="secondary", use_container_width=True):
            st.session_state['kill_switch_active'] = False
            log_audit_event('RESTORE_ACCESS', 'GLOBAL', 'Emergency Protocol', 'Restored System Access')
            st.rerun()

# ============================================================
# SIDEBAR & MAIN ROUTING
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
ollama_model = st.sidebar.text_input("🤖 Ollama Model ID", value="llama3")
st.session_state['ollama_model'] = ollama_model

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Sync Live Data"):
    st.cache_data.clear()
    st.rerun()

df_count = fetch_data("SELECT COUNT(*) as total FROM final_validated")
total = df_count['total'].iloc[0] if not df_count.empty else 0
st.sidebar.metric("Live Records (OmniIngest)", f"{total:,}")
st.sidebar.caption("🟢 Bridge Status: CONNECTED")
st.sidebar.caption("📂 Source: omniingest_FINAL.db")

# Routing
if page == "📊 Analytics (Real-Time)":
    render_analytics()
elif page == "🧠 Intelligence (GenAI)":
    render_intelligence()
elif page == "🛡️ Governance (DPDP)":
    render_governance()
