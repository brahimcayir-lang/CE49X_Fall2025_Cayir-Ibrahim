# CE49X Final Project – Civil Engineering & AI Trend Analysis

## Project Overview
This project analyzes the adoption of Artificial Intelligence (AI) across Civil Engineering sub-disciplines by examining trends in industry news and selected publications. Using Python-based NLP techniques, we identify dominant AI applications and their distribution across the engineering domain.

## Team Members
* **Hakan ARMAN**
* **İbrahim ÇAYIR**

## Aim
To quantitatively assess AI usage trends in Civil Engineering by processing textual data and visualizing patterns that identify which sub-disciplines are leading in AI integration.

## Project Workflow
Our methodology follows a focused data-driven pipeline:
1. **Data Collection**: Large-scale collection primarily via RSS feeds and industry-specific sources, stored in a structured SQLite database.
2. **Preprocessing**: Advanced cleaning using NLTK, including noise reduction (HTML/Scraper artifacts), stopword removal, and lemmatization.
3. **Categorization**: Dictionary-based classification to map articles to specific Civil Engineering areas (Structural, Geotechnical, etc.) and AI technologies.
4. **Visualization**: Generation of volume charts, relationship heatmaps, concept network graphs, and sector-specific word clouds.

## Deliverables

### Final Report
- **Markdown Version**: `Final_Report.md` (ready for PDF conversion)
- **PDF Conversion**: 
  - Use `convert_report_to_pdf.py` script (requires pandoc)
  - Or use VS Code extension "Markdown PDF"
  - Or online markdown-to-PDF converters

### Task 1 Data Description
- **Document**: `Task1_Data_Description.md`
- Contains complete list of data sources, search queries, and collection methodology

### Visualizations & Outputs
All visualizations and analysis reports are located in `/Outputs/AfterLLM/`:
- `BarChart_CE_Distribution.png` - Articles per CE discipline
- `Task3_Heatmap.png` - CE Area × AI Technology co-occurrence
- `NetworkGraph_Terms.png` - Semantic term relationships
- `WordCloud_*.png` - Discipline-specific word clouds (5 files)
- `Task3_Temporal_Trends.png` - Temporal evolution of AI mentions
- Analysis reports (Task2, Task3, Final Conclusion)

## Quick Start

### Running the Analysis Pipeline

1. **Initialize Database**:
   ```bash
   python Scripts/init_db.py
   ```

2. **Collect Data** (optional - data already collected):
   ```bash
   python Scripts/scraper_rss.py
   python Scripts/scraper_gnews.py
   python Scripts/scraper_arxiv.py
   ```

3. **Preprocess Data**:
   ```bash
   python Scripts/task2_preprocessing.py
   ```

4. **Categorize Articles**:
   ```bash
   python Scripts/task3_afterLLM.py
   ```

5. **Generate Visualizations**:
   ```bash
   python Scripts/task4_afterLLM.py
   ```

### Converting Report to PDF

**Option 1: Using pandoc** (recommended)
```bash
pandoc Final_Report.md -o Final_Report.pdf --pdf-engine=xelatex --toc -V geometry:margin=1in
```

**Option 2: Using Python script**
```bash
python convert_report_to_pdf.py
```

**Option 3: Using VS Code**
1. Install "Markdown PDF" extension
2. Open `Final_Report.md`
3. Press `Ctrl+Shift+P` → "Markdown PDF: Export (pdf)"

## Repository Structure

```
/CE49X Final Project
├── /Data/                    # SQLite databases
│   ├── corpus.db            # Raw collected data
│   └── corpus_LLM_Improved.db  # Final labeled dataset
├── /Scripts/                 # Python scripts
│   ├── scraper_*.py         # Data collection
│   ├── task2_*.py           # Preprocessing
│   ├── task3_*.py           # Categorization
│   └── task4_*.py           # Visualization
├── /Outputs/                 # Results and visualizations
│   └── /AfterLLM/           # Final analysis outputs
├── Final_Report.md          # Comprehensive final report
├── Task1_Data_Description.md # Data collection documentation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Requirements

See `Required Libraries.txt` or install via:
```bash
pip install pandas numpy nltk scikit-learn matplotlib seaborn networkx wordcloud feedparser newspaper3k GoogleNews beautifulsoup4 requests
```

***

Course: CE49X – Introduction to Data Science for Civil Engineering

Institution: Boğaziçi University

Semester: Fall 2025

***
