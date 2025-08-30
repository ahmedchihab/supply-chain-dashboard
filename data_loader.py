import pandas as pd

# 🔹 Charger le CSV brut
file_path = r"C:\Users\Galaxy\Downloads\DataCoSupplyChainDataset_clean.csv"
df = pd.read_csv(file_path)

# ================================
# 🔹 Renommer les colonnes importantes
df.rename(columns={
    'order date (DateOrders)': 'Order Date',
    'shipping date (DateOrders)': 'Shipping Date'
}, inplace=True)

# ================================
# 🔹 Convertir en datetime
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Shipping Date'] = pd.to_datetime(df['Shipping Date'], errors='coerce')

# ================================
# 🔹 Nettoyage des colonnes inutiles
# Supprimer la colonne Email
if 'Customer Email' in df.columns:
    df.drop(columns=['Customer Email'], inplace=True)

# ================================
# 🔹 Nettoyage des doublons et valeurs manquantes
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)  # supprime toutes les lignes contenant NaN

# ================================
# 🔹 Extraction mois et année
df['Month'] = df['Order Date'].dt.month
df['Year'] = df['Order Date'].dt.year

# ================================
# 🔹 Correction des codes postaux erronés
# On peut supprimer ou remplacer les codes postaux trop petits/invalides
df = df[df['Customer Zipcode'] > 1000]  # exemple simple pour enlever les codes < 1000

# ================================
# 🔹 Conversion des colonnes numériques si nécessaire
numeric_cols = [
    'Days for shipping (real)', 'Days for shipment (scheduled)',
    'Benefit per order', 'Sales per customer', 'Late_delivery_risk',
    'Order Item Discount', 'Order Item Discount Rate',
    'Order Item Product Price', 'Order Item Profit Ratio',
    'Order Item Quantity', 'Sales', 'Order Item Total', 'Order Profit Per Order',
    'Product Price'
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')


# ================================
# 🔹 Sauvegarde du nouveau fichier propre
output_path = r"C:\Users\Galaxy\Downloads\DataCoSupplyChainDataset_clean_ready.csv"
df.to_csv(output_path, index=False)

print(f"✅ Fichier nettoyé et sauvegardé ici : {output_path}")
