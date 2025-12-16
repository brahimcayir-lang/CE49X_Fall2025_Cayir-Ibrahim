"""
Text cleaning utilities.
"""

import re
from typing import List
import nltk
import spacy
from nltk.corpus import stopwords

# Ensure stopwords are available
try:
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOP_WORDS = set(stopwords.words("english"))

# Lazy-load spaCy model
_NLP = None


def _get_nlp():
    global _NLP
    if _NLP is None:
        _NLP = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    return _NLP


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str) -> List[str]:
    return text.split()


def remove_stopwords(tokens: List[str]) -> List[str]:
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def lemmatize(tokens: List[str]) -> List[str]:
    nlp = _get_nlp()
    doc = nlp(" ".join(tokens))
    return [tok.lemma_ for tok in doc if tok.lemma_ != "-PRON-"]


def clean_text(text: str, return_tokens: bool = False):
    norm = normalize(text)
    tokens = tokenize(norm)
    tokens = remove_stopwords(tokens)
    tokens = lemmatize(tokens)
    clean = " ".join(tokens)
    if return_tokens:
        return clean, tokens
    return clean

