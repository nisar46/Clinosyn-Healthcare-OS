import streamlit as st
from modules.db_utils import fetch_data

def render_analytics():
    st.title("📊 Clinical Analytics")
    st.markdown("Real-time visualization — **live from OmniIngest ABDM 2.0 database**.")

    try:
        df = fetch_data("SELECT * FROM patients")

        if df.empty:
            st.warning("No data found. Please run OmniIngest first and activate Sandbox or upload a file.")
        else:
            # --- Top Metrics ---
            total = len(df)
            processed = len(df[df['ingest_status'] == 'PROCESSED']) if 'ingest_status' in df.columns else 0
            purged = len(df[df['ingest_status'] == 'PURGED']) if 'ingest_status' in df.columns else 0
            quarantined = total - processed - purged

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Ingested Records", f"{total:,}")
            col2.metric("✅ Processed (Valid)", f"{processed:,}")
            col3.metric("🚫 Purged", f"{purged:,}")
            col4.metric("⚠️ Quarantined", f"{max(quarantined, 0):,}")

            st.markdown("---")

            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.subheader("Record Status Breakdown")
                if 'ingest_status' in df.columns:
                    status_counts = df['ingest_status'].value_counts().reset_index()
                    status_counts.columns = ['Status', 'Count']
                    st.bar_chart(status_counts.set_index('Status'), color="#00d2ff")

            with col_chart2:
                st.subheader("Consent Status")
                if 'consent_status' in df.columns:
                    consent_counts = df['consent_status'].value_counts().reset_index()
                    consent_counts.columns = ['Consent', 'Count']
                    st.bar_chart(consent_counts.set_index('Consent'), color="#ff4b4b")

            st.subheader("Latest Records from OmniIngest (Preview)")
            preview_cols = ['patient_name', 'abha_id', 'consent_status', 'ingest_status', 'status_reason', 'ingest_timestmp']
            available_cols = [c for c in preview_cols if c in df.columns]
            st.dataframe(df[available_cols].tail(20), use_container_width=True)

    except Exception as e:
        st.error(f"Database error: {e}")
        st.info("Make sure OmniIngest ABDM 2.0 has been run at least once.")
