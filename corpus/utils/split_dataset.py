# split_dataset.py
import json
import os
from sklearn.model_selection import train_test_split

def split_json(input_path, output_train, output_eval, test_size=0.2, seed=42):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data or not isinstance(data, list):
        raise ValueError("❌ Le fichier doit contenir une liste d’objets JSON.")

    print(f"📦 {len(data)} exemples trouvés dans : {input_path}")
    
    train_data, eval_data = train_test_split(data, test_size=test_size, random_state=seed)

    os.makedirs(os.path.dirname(output_train), exist_ok=True)
    os.makedirs(os.path.dirname(output_eval), exist_ok=True)

    with open(output_train, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)
    with open(output_eval, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier d'entraînement : {output_train} ({len(train_data)} lignes)")
    print(f"✅ Fichier d'évaluation : {output_eval} ({len(eval_data)} lignes)")

