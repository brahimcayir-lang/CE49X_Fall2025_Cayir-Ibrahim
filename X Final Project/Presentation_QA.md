# CE49X Final Project - Presentation Q&A Guide

**Project:** Civil Engineering & AI Integration: Analyzing Industry Trends through News & Media  
**Team:** Hakan ARMAN, İbrahim ÇAYIR  
**Course:** CE49X - Introduction to Data Science for Civil Engineering  
**Institution:** Boğaziçi University, Fall 2025

---

## 1. PROJECT AIM & OBJECTIVES

### Q: What is the main aim of your project?

**A:** Our main aim is to quantitatively assess AI usage trends in Civil Engineering by processing textual data and visualizing patterns that identify which sub-disciplines are leading in AI integration. We analyzed 750 curated articles from industry news, academic publications, and technical blogs to understand how AI technologies are being adopted across different Civil Engineering areas.

### Q: What specific research question are you trying to answer?

**A:** The primary research question is: **"Which Civil Engineering sub-discipline uses AI most, and what are the dominant AI technologies in each area?"** We also examine trends in AI adoption, co-occurrence patterns between CE areas and AI technologies, and temporal evolution of AI mentions.

### Q: Why did you choose this topic?

**A:** Civil Engineering is experiencing a digital transformation, and understanding AI adoption patterns helps identify:
- Which areas are leading in innovation
- What technologies are most commonly deployed
- Where there are opportunities for future development
- How the industry is evolving

This analysis provides valuable insights for practitioners, researchers, and industry stakeholders.

---

## 2. METHODOLOGY QUESTIONS

### Q: Can you explain your methodology step by step?

**A:** Our methodology follows a four-stage pipeline:

1. **Data Collection:** Multi-source approach using RSS feeds (3,000+ articles), arXiv API (200 papers), and Google News aggregator. We used 50+ unique query combinations combining CE and AI terms.

2. **Preprocessing:** Advanced NLP cleaning using NLTK:
   - Tokenization (sentence and word-level)
   - Normalization (lowercase, URL removal, HTML/XML artifact removal)
   - Stopword removal (English + domain-specific noise words)
   - Lemmatization (WordNetLemmatizer)
   - Feature extraction (N-grams, TF-IDF)

3. **Categorization:** Dictionary-based classification:
   - 5 CE areas: Structural, Geotechnical, Transportation, Construction Management, Environmental
   - 5 AI technologies: Computer Vision, Predictive Analytics, Generative Design, Robotics/Automation, Machine Learning
   - Multi-label classification (articles can belong to multiple categories)

4. **Visualization & Analysis:** Generated bar charts, heatmaps, network graphs, word clouds, and temporal trend plots.

### Q: How did you collect the data?

**A:** We used three main sources:

1. **RSS Feeds:** Industry news portals (ENR, Construction Dive, BIMplus, New Civil Engineer, AEC Magazine) and professional blogs (Autodesk, Bentley, Trimble)

2. **arXiv API:** 200 academic papers from computer science categories (cs.AI, cs.CV, cs.LG) with Civil Engineering applications

3. **Google News Aggregator:** Python library (`GoogleNews`) with custom keyword searches combining CE and AI terms

All data was stored in a SQLite database with fields: title, publication_date, source_domain, url, full_text, search_keywords, category_tag.

### Q: How did you ensure data quality?

**A:** We implemented several quality control measures:

- **Relevance Filtering:** Each article required mentions of both CE and AI terms
- **Length Requirement:** Minimum 200-character length to filter out short/incomplete articles
- **Deduplication:** URL-based uniqueness checking to remove duplicates
- **LLM-Assisted Validation:** Used Google Gemini 3 Flash API for semantic validation, removing ~20% of articles that failed relevance checks
- **Data Validation:** Final dataset of 750 validated articles after cleaning

### Q: How does your categorization method work?

