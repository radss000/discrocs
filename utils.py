import pandas as pd
import joblib

def prepare_data(file_path):
    # Cette fonction devrait préparer vos données pour le ML
    # Pour cet exemple, chargeons simplement le fichier CSV/JSON
    return pd.read_csv(file_path)  # ou pd.read_json(file_path) selon votre cas

def load_ml_model(model_path):
    # Charger et retourner le modèle ML
    return joblib.load(model_path)
