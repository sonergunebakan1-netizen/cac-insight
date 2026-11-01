# 📊 CAC Insight

**La santé financière des entreprises du CAC 40, notée comme en banque.**

👉 **Application en ligne : [cac-insight-m2.streamlit.app](https://cac-insight-m2.streamlit.app/)**

Projet de groupe *Pairagogie*, cours **AI & Automation**, Master 2 Analyse financière internationale.

---

## 🎯 Le projet en bref

**Problématique métier :** comparer la santé financière de dizaines d'entreprises demande de récupérer les comptes à la main, de calculer les ratios un par un, puis de rédiger une synthèse. C'est long, répétitif et difficile à faire à grande échelle.

**Notre solution :** un outil qui automatise toute la chaîne d'analyse. On tape le nom d'une entreprise du CAC 40 et on obtient immédiatement :

- 🎯 une **note bancaire de A à E** et un score sur 100 ;
- 📋 ses **ratios financiers** comparés à la médiane du CAC 40, avec un code couleur ;
- 🧩 son **profil financier**, déterminé par un algorithme de Machine Learning ;
- 🤖 un **commentaire d'analyste** rédigé par une IA générative.

---

## ⚙️ Comment ça marche

```
 Yahoo Finance        pandas            scikit-learn         Grille            Gemini            Streamlit
┌────────────┐   ┌─────────────┐   ┌───────────────┐   ┌────────────┐   ┌──────────────┐   ┌─────────────┐
│ 1. Collecte│ → │ 2. Ratios & │ → │ 3. Profils ML │ → │ 4. Score & │ → │ 5. Commentaire│ → │ 6. Appli    │
│ des comptes│   │  nettoyage  │   │   (K-Means)   │   │  note A→E  │   │   IA         │   │  en ligne   │
└────────────┘   └─────────────┘   └───────────────┘   └────────────┘   └──────────────┘   └─────────────┘
```

| Étape | Ce qui se passe | Outil |
|---|---|---|
| 1. Collecte | Récupération automatique des comptes annuels de 34 entreprises | API Yahoo Finance (`yfinance`) |
| 2. Préparation | Nettoyage des données et calcul de 9 ratios | `pandas`, `numpy` |
| 3. Machine Learning | Regroupement des entreprises aux profils similaires | K-Means (`scikit-learn`) |
| 4. Automatisation | Notation selon une grille inspirée des scorecards bancaires | Python |
| 5. IA générative | Rédaction d'un commentaire à partir des seuls chiffres calculés | Gemini (Google) |
| 6. Restitution | Tableau de bord interactif accessible par un lien | Streamlit |

**Choix d'architecture :** le traitement lourd (collecte, calculs, IA) est fait **une fois** dans le notebook. Il produit un fichier `cac40_scoring.csv` que l'application se contente de lire. L'application est donc **instantanée** et ne dépend d'aucune API pendant son utilisation.

---

## 📁 Contenu du dépôt

| Fichier | Rôle |
|---|---|
| `CAC_Insight.ipynb` | Notebook complet et commenté : toute la démarche, de la collecte à l'export |
| `app.py` | Code de l'application Streamlit |
| `cac40_scoring.csv` | Données finales : ratios, scores, notes, profils et commentaires |
| `requirements.txt` | Bibliothèques nécessaires à l'application |

---

## 📖 Dictionnaire des données

### Ratios calculés

| Ratio | Formule | Ce qu'il mesure | Lecture |
|---|---|---|---|
| Marge nette | Résultat net / Chiffre d'affaires | Rentabilité finale | Plus haut = mieux |
| Marge EBIT | EBIT / Chiffre d'affaires | Rentabilité de l'activité, avant frais financiers et impôts | Plus haut = mieux |
| ROE | Résultat net / Capitaux propres | Ce que rapporte 1 € investi par les actionnaires | Plus haut = mieux |
| ROA | Résultat net / Total actif | Rentabilité de l'ensemble des actifs | Plus haut = mieux |
| Gearing | Dette totale / Capitaux propres | Niveau d'endettement | **Plus bas = mieux** |
| Liquidité générale | Actif courant / Passif courant | Capacité à payer les dettes à moins d'un an | Supérieur à 1 = confortable |
| Couverture des intérêts | EBIT / Charges d'intérêts | Combien de fois le résultat couvre les intérêts | Plus haut = mieux |
| PER | Capitalisation boursière / Résultat net | Valorisation par le marché | Informatif |
| Croissance du CA | CA N / CA N-1 − 1 | Dynamique commerciale | Plus haut = mieux |

### Colonnes du fichier `cac40_scoring.csv`

| Colonnes | Contenu |
|---|---|
| `Ticker`, `Entreprise`, `Exercice` | Identification de l'entreprise et année des comptes |
| `CA`, `CA_N-1`, `Resultat_net`, `EBIT`, `Charges_interets`, `Capitaux_propres`, `Total_actif`, `Dette_totale`, `Actif_courant`, `Passif_courant`, `Capitalisation` | Données comptables brutes (en devise de publication) |
| `Marge_nette` … `Croissance_CA` | Les 9 ratios ci-dessus |
| `Perte` | Vrai si l'entreprise a un résultat net négatif |
| `Pts_*` | Points obtenus pour chaque ratio dans la grille |
| `Score`, `Note`, `Appreciation` | Score sur 100, note de A à E et appréciation |
| `Cluster`, `Profil` | Groupe trouvé par le K-Means et son nom |
| `Commentaire` | Commentaire d'analyste généré par l'IA |

---

## 🏦 La grille de notation

| Pilier | Ratio | Points max |
|---|---|---|
| Rentabilité | Marge EBIT | 20 |
| Rentabilité | ROE | 15 |
| Solvabilité | Gearing (capitaux propres négatifs = 0 point) | 20 |
| Solvabilité | Couverture des intérêts | 15 |
| Liquidité | Liquidité générale | 15 |
| Dynamique | Croissance du CA | 15 |
| | **Total** | **100** |

| Note | Score | Appréciation |
|---|---|---|
| 🟢 A | 80 et plus | Excellent |
| 🟩 B | 65 à 79 | Solide |
| 🟡 C | 50 à 64 | Correct |
| 🟠 D | 35 à 49 | Fragile |
| 🔴 E | moins de 35 | Risqué |

Le PER est affiché mais **n'entre pas dans le score** : une banque évalue la capacité à rembourser, pas la valorisation boursière.

---

## 🔁 Reproduire le projet

1. Ouvrir `CAC_Insight.ipynb` dans [Google Colab](https://colab.research.google.com/).
2. Créer une clé API Gemini gratuite sur [aistudio.google.com](https://aistudio.google.com/) et l'ajouter dans les **Secrets** de Colab (icône 🔑) sous le nom `GEMINI_API_KEY`.
3. Lancer **Exécution → Tout exécuter** (environ 5 minutes).
4. Déposer le nouveau `cac40_scoring.csv` dans ce dépôt : l'application se met à jour automatiquement.

**Mise à jour conseillée :** une fois par an, en mai, après la publication des comptes annuels.

---

## ⚠️ Limites

- **Périmètre :** banques, assurances et foncières sont exclues, car leurs bilans ne sont pas comparables.
- **Données :** Yahoo Finance peut contenir des imprécisions ; un ratio atypique doit être vérifié dans le rapport annuel.
- **Grille unique :** les mêmes seuils s'appliquent à tous les secteurs.
- **Machine Learning :** le K-Means décrit des profils, il ne prédit rien.
- **IA générative :** le commentaire peut contenir des imprécisions et doit être relu par un analyste.

## 🚀 Pistes d'amélioration

- Étendre l'analyse à l'Euro Stoxx 50 et sur plusieurs années.
- Adapter les seuils de la grille par secteur.
- Ajouter un modèle de probabilité de défaut.
- Automatiser la mise à jour annuelle (GitHub Actions).

---

*Outil pédagogique. Ce n'est ni une notation officielle, ni un conseil en investissement.*
