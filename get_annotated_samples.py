import os
import json
import random
from faker import Faker
from deep_translator import GoogleTranslator
from collections import Counter
from tqdm import tqdm

# Configuration des paths
data_path = "data/training/annotated_samples_50k.json"
os.makedirs(os.path.dirname(data_path), exist_ok=True)  # Crée le dossier si inexistant

# Initialisation
fake = Faker()
random.seed(42)  # Pour la reproductibilité

# Configuration du traducteur
translator = GoogleTranslator(source='auto', target='en')

# Templates avec marqueurs linguistiques scientifiques
TEMPLATES = {
    "primaire": [
        "Nous avons mesuré {variable} à l'aide de {instrument} (précision: {precision}) sur {n} échantillons",
        "Des données de {phenomenon} ont été acquises par {method} pendant {duration}",
        "{n} expériences ont été conduites en conditions {conditions} pour étudier {process}",
        "Data were collected using {instrument} at {location} with {sampling_freq} sampling frequency",
        "L'étude présente des mesures originales de {variable} obtenues par {technique}",
        "Samples were analyzed with {analytical_method} revealing {n} distinct {components}"
    ],
    
    "secondaire": [
        "Les données de {variable} proviennent de {database} (version {version})",
        "Cette analyse intègre des résultats publiés dans {citation}",
        "Données extraites du jeu {dataset} disponible sous licence {license}",
        "We used the {year} dataset from {repository} (DOI: {doi})",
        "Les valeurs sont issues d'une méta-analyse de {n_studies} études sur {topic}",
        "Historical data were obtained from {source} covering the period {year_range}"
    ]
}

# Dictionnaire de paramètres réalistes
PARAMS = {
    "variable": ["température", "pH", "conductivité", "CO2 concentration", "gene expression", "soil moisture"],
    "instrument": [
        "un spectromètre de masse", "un chromatographe HPLC", 
        "un microscope électronique à balayage", "un accéléromètre triaxial",
        "a mass spectrometer", "an atomic force microscope"
    ],
    "precision": ["±0.1%", "±1σ", "±0.5 unités", "with 95% confidence interval"],
    "phenomenon": ["la croissance bactérienne", "les variations climatiques", "protein folding", "wave propagation"],
    "method": ["spectroscopie Raman", "microscopie à fluorescence", "ELISA", "PCR quantitative"],
    "database": ["PubMed", "Web of Science", "IEEE Xplore", "GenBank", "PANGAEA"],
    "citation": [
        f"{fake.last_name()} et al. ({random.randint(2010,2023)})",
        f"the {fake.word().title()} database ({random.randint(1995,2022)})"
    ],
    "license": ["CC-BY 4.0", "ODC-BY", "GNU GPL", "restricted access"],
    "doi": [f"10.{random.randint(1000,9999)}/zenodo.{random.randint(100000,999999)}" for _ in range(50)],
    "technique": ["spectrométrie", "chromatographie", "microscopie", "electrophorèse"],
    "components": ["peaks", "marqueurs", "espèces", "composés"],
    "repository": ["GitHub", "Figshare", "Zenodo", "Dryad"],
    "source": ["les archives nationales", "la bibliothèque du Congrès", "NASA databases"],
    "topic": ["le changement climatique", "la biodiversité", "les maladies génétiques"],
    "process": ["la photosynthèse", "l'érosion", "la synthèse protéique"]
}

# Complétion dynamique des paramètres
PARAMS["location"] = [f"{fake.city()}, {fake.country()}" for _ in range(30)]
PARAMS["conditions"] = [f"{temp}°C, {pressure} atm" 
                       for temp in range(20,40) 
                       for pressure in [1, 1.5, 2]]
PARAMS["duration"] = [f"{t} {unit}" 
                     for t in [24, 48, 72, 96] 
                     for unit in ["heures", "jours", "hours"]]
PARAMS["analytical_method"] = ["spectroscopy", "mass spectrometry", "microscopy", "chromatography"]
PARAMS["dataset"] = [f"Dataset_{fake.word().title()}_{random.randint(1000,9999)}" for _ in range(20)]
PARAMS["version"] = [f"{random.randint(1,5)}.{random.randint(0,9)}" for _ in range(10)]

def safe_translate(text):
    """Fonction de traduction sécurisée avec deep-translator"""
    try:
        if len(text) <= 5000:  # Respecte la limite de caractères
            translated = translator.translate(text)
            return translated if translated else text  # Retourne l'original si échec
        return text
    except Exception as e:
        print(f"Erreur de traduction ignorée : {str(e)}")
        return text

def generate_sample():
    """Génère un échantillon avec contrôle de qualité"""
    label = random.choices(["primaire", "secondaire"], weights=[0.6, 0.4])[0]
    template = random.choice(TEMPLATES[label])
    
    params = {
        "n": random.randint(3, 100),
        "n_studies": random.randint(5, 200),
        "year": random.randint(1990, 2023),
        "year_range": f"{random.randint(1980,2010)}-{random.randint(2011,2023)}",
        "sampling_freq": random.choice(["quotidienne", "horaire", "10 min", "1Hz"]),
        **{k: random.choice(v) for k,v in PARAMS.items()}
    }
    
    text = template.format(**params)
    
    # Traduction aléatoire (30% de chance) avec vérification de la langue
    if random.random() < 0.3 and not text.startswith(("We ", "Data ", "The ", "This ")):
        text = safe_translate(text)
    
    return {"text": text, "label": label}

# Génération des données avec sauvegarde périodique
print("Génération de 50 000 exemples...")
batch_size = 10000
data = []

for i in tqdm(range(0, 50000, batch_size)):
    batch = [generate_sample() for _ in range(batch_size)]
    data.extend(batch)
    
    # Sauvegarde temporaire
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

# Vérification finale
label_dist = Counter([d["label"] for d in data])
print(f"\nDistribution des labels: {label_dist}")

# Sauvegarde finale formatée
with open(data_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Fichier sauvegardé avec succès à : {os.path.abspath(data_path)}")
print(f"Taille finale : {os.path.getsize(data_path)/1024/1024:.1f} MB")
print(f"Exemple de données : {json.dumps(data[0], indent=2, ensure_ascii=False)}")