**A:** We use a **dictionary-based classification approach**:

- We developed comprehensive keyword dictionaries for each CE area and AI technology
- Each article is scanned for keyword presence in both dictionaries
- Articles can be tagged with multiple categories (multi-label classification)
- We generate a co-occurrence matrix to track CE-AI technology pairs

**Example:** An article mentioning "construction site monitoring using computer vision" would be tagged as:
- CE Area: Construction Management
- AI Technology: Computer Vision

### Q: Why did you use dictionary-based classification instead of machine learning?

**A:** Dictionary-based classification was chosen because:

1. **Interpretability:** We can see exactly which keywords led to each classification
2. **Domain Expertise:** We leveraged domain knowledge to create targeted keyword lists
3. **Transparency:** The classification logic is clear and explainable
4. **Simplicity:** No need for labeled training data
5. **Speed:** Fast classification without model training

However, we acknowledge this is a limitation - it may miss nuanced categorizations that ML models could capture.

### Q: Did you use any LLM/AI in your project?

**A:** Yes, we used **Google Gemini 3 Flash API** for semantic validation:

- **Relevance auditing:** Ensured articles truly discussed both CE and AI intersection
- **Semantic deduplication:** Identified similar articles with different URLs
- **Topic assignment validation:** Verified category assignments
- This helped remove ~20% of articles that failed relevance checks

We used LLM as a validation tool, not as the primary classification method, to ensure data quality.

---

## 3. TOOLS & LIBRARIES USED

### Q: What programming language and tools did you use?

**A:** 
- **Language:** Python 3
- **Database:** SQLite
- **Development Environment:** VS Code / Jupyter Notebooks

### Q: What Python libraries did you use and why?

**A:** We used the following libraries:

**Data Manipulation & Database:**
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical operations
- `sqlite3` - Database management

**Web Scraping & APIs:**
- `feedparser` - RSS feed parsing
- `newspaper3k` - Automated article text extraction
- `GoogleNews` - News aggregation
- `requests` - HTTP requests for API calls
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

**Natural Language Processing (NLP):**
- `nltk` - Tokenization, stopwords, lemmatization (WordNetLemmatizer)
- `scikit-learn` - TF-IDF vectorization (TfidfVectorizer), CountVectorizer for N-grams

**Visualization:**
- `matplotlib` - Plotting and figure generation
- `seaborn` - Statistical visualization (heatmaps)
- `networkx` - Network/graph visualization
- `wordcloud` - Word cloud generation

**LLM Integration:**
- `google-generativeai` - Google Gemini 3 Flash API for semantic validation

**Utilities:**
- `tqdm` - Progress bars for long-running operations

### Q: Why did you choose NLTK over spaCy for NLP?

**A:** We chose NLTK because:
- It provides comprehensive tools for tokenization, stopword removal, and lemmatization that we needed
- Well-documented and widely used in academic settings
- Easy to use for our preprocessing pipeline
- We didn't need advanced features like named entity recognition or dependency parsing that spaCy offers
- NLTK's WordNetLemmatizer worked well for our use case

However, we acknowledge that spaCy could have been used as an alternative.

### Q: Why SQLite instead of other databases?

**A:** SQLite was chosen because:
- **Lightweight:** No server setup required, perfect for local development
- **Simplicity:** Easy to set up and use for our dataset size (750 articles)
- **Python Integration:** Excellent support in Python
- **File-based:** Easy to share and backup (single file)
- **Sufficient:** Our data volume didn't require a more powerful database system

For larger-scale projects, PostgreSQL or MongoDB might be more appropriate.

---

## 4. TOOLS NOT USED (AND WHY)

### Q: Did you consider using machine learning models for classification?

**A:** Yes, we considered it, but chose dictionary-based approach because:
- **No labeled training data:** Would require manual labeling of hundreds of articles
- **Interpretability:** Dictionary-based approach is more transparent
- **Speed:** Faster than training ML models
- **Domain knowledge:** We could leverage our understanding of CE terminology

