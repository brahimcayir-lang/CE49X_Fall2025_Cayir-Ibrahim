# CE49X Final Project — AI in Civil Engineering

End-to-end NLP + web scraping pipeline to explore which civil engineering areas most use AI and which AI technologies are involved. The workflow covers scraping news/articles, preprocessing text, rule-based tagging, co-occurrence analysis, and visualization.

## Project Structure
- `data/raw`: raw scraped articles (`articles.csv`, `articles_master.csv`), scrapy outputs
- `data/processed`: cleaned dataset (`articles_clean.csv`)
- `data/logs`: optional run logs
- `notebooks`: step-by-step notebooks (01–04)
- `src/scraping`: search + article extraction + multi-layer ingestion
- `src/preprocessing`: text cleaning utilities and pipelines
- `src/analysis`: dictionaries, classifiers, visualization helpers
- `figures`: saved plots and word clouds
- `report`: placeholder for write-up
- `spiders/`: Scrapy project for archive crawling

## Quickstart
1) Install Python 3.10+ and create a virtual environment.
2) `pip install -r requirements.txt`
3) (Optional) Install spaCy model: `python -m spacy download en_core_web_sm`
4) Set any API keys you have via env or .env: `NEWSAPI_KEY`, `MEDIASTACK_KEY`, `BING_API_KEY`, `SERPAPI_KEY`.
5) Run `notebooks/01_scraping.ipynb` to collect data (all layers) → `data/raw/articles_master.csv`.
6) Run remaining notebooks in order (`02_preprocessing.ipynb` → `04_visualization.ipynb`) or call the module functions directly.

## Pipeline Overview
1) Ingestion (multi-tier): RSS, News APIs (NewsAPI/GDELT/Mediastack/Bing), Google News (SerpAPI or HTML), AEC site scrapers, Scrapy archive spiders, legacy HTML scraper; merged into `data/raw/articles_master.csv`.
2) Preprocessing: clean text (lowercase, punctuation/number removal, stopwords, lemmatization), save to `data/processed/articles_clean.csv`.
3) Analysis: tag articles with civil engineering areas and AI technologies; build co-occurrence matrix.
4) Visualization: bar charts, heatmaps, networks, and word clouds saved to `figures/`.

## Ingestion tiers
- RSS (fast/safe): `src.scraping.rss.fetch_rss_articles`
- APIs (keyed, higher volume): NewsAPI, GDELT, Mediastack, Bing (toggled by env keys)
- Google News: SerpAPI if `SERPAPI_KEY`, otherwise HTML fallback
- AEC site scrapers: ENR, ConstructionDive, Civil+Structural Engineer, Engineering.com, BIMPlus, NewCivilEngineer
- Scrapy spiders: archive crawlers (run separately) save to `data/raw/*archive*.json`
- Aggregator: `src.scraping.aggregator.collect_all_articles` merges all into `data/raw/articles_master.csv`

## Running Scrapy spiders
From project root:
- `scrapy crawl enr_archive -o data/raw/enr_archive.json`
- `scrapy crawl constructiondive_archive -o data/raw/constructiondive_archive.json`
- `scrapy crawl engineeringcom_archive -o data/raw/engineeringcom_archive.json`

## Notebook flow
- `01_scraping.ipynb`: runs all ingestion layers with runtime knobs (API toggles via env, page limits, result caps) and saves `data/raw/articles_master.csv`.
- `02_preprocessing.ipynb`: clean text → `data/processed/articles_clean.csv`.
- `03_analysis.ipynb`: classify/tag + co-occurrence.
- `04_visualization.ipynb`: charts/heatmap/network/word clouds.

## Outputs
- `data/raw/articles.csv`: scraped articles with metadata/text
- `data/raw/articles_master.csv`: merged multi-layer ingestion dataset
- `data/processed/articles_clean.csv`: cleaned text and tokens
- `figures/`: bar plots, heatmap, network graph, word clouds
- Co-occurrence matrix and frequency tables produced in notebooks

