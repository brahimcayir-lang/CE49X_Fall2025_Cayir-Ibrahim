import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from collections import Counter
import re

# Page configuration
st.set_page_config(
    page_title="Interactive Trend Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PATH CONFIGURATION ---
@st.cache_data
def get_base_path():
    """Get the base path of the project."""
    # Get absolute path of this file
    current_file = os.path.abspath(__file__)
    # Go up one level from Interactive_Trend_Analyzer to project root
    base_dir = os.path.dirname(os.path.dirname(current_file))
    # Normalize path to handle any path separator issues
    return os.path.normpath(base_dir)

@st.cache_resource
def find_database():
    """Find and connect to the database."""
    base_dir = get_base_path()
    db_paths = [
        os.path.join(base_dir, 'Data', 'corpus_LLM_Improved.db'),
        os.path.join(base_dir, 'data', 'corpus_LLM_Improved.db'),
        os.path.join(base_dir, 'Data', 'corpus_LLM.db'),
        os.path.join(base_dir, 'Data', 'corpus.db'),
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            return db_path
    return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(table_name='articles_labeled'):
    """Load data from the database."""
    db_path = find_database()
    if not db_path:
        return None, f"Database not found. Checked paths in Data folder."
    
    try:
        conn = sqlite3.connect(db_path)
        # Try articles_labeled first, fall back to articles
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            if df.empty:
                # If table exists but is empty, try articles table
                df = pd.read_sql_query("SELECT * FROM articles", conn)
        except (sqlite3.OperationalError, pd.errors.DatabaseError):
            # Table doesn't exist, try articles table
            try:
                df = pd.read_sql_query("SELECT * FROM articles", conn)
            except Exception as e2:
                conn.close()
                return None, f"Error: Neither '{table_name}' nor 'articles' table found. {str(e2)}"
        conn.close()
        
        if df.empty:
            return None, "Database table is empty."
        
        return df, None
    except Exception as e:
        return None, f"Error loading database: {str(e)}"

def filter_articles_by_keywords(df, keywords, search_in='both'):
    """Filter articles by keywords."""
    if df is None or df.empty:
        return df.copy() if df is not None else df
    
    keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
    if not keywords:
        return df.copy()
    
    # Work with a copy to avoid modifying original
    df_copy = df.copy()
    # Normalize column names
    df_copy.columns = [c.lower() for c in df_copy.columns]
    
    mask = pd.Series([False] * len(df_copy))
    
    for keyword in keywords:
        if search_in in ['title', 'both']:
            if 'title' in df_copy.columns:
                mask |= df_copy['title'].astype(str).str.lower().str.contains(keyword, na=False, regex=False)
        if search_in in ['text', 'both']:
            if 'full_text' in df_copy.columns:
                mask |= df_copy['full_text'].astype(str).str.lower().str.contains(keyword, na=False, regex=False)
            elif 'clean_text' in df_copy.columns:
                mask |= df_copy['clean_text'].astype(str).str.lower().str.contains(keyword, na=False, regex=False)
    
    return df_copy[mask].copy()

def parse_dates(df):
    """Parse publication dates."""
    # Work with copy to avoid modifying original
    df_copy = df.copy()
    # Only normalize if not already normalized (check if already lowercase)
    if df_copy.columns.tolist() and not all(c.islower() for c in df_copy.columns):
        df_copy.columns = [c.lower() for c in df_copy.columns]
    
    if 'publication_date' not in df_copy.columns:
        return df_copy, None
    
    df_copy['date'] = pd.to_datetime(df_copy['publication_date'], errors='coerce', utc=True, infer_datetime_format=True)
    
    if df_copy['date'].notna().any():
        df_copy['year'] = df_copy['date'].dt.year
        df_copy['month'] = df_copy['date'].dt.month
        return df_copy, 'date'
    else:
        # Try extracting year from strings
        yrs = df_copy['publication_date'].astype(str).str.extract(r'([12]\d{3})')
        df_copy['year'] = pd.to_numeric(yrs[0], errors='coerce')
        return df_copy, 'year'

def create_temporal_chart(df, date_col):
    """Create temporal trend chart."""
    if date_col == 'year':
        temporal = df.groupby('year').size().reset_index(name='count')
        temporal = temporal.dropna(subset=['year'])
        if temporal.empty:
            return None
        
        fig = px.line(temporal, x='year', y='count', 
                     title='Article Count Over Time (by Year)',
                     markers=True)
        fig.update_layout(xaxis_title='Year', yaxis_title='Number of Articles')
        return fig
    elif date_col == 'date':
        # Convert dates to year-month strings for better visualization
        df_copy = df.copy()
        df_copy['year_month'] = df_copy['date'].dt.to_period('M').astype(str)
        temporal = df_copy.groupby('year_month').size().reset_index(name='count')
        
        if temporal.empty:
            return None
        
        fig = px.line(temporal, x='year_month', y='count',
                     title='Article Count Over Time (by Month)',
                     markers=True)
        fig.update_layout(xaxis_title='Date (Year-Month)', yaxis_title='Number of Articles',
                         xaxis_tickangle=-45)
        return fig
    return None

def extract_word_frequencies(df, top_n=20):
    """Extract most common words from article text."""
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Get text column
    text_col = None
    for col in ['clean_text', 'full_text', 'title']:
        if col in df.columns:
            text_col = col
            break
    
    if text_col is None:
        return pd.DataFrame()
    
    # Combine all text
    all_text = ' '.join(df[text_col].astype(str).fillna(''))
    
    # Simple word extraction (can be improved with NLTK)
    words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
    
    # Common stopwords to exclude
    stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 
                'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 
                'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two',
                'who', 'way', 'use', 'her', 'she', 'use', 'use', 'their', 'what'}
    
    words = [w for w in words if w not in stopwords]
    
    word_counts = Counter(words)
    top_words = word_counts.most_common(top_n)
    
    return pd.DataFrame(top_words, columns=['Word', 'Frequency'])

# --- MAIN APP ---
def main():
    st.title("📊 Interactive Trend Analyzer")
    st.markdown("Analyze trends for any topic or field by searching articles in the database.")
    
    # Load data
    df, error = load_data()
    if error:
        st.error(f"❌ {error}")
        st.stop()
    
    if df is None or df.empty:
        st.error("❌ No data found in the database.")
        st.stop()
    
    # Sidebar for inputs
    st.sidebar.header("🔍 Search Parameters")
    
    # Keyword input
    keyword_input = st.sidebar.text_input(
        "Enter Keywords",
        help="Enter one or more keywords separated by commas. Articles containing any of these keywords will be shown.",
        placeholder="e.g., bridge, construction, AI, safety"
    )
    
    # Parse keywords
    keywords = [kw.strip() for kw in keyword_input.split(',')] if keyword_input else []
    
    # Search options
    search_in = st.sidebar.selectbox(
        "Search in",
        options=['both', 'title', 'text'],
        help="Choose where to search for keywords"
    )
    
    # Normalize column names for main dataframe
    df.columns = [c.lower() for c in df.columns]
    
    # Filter data
    if keywords:
        filtered_df = filter_articles_by_keywords(df, keywords, search_in)
    else:
        filtered_df = df.copy()
        st.sidebar.info("💡 Enter keywords in the sidebar to filter articles")
    
    # Parse dates (will normalize columns internally if needed)
    filtered_df, date_col = parse_dates(filtered_df)
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles Found", len(filtered_df))
    with col2:
        if date_col and 'year' in filtered_df.columns:
            years = filtered_df['year'].dropna().unique()
            if len(years) > 0:
                try:
                    year_min = int(years.min())
                    year_max = int(years.max())
                    st.metric("Year Range", f"{year_min}-{year_max}")
                except (ValueError, TypeError):
                    st.metric("Year Range", "N/A")
            else:
                st.metric("Year Range", "N/A")
        else:
            st.metric("Year Range", "N/A")
    with col3:
        if 'source_domain' in filtered_df.columns:
            sources = filtered_df['source_domain'].nunique()
            st.metric("Unique Sources", sources)
        else:
            st.metric("Unique Sources", "N/A")
    with col4:
        if date_col == 'date' and 'date' in filtered_df.columns:
            date_range = filtered_df['date'].dropna()
            if not date_range.empty:
                st.metric("Date Range", f"{date_range.min().date()} to {date_range.max().date()}")
            else:
                st.metric("Date Range", "N/A")
        else:
            st.metric("Date Range", "N/A")
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Temporal Trends", "📊 Frequency Analysis", "🔤 Word Analysis", "📄 Article List"])
    
    with tab1:
        st.header("Temporal Trends")
        if date_col:
            fig = create_temporal_chart(filtered_df, date_col)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No temporal data available for the filtered results.")
        else:
            st.info("No date information available in the dataset.")
        
        # Yearly breakdown if available
        if date_col and 'year' in filtered_df.columns:
            yearly_counts = filtered_df['year'].value_counts().sort_index()
            yearly_counts = yearly_counts[yearly_counts.index.notna()]
            if not yearly_counts.empty:
                st.subheader("Yearly Breakdown")
                try:
                    yearly_df = pd.DataFrame({
                        'Year': yearly_counts.index.astype(int),
                        'Count': yearly_counts.values
                    })
                    st.dataframe(yearly_df, use_container_width=True)
                except (ValueError, TypeError):
                    st.info("Could not display yearly breakdown due to data format issues.")
    
    with tab2:
        st.header("Frequency Analysis")
        
        # Source distribution
        if 'source_domain' in filtered_df.columns:
            st.subheader("Articles by Source")
            source_counts = filtered_df['source_domain'].value_counts().head(15)
            # Filter out None/NaN values
            source_counts = source_counts[source_counts.index.notna()]
            if not source_counts.empty:
                fig = px.bar(x=source_counts.index, y=source_counts.values,
                            labels={'x': 'Source', 'y': 'Article Count'},
                            title='Top 15 Sources')
                fig.update_xaxis(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        
        # Category distribution (if available) - columns already normalized
        ce_col = next((c for c in filtered_df.columns if 'ce' in c and 'topic' in c), None)
        if ce_col:
            st.subheader("Articles by CE Discipline")
            ce_counts = filtered_df[ce_col].value_counts()
            # Filter out empty/None values
            ce_counts = ce_counts[ce_counts.index.notna() & (ce_counts.index != '') & (ce_counts.index != 'Uncategorized')]
            if not ce_counts.empty:
                fig = px.pie(values=ce_counts.values, names=ce_counts.index,
                           title='Distribution by Civil Engineering Discipline')
                st.plotly_chart(fig, use_container_width=True)
        
        ai_col = next((c for c in filtered_df.columns if 'ai' in c and 'topic' in c), None)
        if ai_col:
            st.subheader("Articles by AI Technology")
            ai_counts = filtered_df[ai_col].value_counts()
            # Filter out empty/None values
            ai_counts = ai_counts[ai_counts.index.notna() & (ai_counts.index != '') & (ai_counts.index != 'Uncategorized')]
            if not ai_counts.empty:
                fig = px.bar(x=ai_counts.index, y=ai_counts.values,
                           labels={'x': 'AI Technology', 'y': 'Article Count'},
                           title='Distribution by AI Technology')
                fig.update_xaxis(tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.header("Word Frequency Analysis")
        st.markdown("Most common words in the filtered articles (excluding common stopwords)")
        
        word_freq = extract_word_frequencies(filtered_df, top_n=30)
        if not word_freq.empty:
            fig = px.bar(word_freq, x='Word', y='Frequency',
                        title='Top 30 Most Common Words',
                        labels={'Word': 'Word', 'Frequency': 'Frequency'})
            fig.update_xaxis(tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display as table
            st.subheader("Word Frequency Table")
            st.dataframe(word_freq, use_container_width=True)
        else:
            st.info("No word frequency data available.")
    
    with tab4:
        st.header("Filtered Articles")
        st.markdown(f"Showing {len(filtered_df)} articles matching your search criteria.")
        
        # Display options
        cols_per_row = st.selectbox("Columns to display", options=['Title Only', 'Title + Date', 'Title + Date + Source', 'All Columns'])
        
        # Prepare display dataframe (columns already normalized)
        display_df = filtered_df.copy()
        
        # Search/filter within results
        search_in_results = st.text_input("Search within results", placeholder="Filter articles...")
        if search_in_results:
            if 'title' in display_df.columns:
                mask = display_df['title'].astype(str).str.contains(search_in_results, case=False, na=False)
                display_df = display_df[mask]
        
        # Store full dataframe for text retrieval (before column selection)
        full_display_df = display_df.copy()
        
        # Select columns to display
        if cols_per_row == 'Title Only':
            if 'title' in display_df.columns:
                display_df = display_df[['title']]
        elif cols_per_row == 'Title + Date':
            cols = ['title']
            if 'publication_date' in display_df.columns:
                cols.append('publication_date')
            display_df = display_df[cols]
        elif cols_per_row == 'Title + Date + Source':
            cols = ['title']
            if 'publication_date' in display_df.columns:
                cols.append('publication_date')
            if 'source_domain' in display_df.columns:
                cols.append('source_domain')
            display_df = display_df[cols]
        # 'All Columns' shows everything
        
        st.dataframe(display_df, use_container_width=True, height=600)
        
        # Show full text for selected article (use full_display_df which has all columns)
        if 'title' in full_display_df.columns and len(full_display_df) > 0:
            selected_index = st.selectbox("View full text of article", 
                                         options=range(len(full_display_df)),
                                         format_func=lambda x: full_display_df.iloc[x]['title'][:80] if 'title' in full_display_df.columns else f"Article {x}")
            
            if selected_index is not None and selected_index < len(full_display_df):
                selected_article = full_display_df.iloc[selected_index]
                st.subheader("Full Article Text")
                text_col = None
                for col in ['full_text', 'clean_text']:
                    if col in full_display_df.columns:
                        text_col = col
                        break
                
                if text_col and text_col in full_display_df.columns:
                    full_text = selected_article[text_col]
                    st.text_area("", str(full_text) if pd.notna(full_text) else "N/A", height=300, disabled=True)
                else:
                    st.info("Full text column not available for this article.")

if __name__ == "__main__":
    main()