**However**, for future work, we could use:
- **Supervised learning:** Train a classifier on manually labeled data
- **Topic modeling:** Use LDA (Latent Dirichlet Allocation) for automatic topic discovery
- **Embeddings:** Use word embeddings (Word2Vec, GloVe, BERT) for semantic similarity

### Q: Why didn't you use deep learning models?

**A:** Deep learning wasn't necessary for this project because:
- Our classification task could be solved with simpler methods
- Deep learning requires large labeled datasets
- Training time and computational resources would be higher
- Dictionary-based approach provided sufficient accuracy for our needs

For future work, transformer models (BERT, RoBERTa) could improve classification accuracy.

### Q: Did you use any cloud services?

**A:** No, we used local processing:
- **Why:** Our dataset size (750 articles) was manageable locally
- **Privacy:** All processing done on local machines
- **Cost:** No cloud computing costs
- **Simplicity:** No need for cloud infrastructure setup

For larger datasets, cloud services (AWS, Google Cloud) could be beneficial.

### Q: Why not use Jupyter Notebooks for the entire project?

**A:** We used a mix:
- **Scripts (.py files):** For the main pipeline - easier to version control, more modular, can be run from command line
- **Jupyter Notebooks:** For exploratory analysis and visualization
- **Why scripts:** Better for reproducibility, easier to share with collaborators, standard Python development practices

### Q: Did you use any version control?

**A:** This wasn't mentioned in the report, but best practice would be Git. It's useful for:
- Tracking changes to code
- Collaboration between team members
- Backup and recovery
- Reproducibility

---

## 5. ADVANTAGES & STRENGTHS

### Q: What are the main advantages of your approach?

**A:**

1. **Comprehensive Data Collection:** Multi-source approach (RSS, arXiv, Google News) ensures broad coverage

2. **Rigorous Preprocessing:** Advanced NLP pipeline removes noise and standardizes text

3. **Interpretable Results:** Dictionary-based classification is transparent and explainable

4. **Quality Validation:** LLM-assisted validation ensures data relevance

5. **Rich Visualizations:** Multiple visualization types (charts, heatmaps, networks, word clouds) provide comprehensive insights

6. **Quantitative Analysis:** Objective, data-driven approach with clear metrics

7. **Reproducible Pipeline:** Well-documented scripts can be rerun with new data

### Q: What makes your methodology robust?

**A:**
- **Multi-source data:** Reduces bias from single source
- **Quality control:** Multiple validation steps (length, deduplication, LLM validation)
- **Transparent classification:** Dictionary-based approach is explainable
- **Comprehensive preprocessing:** Handles various text artifacts and noise
- **Scalable pipeline:** Can be extended to larger datasets

### Q: What are the unique aspects of your project?

**A:**
1. **Industry + Academic Coverage:** Combined industry news with academic publications (arXiv)
2. **LLM-Assisted Validation:** Used modern AI tools for quality control
3. **Multi-label Classification:** Articles can belong to multiple categories (more realistic)
4. **Comprehensive Visualizations:** Multiple visualization types for different insights
5. **Quantitative + Qualitative:** Both statistical analysis and qualitative insights

---

## 6. LIMITATIONS & DISADVANTAGES

### Q: What are the limitations of your study?

**A:** We identified several limitations in our report:

1. **Data Source Bias:** Industry news may over-represent commercial applications vs. academic research

2. **Keyword-Based Classification:** Dictionary-based approach may miss nuanced categorizations that ML models could capture

3. **Temporal Coverage:** Publication dates vary across sources, limiting temporal analysis accuracy

4. **Language:** Analysis limited to English-language sources only

5. **Sample Size:** While 750 articles is substantial, some categories (especially Geotechnical with only 6 articles) have very small samples

6. **Static Dictionaries:** Keyword lists may not capture emerging terminology or synonyms

