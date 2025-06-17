# train_classifier.py
import argparse
import json
import os
import joblib
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


def load_annotated_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [entry["text"] for entry in data]
    labels = [entry["label"] for entry in data]
    return texts, labels


def get_pipeline_and_grid(model_type):
    if model_type == "logistic":
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=1000))
        ])
        param_grid = {
            "tfidf__max_features": [1000, 2000],
            "tfidf__ngram_range": [(1, 1), (1, 2)],
            "clf__C": [0.1, 1, 10],
            "clf__solver": ["liblinear", "lbfgs"]
        }

    elif model_type == "randomforest":
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer()),
            ("clf", RandomForestClassifier(random_state=42))
        ])
        param_grid = {
            "tfidf__max_features": [1000, 2000],
            "tfidf__ngram_range": [(1, 1), (1, 2)],
            "clf__n_estimators": [100, 200],
            "clf__max_depth": [None, 10, 20]
        }

    else:
        raise ValueError("❌ Modèle non supporté : choisissez 'logistic' ou 'randomforest'.")

    return pipeline, param_grid


def main():
    parser = argparse.ArgumentParser(description="Entraîne un classifieur sur les citations de données.")
    parser.add_argument("--model", choices=["logistic", "randomforest"], required=True, help="Type de modèle à entraîner")
    args = parser.parse_args()

    data_path = "data/training/annotated_samples_50k.json"
    model_name = f"data_classifier_{args.model}.joblib"
    model_path = Path(f"models/saved/{model_name}")
    stable_path = Path("models/saved/final_classifier_50k.joblib")
    model_path.parent.mkdir(parents=True, exist_ok=True)

    print("📥 Chargement des données annotées...")
    texts, labels = load_annotated_data(data_path)

    print("📊 Division en jeu d'entraînement/test...")
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

    print("🔍 Recherche des meilleurs hyperparamètres avec GridSearchCV...")
    pipeline, param_grid = get_pipeline_and_grid(args.model)
    grid = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=1)
    grid.fit(X_train, y_train)

    print("🏆 Meilleurs paramètres :", grid.best_params_)

    print("💾 Sauvegarde du modèle optimisé...")
    joblib.dump(grid.best_estimator_, model_path)

    print("📄 Sauvegarde du modèle stable sous final_classifier.joblib...")
    shutil.copy(model_path, stable_path)
    print(f"✅ Modèle enregistré comme version stable : {stable_path}")

    print("📈 Évaluation sur le jeu de test...")
    predictions = grid.predict(X_test)

    print("\n✅ Rapport de classification :")
    print(classification_report(y_test, predictions))

    print("📉 Matrice de confusion :")
    print(confusion_matrix(y_test, predictions))


if __name__ == "__main__":
    main()

