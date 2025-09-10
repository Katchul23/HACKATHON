# utils/logger.py
import json
import os
from datetime import datetime

LOG_FILE = "data/output/low_confidence_log.json"

def log_low_confidence(text, predicted_label, confidence):
    """
    Enregistre une prédiction à faible confiance dans un fichier JSON.

    Args:
        text (str): Phrase analysée
        predicted_label (str): Label prédit (primaire/secondaire)
        confidence (float): Score de confiance du modèle
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "text": text,
        "predicted_label": predicted_label,
        "confidence": round(confidence, 3)
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[Logger] 🔎 Faible confiance loggée : {confidence} pour '{text[:50]}...' -> {predicted_label}")