7. **Multi-label Ambiguity:** Some articles might be incorrectly tagged or miss relevant categories

### Q: How accurate do you think your classification is?

**A:** While we didn't calculate formal accuracy metrics, we acknowledge that:
- Dictionary-based classification is less sophisticated than ML models
- Some articles may be misclassified or miss relevant categories
- We used LLM validation to improve quality, but some errors likely remain
- For future work, we'd validate with manual labeling and calculate precision/recall metrics

### Q: Why did Geotechnical Engineering have so few articles (only 6)?

**A:** Possible reasons:
- **Data scarcity:** Geotechnical work often involves site-specific investigations with limited online coverage
- **Industry conservatism:** Geotechnical engineering has strict safety margins, limiting AI experimentation
- **Academic vs. Industry:** Research may exist but not translate to industry news
- **Search query bias:** Our keywords might not have captured all geotechnical AI applications

This gap represents a significant opportunity for future research.

---

## 7. GENERAL ANALYSIS QUESTIONS

### Q: What were your main findings?

**A:** Key findings:

1. **Construction Management dominates:** 70.27% (527 articles) of all AI-related content
2. **Transportation is second:** 12.13% (91 articles), driven by autonomous infrastructure
3. **Structural Engineering:** 9.20% (69 articles), focusing on SHM and digital twins
4. **Environmental Engineering:** 7.60% (57 articles), sustainability-driven applications
5. **Geotechnical Engineering:** Only 0.80% (6 articles) - significant gap

**AI Technologies:**
- Machine Learning (general): Most cited (323 mentions)
- Robotics/Automation: Second (172 mentions)
- Computer Vision & Predictive Analytics: Tied at 98 mentions each

### Q: Why do you think Construction Management dominates?

**A:** Several converging factors:

1. **Data-Rich Environment:** IoT sensors, image/video streams, BIM models generate massive data
2. **Safety & Compliance:** High injury rates drive AI safety applications (PPE detection, hazard identification)
3. **Economic Imperatives:** Cost reduction, scheduling optimization, delay minimization
4. **Digital Transformation:** BIM and Digital Twins create natural foundation for AI integration

### Q: What does the heatmap tell us?

**A:** The co-occurrence heatmap shows:
- **Strong pairings:**
  - Construction Management × Computer Vision (site monitoring, safety)
  - Construction Management × Predictive Analytics (risk assessment, cost prediction)
  - Transportation × Robotics/Automation (autonomous vehicles)
  - Structural × Machine Learning (SHM applications)
- **Weak pairings:** Geotechnical × any AI technology (consistently low)

### Q: What insights do the word clouds provide?

**A:** Word clouds show discipline-specific themes:

- **Construction Management:** "safety", "site", "monitoring", "digital", "BIM"
- **Transportation:** "traffic", "highway", "autonomous", "smart"
- **Structural:** "monitoring", "health", "bridge", "digital twin"
- **Environmental:** "energy", "sustainability", "green", "carbon"
- **Geotechnical:** Sparse (reflecting low article count)

### Q: What are the temporal trends?

**A:** Temporal analysis shows:
- Increasing trend in AI mentions across all disciplines over time
- Construction Management shows the steepest growth curve
- Transportation demonstrates steady upward trajectory
- Structural maintains consistent but lower volume

*Note: Limited by publication date availability in some sources.*

---

## 8. TECHNICAL QUESTIONS

### Q: How did you handle text preprocessing?

**A:** Our preprocessing pipeline:

1. **Tokenization:** NLTK's Punkt tokenizer for sentence and word tokenization
2. **Normalization:** Lowercase conversion, URL removal, HTML/XML artifact removal
3. **Stopword Removal:** English stopwords + domain-specific noise words (HTML artifacts, scraper junk, generic verbs)
4. **Lemmatization:** WordNetLemmatizer to reduce words to root forms (e.g., "buildings" → "building")
5. **Feature Extraction:** 
   - N-grams (2-word and 3-word phrases) using CountVectorizer
   - TF-IDF scores using TfidfVectorizer (max_features=1000)

