# Task 1: Data Description Document

**CE49X Final Project - Civil Engineering & AI Trend Analysis**  
**Team:** Hakan ARMAN, İbrahim ÇAYIR  
**Date:** December 2025

---

## 1. Data Collection Summary

**Total Articles Collected:** 750 (after validation and cleaning)  
**Initial Collection:** ~3,000+ articles from various sources  
**Final Validated Dataset:** 750 articles meeting CE+AI relevance criteria  
**Collection Period:** Multiple sessions during Fall 2025

---

## 2. Data Sources

### 2.1 RSS Feeds (Primary Source)

We collected articles from the following RSS feeds:

#### Industry News Portals:
- **Engineering News-Record (ENR)**: https://www.enr.com/rss
  - Topic-specific feed: https://www.enr.com/rss/topic/587 (Construction Technology)
- **Construction Dive**: https://www.constructiondive.com/feeds/news/
- **BIMplus**: https://www.bimplus.co.uk/feed/
- **New Civil Engineer**: https://www.newcivilengineer.com/feed/
- **Construction Enquirer**: https://www.constructionenquirer.com/feed/
- **Global Construction Review**: https://www.globalconstructionreview.com/feed
- **Civil Engineering Blog**: https://civilengineerblog.com/feed

#### Technology-Focused Feeds:
- **AEC Magazine**: https://www.aecmag.com/feed/
- **AEC Business**: https://aec-business.com/feed
- **Stack Construction Tech**: https://stackct.com/feed
- **Geospatial World**: https://www.geospatialworld.net/feed/
- **Revit/BIM News**: https://revit.news/feed
- **The Revit Kid**: https://feeds.feedburner.com/TheRevitKid

#### Professional/Corporate Blogs:
- **PlanGrid/Autodesk Blog**: https://blog.plangrid.com/feed/
- **Trimble Constructible**: https://constructible.trimble.com/blog/rss.xml
- **O'Reilly Radar**: http://feeds.feedburner.com/oreilly/radar/atom

#### Architecture & Design:
- **ArchDaily**: https://feeds.feedburner.com/Archdaily
- **Dezeen**: https://www.dezeen.com/feed/
- **The Architect's Newspaper**: https://archpaper.com/feed

### 2.2 Google News RSS Queries

We utilized Google News RSS feeds with custom search queries combining Civil Engineering and AI terms:

**General Queries:**
- "Construction Artificial Intelligence"
- "Civil Engineering Machine Learning"
- "BIM Digital Twins"
- "Construction Robotics"

**Construction Management Focus:**
- "Construction Management Artificial Intelligence"
- "Construction Safety Computer Vision"
- "Construction Scheduling Optimization AI"
- "Construction Health and Safety Artificial Intelligence"
- "Construction Site Safety Machine Learning"
- "PPE Detection AI Construction"

**Structural Engineering Focus:**
- "Structural Engineering Machine Learning"
- "Structural Health Monitoring AI"
- "Concrete Strength Prediction AI"
- "Generative Design Structural Engineering"
- "Structural Engineering Artificial Intelligence"
- "Earthquake Engineering Machine Learning"

**Geotechnical Focus:**
- "Geotechnical Engineering Machine Learning"
- "Soil Analysis Artificial Intelligence"
- "Tunneling Automation AI"
- "Geotechnical Engineering Artificial Intelligence"

**Transportation Focus:**
- "Smart Highway Infrastructure AI"
- "Bridge Inspection Drone AI"
- "Traffic Engineering Machine Learning"
- "Transportation Engineering Artificial Intelligence"
- "Smart Infrastructure Machine Learning"

**BIM & Digital Twins:**
- "Building Information Modeling Artificial Intelligence"
- "BIM Machine Learning"
- "Digital Twins Construction Artificial Intelligence"
- "Scan to BIM AI"
- "Digital Twin Safety Monitoring Construction"

**Sustainability & Environmental:**
- "Green Building AI Optimization"
- "Energy Efficient Buildings Machine Learning"
- "Net Zero Construction AI"

*Full query list available in: `Scripts/scraper_rss.py` and `Scripts/scraper_gnews.py`*

### 2.3 Scientific Publications (arXiv)

**Source:** arXiv API  
**API Endpoint:** http://export.arxiv.org/api/query  
**Method:** Automated query via Python feedparser library

**Search Strategy:**
- **Categories:** Computer Science - Artificial Intelligence (cs.AI), Computer Vision (cs.CV), Machine Learning (cs.LG)
- **Method Terms:** "finite element", "topology optimization", "structural health monitoring", "crack detection", "damage detection", "predictive maintenance", "digital twin", "BIM", "computer vision", "reinforcement learning", "deep learning", "neural network"
- **Application Terms:** "bridge", "pavement", "tunnel", "geotechnical", "soil", "retaining wall", "highway", "railway", "airport", "building", "foundation", "slope", "structural", "load-bearing"

**Collection:** 200 academic papers from arXiv  
**Query Structure:** `(cat:cs.AI OR cat:cs.CV OR cat:cs.LG) AND (method_query OR app_query)`

---

## 3. Search Keywords Used

