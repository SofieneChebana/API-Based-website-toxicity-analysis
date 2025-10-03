import sqlite3
import pandas as pd
import re
from urllib.parse import urlparse
from utils.feature_utils import extract_features

# cette classe à pour but de nettoyer les données avant l'entrainement

def load_data_from_db(db_path: str, table_name: str) -> pd.DataFrame:
    """Connexion à la base SQLite et lecture des données"""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def clean_urls(df: pd.DataFrame, url_column: str) -> pd.DataFrame:
    """Nettoyage basique des URLs"""
    df = df.copy()
    df[url_column] = df[url_column].str.lower().str.strip()
    df[url_column] = df[url_column].apply(lambda x: re.sub(r'[^a-z0-9:/.\-_]', '', x))
    return df


def preprocess_data(db_path: str, table_name: str, url_column: str = 'url', label_column: str = 'label') -> pd.DataFrame:
    """Pipeline de prétraitement complet"""
    print("[INFO] Chargement des données depuis la base...")
    df = load_data_from_db(db_path, table_name)

    print("[INFO] Nettoyage des URLs...")
    df = clean_urls(df, url_column)

    print("[INFO] Extraction des features...")
    features_df = df[url_column].apply(extract_features)
    features_df = pd.DataFrame(features_df.tolist())

    print("[INFO] Ajout des labels...")
    features_df[label_column] = df[label_column].values

    return features_df

#un exemple de main on doit le rétirer après
if __name__ == "__main__":
    db_path = "data/urls.db"
    table_name = "all_url"  #a adapté selon la base de données
    processed_df = preprocess_data(db_path, table_name)

    print("[INFO] Sauvegarde du fichier prétraité...")
    processed_df.to_csv("data/processed_data.csv", index=False)
    print("[SUCCESS] Données sauvegardées dans data/processed_data.csv")
