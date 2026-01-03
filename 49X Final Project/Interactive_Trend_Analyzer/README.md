# Interactive Trend Analyzer

An interactive web-based application for analyzing trends in the article database. Search for any topic or field and visualize trends over time, frequency distributions, and word analysis.

## Features

- **Keyword Search**: Search articles by keywords in titles and/or text content
- **Temporal Trends**: Visualize article counts over time (by year or month)
- **Frequency Analysis**: 
  - Distribution by source
  - Distribution by CE discipline (if available)
  - Distribution by AI technology (if available)
- **Word Analysis**: Top 30 most common words in filtered articles
- **Article Browser**: Browse and view filtered articles with full text

## Installation

1. Install required dependencies:
```bash
pip install streamlit pandas plotly
```

Or install all dependencies from the main project:
```bash
pip install -r ../Required Libraries.txt
pip install streamlit
```

## Usage

1. Navigate to the `Interactive_Trend_Analyzer` folder:
```bash
cd Interactive_Trend_Analyzer
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. The application will open in your default web browser (usually at `http://localhost:8501`)

## How to Use

1. **Enter Keywords**: In the sidebar, enter keywords separated by commas (e.g., "bridge, construction, AI")
2. **Select Search Scope**: Choose to search in "both", "title only", or "text only"
3. **Explore Tabs**:
   - **Temporal Trends**: See how article counts change over time
   - **Frequency Analysis**: View distributions by source, discipline, or technology
   - **Word Analysis**: See most common words in filtered articles
   - **Article List**: Browse individual articles and view full text

## Database Connection

The application automatically searches for databases in the following locations:
- `../Data/corpus_LLM_Improved.db` (preferred)
- `../Data/corpus_LLM.db`
- `../Data/corpus.db`

It will use the first database found.

## Tips

- Use specific keywords for better results
- Multiple keywords are combined with OR logic (articles containing ANY keyword)
- Case-insensitive search
- You can search within results to further narrow down articles
- Click on individual articles to view full text

## Troubleshooting

**Database not found**: Make sure the database file exists in the `Data` folder relative to the project root.

**No results**: Try broader keywords or check if articles exist in the database.

**Date parsing issues**: The app tries multiple methods to parse dates. If dates don't appear, the original date format may not be recognized.

