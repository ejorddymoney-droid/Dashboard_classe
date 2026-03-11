import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="OptiStock Pro | Dashboard Supply Chain",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DESIGN SYSTEM (CSS PERSONNALISÉ) ---
st.markdown("""
    <style>
    /* Fond principal sombre */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
    }
    
    /* Style des cartes de KPIs */
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #00D1FF !important;
    }
    
    .stMetric {
        background-color: #1C2128;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Conteneurs de sections */
    .section-container {
        background-color: #161B22;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #30363D;
        margin-bottom: 20px;
    }

    /* Titres personnalisés */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 30px;
        background: -webkit-linear-gradient(#fff, #888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Badges ABC */
    .badge {
        padding: 4px 12px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 12px;
    }
    .badge-a { background-color: #00FFC2; color: #000; }
    .badge-b { background-color: #FFD700; color: #000; }
    .badge-c { background-color: #FF6B6B; color: #fff; }

    /* Boutons */
    .stButton>button {
        border-radius: 10px;
        background-color: #00D1FF;
        color: black;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00A3C7;
        box-shadow: 0 0 15px rgba(0, 209, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE CALCUL (ENGINE) ---
def perform_analytics(df):
    # 1. Valeur de Consommation Annuelle
    df['Valeur_Annuelle'] = df['Demande_Annuelle'] * df['Prix_Unitaire']
    
    # 2. Formule de Wilson (EOQ)
    # EOQ = sqrt( (2 * D * S) / H )
    df['Q_Economique'] = np.sqrt((2 * df['Demande_Annuelle'] * df['Cout_Commande']) / df['Cout_Stockage_Unitaire'].replace(0, np.nan))
    df['Q_Economique'] = df['Q_Economique'].fillna(0).round(0)
    
    # 3. Fréquence et temps
    df['Commandes_Par_An'] = (df['Demande_Annuelle'] / df['Q_Economique'].replace(0, np.nan)).fillna(0).round(1)
    df['Rotation_Jours'] = (365 / df['Commandes_Par_An'].replace(0, np.nan)).fillna(0).round(0)
    
    # 4. Analyse de Pareto (ABC)
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

# --- DONNÉES INITIALES ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Article_ID': ['ART-101', 'ART-202', 'ART-303', 'ART-404', 'ART-505', 'ART-606', 'ART-707', 'ART-808'],
        'Nom_Article': ['Moteur V6', 'Transmission Pro', 'Injecteur Fuel', 'Plaquettes Frein', 'Filtre Huile', 'Phare LED', 'Bougie Allumage', 'Filtre Air'],
        'Demande_Annuelle': [450, 280, 5200, 1800, 9500, 1100, 14000, 8200],
        'Cout_Commande': [120, 180, 40, 25, 15, 75, 10, 18],
        'Cout_Stockage_Unitaire': [45.0, 75.0, 4.5, 3.8, 1.2, 10.5, 0.4, 1.1],
        'Prix_Unitaire': [1150, 2300, 82, 42, 11, 145, 7, 14]
    })

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3061/3061341.png", width=80)
    st.markdown("### OptiStock Pro `v2.1`")
    st.info(f"Heure système : {datetime.now().strftime('%H:%M')}")
    
    menu = st.radio(
        "Navigation",
        ["Tableau de Bord", "Données Brutes", "Analyse EOQ", "Analyse Pareto", "Insights Stratégiques"]
    )
    
    st.divider()
    if st.button("🔄 Réinitialiser"):
        st.session_state.clear()
        st.rerun()

# Calcul des données traitées
df_proc = perform_analytics(st.session_state.data)

# --- PAGES ---

if menu == "Tableau de Bord":
    st.markdown('<h1 class="main-title">Aperçu Exécutif</h1>', unsafe_allow_html=True)
    
    # KPIs Top Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Articles", len(df_proc))
    with c2:
        st.metric("Valeur Stock Annuel", f"{df_proc['Valeur_Annuelle'].sum():,.0f} €")
    with c3:
        st.metric("Commandes Moy/An", f"{df_proc['Commandes_Par_An'].mean():.1f}")
    with c4:
        a_val = df_proc[df_proc['Classe_ABC'] == 'A']['Part_Contribution'].sum()
        st.metric("Poids Classe A", f"{a_val:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.subheader("Courbe de Pareto (ABC)")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df_proc['Nom_Article'], y=df_proc['Valeur_Annuelle'], name="Valeur (€)", marker_color='#00D1FF'))
        fig.add_trace(go.Scatter(x=df_proc['Nom_Article'], y=df_proc['Cumul_Pourcentage'], name="% Cumulé", yaxis="y2", line=dict(color='#00FFC2', width=3)))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Valeur de Consommation"),
            yaxis2=dict(title="% Cumulé", overlaying="y", side="right", range=[0, 105]),
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("Répartition ABC")
        counts = df_proc['Classe_ABC'].value_counts().reset_index()
        fig_pie = px.pie(counts, values='count', names='Classe_ABC', hole=0.6,
                         color='Classe_ABC', color_discrete_map={'A':'#00FFC2', 'B':'#FFD700', 'C':'#FF6B6B'})
        fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

elif menu == "Données Brutes":
    st.markdown('<h1 class="main-title">Gestion des Données</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="section-container">
        Modifiez les valeurs directement dans le tableau ci-dessous. Le système recalculera les métriques instantanément.
    </div>
    """, unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        st.session_state.data,
        num_rows="dynamic",
        use_container_width=True,
        key="editor"
    )
    
    if st.button("Enregistrer les modifications"):
        st.session_state.data = edited_df
        st.success("Base de données mise à jour !")
        st.rerun()

