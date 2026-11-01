import html
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
st.set_page_config(page_title="CAC Insight", page_icon="📊", layout="wide")

@st.cache_data
def charger():
    return pd.read_csv("cac40_scoring.csv")

df = charger()
df = df.sort_values("Score", ascending=False).reset_index(drop=True)
df["Rang"] = df.index + 1
NB = len(df)

COULEUR_NOTE = {"A": "#1a9850", "B": "#66bd63", "C": "#e6b800", "D": "#f46d43", "E": "#d73027"}
EMOJI_NOTE = {"A": "🟢", "B": "🟩", "C": "🟡", "D": "🟠", "E": "🔴"}
DEVISE_USD = ["MT.AS", "STMPA.PA"]

SECTEURS = {
    "Accor": "Hôtellerie", "Air Liquide": "Gaz industriels", "Airbus": "Aéronautique",
    "ArcelorMittal": "Sidérurgie", "Bouygues": "BTP & Télécoms", "Bureau Veritas": "Inspection & certification",
    "Capgemini": "Services informatiques", "Carrefour": "Grande distribution", "Danone": "Agroalimentaire",
    "Dassault Systèmes": "Logiciels", "Edenred": "Services aux entreprises", "Engie": "Énergie",
    "EssilorLuxottica": "Optique", "Eurofins": "Laboratoires d'analyse", "Hermès": "Luxe",
    "Kering": "Luxe", "L'Oréal": "Cosmétiques", "Legrand": "Équipements électriques",
    "LVMH": "Luxe", "Michelin": "Pneumatiques", "Orange": "Télécoms",
    "Pernod Ricard": "Vins & spiritueux", "Publicis": "Communication", "Renault": "Automobile",
    "Safran": "Aéronautique", "Saint-Gobain": "Matériaux", "Sanofi": "Pharmacie",
    "Schneider Electric": "Équipements électriques", "Stellantis": "Automobile",
    "STMicroelectronics": "Semi-conducteurs", "Thales": "Défense & aéronautique",
    "TotalEnergies": "Énergie", "Veolia": "Environnement", "Vinci": "BTP & Concessions",
}

# (colonne, titre, emoji, format, colonne points, points max, explication simple)
RATIOS = [
    ("Marge_EBIT", "Marge opérationnelle", "💰", "pct", "Pts_Marge_EBIT", 20,
     "Part des ventes qui reste après les coûts d'exploitation"),
    ("ROE", "Rentabilité des fonds propres", "📈", "pct", "Pts_ROE", 15,
     "Ce que rapporte 1 € investi par les actionnaires"),
    ("Gearing", "Endettement", "🏦", "x", "Pts_Gearing", 20,
     "Dette / capitaux propres — plus c'est bas, mieux c'est"),
    ("Couverture_int", "Couverture des intérêts", "🛡️", "fois", "Pts_Couverture", 15,
     "Combien de fois le résultat couvre les intérêts de la dette"),
    ("Liquidite", "Liquidité", "💧", "x", "Pts_Liquidite", 15,
     "Capacité à payer les dettes à court terme"),
    ("Croissance_CA", "Croissance des ventes", "🚀", "pct", "Pts_Croissance", 15,
     "Évolution du chiffre d'affaires sur un an"),
]
MEDIANES = df[[r[0] for r in RATIOS]].median()

def fmt(v, f):
    if pd.isna(v):
        return "n.d."
    if f == "pct":
        return f"{v * 100:.1f} %"
    if f == "fois":
        return f"{v:.1f}x"
    return f"{v:.2f}"

def couleur_points(pts, maxi):
    part = pts / maxi
    if part >= 0.7:
        return "#1a9850"
    if part >= 0.4:
        return "#f39c12"
    return "#d73027"

def mise_en_forme(texte):
    """Rend le texte de l'IA sûr et lisible dans la boîte HTML."""
    texte = html.escape(str(texte).strip())
    texte = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texte)
    return texte.replace("\n\n", "<br><br>").replace("\n", "<br>")

def commentaire_auto(r):
    """Résumé de secours si le commentaire IA est absent."""
    piliers = {
        "la rentabilité": (r["Pts_Marge_EBIT"] + r["Pts_ROE"]) / 35,
        "la solvabilité": (r["Pts_Gearing"] + r["Pts_Couverture"]) / 35,
        "la liquidité": r["Pts_Liquidite"] / 15,
        "la dynamique commerciale": r["Pts_Croissance"] / 15,
    }
    fort = max(piliers, key=piliers.get)
    faible = min(piliers, key=piliers.get)
    return (f"{r['Entreprise']} obtient la note {r['Note']} ({r['Appreciation'].lower()}) "
            f"avec un score de {int(r['Score'])}/100. Son principal point fort est {fort}, "
            f"tandis que {faible} constitue le principal point de vigilance.")

