import os
import json
import joblib
import argparse
import traceback
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold

def load_dataset(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ Fichier non trouvé : {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not data:
        raise ValueError("❌ Dataset vide.")
    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    return texts, labels

def find_latest_model():
    saved_dir = Path("models/saved")
    if not saved_dir.exists():
        raise FileNotFoundError("❌ Aucun dossier 'models/saved' trouvé.")
    models = list(saved_dir.glob("data_classifier_*.joblib"))
    if not models:
        raise FileNotFoundError("❌ Aucun modèle trouvé dans models/saved/")
    return max(models, key=os.path.getmtime)

def evaluate_model(model_path, data_path, markdown_report_path="data/output/eval_errors.md", json_report_path="data/output/eval_metrics.json"):
    print("📥 Chargement des données...")
    texts, labels = load_dataset(data_path)

    print("📊 Découpage train/test...")
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.3, random_state=42)

    print(f"📦 Chargement du modèle : {model_path.name}")
    loaded = joblib.load(model_path)

    try:
        y_pred = loaded.predict(X_test)
        vectorizer = None
    except AttributeError:
        model, vectorizer = loaded
        X_vec = vectorizer.transform(X_test)
        y_pred = model.predict(X_vec)

    print("\n✅ Rapport de classification :\n")
    report = classification_report(y_test, y_pred, digits=4, output_dict=True)
    print(classification_report(y_test, y_pred, digits=4))

    print("📉 Matrice de confusion :")
    matrix = confusion_matrix(y_test, y_pred)
    print(matrix)

    os.makedirs(os.path.dirname(json_report_path), exist_ok=True)
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    print(f"💾 Rapport JSON sauvegardé : {json_report_path}")

    # Markdown erreurs
    errors = [
        (i, text, true, pred) for i, (text, true, pred) in enumerate(zip(X_test, y_test, y_pred))
        if true != pred
    ]
    if errors:
        os.makedirs(os.path.dirname(markdown_report_path), exist_ok=True)
        with open(markdown_report_path, "w", encoding="utf-8") as f:
            f.write("# ⚠️ Erreurs de classification\n\n")
            for i, phrase, true, pred in errors:
                f.write(f"## Erreur {i+1}\n")
                f.write(f"- **Texte** : {phrase}\n")
                f.write(f"- **Vérité terrain** : `{true}`\n")
                f.write(f"- **Prédiction** : `{pred}`\n\n")
        print(f"📝 Rapport Markdown des erreurs : {markdown_report_path}")
    else:
        print("✅ Aucune erreur de classification détectée.")

def run_cross_val(model_path, data_path, cv=5):
    print("🔄 Validation croisée avec KFold...")
    texts, labels = load_dataset(data_path)
    loaded = joblib.load(model_path)

    if isinstance(loaded, tuple):
        # Modèle et vectorizer séparés
        model, vectorizer = loaded
        X_vec = vectorizer.transform(texts)
        input_data = X_vec
    else:
        # Pipeline complet (ex: TfidfVectorizer + Classifier)
        model = loaded
        input_data = texts  # Ne surtout pas transformer ici

    kfold = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    try:
        scores = cross_val_score(model, input_data, labels, cv=kfold, scoring='f1_macro')
        print(f"🎯 Scores F1 macro : {scores}")
        print(f"📊 Moyenne : {scores.mean():.4f} ± {scores.std():.4f}")
    except Exception:
        print("❌ Erreur pendant la validation croisée :")
        traceback.print_exc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Évaluer un classifieur IA (RandomForest, etc.)")
    parser.add_argument("--model", type=str, help="Chemin du modèle (.joblib)")
    parser.add_argument("--data", type=str, default="data/training/annotated_samples_50k.json", help="Fichier JSON d’annotation")
    parser.add_argument("--kfold", action="store_true", help="Effectuer une validation croisée")
    args = parser.parse_args()

    try:
        model_path = Path(args.model) if args.model else find_latest_model()
        if args.kfold:
            run_cross_val(model_path, args.data)
        else:
            evaluate_model(model_path=model_path, data_path=args.data)
    except Exception:
        print("❌ Erreur détectée :")
        traceback.print_exc()
