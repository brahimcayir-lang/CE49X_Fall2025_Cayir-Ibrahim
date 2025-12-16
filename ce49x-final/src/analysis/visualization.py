"""
Visualization helpers.
"""

import os
from typing import Dict
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from wordcloud import WordCloud
import pandas as pd

FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)


def bar_counts(series, title, filename):
    counts = series.explode().dropna()
    counts = counts[counts != ""]
    summary = counts.value_counts().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    sns.barplot(x=summary.values, y=summary.index, color="steelblue")
    plt.title(title)
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename))
    plt.close()


def plot_cooccurrence_heatmap(matrix: pd.DataFrame, filename: str):
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues")
    plt.title("CE vs AI Co-occurrence")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename))
    plt.close()


def plot_network(matrix: pd.DataFrame, filename: str):
    G = nx.Graph()
    for ce in matrix.index:
        G.add_node(ce, bipartite=0)
    for ai in matrix.columns:
        G.add_node(ai, bipartite=1)

    for ce in matrix.index:
        for ai in matrix.columns:
            weight = matrix.loc[ce, ai]
            if weight > 0:
                G.add_edge(ce, ai, weight=weight)

    pos = nx.spring_layout(G, seed=42, k=0.5)
    weights = [G[u][v]["weight"] for u, v in G.edges()]
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=1200, width=weights)
    plt.title("CE-AI Co-occurrence Network")
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, filename))
    plt.close()


def wordclouds_by_area(df: pd.DataFrame, ce_dict: Dict[str, list], filename_prefix: str = "wordcloud"):
    for area in ce_dict.keys():
        subset = df[df["ce_areas"].apply(lambda lst: area in lst if isinstance(lst, list) else False)]
        text = " ".join(subset["clean_text"].fillna(""))
        if not text.strip():
            continue
        wc = WordCloud(width=800, height=400, background_color="white").generate(text)
        plt.figure(figsize=(8, 4))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(os.path.join(FIG_DIR, f"{filename_prefix}_{area.replace(' ', '_')}.png"))
        plt.close()