### Q: How did you extract features from text?

**A:** We used two approaches:

1. **N-grams:** Identified 2-word and 3-word phrases (e.g., "digital twin", "structural health monitoring")
2. **TF-IDF:** Term Frequency-Inverse Document Frequency to identify important keywords per document
   - Used scikit-learn's TfidfVectorizer
   - max_features=1000 to limit dimensionality

### Q: How did you create the visualizations?

**A:**

- **Bar Charts:** matplotlib - Shows article counts per CE discipline
- **Heatmaps:** seaborn - Co-occurrence matrix (CE areas × AI technologies)
- **Network Graphs:** networkx - Semantic term relationships
- **Word Clouds:** wordcloud library - Discipline-specific frequent terms
- **Temporal Trends:** matplotlib line plots - Evolution over time

### Q: How did you handle duplicate articles?

**A:** 
- **URL-based deduplication:** Checked for unique URLs in the database
- **LLM-assisted semantic deduplication:** Used Gemini API to identify similar articles with different URLs
- This ensured we didn't double-count the same content

### Q: How long did data collection take?

**A:** Data was collected over multiple sessions:
- RSS feeds: Automated collection via feedparser
- arXiv: API calls for 200 papers
- Google News: Variable per query session
- Total initial collection: ~3,000+ articles, filtered down to 750 relevant ones

Actual time depends on network speed and API rate limits.

---

## 9. RESULTS & FINDINGS

### Q: What is your most surprising finding?

**A:** The extreme dominance of Construction Management (70.27%) was surprising, as was the minimal representation of Geotechnical Engineering (only 6 articles, 0.80%). This huge gap suggests a significant opportunity for AI innovation in geotechnical applications.

### Q: What are the practical implications of your findings?

**A:**

**For Practitioners:**
- Construction Management: Continue investing in Computer Vision for safety, Predictive Analytics for optimization
- Transportation: Prepare for autonomous infrastructure
- Structural: Explore Digital Twin and SHM applications
- Environmental: Leverage AI for energy efficiency
- Geotechnical: Significant opportunity for AI innovation

**For Researchers:**
- Address the Geotechnical gap
- Deepen Digital Twin research
- Improve data collection standardization
- Focus on explainable AI for safety-critical applications

### Q: How do your results compare to industry expectations?

**A:** The results align with industry trends:
- Construction's focus on safety and efficiency (Computer Vision, Predictive Analytics)
- Transportation's investment in smart infrastructure
- Structural's emphasis on monitoring and digital twins

However, the Geotechnical gap is larger than expected, suggesting an underserved area.

### Q: What is the statistical significance of your findings?

**A:** While we have a substantial dataset (750 articles), we acknowledge:
- Some categories have small samples (Geotechnical: 6 articles)
- No formal statistical significance tests were performed
- Results are descriptive rather than inferential
- For future work, we'd perform statistical tests (chi-square, etc.)

---

## 10. FUTURE WORK & IMPROVEMENTS

### Q: What would you do differently if you did this project again?

**A:**

1. **Improved Classification:** Use supervised learning with manually labeled training data
2. **Larger Dataset:** Collect more articles, especially for underrepresented categories
3. **Better Temporal Analysis:** Ensure consistent publication dates across all sources
4. **Multilingual:** Expand to non-English sources
5. **Validation Metrics:** Calculate precision, recall, F1-score for classification
6. **Alternative Methods:** Compare dictionary-based vs. ML-based classification
7. **Longitudinal Study:** Track trends over multiple years

### Q: What are your future research directions?

**A:** We identified several in our report:

