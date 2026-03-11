import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="OptiStock Pro | Dashboard Bleu",
    page_icon="🟦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DESIGN SYSTEM (CSS PERSONNALISÉ - PALETTE BLEU PROFESSIONNEL) ---
st.markdown("""
    <style>
    /* Arrière-plan global en dégradé de bleu profond */
    .stApp {
        background: linear-gradient(135deg, #0B172A 0%, #102A43 100%);
        color: #F0F4F8;
    }
    
    /* Sidebar avec un bleu plus sombre */
    [data-testid="stSidebar"] {
        background-color: #050E1B !important;
        border-right: 1px solid #1B3A57;
    }

    /* Style des cartes de KPIs (Bleu Steel) */
    .stMetric {
        background-color: #16243A;
        padding: 25px;
        border-radius: 18px;
        border: 1px solid #243B53;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        transition: transform 0.2s;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        border-color: #00D1FF;
    }
    
    [data-testid="stMetricValue"] {
        color: #00D1FF !important;
        font-family: 'Inter', sans-serif;
    }

    /* Conteneurs de sections */
    .section-container {
        background-color: rgba(22, 36, 58, 0.8);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #334E68;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    /* Titre Principal avec effet néon bleu */
    .main-title {
        font-size: 40px;
        font-weight: 800;
        color: #FFFFFF;
        text-shadow: 0 0 15px rgba(0, 209, 255, 0.3);
        margin-bottom: 25px;
    }

    /* Badges ABC */
    .badge-a { background-color: #00FFC2; color: #002D24; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-b { background-color: #FFD700; color: #332B00; padding: 4px 10px; border-radius: 6px; font-weight: bold; }
    .badge-c { background-color: #FF6B6B; color: #FFFFFF; padding: 4px 10px; border-radius: 6px; font-weight: bold; }

    /* Tables de données */
    .stDataFrame {
        border: 1px solid #334E68;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE CALCUL ---
def perform_analytics(df):
    df['Valeur_Annuelle'] = df['Demande_Annuelle'] * df['Prix_Unitaire']
    df['Q_Economique'] = np.sqrt((2 * df['Demande_Annuelle'] * df['Cout_Commande']) / df['Cout_Stockage_Unitaire'].replace(0, np.nan))
    df['Q_Economique'] = df['Q_Economique'].fillna(0).round(0)
    df['Commandes_Par_An'] = (df['Demande_Annuelle'] / df['Q_Economique'].replace(0, np.nan)).fillna(0).round(1)
    df['Rotation_Jours'] = (365 / df['Commandes_Par_An'].replace(0, np.nan)).fillna(0).round(0)
    
    df = df.sort_values(by='Valeur_Annuelle', ascending=False)
    total_val = df['Valeur_Annuelle'].sum()
    df['Part_Contribution'] = (df['Valeur_Annuelle'] / total_val) * 100
    df['Cumul_Pourcentage'] = df['Part_Contribution'].cumsum()
    
    def classify(x):
        if x <= 80: return 'A'
        elif x <= 95: return 'B'
        else: return 'C'
    df['Classe_ABC'] = df['Cumul_Pourcentage'].apply(classify)
    return df

# --- INITIALISATION DATA ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Article_ID': ['ART-101', 'ART-202', 'ART-303', 'ART-404', 'ART-505', 'ART-606', 'ART-707', 'ART-808'],
        'Nom_Article': ['Moteur V6', 'Transmission Pro', 'Injecteur Fuel', 'Plaquettes Frein', 'Filtre Huile', 'Phare LED', 'Bougie Allumage', 'Filtre Air'],
        'Demande_Annuelle': [450, 280, 5200, 1800, 9500, 1100, 14000, 8200],
        'Cout_Commande': [120, 180, 40, 25, 15, 75, 10, 18],
        'Cout_Stockage_Unitaire': [45.0, 75.0, 4.5, 3.8, 1.2, 10.5, 0.4, 1.1],
        'Prix_Unitaire': [1150, 2300, 82, 42, 11, 145, 7, 14]
    })

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color: #00D1FF;'>OptiStock Pro</h2>", unsafe_allow_html=True)
    menu = st.radio("Menu Principal", ["Dashboard", "Édition Données", "Analyse EOQ", "Classement ABC", "Décisions"])
    st.divider()
    st.write(f"🌍 Session: {datetime.now().strftime('%d/%m/%Y')}")

df_proc = perform_analytics(st.session_state.data)

# --- PAGE: DASHBOARD ---
if menu == "Dashboard":
    st.markdown('<h1 class="main-title">Synthèse des Stocks</h1>', unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Articles", len(df_proc))
    c2.metric("Valeur Totale", f"{df_proc['Valeur_Annuelle'].sum():,.0f} €")
    c3.metric("Commandes/An", f"{df_proc['Commandes_Par_An'].mean():.1f}")
    c4.metric("Couverture A", f"{df_proc[df_proc['Classe_ABC'] == 'A']['Part_Contribution'].sum():.1f}%")

    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader("Performance par Article")
        fig = px.bar(df_proc, x='Nom_Article', y='Valeur_Annuelle', color='Classe_ABC',
                     color_discrete_map={'A':'#00FFC2', 'B':'#FFD700', 'C':'#FF6B6B'})
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.subheader("Répartition Valeur")
        fig_pie = px.pie(df_proc, values='Valeur_Annuelle', names='Classe_ABC', hole=0.5,
                         color='Classe_ABC', color_discrete_map={'A':'#00FFC2', 'B':'#FFD700', 'C':'#FF6B6B'})
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: CLASSEMENT ABC (Style de la photo) ---
elif menu == "Classement ABC":
    st.markdown('<h1 class="main-title">Classement ABC</h1>', unsafe_allow_html=True)
    
    for cls in ['A', 'B', 'C']:
        items = df_proc[df_proc['Classe_ABC'] == cls]
        badge_class = f"badge-{cls.lower()}"
        with st.expander(f"Classe {cls} - {len(items)} Articles", expanded=(cls=='A')):
            # On arrondit pour un look plus propre comme sur l'image
            st.table(items[['Nom_Article', 'Valeur_Annuelle', 'Part_Contribution', 'Cumul_Pourcentage']].round(2))

# --- PAGE: ÉDITION ---
elif menu == "Édition Données":
    st.markdown('<h1 class="main-title">Base de Données</h1>', unsafe_allow_html=True)
    edited = st.data_editor(st.session_state.data, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Sauvegarder"):
        st.session_state.data = edited
        st.success("Données enregistrées !")

# --- PAGE: EOQ ---
elif menu == "Analyse EOQ":
    st.markdown('<h1 class="main-title">Optimisation Wilson (EOQ)</h1>', unsafe_allow_html=True)
    st.dataframe(df_proc[['Nom_Article', 'Q_Economique', 'Commandes_Par_An', 'Rotation_Jours']].round(1), use_container_width=True)

# --- PAGE: DECISIONS ---
elif menu == "Décisions":
    st.markdown('<h1 class="main-title">Insights Stratégiques</h1>', unsafe_allow_html=True)
    st.info("💡 Conseil : Les articles de Classe A doivent être vérifiés de manière hebdomadaire.")
    st.warning(f"L'article {df_proc.iloc[0]['Nom_Article']} demande une attention particulière (Top 1 valeur).")
