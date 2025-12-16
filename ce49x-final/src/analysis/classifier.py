"""
Rule-based tagging and co-occurrence analysis.
"""

import pandas as pd
from typing import List, Dict


def tag_article(text: str, ce_dict: Dict[str, List[str]], ai_dict: Dict[str, List[str]]):
    text_lower = text.lower()
    ce_labels = [area for area, kws in ce_dict.items() if any(kw in text_lower for kw in kws)]
    ai_labels = [tech for tech, kws in ai_dict.items() if any(kw in text_lower for kw in kws)]
    return ce_labels, ai_labels


def classify_all_articles(df: pd.DataFrame, ce_dict: Dict[str, List[str]], ai_dict: Dict[str, List[str]]) -> pd.DataFrame:
    ce_areas = []
    ai_techs = []
    for text in df["clean_text"].fillna(""):
        ce_labels, ai_labels = tag_article(text, ce_dict, ai_dict)
        ce_areas.append(ce_labels)
        ai_techs.append(ai_labels)
    df = df.copy()
    df["ce_areas"] = ce_areas
    df["ai_techs"] = ai_techs
    return df


def cooccurrence_matrix(df: pd.DataFrame, ce_dict: Dict[str, List[str]], ai_dict: Dict[str, List[str]]) -> pd.DataFrame:
    ce_keys = list(ce_dict.keys())
    ai_keys = list(ai_dict.keys())
    matrix = pd.DataFrame(0, index=ce_keys, columns=ai_keys)

    for _, row in df.iterrows():
        for ce in row.get("ce_areas", []):
            for ai in row.get("ai_techs", []):
                if ce in matrix.index and ai in matrix.columns:
                    matrix.loc[ce, ai] += 1
    return matrix