# ------------------------------------------------------------------
# Style
# ------------------------------------------------------------------
st.markdown("""
<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
.carte {border-radius: 14px; padding: 16px 18px; margin-bottom: 14px;
        background: rgba(128,128,128,0.08); border-left: 6px solid;}
.carte .titre {font-size: 0.9rem; opacity: 0.8;}
.carte .valeur {font-size: 1.8rem; font-weight: 700; margin: 2px 0;}
.carte .sous {font-size: 0.8rem; opacity: 0.7;}
.badge {display: inline-block; padding: 4px 12px; border-radius: 20px;
        background: rgba(128,128,128,0.15); font-size: 0.85rem; margin-right: 6px;}
.note {width: 120px; height: 120px; border-radius: 50%; display: flex;
       align-items: center; justify-content: center; font-size: 4rem;
       font-weight: 800; color: white; margin: auto;}
.comment {border-radius: 14px; padding: 18px 20px; background: rgba(100,140,255,0.10);
          border: 1px solid rgba(100,140,255,0.35); line-height: 1.6;}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# En-tête
# ------------------------------------------------------------------
st.title("📊 CAC Insight")
st.caption("La santé financière des entreprises du CAC 40, notée comme en banque — "
           f"comptes annuels {int(df['Exercice'].max())}")

onglet_fiche, onglet_classement, onglet_methode = st.tabs(
    ["🔎 Fiche entreprise", "🏆 Classement CAC 40", "📘 Méthodologie"])

# ------------------------------------------------------------------
# Onglet 1 : fiche entreprise
# ------------------------------------------------------------------
with onglet_fiche:
    noms = sorted(df["Entreprise"].tolist())
    choix = st.selectbox("Tape ou choisis le nom d'une entreprise",
                         noms, index=noms.index("LVMH") if "LVMH" in noms else 0)
    r = df[df["Entreprise"] == choix].iloc[0]
    couleur = COULEUR_NOTE[r["Note"]]

    st.markdown(f"## {r['Entreprise']}")
    st.markdown(
        f"<span class='badge'>🏷️ {SECTEURS.get(r['Entreprise'], 'Secteur n.d.')}</span>"
        f"<span class='badge'>📌 {r['Ticker']}</span>"
        f"<span class='badge'>🧩 Profil : {r['Profil']}</span>"
        f"<span class='badge'>🏅 {int(r['Rang'])}<sup>e</sup> sur {NB}</span>",
        unsafe_allow_html=True)
    st.write("")

    # --- Note + jauge + chiffres clés ---
    c1, c2, c3 = st.columns([1, 1.4, 1.2])
    with c1:
        st.markdown(f"<div class='note' style='background:{couleur}'>{r['Note']}</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;font-size:1.2rem;font-weight:600;"
                    f"margin-top:8px'>{r['Appreciation']}</p>", unsafe_allow_html=True)
    with c2:
        jauge = go.Figure(go.Indicator(
            mode="gauge+number", value=r["Score"],
            number={"suffix": " / 100", "font": {"size": 34}},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": couleur, "thickness": 0.3},
                   "steps": [{"range": [0, 35], "color": "rgba(215,48,39,0.25)"},
                             {"range": [35, 50], "color": "rgba(244,109,67,0.25)"},
                             {"range": [50, 65], "color": "rgba(230,184,0,0.25)"},
                             {"range": [65, 80], "color": "rgba(102,189,99,0.25)"},
                             {"range": [80, 100], "color": "rgba(26,152,80,0.25)"}]}))
        jauge.update_layout(height=220, margin=dict(l=30, r=30, t=30, b=0),
                            paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(jauge, width="stretch")
    with c3:
        devise = "$" if r["Ticker"] in DEVISE_USD else "€"
        st.metric("Chiffre d'affaires", f"{r['CA'] / 1e9:.1f} Md{devise}",
                  f"{r['Croissance_CA'] * 100:+.1f} % sur un an")
        st.metric("Capitalisation boursière",
                  f"{r['Capitalisation'] / 1e9:.1f} Md€" if pd.notna(r["Capitalisation"]) else "n.d.")
        st.metric("PER (valorisation)", "n.s. (perte)" if r["Perte"] else f"{r['PER']:.1f}")

    # --- Détail du score par pilier ---
    st.markdown("### 🧱 D'où vient la note ?")
    piliers = [
        ("Rentabilité", r["Pts_Marge_EBIT"] + r["Pts_ROE"], 35),
        ("Solvabilité", r["Pts_Gearing"] + r["Pts_Couverture"], 35),
        ("Liquidité", r["Pts_Liquidite"], 15),
        ("Dynamique", r["Pts_Croissance"], 15),
    ]
    cols = st.columns(4)
    for col, (nom, pts, maxi) in zip(cols, piliers):
        with col:
            st.markdown(f"**{nom}** — {int(pts)}/{maxi}")
            st.progress(pts / maxi)

    # --- Cartes de ratios ---
    st.markdown("### 📋 Les ratios en un coup d'œil")
    st.caption("🟢 bon   🟠 moyen   🔴 faible — comparé à la médiane du CAC 40")
    cols = st.columns(3)
    for i, (colname, titre, emoji, f, pts_col, maxi, expl) in enumerate(RATIOS):
        coul = couleur_points(r[pts_col], maxi)
        valeur = fmt(r[colname], f)
        if colname == "Gearing" and r["Capitaux_propres"] < 0:
            valeur = "Fonds propres négatifs"
        with cols[i % 3]:
            st.markdown(
                f"<div class='carte' style='border-left-color:{coul}'>"
                f"<div class='titre'>{emoji} {titre}</div>"
                f"<div class='valeur' style='color:{coul}'>{valeur}</div>"
                f"<div class='sous'>Médiane CAC 40 : {fmt(MEDIANES[colname], f)}</div>"
                f"<div class='sous'>{expl}</div></div>",
                unsafe_allow_html=True)

    # --- Commentaire IA ---
    st.markdown("### 🤖 L'avis de l'analyste IA")
    texte = r.get("Commentaire")
    if pd.isna(texte) or texte == "Commentaire indisponible.":
        texte = commentaire_auto(r)
    st.markdown(f"<div class='comment'>{mise_en_forme(texte)}</div>", unsafe_allow_html=True)
    st.caption("Commentaire rédigé par une IA générative (Gemini) à partir des seuls ratios "
               "calculés ci-dessus. À relire avec un regard d'analyste.")

# ------------------------------------------------------------------
# Onglet 2 : classement
# ------------------------------------------------------------------
with onglet_classement:
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, n in zip([c1, c2, c3, c4, c5], ["A", "B", "C", "D", "E"]):
        col.metric(f"{EMOJI_NOTE[n]} Note {n}", f"{(df['Note'] == n).sum()} entreprises")

    tableau = df[["Rang", "Entreprise", "Note", "Score", "Appreciation", "Profil"]].copy()
    tableau["Note"] = tableau["Note"].map(lambda n: f"{EMOJI_NOTE[n]} {n}")
    tableau["Secteur"] = tableau["Entreprise"].map(SECTEURS)
    st.dataframe(
        tableau[["Rang", "Entreprise", "Secteur", "Note", "Score", "Appreciation", "Profil"]],
        hide_index=True, width="stretch", height=500,
        column_config={"Score": st.column_config.ProgressColumn(
            "Score", min_value=0, max_value=100, format="%d")})

    st.markdown("### 🗺️ La carte du CAC 40 : rentabilité vs endettement")
    st.caption("Chaque point est une entreprise. En haut à gauche : rentable et peu endettée. "
               "Les couleurs sont les profils trouvés par le Machine Learning (K-Means).")
    carte = df.copy()
    carte["Marge EBIT (%)"] = carte["Marge_EBIT"] * 100
    fig = px.scatter(carte, x="Gearing", y="Marge EBIT (%)", color="Profil",
                     hover_name="Entreprise", size="Score", size_max=22,
                     hover_data={"Note": True, "Score": True, "Gearing": ":.2f",
                                 "Marge EBIT (%)": ":.1f"})
    fig.add_hline(y=0, line_color="grey", line_width=1)
    fig.update_layout(height=520, xaxis_title="Endettement (Gearing)",
                      legend_title="Profil ML", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------------
# Onglet 3 : méthodologie
# ------------------------------------------------------------------
with onglet_methode:
    st.markdown("""
### Comment ça marche ?

1. **Collecte automatique** — les comptes annuels sont récupérés via l'API Yahoo Finance.
2. **Calcul des ratios** — rentabilité, endettement, liquidité, croissance.
3. **Scoring bancaire** — chaque ratio rapporte des points selon une grille (total sur 100).
4. **Machine Learning** — un algorithme K-Means regroupe les entreprises aux profils similaires.
5. **IA générative** — un modèle Gemini rédige un commentaire à partir des seuls chiffres calculés.

### La grille de notation

| Pilier | Ratio | Points |
|---|---|---|
| Rentabilité | Marge opérationnelle (EBIT / CA) | 20 |
| Rentabilité | ROE (Résultat net / Capitaux propres) | 15 |
| Solvabilité | Gearing (Dette / Capitaux propres) | 20 |
| Solvabilité | Couverture des intérêts (EBIT / Intérêts) | 15 |
| Liquidité | Actif courant / Passif courant | 15 |
| Dynamique | Croissance du chiffre d'affaires | 15 |

**Notes :** A ≥ 80 (Excellent) · B ≥ 65 (Solide) · C ≥ 50 (Correct) · D ≥ 35 (Fragile) · E < 35 (Risqué)

Le PER est affiché à titre informatif mais n'entre pas dans le score :
une banque évalue la capacité à rembourser, pas la valorisation boursière.

### Périmètre et limites
- Banques, assurances et foncières sont exclues : leurs bilans ne sont pas comparables.
- Données Yahoo Finance, parfois incomplètes : un ratio atypique doit être vérifié dans le rapport annuel.
- Les seuils de la grille sont identiques pour tous les secteurs.
- Le commentaire IA peut contenir des imprécisions : il complète l'analyse, il ne la remplace pas.

*Outil pédagogique réalisé dans le cadre du cours AI & Automation. Ce n'est ni une notation
officielle, ni un conseil en investissement.*
""")