### 3.1 Civil Engineering Terms
- Construction
- Structural
- Geotechnical
- Transportation
- Infrastructure
- Concrete
- Bridge
- Tunnel
- Civil Engineering
- Foundation
- Pavement
- Highway
- Building
- Site
- Safety
- BIM (Building Information Modeling)
- Digital Twin

### 3.2 AI Terms
- Artificial Intelligence
- Machine Learning
- Computer Vision
- Generative AI
- Neural Networks
- Robotics
- Automation
- Deep Learning
- Predictive Analytics
- Predictive Maintenance
- Natural Language Processing
- AI Algorithm

### 3.3 Combined Query Strategy

We systematically combined CE terms with AI terms to create 50+ unique search queries. Examples:
- "Construction + Artificial Intelligence"
- "Structural + Machine Learning"
- "Computer Vision + Construction Safety"
- "Transportation + Autonomous"
- "BIM + AI Integration"

*Full list available in scraping scripts*

---

## 4. Data Collection Methods

### 4.1 RSS Feed Parsing
- **Library:** `feedparser` (Python)
- **Process:** Iterate through RSS feed URLs, parse entries, extract title, date, link, and content
- **Filtering:** Initial keyword-based relevance check (must contain AI-related terms)
- **Deduplication:** URL-based uniqueness checking

### 4.2 Google News Aggregation
- **Library:** `GoogleNews` (Python)
- **Process:** 
  1. Search Google News for each query
  2. Extract article URLs
  3. Download full text using `newspaper3k`
  4. Validate relevance (must contain both CE and AI terms)
- **Rate Limiting:** 1-second delay between requests

### 4.3 arXiv API
- **Library:** `feedparser` with custom arXiv query URLs
- **Process:**
  1. Construct API query URL with encoded search terms
  2. Parse XML response
  3. Extract title, date, abstract, and URL
  4. Store abstracts as full text content

### 4.4 Web Scraping (Limited Use)
- **Library:** `newspaper3k`, `BeautifulSoup`
- **Use Case:** Secondary method when direct feeds unavailable
- **Note:** Limited due to rate limiting and structural inconsistencies

---

## 5. Data Storage Format

**Format:** SQLite Database  
**Database File:** `Data/corpus.db`  
**Schema:**

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    publication_date TEXT,
    source_domain TEXT,
    url TEXT UNIQUE,
    full_text TEXT,
    search_keywords TEXT,
    category_tag TEXT
);
```

**Field Descriptions:**
- `id`: Unique identifier
- `title`: Article headline
- `publication_date`: Publication date (format varies by source)
- `source_domain`: Publisher/source name
- `url`: Original article URL
- `full_text`: Complete article text content or abstract
- `search_keywords`: Query/keywords used to find the article
- `category_tag`: Source type (e.g., "Blog_RSS", "Scientific", "Aggregated_News")

---

## 6. Data Validation & Cleaning

### 6.1 Initial Validation
- **Minimum Length:** Articles must have at least 200 characters of text
- **Relevance Check:** Must contain at least one CE term AND one AI term
- **Deduplication:** URL uniqueness enforced at database level

### 6.2 Post-Collection Cleaning
1. **Pandas-Based Cleaning:**
   - Remove duplicates based on title similarity
   - Remove very short articles (<200 characters)
   - Standardize date formats

2. **LLM-Assisted Validation:**
   - Used Google Gemini 3 Flash API
   - Semantic relevance checking
   - Deduplication (semantic similarity detection)
   - Topic assignment validation
   - Removed ~20% of articles that failed validation

**Final Dataset:** 750 validated articles

---

## 7. Data Collection Scripts

All data collection scripts are located in the `/Scripts/` directory:

1. **`scraper_rss.py`**: RSS feed collection
2. **`scraper_gnews.py`**: Google News aggregation
3. **`scraper_arxiv.py`**: arXiv scientific paper collection
4. **`init_db.py`**: Database initialization

---

## 8. Data Collection Statistics

| Source Type | Initial Collection | Final Validated | Percentage |
|------------|-------------------|-----------------|------------|
| RSS Feeds | ~2,500+ | ~550 | ~73% |
| Google News | ~300+ | ~150 | ~20% |
| arXiv | 200 | ~50 | ~7% |
| **Total** | **~3,000+** | **750** | **100%** |

*Note: These are approximate numbers. Exact counts may vary based on collection sessions and filtering criteria.*

---

## 9. Challenges Encountered

1. **Rate Limiting:** Some sources rate-limited requests, requiring delays
2. **Inconsistent Formats:** RSS feeds vary in structure, requiring flexible parsing
3. **Relevance Filtering:** Balancing strictness (removing noise) vs. inclusivity (maintaining dataset size)
4. **Date Parsing:** Publication dates in various formats required normalization
5. **Text Extraction:** Some articles required manual parsing due to paywalls or complex HTML structures

---

## 10. Data Quality Measures

- **Relevance:** All articles validated for CE+AI intersection
- **Completeness:** Required fields (title, text, URL) present for all entries
- **Uniqueness:** URL-based deduplication ensures no duplicate articles
- **Freshness:** Articles collected from active, up-to-date sources
- **Diversity:** Multiple sources ensure broad coverage of perspectives

---

**Document Prepared By:** Hakan ARMAN, İbrahim ÇAYIR  
**Last Updated:** December 2025

