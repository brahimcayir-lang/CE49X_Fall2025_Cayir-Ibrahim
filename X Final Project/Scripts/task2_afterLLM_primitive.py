import sqlite3
import pandas as pd
import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from datetime import datetime
import shutil

# --- 1. CONFIGURATION & SETUP ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'corpus_LLM.db')

# Output Directory for Reports
OUTPUT_DIR = r"C:\Users\Hakan\Desktop\CE49X Final Project\Outputs\AfterLLM_Primitive"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
REPORT_FILE = os.path.join(OUTPUT_DIR, "Task2_Analysis_Report_AfterDetailedLMM.txt")

print("📥 Checking NLTK resources...")
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

# --- DEFINING THE TRASH BIN (AGGRESSIVE) ---
stop_words = set(stopwords.words('english'))

# 1. Standard Noise & Generic Verbs
domain_noise = {
    "subscribe", "click", "here", "share", "article", "read", "more", 
    "advertisement", "newsletter", "sign", "login", "register", "copyright",
    "reserved", "rights", "author", "published", "posted", "follow", "email",
    "free", "access", "cookies", "policy", "terms", "loading", "said", "also",
    "would", "could", "should", "using", "used", "made", "make", "like", "div",
    "one", "two", "new", "year", "time", "work", "people", "many", "way", "get",
    "company", "market", "business", "service", "project"
}

# 2. HTML, Scraper Artifacts & "Glued" Words
scraper_junk = {
    "class", "span", "href", "http", "https", "url", "copied", 
    "opener", "noreferrer", "rel", "target", "blank", "img", "src", "width", 
    "height", "alt", "caption", "figure", "wp", "content", "summary", 
    "assisted", "full", "appeared", "first", "post", "per", "cent",
    "elementor", "widget", "container", "utc", "azerbaijan",
    "estopens", "window", "december", "january", "february", "march", "april", 
    "may", "june", "july", "august", "september", "october", "november",
    "ago", "hour", "minute", "lia", "relnoopener", "opens", "link", "date", "yet"
}

stop_words.update(domain_noise)
stop_words.update(scraper_junk)

lemmatizer = WordNetLemmatizer()

# --- 2. THE PIPELINE ---
def preprocess_text(text):
    if not text: return ""
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\b(rel|target|class)=["\'].*?["\']', '', text)
    text = re.sub(r'\b(est)?opens\s+in\s+new\s+window\b', '', text)
    text = re.sub(r'[^a-z\s]', '', text)

    try:
        tokens = word_tokenize(text)
    except LookupError:
        nltk.download('punkt_tab', quiet=True)
        tokens = word_tokenize(text)

    clean_tokens = []
    for token in tokens:
        if (token not in stop_words) and (len(token) > 2) and \
           ("noreferrer" not in token) and ("noopener" not in token) and ("elementor" not in token):
            root_word = lemmatizer.lemmatize(token)
            clean_tokens.append(root_word)
            
    return " ".join(clean_tokens)

# --- 3. HELPER FOR REPORTING ---
def write_report(f, text):
    """Writes to both console and file"""
    print(text)
    f.write(text + "\n")

# --- 4. MAIN EXECUTION ---
def run_task2_pipeline():
    print("⚙️ Loading data from corpus.db...")
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT id, title, full_text FROM articles_labeled", conn)
        conn.close()
    except Exception as e:
        print(f"❌ Error reading DB: {e}")
        return

    if df.empty:
        print("⚠️ Database is empty!")
        return

    print(f"📚 Re-Cleaning {len(df)} articles_labeled...")
    df['clean_text'] = df['full_text'].apply(preprocess_text)

    print("💾 Saving cleaned data to DB...")
    shutil.copyfile(DB_PATH, DB_PATH + '.bak')  # create a backup copy before modifying
    conn = sqlite3.connect(DB_PATH)
    # write to a new table name to keep the original intact
    df[['id', 'title', 'clean_text']].to_sql('articles_labeled_clean', conn, if_exists='replace', index=False)
    conn.close()

    # --- START REPORT GENERATION ---
    print(f"\n📝 Generating Report at: {REPORT_FILE}")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        write_report(f, "="*50)
        write_report(f, f"CE49X TASK 2 REPORT - GENERATED ON {datetime.now()}")
        write_report(f, "="*50 + "\n")
        
        # Helper function for N-grams
        def get_top_ngrams(corpus, n=1, limit=20):
            try:
                vec = CountVectorizer(ngram_range=(n, n)).fit(corpus)
                bag_of_words = vec.transform(corpus)
                sum_words = bag_of_words.sum(axis=0) 
                words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
                return sorted(words_freq, key = lambda x: x[1], reverse=True)[:limit]
            except ValueError: return []

        # A. Top 20 Words
        top_words = get_top_ngrams(df['clean_text'], n=1, limit=20)
        df_words = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
        
        write_report(f, "🏆 TOP 20 MOST FREQUENT WORDS (CLEANED)")
        write_report(f, "-"*40)
        write_report(f, df_words.to_string(index=False))
        write_report(f, "\n" + "-"*40 + "\n")

        # B. Top 20 Bi-grams
        top_bigrams = get_top_ngrams(df['clean_text'], n=2, limit=20)
        df_bigrams = pd.DataFrame(top_bigrams, columns=['Bi-gram', 'Frequency'])
        
        write_report(f, "🔗 TOP 20 BI-GRAMS (TWO-WORD PHRASES)")
        write_report(f, "-"*40)
        write_report(f, df_bigrams.to_string(index=False))
        write_report(f, "\n" + "-"*40 + "\n")

        # C. TF-IDF
        write_report(f, "🧮 TF-IDF EXAMPLE (FEATURE EXTRACTION)")
        write_report(f, "-"*40)
        
        tfidf = TfidfVectorizer(max_features=1000) 
        tfidf_matrix = tfidf.fit_transform(df['clean_text'])
        feature_names = tfidf.get_feature_names_out()
        
        # Example for the first article
        first_title = df['title'][0][:60]
        write_report(f, f"Article: '{first_title}...'")
        
        first_doc_vector = tfidf_matrix[0]
        df_tfidf = pd.DataFrame(first_doc_vector.T.todense(), index=feature_names, columns=["tfidf"])
        top_tfidf = df_tfidf.sort_values(by=["tfidf"], ascending=False).head(5)
        
        write_report(f, top_tfidf.to_string())
        write_report(f, "\n" + "="*50)

    print("\n✅ Task 2 Complete. Report saved successfully.")

if __name__ == "__main__":
    run_task2_pipeline()