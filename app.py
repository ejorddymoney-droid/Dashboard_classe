import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SupplyChain Pro | Inventory Optimizer",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR PROFESSIONAL UI (Inspired by the provided image) ---
st.markdown("""
    <style>
    /* Main background */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }

    /* Card-like containers */
    div[data-testid="metric-container"] {
        background-color: #1C2128;
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Custom classes for insights */
    .insight-card {
        background-color: #1C2128;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00D1FF;
        margin-bottom: 10px;
    }

    .class-a { color: #00FFC2; font-weight: bold; }
    .class-b { color: #FFD700; font-weight: bold; }
    .class-c { color: #FF6B6B; font-weight: bold; }

    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA INITIALIZATION ---
def initialize_data():
    if 'inventory_df' not in st.session_state:
        # Initial professional sample dataset
        data = {
            'Article_ID': ['ITM-001', 'ITM-002', 'ITM-003', 'ITM-004', 'ITM-005', 'ITM-006', 'ITM-007', 'ITM-008'],
            'Nom_Article': ['Engine Block V8', 'Transmission Kit', 'Fuel Injector', 'Brake Pads', 'Oil Filter', 'LED Headlight', 'Spark Plug', 'Air Filter'],
            'Demande_Annuelle': [500, 300, 4500, 2000, 8000, 1200, 15000, 7500],
            'Cout_Commande': [150, 200, 45, 30, 20, 80, 15, 20],
            'Cout_Possession_Unitaire': [50, 80, 5, 4, 1.5, 12, 0.5, 1.2],
            'Prix_Unitaire': [1200, 2500, 85, 45, 12, 150, 8, 15]
        }
        st.session_state.inventory_df = pd.DataFrame(data)

# --- ANALYTICS ENGINE ---
def calculate_metrics(df):
    # Calculations with error handling
    df = df.copy()
    
    # 1. Annual Consumption Value
    df['Valeur_Annuelle'] = df['Demande_Annuelle'] * df['Prix_Unitaire']
    
    # 2. EOQ Calculation (Standard Wilson Formula)
    # EOQ = sqrt( (2 * D * S) / H )
    df['EOQ'] = np.sqrt((2 * df['Demande_Annuelle'] * df['Cout_Commande']) / df['Cout_Possession_Unitaire'].replace(0, np.nan))
    df['EOQ'] = df['EOQ'].fillna(0).round(0)
    
    # 3. Frequency Metrics
    df['Nombre_Commandes_An'] = (df['Demande_Annuelle'] / df['EOQ'].replace(0, np.nan)).fillna(0).round(2)
    df['Temps_Entre_Commandes'] = (365 / df['Nombre_Commandes_An'].replace(0, np.nan)).fillna(0).round(1)
    
    # 4. Pareto Analysis (ABC)
    df = df.sort_values(by='Valeur_Annuelle', ascending=False)
    total_value = df['Valeur_Annuelle'].sum()
    df['Pourcentage_Contribution'] = (df['Valeur_Annuelle'] / total_value) * 100
    df['Pourcentage_Cumulatif'] = df['Pourcentage_Contribution'].cumsum()
    
    def classify_abc(cum_perc):
        if cum_perc <= 80: return 'A'
        elif cum_perc <= 95: return 'B'
        else: return 'C'
        
    df['Classe_ABC'] = df['Pourcentage_Cumulatif'].apply(classify_abc)
    return df

# --- PAGE: EXECUTIVE DASHBOARD ---
def show_executive_dashboard(df):
    st.title("📊 Supply Chain Executive Overview")
    
    # Top Row KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", len(df))
    with col2:
        st.metric("Total Annual Value", f"${df['Valeur_Annuelle'].sum():,.0f}")
    with col3:
        st.metric("Avg Orders/Year", f"{df['Nombre_Commandes_An'].mean():.1f}")
    with col4:
        a_items = len(df[df['Classe_ABC'] == 'A'])
        a_val_pct = df[df['Classe_ABC'] == 'A']['Pourcentage_Contribution'].sum()
        st.metric("Class A Items", f"{a_items} ({a_val_pct:.1f}%)")

    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Pareto Analysis (Value vs. Cumulative %)")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['Nom_Article'], y=df['Valeur_Annuelle'], name="Annual Value", marker_color='#00D1FF'))
        fig.add_trace(go.Scatter(x=df['Nom_Article'], y=df['Pourcentage_Cumulatif'], name="Cumulative %", yaxis="y2", line=dict(color='#00FFC2', width=3)))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Annual Value ($)"),
            yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("Inventory Distribution")
        abc_counts = df['Classe_ABC'].value_counts().reset_index()
        fig_pie = px.pie(abc_counts, values='count', names='Classe_ABC', 
                         color='Classe_ABC',
                         color_discrete_map={'A':'#00FFC2', 'B':'#FFD700', 'C':'#FF6B6B'},
                         hole=0.4)
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- PAGE: RAW DATA ---
def show_raw_data():
    st.title("📋 Inventory Master Data")
    st.markdown("Modify values directly in the table below to update calculations.")
    
    # Upload Feature
    uploaded_file = st.file_uploader("Upload CSV Data", type="csv")
    if uploaded_file:
        st.session_state.inventory_df = pd.read_csv(uploaded_file)
    
    # Editable Table
    edited_df = st.data_editor(
        st.session_state.inventory_df,
        num_rows="dynamic",
        use_container_width=True,
        key="data_editor"
    )
    
    if st.button("Save Changes"):
        st.session_state.inventory_df = edited_df
        st.success("Data updated successfully!")
    
    # Export
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export to CSV", data=csv, file_name="inventory_data.csv", mime="text/csv")

# --- PAGE: EOQ ANALYSIS ---
def show_eoq_analysis(df):
    st.title("📦 EOQ Optimization Analysis")
    
    st.markdown("""
    **Understanding the Economic Order Quantity:**
    The EOQ model minimizes the sum of ordering and holding costs. 
    High EOQ items suggest volume purchasing, while low EOQ items suggest lean, frequent deliveries.
    """)
    
    # Visualizing EOQ vs Demand
    fig = px.scatter(df, x="Demande_Annuelle", y="EOQ", size="Valeur_Annuelle", color="Classe_ABC",
                 hover_name="Nom_Article", text="Nom_Article", log_x=True,
                 title="EOQ vs Demand (Bubble size = Annual Value)")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    # Data Table
    display_cols = ['Nom_Article', 'Demande_Annuelle', 'EOQ', 'Nombre_Commandes_An', 'Temps_Entre_Commandes']
    st.dataframe(df[display_cols].style.background_gradient(subset=['EOQ'], cmap='GnBu'), use_container_width=True)

# --- PAGE: PARETO ANALYSIS ---
def show_pareto_details(df):
    st.title("🎯 ABC Classification Details")
    
    col1, col2, col3 = st.columns(3)
    for cls, color, col in zip(['A', 'B', 'C'], ['#00FFC2', '#FFD700', '#FF6B6B'], [col1, col2, col3]):
        with col:
            val = df[df['Classe_ABC'] == cls]['Valeur_Annuelle'].sum()
            st.markdown(f"<div style='border:1px solid {color}; padding:10px; border-radius:10px; text-align:center;'>"
                        f"<h3 style='color:{color}'>Class {cls}</h3>"
                        f"Value: ${val:,.0f}</div>", unsafe_allow_html=True)

    st.write("### Detailed Sorted Inventory")
    def color_abc(val):
        color = '#00FFC2' if val == 'A' else '#FFD700' if val == 'B' else '#FF6B6B'
        return f'background-color: {color}44; color: white'

    st.dataframe(df.style.applymap(color_abc, subset=['Classe_ABC']), use_container_width=True)

# --- PAGE: DECISION INSIGHTS ---
def show_insights(df):
    st.title("💡 Strategic Decision Support")
    
    # Automated logic
    top_item = df.iloc[0]
    high_freq = df.loc[df['Nombre_Commandes_An'].idxmax()]
    high_eoq = df.loc[df['EOQ'].idxmax()]
    
    st.markdown(f"""
    <div class="insight-card">
        <h4>🚨 Critical Focus</h4>
        The item <b>{top_item['Nom_Article']}</b> represents <b>{top_item['Pourcentage_Contribution']:.1f}%</b> of your total inventory value. 
        Any disruption here has major financial impact.
    </div>
    
    <div class="insight-card">
        <h4>🔄 Operational Frequency</h4>
        <b>{high_freq['Nom_Article']}</b> requires the highest replenishment frequency 
        (<b>{high_freq['Nombre_Commandes_An']} orders/year</b>). Consider negotiating a blanket purchase order 
        to reduce administrative costs.
    </div>

    <div class="insight-card" style="border-left-color: #FFD700;">
        <h4>📦 Storage Strategy</h4>
        <b>{high_eoq['Nom_Article']}</b> has the highest EOQ (<b>{high_eoq['EOQ']} units</b>). 
        Ensure your warehouse has sufficient physical capacity for these bulk deliveries.
    </div>
    """, unsafe_allow_html=True)
    
    # Inventory Health Score (Mock logic)
    st.subheader("Inventory Health Score")
    score = 85 # Calculated mock
    st.progress(score/100)
    st.write(f"Current System Optimization: {score}%")

# --- MAIN APP FLOW ---
def main():
    initialize_data()
    
    # Navigation
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2897/2897832.png", width=100)
    st.sidebar.title("SCM Optimizer v2.0")
    page = st.sidebar.radio("Navigate to:", 
        ["Executive Dashboard", "Raw Data", "EOQ Analysis", "Pareto Analysis", "Decision Insights"])
    
    # Process Data
    processed_df = calculate_metrics(st.session_state.inventory_df)
    
    # Page Routing
    if page == "Executive Dashboard":
        show_executive_dashboard(processed_df)
    elif page == "Raw Data":
        show_raw_data()
    elif page == "EOQ Analysis":
        show_eoq_analysis(processed_df)
    elif page == "Pareto Analysis":
        show_pareto_details(processed_df)
    elif page == "Decision Insights":
        show_insights(processed_df)

if __name__ == "__main__":
    main()