1. **Longitudinal Analysis:** Track AI adoption year-over-year
2. **Cross-Disciplinary Analysis:** Examine how AI applications transfer between CE sub-disciplines
3. **Geotechnical AI Development:** Targeted research for this gap
4. **Qualitative Case Studies:** Deep-dive into specific implementations
5. **Cost-Benefit Analysis:** Quantify ROI of AI implementations
6. **Regulatory Impact Study:** Analyze how regulations affect adoption

### Q: How could this project be extended?

**A:**

1. **Machine Learning Models:** Train classifiers for automated categorization
2. **Topic Modeling:** Use LDA to discover themes automatically
3. **Sentiment Analysis:** Analyze positive/negative sentiment toward AI adoption
4. **Network Analysis:** Deeper analysis of co-authorship, citation networks
5. **Real-time Monitoring:** Continuous data collection and analysis
6. **Interactive Dashboard:** Web application for exploration (could use Streamlit)
7. **Comparative Analysis:** Compare with other engineering disciplines

### Q: What improvements would enhance your methodology?

**A:**

1. **Active Learning:** Use ML models with human-in-the-loop for better classification
2. **Embeddings:** Use word embeddings (BERT, Word2Vec) for semantic similarity
3. **Ensemble Methods:** Combine multiple classification approaches
4. **Better Preprocessing:** Advanced techniques like coreference resolution
5. **Validation Dataset:** Manual labeling of subset for accuracy measurement
6. **Ablation Studies:** Test impact of different preprocessing steps

---

## 11. CHALLENGES ENCOUNTERED

### Q: What were the biggest challenges you faced?

**A:**

1. **Data Quality:** Many articles had HTML artifacts, scraper noise, and irrelevant content - required extensive preprocessing
2. **Classification Accuracy:** Dictionary-based approach had limitations in handling nuanced articles
3. **Data Imbalance:** Construction Management dominated, while Geotechnical had very few articles
4. **LLM API Limits:** Rate limits and costs when using Gemini API for validation
5. **Temporal Data:** Inconsistent publication dates across sources
6. **Keyword Selection:** Determining comprehensive keyword lists for each category

### Q: How did you overcome these challenges?

**A:**

1. **Data Quality:** Aggressive preprocessing pipeline with domain-specific stopword lists
2. **Classification:** Used LLM validation to improve quality, accepted limitations of dictionary-based approach
3. **Data Imbalance:** Acknowledged as limitation, used it as finding (Geotechnical gap)
4. **LLM Limits:** Used efficient batch processing, focused on validation rather than full classification
5. **Temporal Data:** Acknowledged limitation, provided analysis where dates were available
6. **Keywords:** Iterative refinement based on domain knowledge and manual review

---

## 12. LIBRARY-SPECIFIC QUESTIONS

### Q: Why NLTK instead of spaCy?

**A:** 
- NLTK provided all features we needed (tokenization, stopwords, lemmatization)
- Well-documented and widely used
- We didn't need advanced features like NER or dependency parsing
- WordNetLemmatizer worked well for our use case

### Q: Why pandas instead of other data manipulation tools?

**A:**
- Industry standard for data manipulation in Python
- Excellent integration with other libraries (SQLite, matplotlib, scikit-learn)
- Easy to use and well-documented
- Sufficient for our dataset size

### Q: Why matplotlib/seaborn instead of Plotly for visualizations?

**A:**
- matplotlib: Standard, well-established, static visualizations sufficient for PDF report
- seaborn: Better statistical visualizations (heatmaps) with less code
- Plotly: Could be used for interactive visualizations, but static was sufficient for report
- We did have plotly in requirements but used it minimally

### Q: Did you use any database ORMs (like SQLAlchemy)?

**A:** No, we used sqlite3 directly:
- Simpler for our needs
- No need for ORM complexity
- Direct SQL queries were sufficient
- Smaller dependency footprint

---

## 13. PROJECT EXECUTION QUESTIONS

### Q: How did you divide the work between team members?

