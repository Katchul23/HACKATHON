import os
import json
import joblib
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

def load_dataset(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
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

def evaluate_model(model_path, data_path, markdown_report_path="data/output/eval_errors.md"):
    print("📥 Chargement des données...")
    texts, labels = load_dataset(data_path)

    print("📊 Découpage train/test...")
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.3, random_state=42)

    print(f"📦 Chargement du modèle : {model_path.name}")
    loaded = joblib.load(model_path)

    try:
        # Si modèle est un pipeline
        y_pred = loaded.predict(X_test)
    except AttributeError:
        # Sinon, ancien format (modèle, vectorizer)
        model, vectorizer = loaded
        X_vec = vectorizer.transform(X_test)
        y_pred = model.predict(X_vec)

    print("\n✅ Rapport de classification :\n")
    print(classification_report(y_test, y_pred))

    print("📉 Matrice de confusion :")
    print(confusion_matrix(y_test, y_pred))

    # 🔍 Générer rapport Markdown des erreurs
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

if __name__ == "__main__":
    try:
        model_path = find_latest_model()
        evaluate_model(
            model_path=model_path,
            data_path="data/training/annotated_samples_50k.json"
        )
    except Exception as e:
        print(f"❌ Erreur : {e}")
