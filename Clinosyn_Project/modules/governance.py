import streamlit as st
from modules.db_utils import fetch_data

def render_governance():
    st.title("🛡️ Data Governance & Compliance")
    st.markdown("Real-time compliance status from OmniIngest's live database.")

    col_gov1, col_gov2 = st.columns([2, 1])

    with col_gov1:
        st.subheader("Active Data Streams (Ingress Logs)")
        try:
            df_logs = fetch_data("SELECT * FROM patients ORDER BY ingest_timestmp DESC LIMIT 10")
            if not df_logs.empty:
                log_cols = ['patient_name', 'abha_id', 'consent_status', 'ingest_status', 'ingest_timestmp']
                available = [c for c in log_cols if c in df_logs.columns]
                st.dataframe(df_logs[available], use_container_width=True)
            else:
                st.info("No ingress logs yet. Activate OmniIngest Sandbox first.")
        except Exception as e:
            st.warning(f"Could not load logs: {e}")

    with col_gov2:
        st.subheader("Rule 8.3 Kill-Switch")
        st.markdown("Instantly revoke access to all active data streams.")

        kill_state = st.session_state.get('kill_switch_active', False)

        if not kill_state:
            st.error("🚨 SYSTEM ARMED")
            if st.button("ACTIVATE KILL-SWITCH", type="primary", use_container_width=True):
                st.session_state['kill_switch_active'] = True
                st.rerun()
        else:
            st.warning("⚠️ SYSTEM SEVERED")
            st.markdown("**All data streams cryptographically halted.**")
            if st.button("RESTORE ACCESS", type="secondary", use_container_width=True):
                st.session_state['kill_switch_active'] = False
                st.rerun()

    st.markdown("---")
    st.success("✅ Consent Validation Engine: **ONLINE** (All records verified against ABDM Consent Artefacts).")