**A:** (This is for the team to answer based on their actual division of labor)

*Suggested answer template:*
- Hakan: Data collection, preprocessing pipeline, database management
- İbrahim: Classification logic, visualization generation, report writing
- Both: Analysis, quality control, presentation preparation

### Q: How long did the project take?

**A:** (Adjust based on actual timeline)

*Suggested answer:*
- Data collection: X weeks
- Preprocessing: X weeks  
- Classification: X weeks
- Visualization & Analysis: X weeks
- Report writing: X weeks
- Total: One semester (Fall 2025)

### Q: What was your workflow?

**A:**
1. Literature review and methodology design
2. Data collection from multiple sources
3. Database setup and data storage
4. Preprocessing pipeline development
5. Classification dictionary creation
6. LLM-assisted validation
7. Visualization generation
8. Analysis and interpretation
9. Report writing
10. Presentation preparation

---

## 14. VALIDATION & REPRODUCIBILITY

### Q: How can someone reproduce your results?

**A:**
1. **Code:** All scripts are available in the `/Scripts` folder
2. **Data:** Database schema documented, can collect new data using provided scrapers
3. **Dependencies:** Requirements listed in `Required Libraries.txt`
4. **Pipeline:** Clear workflow: init_db → scraper_*.py → task2_*.py → task3_*.py → task4_*.py
5. **Documentation:** README.md and Final_Report.md provide methodology details

**Challenges:**
- Some data sources may change over time
- LLM API keys needed for validation step
- Results may vary slightly with new data collection

### Q: How did you validate your results?

**A:**
- **LLM Validation:** Google Gemini API checked relevance and categories
- **Manual Review:** Spot-checked random samples of classified articles
- **Cross-validation:** Compared results across different data sources
- **Sensitivity Analysis:** Tested impact of keyword lists on classification

---

## 15. PRESENTATION-SPECIFIC QUESTIONS

### Q: Can you show me a specific example from your data?

**A:** (Prepare 2-3 concrete examples)

*Example 1:* Article about "Computer Vision for Construction Site Safety" would be classified as:
- CE Area: Construction Management
- AI Technology: Computer Vision
- Key terms: "safety", "monitoring", "PPE detection"

*Example 2:* Article about "Machine Learning in Bridge Health Monitoring" would be:
- CE Area: Structural Engineering
- AI Technology: Machine Learning
- Key terms: "structural health monitoring", "sensors", "predictive maintenance"

### Q: What would you say is the most important takeaway?

**A:** **Construction Management is the clear leader in AI adoption (70.27%), primarily driven by safety applications and data-rich environments. However, Geotechnical Engineering shows a significant gap (only 6 articles, 0.80%), representing both a challenge and opportunity for future AI innovation in Civil Engineering.**

### Q: If you had more time/resources, what would you do?

**A:**
- Collect larger dataset (especially for Geotechnical)
- Implement machine learning classification models
- Perform statistical significance testing
- Create interactive web dashboard
- Expand to multilingual sources
- Longitudinal study over multiple years
- Detailed case studies of specific applications

---

## QUICK REFERENCE: KEY STATISTICS

- **Total Articles:** 750
- **CE Distribution:**
  - Construction Management: 527 (70.27%)
  - Transportation: 91 (12.13%)
  - Structural: 69 (9.20%)
  - Environmental: 57 (7.60%)
  - Geotechnical: 6 (0.80%)
- **Top AI Technology:** Machine Learning (323 mentions)
- **Key Finding:** Construction Management dominates; Geotechnical has significant gap
- **Tools:** Python, SQLite, NLTK, scikit-learn, matplotlib, seaborn, networkx, wordcloud
- **LLM Used:** Google Gemini 3 Flash API for validation

---

**Good luck with your presentation!**

*Remember: Be confident, know your methodology, acknowledge limitations honestly, and emphasize the value of your findings.*

