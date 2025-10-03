import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_auc_score,
    RocCurveDisplay,
)


def load_processed_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def split_data(df: pd.DataFrame, target_col: str = "label"):
    X = df.drop(columns=[target_col])
    y = df[target_col]
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_model(X_train, y_train) -> RandomForestClassifier:
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    return clf


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    print("\n=== Rapport de classification ===")
    print(classification_report(y_test, y_pred))

    print("\n=== Matrice de confusion ===")
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot()
    plt.title("Matrice de confusion")
    plt.show()

    if y_proba is not None:
        auc = roc_auc_score(y_test, y_proba)
        print(f"AUC: {auc:.4f}")
        RocCurveDisplay.from_predictions(y_test, y_proba)
        plt.title("Courbe ROC")
        plt.show()


def save_model(model, path: str):
    joblib.dump(model, path)
    print(f"[SUCCESS] Modèle sauvegardé dans {path}")


if __name__ == "__main__":
    print("[INFO] Chargement des données...")
    df = load_processed_data("data/processed_data.csv")

    print("[INFO] Séparation train/test...")
    X_train, X_test, y_train, y_test = split_data(df)

    print("[INFO] Entraînement du modèle...")
    model = train_model(X_train, y_train)

    print("[INFO] Évaluation du modèle...")
    evaluate_model(model, X_test, y_test)

    print("[INFO] Sauvegarde du modèle...")
    save_model(model, "models/random_forest_model.pkl")
