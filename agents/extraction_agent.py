# Placeholder for extraction_agent.py
import re

class ExtractionAgent:
    def __init__(self):
        self.name = "ExtractionAgent"

    def extract_data_mentions(self, text):
        """
        Repère les phrases contenant des références à des données,
        en utilisant une liste multilingue de mots-clés.

        Args:
            text (str): Texte complet de l'article scientifique.

        Returns:
            list[dict]: Liste des phrases suspectées de mentionner des données,
                        contenant l'index et le texte.
        """
        data_keywords = [
            # 🔷 Français - Termes généraux
            r"\bdonnées?\b", r"\bsources?\b", r"\bjeux?\sde\sdonnées\b",
            r"\bjeux?\sde\sd[ée]p[âa]rt\b", r"\bmat[ée]riau[x]?\sde\sbase\b",
            
            # 🔹 Français - Collecte
            r"\brecueilli[e]?s?\b", r"\bcollect[ée]?s?\b", r"\bobtenu[e]?s?\b",
            r"\bmesur[ée]?s?\b", r"\bpr[ée]lev[ée]?s?\b", r"\bacquis[e]?s?\b",
            r"\bengrang[ée]?s?\b", r"\bg[ée]n[ée]r[ée]?s?\b",
            
            # 🔹 Français - Traitement
            r"\btrait[ée]?s?\b", r"\btransform[ée]?s?\b", r"\bnettoy[ée]?s?\b",
            r"\bstandardis[ée]?s?\b", r"\bfiltr[ée]?s?\b", r"\bcorrig[ée]?s?\b",
            r"\banonymis[ée]?s?\b", r"\bagr[ée]g[ée]?s?\b",
            
            # 🔹 Français - Sources
            r"\bbases?\sde\sdonn[ée]es\b", r"\bentrep[ôo]ts?\sde\sdonn[ée]es\b",
            r"\barchives?\b", r"\brepositoires?\b", r"\bregistres?\b",
            r"\bcatalogues?\b", r"\binventaires?\b",
            
            # 🔹 Français - Types
            r"\bstatistiques?\b", r"\bm[ée]triques?\b", r"\bindicateurs?\b",
            r"\bobservations?\b", r"\bvariables?\b", r"\bparam[èe]tres?\b",
            r"\béchantillons?\b", r"\bs[ée]ries?\stemporelles\b",
            
            # 🔷 Anglais - General Terms
            r"\bdata\b", r"\bdataset[s]?\b", r"\braw\sdata\b",
            r"\bsource\sdata\b", r"\bprimary\sdata\b", r"\bsecondary\sdata\b",
            
            # 🔸 Anglais - Collection
            r"\bcollected\b", r"\bgathered\b", r"\bacquired\b",
            r"\bmeasured\b", r"\bsampled\b", r"\bgenerated\b",
            r"\bharvested\b", r"\bcompiled\b",
            
            # 🔸 Anglais - Processing
            r"\bprocessed\b", r"\bcleaned\b", r"\bnormalized\b",
            r"\bfiltered\b", r"\banonymized\b", r"\baggregated\b",
            r"\btransformed\b", r"\bcurated\b",
            
            # 🔸 Anglais - Sources
            r"\bdatabase[s]?\b", r"\bdata\swarehouse[s]?\b", r"\barchive[s]?\b",
            r"\brepository[\w]*\b", r"\bregistry[\w]*\b", r"\bcatalog[\w]*\b",
            
            # 🔸 Anglais - Types
            r"\bstatistics?\b", r"\bmetrics?\b", r"\bindicators?\b",
            r"\bobservations?\b", r"\bvariables?\b", r"\bparameters?\b",
            r"\bsamples?\b", r"\btime\sseries\b",
            
            # 🔶 Termes techniques communs
            r"\b(?:csv|json|xml)\s?files?\b", r"\b(?:excel|spreadsheet)s?\b",
            r"\bsql\s(?:tables?|databases?)\b", r"\bno[s]?ql\sstores?\b",
            r"\b(?:api|web)\s?services?\b", r"\b(?:ftp|sftp)\s?servers?\b",
            
            # 🔷 Expressions contextuelles françaises
            r"\bdonnées?\s(?:brutes?|originales?|expérimentales?)\b",
            r"\banalyses?\s(?:statistiques?|de\sdonnées?)\b",
            r"\btraitement\s(?:automatique|manuel)\sdes\sdonnées\b",
            
            # 🔸 English Contextual Phrases
            r"\bdata\s(?:mining|analysis|visualization)\b",
            r"\b(?:statistical|quantitative)\sanalysis\b",
            r"\b(?:machine\slearning|ai)\sdatasets?\b",
            
            # 🆕 Nouveaux termes scientifiques (2023-2024)
            r"\bsynthetic\sdata\b", r"\bdata\sfabric\b",
            r"\bdata\smesh\b", r"\bdata\sproducts?\b",
            r"\bdonnées?\ssynthétiques\b", r"\btissu\sde\sdonnées\b"
        ]

        pattern = re.compile("|".join(data_keywords), re.IGNORECASE)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        mentions = []
        for idx, sentence in enumerate(sentences):
            if pattern.search(sentence) and len(sentence.strip()) > 20:
                mentions.append({
                    "index": idx,
                    "text": sentence.strip()
                })

        return mentions
