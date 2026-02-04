import streamlit as st
import pandas as pd
import json
import os
import sys  # <--- NEW IMPORT
import plotly.express as px

# PAGE SETUP - BRANDING UPDATE
st.set_page_config(page_title="Civic Works | Market Intelligence", layout="wide")

# HELPER FUNCTIONS
def load_data():
    if not os.path.exists("swarm_data.json"):
        return pd.DataFrame()
    with open("swarm_data.json", "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def save_scan_config(state, types):
    config = {"state": state, "types": types}
    with open("scan_config.json", "w") as f:
        json.dump(config, f)

# SIDEBAR CONTROLS
st.sidebar.title("🏛️ Civic Works")
st.sidebar.caption("Alliance Management System v1.0")
st.sidebar.markdown("---")

# User Inputs
selected_state = st.sidebar.selectbox("Target Region", ["WA", "OR", "ID"])
selected_types = st.sidebar.multiselect(
    "Jurisdiction Types", 
    ["City", "School District", "Port", "County"],
    default=["City", "School District"]
)

st.sidebar.markdown("---")

if st.sidebar.button("🚀 RUN INTELLIGENCE SCAN"):
    with st.spinner(f"Civic Works agents scanning {selected_state}..."):
        save_scan_config(selected_state, selected_types)
        
        # --- THE FIX FOR MAC USERS ---
        # Instead of "python", we use sys.executable to find the right command automatically
        os.system(f"{sys.executable} swarm_engine.py") 
        # -----------------------------
        
        st.success("Scan Complete.")
        st.rerun()

# MAIN DASHBOARD
st.title("Civic Works")
st.markdown(f"### 📡 Live Market Intelligence: **{selected_state}**")

df = load_data()

if df.empty:
    st.info("👋 Welcome to Civic Works. Select a Region on the left and click 'Run Intelligence Scan' to begin.")
else:
    # KPIS
    c1, c2, c3 = st.columns(3)
    c1.metric("Pipeline Value", f"${df['budget'].sum():,.0f}")
    c2.metric("Active Opportunities", len(df))
    c3.metric("Primary Sector", df['type'].mode()[0])

    # TABS
    tab1, tab2, tab3 = st.tabs(["📊 Market Analysis", "📋 Opportunity Grid", "💡 Strategic Advisor"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Budget by Jurisdiction")
            fig = px.pie(df, names='type', values='budget', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("RFP Forecast")
            fig2 = px.bar(df, x='rfp_date', y='budget', color='status')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.dataframe(
            df[['entity', 'project', 'budget', 'status', 'rfp_date']],
            column_config={
                "budget": st.column_config.NumberColumn("Est. Value", format="$%d"),
                "status": st.column_config.TextColumn("Current Status"),
            },
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        for i, row in df.iterrows():
            with st.expander(f"Strategy: {row['project']}"):
                st.write(f"**Value:** ${row['budget']:,.0f}")
                st.info(f"**Civic Works Advisor:** {row['strategy']}")