elif menu == "Analyse EOQ":
    st.markdown('<h1 class="main-title">Optimisation EOQ (Wilson)</h1>', unsafe_allow_html=True)
    
    st.markdown("### Quantité Économique de Commande par Article")
    fig_eoq = px.bar(df_proc, x='Nom_Article', y='Q_Economique', color='Q_Economique',
                     color_continuous_scale='GnBu', labels={'Q_Economique': 'Quantité'})
    fig_eoq.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_eoq, use_container_width=True)
    
    st.dataframe(df_proc[['Nom_Article', 'Demande_Annuelle', 'Q_Economique', 'Commandes_Par_An', 'Rotation_Jours']], 
                 use_container_width=True)

elif menu == "Analyse Pareto":
    st.markdown('<h1 class="main-title">Classement ABC</h1>', unsafe_allow_html=True)
    
    # Affichage stylisé
    for cls in ['A', 'B', 'C']:
        items = df_proc[df_proc['Classe_ABC'] == cls]
        with st.expander(f"Classe {cls} - {len(items)} Articles", expanded=(cls=='A')):
            st.table(items[['Nom_Article', 'Valeur_Annuelle', 'Part_Contribution', 'Cumul_Pourcentage']])

elif menu == "Insights Stratégiques":
    st.markdown('<h1 class="main-title">Analyses & Décisions</h1>', unsafe_allow_html=True)
    
    top_article = df_proc.iloc[0]
    best_rotation = df_proc.loc[df_proc['Rotation_Jours'].idxmin()]
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"""
        <div class="section-container">
            <h3 style="color:#00FFC2">⚠️ Priorité d'Approvisionnement</h3>
            L'article <b>{top_article['Nom_Article']}</b> représente à lui seul <b>{top_article['Part_Contribution']:.1f}%</b> 
            de la valeur totale de consommation. Un stock de sécurité rigoureux est impératif pour éviter les ruptures.
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="section-container">
            <h3 style="color:#00D1FF">🔄 Flux Tendus</h3>
            <b>{best_rotation['Nom_Article']}</b> nécessite une commande tous les <b>{best_rotation['Rotation_Jours']} jours</b>. 
            Une automatisation des commandes (EDI) est recommandée pour cet article.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Score de Santé de l'Inventaire")
    score = 88
    st.progress(score / 100)
    st.write(f"Optimisation globale du catalogue : {score}%")
