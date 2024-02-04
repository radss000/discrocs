import pandas as pd
import json
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error




def load_and_process_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    records = [record for record in data.values()]
    df = pd.DataFrame(records)
    print(df)
    print("Colonnes chargées:", df.columns) 
    return df


def automate_ml_process(file_path, output_file_path):
    df_records = load_and_process_json(file_path)
    print(df_records.columns)
    if 'wantlist' not in df_records.columns:
        df_records['wantlist'] = 0
    else:
        # Si 'wantlist' existe, remplacez les valeurs NaN par 0
        df_records['wantlist'] = df_records['wantlist'].fillna(0)
    # Ajout et calcul de nouvelles caractéristiques si nécessaire
    df_records['wantlist_to_collection_ratio'] = df_records['wantlist'] / df_records['collection'].replace(0, 1) # Éviter la division par zéro
    df_records['wantlist_to_collection_ratio'].replace([float('inf'), -float('inf')], 9999, inplace=True)

    # Sélection des caractéristiques pour la régression
    X = df_records[['collection', 'lowest_price', 'rating', 'release_year', 'wantlist_to_collection_ratio']]
    y = df_records['rating']  # Exemple de cible; ajustez selon votre besoin

    # Séparation des données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalisation des données
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Construction et entraînement du modèle
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train_scaled, y_train)

    # Prédictions et évaluation
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Mean Squared Error: {mse}")

    # Exporter les résultats dans un fichier CSV
    df_records['predicted_rating'] = model.predict(scaler.transform(X))  # Prédiction sur l'ensemble des données
    df_records.to_csv(output_file_path, index=False)
    print(f"Les résultats ont été enregistrés dans {output_file_path}")
# Exemple d'utilisation
#file_path = r"C:\Users\radia\Downloads\discogs-voodoo-vinylshops-default-rtdb-export.json"
#output_file_path = r"C:\Users\radia\Downloads\Discogs_DB_Credentials\discogs-entrall-ukraine.csv"

