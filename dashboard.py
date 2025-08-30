# dashboard_ultra_full.py
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ================================
# 🔹 Paramètres de la page
# ================================
st.set_page_config(page_title="Ultra Dashboard Supply Chain", layout="wide", page_icon="🚀")

# ================================
# 🔹 Charger les données
# ================================
DATA_PATH = r"https://drive.google.com/uc?export=download&id=1fZlS4aDC5i7dqFvihM_ap7yfNcuqzDWP"

df = pd.read_csv(DATA_PATH)

# Convertir les dates
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Shipping Date'] = pd.to_datetime(df['Shipping Date'], errors='coerce')

# ================================
# 🔹 Thème sombre / clair
# ================================
theme = st.sidebar.radio("Choisir thème :", ["Clair", "Sombre"])
if theme == "Sombre":
    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: #0E1117;
            color: white;
        }
        .stSidebar {background-color: #111827;}
        </style>
        """, unsafe_allow_html=True
    )

# ================================
# 🔹 Sidebar - Navigation
# ================================
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Choisir la page :", [
    "Accueil", "Ventes & Produits", "Clients", "Supply Chain", "Géographie", "Insights"
])

# ================================
# 🔹 Sidebar - Filtres globaux
# ================================
st.sidebar.header("Filtres globaux")

year_filter = st.sidebar.multiselect("Année :", sorted(df['Year'].unique()), default=sorted(df['Year'].unique()))
city_filter = st.sidebar.multiselect("Ville :", df['Customer City'].unique(), default=df['Customer City'].unique())
segment_filter = st.sidebar.multiselect("Segment client :", df['Customer Segment'].unique(),
                                        default=df['Customer Segment'].unique())
category_filter = st.sidebar.multiselect("Catégorie produit :", df['Category Name'].unique(),
                                         default=df['Category Name'].unique())

# Bouton Reset filtres
if st.sidebar.button("🔄 Réinitialiser filtres"):
    year_filter = sorted(df['Year'].unique())
    city_filter = df['Customer City'].unique()
    segment_filter = df['Customer Segment'].unique()
    category_filter = df['Category Name'].unique()

df_filtered = df[
    (df['Year'].isin(year_filter)) &
    (df['Customer City'].isin(city_filter)) &
    (df['Customer Segment'].isin(segment_filter)) &
    (df['Category Name'].isin(category_filter))
    ]

# ================================
# 🔹 Bouton Export CSV
# ================================
csv_export = df_filtered.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="💾 Export CSV",
    data=csv_export,
    file_name='filtered_data.csv',
    mime='text/csv'
)

# ================================
# 🔹 Pages
# ================================

# ---------------- Accueil ----------------
if page == "Accueil":
    st.markdown("<h1 style='text-align:center;color:#4B0082;'>📊 Dashboard Global Ultra</h1>", unsafe_allow_html=True)

    total_revenue = df_filtered['Sales'].sum()
    total_orders = df_filtered['Order Id'].nunique()
    total_customers = df_filtered['Customer Id'].nunique()
    avg_delivery_days = df_filtered['Days for shipping (real)'].mean()
    late_percentage = df_filtered['Late_delivery_risk'].mean() * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("💰 CA total", f"${total_revenue:,.0f}")
    col2.metric("📦 Commandes", f"{total_orders:,}")
    col3.metric("👥 Clients", f"{total_customers:,}")
    col4.metric("⏱️ Délai moyen", f"{avg_delivery_days:.2f} jours")
    col5.metric("🚨 % Retards", f"{late_percentage:.2f}%")

    # Heatmap CA par mois et catégorie
    pivot = df_filtered.pivot_table(index='Month', columns='Category Name', values='Sales', aggfunc='sum').fillna(0)
    fig_heat = px.imshow(pivot, text_auto=True, aspect="auto", color_continuous_scale="Viridis",
                         title="🔥 Heatmap CA par Mois et Catégorie")
    st.plotly_chart(fig_heat, use_container_width=True)

    # Scatter avancé : Livraison vs Profit
    fig_scatter = px.scatter(df_filtered, x='Days for shipping (real)', y='Order Item Profit Ratio',
                             size='Sales', color='Category Name', hover_data=['Product Name'],
                             title="📍 Livraison vs Profit par produit")
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------- Ventes & Produits ----------------
elif page == "Ventes & Produits":
    st.title("📈 Analyse Ventes & Produits Ultra")

    top_products = df_filtered.groupby("Product Name")['Order Item Quantity'].sum().sort_values(ascending=False).head(
        10).reset_index()
    fig_products = px.bar(top_products, x="Order Item Quantity", y="Product Name", orientation="h",
                          color="Order Item Quantity", color_continuous_scale="Plasma", text_auto=True,
                          title="🔥 Top 10 Produits par Quantité")
    st.plotly_chart(fig_products, use_container_width=True)

    st.subheader("CA par Catégorie")
    cat_sales = df_filtered.groupby("Category Name")['Sales'].sum().reset_index()
    fig_cat = px.pie(cat_sales, names='Category Name', values='Sales', title="📊 Répartition CA par Catégorie")
    st.plotly_chart(fig_cat, use_container_width=True)

# ---------------- Clients ----------------
elif page == "Clients":
    st.title("👥 Analyse Clients Ultra")

    segment_count = df_filtered['Customer Segment'].value_counts().reset_index()
    segment_count.columns = ['Segment', 'Count']
    fig_segment = px.pie(segment_count, names='Segment', values='Count', title="📊 Répartition par Segment")
    st.plotly_chart(fig_segment, use_container_width=True)

    st.subheader("Top Villes par CA")
    city_sales = df_filtered.groupby("Customer City")['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
    fig_city = px.bar(city_sales, x='Sales', y='Customer City', orientation='h', color='Sales', text_auto=True,
                      title="🏙️ Top Villes par CA")
    st.plotly_chart(fig_city, use_container_width=True)

# ---------------- Supply Chain ----------------
elif page == "Supply Chain":
    st.title("🚚 Analyse Supply Chain Ultra")

    st.subheader("Délais réels vs prévus")
    df_sc = df_filtered[['Days for shipment (scheduled)', 'Days for shipping (real)']]
    fig_sc = px.box(df_sc, points="all", title="📦 Distribution des délais")
    st.plotly_chart(fig_sc, use_container_width=True)

    st.subheader("Top 10 Retards")
    late_orders = df_filtered.sort_values('Days for shipping (real)', ascending=False).head(10)
    fig_late = px.bar(late_orders, x='Days for shipping (real)', y='Order Id', orientation='h', text_auto=True,
                      title="🚨 Top 10 Commandes en Retard")
    st.plotly_chart(fig_late, use_container_width=True)

# ---------------- Géographie ----------------
elif page == "Géographie":
    st.title("🌍 Analyse Géographique Ultra")

    city_sales = df_filtered.groupby("Customer City")['Sales'].sum().reset_index()
    fig_map = px.scatter_geo(city_sales, locations="Customer City", locationmode="USA-states",
                             size="Sales", color="Sales", hover_name="Customer City",
                             projection="natural earth", title="🗺️ CA par Ville")
    st.plotly_chart(fig_map, use_container_width=True)

# ---------------- Insights ----------------
elif page == "Insights":
    st.title("💡 Insights & Recommandations Ultra")

    st.markdown("""
    - Identifier les produits à fort potentiel mais faible stock  
    - Régions avec retards fréquents → prioriser la logistique  
    - Segments clients à forte valeur → actions marketing  
    - Visualisation des anomalies de livraison  
    - Analyse des profits par catégorie et produit
    """)

    st.subheader("Top Profits par Produit")
    profit_products = df_filtered.groupby("Product Name")['Order Item Profit Ratio'].sum().sort_values(
        ascending=False).head(10).reset_index()
    fig_profit = px.bar(profit_products, x='Order Item Profit Ratio', y='Product Name', orientation='h',
                        color='Order Item Profit Ratio', text_auto=True, title="💵 Top Profits Produits")
    st.plotly_chart(fig_profit, use_container_width=True)

