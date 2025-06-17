# models/classify_model.py

import joblib
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

class DataClassifierModel:
    def __init__(self, model_path=None):
        """
        Initialise le modèle. Si un chemin est fourni, il charge un pipeline existant.
        """
        self.model_path = model_path
        self.model = None

        if model_path:
            self.load_model(model_path)

    def train(self, texts, labels):
        """
        Entraîne le modèle à partir de textes annotés avec GridSearchCV.

        Args:
            texts (list[str]): Liste de phrases.
            labels (list[str]): Liste des étiquettes ("primaire", "secondaire").
        """
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

        grid = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=1)
        grid.fit(texts, labels)

        print("🏆 Meilleurs paramètres :", grid.best_params_)
        self.model = grid.best_estimator_

    def predict(self, texts):
        """
        Prédit les étiquettes pour une liste de textes.

        Returns:
            list[str]: Étiquettes ("primaire" ou "secondaire").
        """
        return self.model.predict(texts)

    def predict_with_confidence(self, text):
        """
        Retourne le label prédit + score de confiance (entre 0 et 1).

        Args:
            text (str): Une phrase.

        Returns:
            tuple(str, float): Label prédit et probabilité associée.
        """
        if hasattr(self.model.named_steps["clf"], "predict_proba"):
            proba = self.model.predict_proba([text])[0]
            label_index = proba.argmax()
            label = self.model.classes_[label_index]
            confidence = proba[label_index]
            return label, confidence
        else:
            label = self.model.predict([text])[0]
            return label, 1.0  # Aucun score dispo

    def save_model(self, path):
        """Sauvegarde le pipeline complet dans un fichier .joblib"""
        joblib.dump(self.model, path)

    def load_model(self, path):
        """Charge un pipeline préentraîné .joblib"""
        self.model = joblib.load(path)
