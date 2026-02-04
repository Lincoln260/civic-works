import streamlit as st
import pandas as pd
import json
import os
import sys
import plotly.express as px

# PAGE SETUP
st.set_page_config(page_title="Civic Works | Market Intelligence", layout="wide")

# ==========================================
# MASTER ENTITY LIST (Major Markets WA/OR/ID)
# ==========================================
ENTITY_OPTIONS = {
    "WA": {
        "City": [
            "City of Seattle", "City of Spokane", "City of Tacoma", "City of Vancouver", 
            "City of Bellevue", "City of Kent", "City of Everett", "City of Renton", 
            "City of Spokane Valley", "City of Federal Way", "City of Yakima", 
            "City of Kirkland", "City of Bellingham", "City of Kennewick", "City of Auburn", 
            "City of Pasco", "City of Richland", "City of Redmond", "City of Sammamish"
        ],
        "School District": [
            "Seattle Public Schools", "Lake Washington School District", "Spokane Public Schools",
            "Tacoma Public Schools", "Kent School District", "Evergreen Public Schools",
            "Pasco School District", "Kennewick School District", "Richland School District"
        ],
        "Port": [
            "Port of Seattle", "Port of Tacoma", "Port of Vancouver USA", "Port of Everett",
            "Port of Bellingham", "Port of Benton", "Port of Pasco", "Port of Kennewick"
        ],
        "County": [
            "King County", "Pierce County", "Snohomish County", "Spokane County", 
            "Clark County", "Thurston County", "Benton County", "Yakima County"
        ]
    },
    "OR": {
        "City": [
            "City of Portland", "City of Salem", "City of Eugene", "City of Gresham",
            "City of Hillsboro", "City of Beaverton", "City of Bend", "City of Medford",
            "City of Springfield", "City of Corvallis", "City of Albany", "City of Tigard"
        ],
        "School District": [
            "Portland Public Schools", "Salem-Keizer Public Schools", "Beaverton School District",
            "Hillsboro School District", "Eugene School District", "Bend-La Pine Schools"
        ],
        "Port": [
            "Port of Portland", "Port of Coos Bay", "Port of Astoria"
        ],
        "County": [
            "Multnomah County", "Washington County", "Clackamas County", "Lane County", 
            "Marion County", "Deschutes County"
        ]
    },
    "ID": {
        "City": [
            "City of Boise", "City of Meridian", "City of Nampa", "City of Idaho Falls",
            "City of Caldwell", "City of Pocatello", "City of Coeur d'Alene", "City of Twin Falls"
        ],
        "School District": [
            "Boise School District", "West Ada School District", "Nampa School District",
            "Pocatello-Chubbuck School District"
        ],
        "County": [
            "Ada County", "Canyon County", "Kootenai County", "Bonneville County"
        ]
    }
}

# HELPER FUNCTIONS
def load_data():
    if not os.path.exists("swarm_data.json"):
        return pd.DataFrame()
    with open("swarm_data.json", "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)

def save_scan_config(state, types, specific_names):
    # If specific_names is EMPTY, we grab ALL names from the list above for the selected types
    if not specific_names:
        final_list = []
        for t in types:
            final_list.extend(ENTITY_OPTIONS[state].get(t, []))
    else:
        final_list = specific_names

    config = {
        "state": state, 
        "types": types,
        "specific_names": final_list
    }
    with open("scan_config.json", "w") as f:
        json.dump(config, f)

# ==========================================
# SIDEBAR CONTROLS
# ==========================================
st.sidebar.title("🏛️ Civic Works")
st.sidebar.caption("Alliance Management System v1.3")
st.sidebar.markdown("---")

# 1. Select State
selected_state = st.sidebar.selectbox("Target Region", ["WA", "OR", "ID"])

# 2. Select Types
selected_types = st.sidebar.multiselect(
    "Jurisdiction Types", 
    ["City", "School District", "Port", "County"],
    default=["City"]
)

# 3. DYNAMIC DROPDOWN
available_names = []
if selected_state in ENTITY_OPTIONS:
    for t in selected_types:
        names = ENTITY_OPTIONS[selected_state].get(t, [])
        available_names.extend(names)

selected_specifics = st.sidebar.multiselect(
    "Specific Governments (Optional)",
    available_names,
    placeholder="Leave empty to scan ALL above..."
)

st.sidebar.markdown("---")

# 4. Launch Button
if st.sidebar.button("🚀 RUN INTELLIGENCE SCAN"):
    with st.spinner(f"Civic Works agents scanning..."):
        save_scan_config(selected_state, selected_types, selected_specifics)
        os.system(f"{sys.executable} swarm_engine.py")
        st.success("Scan Complete.")
        st.rerun()

# ==========================================
# MAIN DASHBOARD
# ==========================================
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
    sector_label = df['type'].mode()[0] if not df.empty else "N/A"
    c3.metric("Primary Sector", sector_label)

    # TABS
    tab1, tab2, tab3 = st.tabs(["📊 Market Analysis", "📋 Opportunity Grid", "💡 Strategic Advisor"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Budget by Jurisdiction")
            if not df.empty:
                fig = px.pie(df, names='entity', values='budget', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("RFP Forecast")
            if not df.empty:
                fig2 = px.bar(df, x='rfp_date', y='budget', color='status')
                st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        # Check if 'pdf_link' column exists
        cols_to_show = ['entity', 'project', 'budget', 'status']
        col_config = {
            "budget": st.column_config.NumberColumn("Est. Value", format="$%d"),
            "status": st.column_config.TextColumn("Current Status"),
        }
        
        if 'pdf_link' in df.columns:
            cols_to_show.append('pdf_link')
            col_config["pdf_link"] = st.column_config.LinkColumn("Source Document")

        st.dataframe(
            df[cols_to_show],
            column_config=col_config,
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        for i, row in df.iterrows():
            with st.expander(f"Strategy: {row['project']}"):
                st.write(f"**Entity:** {row['entity']}")
                st.write(f"**Value:** ${row['budget']:,.0f}")
                st.info(f"**Civic Works Advisor:** {row['strategy']}")
