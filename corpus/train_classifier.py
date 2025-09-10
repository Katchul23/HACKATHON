# train_classifier.py — entraînement + évaluation + export CSV
import argparse
import json
import os
import joblib
import shutil
import csv
from pathlib import Path
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from utils.split_dataset import split_json

def load_annotated_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [entry["text"].lower() for entry in data]
    labels = [entry["label"].lower() for entry in data]
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

def export_errors_csv(X_test, y_test, predictions, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "true_label", "predicted"])
        for text, true, pred in zip(X_test, y_test, predictions):
            if true != pred:
                writer.writerow([text, true, pred])

def ensure_split_done():
    train_path = "data/training/train.json"
    eval_path = "data/eval/eval.json"
    full_data = "data/training/annotated_samples_50k.json"
    if not os.path.exists(train_path) or not os.path.exists(eval_path):
        print("🪄 Données non encore divisées. Lancement du split...")
        split_json(full_data, train_path, eval_path)

def main():
    parser = argparse.ArgumentParser(description="Entraîne un classifieur sur les citations de données.")
    parser.add_argument("--model", choices=["logistic", "randomforest"], required=True, help="Type de modèle à entraîner")
    parser.add_argument("--eval-only", action="store_true", help="Ne pas réentraîner, juste évaluer le modèle stable")
    args = parser.parse_args()

    # Assurer le découpage train/eval
    ensure_split_done()

    train_file = "data/training/train.json"
    eval_file = "data/eval/eval.json"
    model_name = f"data_classifier_{args.model}.joblib"
    model_path = Path(f"models/saved/{model_name}")
    stable_path = Path("models/saved/final_classifier_50k.joblib")
    model_path.parent.mkdir(parents=True, exist_ok=True)

    if args.eval_only:
        print("📥 Chargement du jeu de test uniquement...")
        X_test, y_test = load_annotated_data(eval_file)
        print("🔍 Évaluation du modèle existant sans nouvel entraînement...")
        model = joblib.load(stable_path)
    else:
        print("📥 Chargement des données d'entraînement...")
        X_train, y_train = load_annotated_data(train_file)
        print("🔍 Recherche des meilleurs hyperparamètres avec GridSearchCV...")
        pipeline, param_grid = get_pipeline_and_grid(args.model)
        grid = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=1)
        grid.fit(X_train, y_train)
        print("🏆 Meilleurs paramètres :", grid.best_params_)

        print("💾 Sauvegarde du modèle optimisé...")
        joblib.dump(grid.best_estimator_, model_path)
        shutil.copy(model_path, stable_path)
        print(f"✅ Modèle enregistré comme version stable : {stable_path}")
        model = grid.best_estimator_
        print("💾 Sauvegarde du modèle optimisé...")

        # ➕ Export des meilleurs paramètres
        params_output_path = "data/output/best_params.json"
        os.makedirs(os.path.dirname(params_output_path), exist_ok=True)
        with open(params_output_path, "w", encoding="utf-8") as f:
            json.dump(grid.best_params_, f, indent=2)
        print(f"📝 Paramètres optimaux sauvegardés : {params_output_path}")


        print("📥 Chargement du jeu de test...")
        X_test, y_test = load_annotated_data(eval_file)

    print("📈 Évaluation sur le jeu de test...")
    predictions = model.predict(X_test)

    print("\n✅ Rapport de classification :")
    print(classification_report(y_test, predictions))

    print("📉 Matrice de confusion :")
    print(confusion_matrix(y_test, predictions))

    print("📤 Export des erreurs de prédiction : errors_eval.csv")
    export_errors_csv(X_test, y_test, predictions, "errors_eval.csv")


if __name__ == "__main__":
    main()
