import feedparser
import sqlite3
import os
import ssl
import urllib.parse

# --- CONFIGURATION ---
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'corpus.db')

# Targeted Industry Feeds
RSS_FEEDS = [
    "https://www.bimplus.co.uk/feed/",           # BIM & Digital Construction
    "https://www.aecmag.com/feed/",              # AEC Technology
    "https://www.constructionenquirer.com/feed/",# General Construction
    "https://wesslingarchitects.com/feed/",      # Architecture/Tech
    "https://blog.plangrid.com/feed/",           # Construction Software

    # --- Major Industry News ---
    "https://www.constructiondive.com/feeds/news/",           # Top Tier: General Construction News
    "https://www.enr.com/rss",                                # Engineering News-Record (The "Bible" of the industry)
    "https://www.constructionenquirer.com/feed/",             # UK's biggest construction news
    "https://www.newcivilengineer.com/feed/",                 # New Civil Engineer (Global projects)
    "https://www.globalconstructionreview.com/feed",          # GCR: Large scale international projects

    # --- Tech, AI & BIM Specific (The "Gold" for your project) ---
    "https://www.bimplus.co.uk/feed/",                        # Digital Construction focus
    "https://www.aecmag.com/feed/",                           # AEC Technology & Software
    "https://aec-business.com/feed",                          # Innovation in Construction
    "https://www.geospatialworld.net/feed/",                  # GIS, Mapping & Digital Twins
    "https://revit.news/feed",                                # Specific to Revit/BIM software
    "https://feeds.feedburner.com/TheRevitKid",               # Practical BIM tutorials/news

    # --- Corporate Tech Blogs (Great for "Implementation" examples) ---
    "https://blog.plangrid.com/feed/",                        # Autodesk's Construction Blog
    "https://constructible.trimble.com/blog/rss.xml",         # Trimble (Hardware/Software)
    "http://feeds.feedburner.com/oreilly/radar/atom",         # O'Reilly (General Tech/AI trends)
    
    # --- Academic & Structural ---
    "https://civilengineerblog.com/feed",                     # General Civil Engineering
    "https://structuralengineer.info/feed/",                  # Specific to Structural

    # --- 🏗️ CONSTRUCTION TECH & AI (High Priority) ---
    "https://www.enr.com/rss/topic/587",                      # ENR: Construction Technology (Gold Mine)
    "https://aec-business.com/feed",                          # AEC Business (Innovation focus)
    "https://www.bimplus.co.uk/feed/",                        # BIM & Digital Construction
    "https://www.aecmag.com/feed/",                           # AEC Magazine (Tech focus)
    "https://stackct.com/feed",                               # Stack Construction Tech
    "https://feeds.feedburner.com/TheRevitKid",               # BIM/Revit specific

    # --- 🚜 GENERAL CONSTRUCTION NEWS ---
    "https://www.constructiondive.com/feeds/news/",           # Construction Dive: General
    "https://www.constructionenquirer.com/feed/",             # UK Construction News
    "https://www.theconstructionindex.co.uk/news/rss",        # Construction Index (UK)
    "https://contractormag.com/__rss/all-content-xml",        # Contractor Magazine
    "https://www.equipmentworld.com/feed",                    # Equipment & Machinery

    # --- 🌉 CIVIL & STRUCTURAL ENGINEERING ---
    "https://www.newcivilengineer.com/feed/",                 # New Civil Engineer
    "https://theconstructor.org/feed",                        # The Constructor (Academic/Practical)
    "https://civilengineerblog.com/feed",                     # Civil Engineering Blog
    "https://dailycivil.com/feed",                            # Daily Civil

    # --- 🏛️ ARCHITECTURE & DESIGN (Trends) ---
    "https://feeds.feedburner.com/Archdaily",                 # ArchDaily (Global Architecture)
    "https://www.dezeen.com/feed",                            # Dezeen (Design & Tech)
    "https://archpaper.com/feed",                             # The Architect's Newspaper
    
    # --- 🧠 GENERAL TECH (Filtered by your script) ---
    "https://feeds.feedburner.com/TechCrunch/startups",       # TechCrunch
    "http://feeds.feedburner.com/oreilly/radar/atom",         # O'Reilly Radar

    # --- 🔍 GOOGLE NEWS RSS (Custom Queries) ---
    # These effectively replace the need for the complex Google Scraper if that ever fails.
    
    # Query: "Construction Artificial Intelligence"
    "https://news.google.com/rss/search?q=Construction+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    
    # Query: "Civil Engineering Machine Learning"
    "https://news.google.com/rss/search?q=Civil+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    
    # Query: "BIM Digital Twins"
    "https://news.google.com/rss/search?q=BIM+Digital+Twins&hl=en-US&gl=US&ceid=US:en",
    
    # Query: "Construction Robotics"
    "https://news.google.com/rss/search?q=Construction+Robotics&hl=en-US&gl=US&ceid=US:en",

    # --- 🧠 GOOGLE NEWS: AI + SUB-DISCIPLINES (The Volume Drivers) ---
    # These contain the "combine" logic you requested.
    
    # 1. Construction Management & Safety
    "https://news.google.com/rss/search?q=Construction+Management+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Construction+Safety+Computer+Vision&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Construction+Scheduling+Optimization+AI&hl=en-US&gl=US&ceid=US:en",

    # 2. Structural Engineering & Materials
    "https://news.google.com/rss/search?q=Structural+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Structural+Health+Monitoring+AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Concrete+Strength+Prediction+AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Generative+Design+Structural+Engineering&hl=en-US&gl=US&ceid=US:en",

    # 3. BIM & Digital Twins
    "https://news.google.com/rss/search?q=BIM+Artificial+Intelligence+Integration&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Digital+Twins+Construction+Industry&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Scan+to+BIM+AI&hl=en-US&gl=US&ceid=US:en",

    # 4. Geotechnical & Foundations
    "https://news.google.com/rss/search?q=Geotechnical+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Soil+Analysis+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Tunneling+Automation+AI&hl=en-US&gl=US&ceid=US:en",

    # 5. Transportation & Infrastructure
    "https://news.google.com/rss/search?q=Smart+Highway+Infrastructure+AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Bridge+Inspection+Drone+AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Traffic+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",

    # 6. Sustainability & Green Building
    "https://news.google.com/rss/search?q=Green+Building+AI+Optimization&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Energy+Efficient+Buildings+Machine+Learning&hl=en-US&gl=US&ceid=US:en",

    # --- 🏗️ INDUSTRY BLOGS (High Quality / Specific) ---
    "https://www.enr.com/rss/topic/587",                      # ENR Tech
    "https://www.bimplus.co.uk/feed/",                        # BIM Plus
    "https://www.aecmag.com/feed/",                           # AEC Magazine
    "https://www.constructiondive.com/feeds/news/",           # Construction Dive
    "https://stackct.com/feed",                               # Stack Construction Tech
    "https://feeds.feedburner.com/TheRevitKid",               # Revit/BIM
    "https://blog.plangrid.com/feed/",                        # PlanGrid/Autodesk
    "https://www.newcivilengineer.com/feed/",                 # New Civil Engineer
    "https://civilengineerblog.com/feed",                     # Civil Engineering Blog
    "https://www.geospatialworld.net/feed/",                  # GIS & Mapping

    # =========================================================================
    # 🏗️ STRUCTURAL ENGINEERING (AI & ML Combos)
    # =========================================================================
    "https://news.google.com/rss/search?q=Structural+Engineering+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Structural+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Concrete+Structures+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Earthquake+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",

    # =========================================================================
    # 🚜 CONSTRUCTION MANAGEMENT (AI, ML & Safety)
    # =========================================================================
    # Standard Management Combos
    "https://news.google.com/rss/search?q=Construction+Management+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Construction+Management+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Construction+Scheduling+Optimization+AI&hl=en-US&gl=US&ceid=US:en",
    
    # ⛑️ HEALTH & SAFETY SPECIFIC (As requested)
    "https://news.google.com/rss/search?q=Construction+Health+and+Safety+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Construction+Site+Safety+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Computer+Vision+Construction+Safety&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=PPE+Detection+AI+Construction&hl=en-US&gl=US&ceid=US:en",

    # =========================================================================
    # 🏢 BIM & DIGITAL TWINS (AI, ML & Safety)
    # =========================================================================
    # Standard BIM/DT Combos
    "https://news.google.com/rss/search?q=Building+Information+Modeling+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=BIM+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Digital+Twins+Construction+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    
    # ⛑️ HEALTH & SAFETY LAYERS IN BIM/DT
    "https://news.google.com/rss/search?q=BIM+Construction+Safety+AI&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Digital+Twin+Safety+Monitoring+Construction&hl=en-US&gl=US&ceid=US:en",

    # =========================================================================
    # 🚇 GEOTECHNICAL & TRANSPORTATION (AI & ML Combos)
    # =========================================================================
    "https://news.google.com/rss/search?q=Geotechnical+Engineering+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Geotechnical+Engineering+Machine+Learning&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Transportation+Engineering+Artificial+Intelligence&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Smart+Infrastructure+Machine+Learning&hl=en-US&gl=US&ceid=US:en",

    # =========================================================================
    # 📰 TRADITIONAL INDUSTRY FEEDS (The Foundation)
    # =========================================================================
    "https://www.enr.com/rss/topic/587",                      # ENR Tech
    "https://www.bimplus.co.uk/feed/",                        # BIM Plus
    "https://www.aecmag.com/feed/",                           # AEC Magazine
    "https://www.constructiondive.com/feeds/news/",           # Construction Dive
    "https://stackct.com/feed",                               # Stack Construction Tech
    "https://feeds.feedburner.com/TheRevitKid",               # Revit/BIM
    "https://blog.plangrid.com/feed/",                        # PlanGrid/Autodesk
    "https://www.newcivilengineer.com/feed/",                 # New Civil Engineer
    "https://civilengineerblog.com/feed",                     # Civil Engineering Blog
    "https://www.geospatialworld.net/feed/",                  # GIS & Mapping
    "https://source.asce.org/feed/",
    "https://www.bimplus.co.uk/feed/",
    "https://cmaanet.org/news/feed",
    "https://www.construction-institute.org/rss/news",
    "https://ascelibrary.org/action/showFeed?type=etoc&feed=rss&jc=jccee5",
    "https://ascelibrary.org/action/showFeed?type=etoc&feed=rss&jc=jcemd4",
    "https://rss.sciencedirect.com/publication/science/09265805",
    "https://www.projectmanagement.com/rss/projectmanagement.xml",
    "https://www.roofingcontractor.com/rss/16",
    "https://canada.constructconnect.com/feed?site_branch=dcn",
    "https://www.constructconnect.com/blog/rss.xml?order=DESC&orderby=post_views&site_branch=dcn",
    "https://constructconnect.com/feed?site_branch=dcn",
    "https://canada.constructconnect.com/feed?site_branch=dcn&orderby=post_views&order=DESC"
    "https://feeds.feedburner.com/ceg",
    "https://www.enr.com/rss/1",
    "https://www.theconstructionindex.co.uk/feeds/news.xml",
    "https://undergroundinfrastructure.com/rss?feed=issue",
    "https://undergroundinfrastructure.com/rss?topic=construction",
    "https://undergroundinfrastructure.com/rss?topic=energy",
    "https://undergroundinfrastructure.com/rss?topic=environment",
    "https://undergroundinfrastructure.com/rss?topic=equipment",
    "https://undergroundinfrastructure.com/rss?topic=first-look",
    "https://undergroundinfrastructure.com/rss?topic=inspection",
    "https://undergroundinfrastructure.com/rss?topic=integrity-management",
    "https://www.osha.gov/news/newsreleases.xml",
    "https://undergroundinfrastructure.com/rss?topic=workforce",
    "https://undergroundinfrastructure.com/rss?topic=technology",
    "https://undergroundinfrastructure.com/rss?topic=skilled-labor",
    "https://undergroundinfrastructure.com/rss?topic=software",
    "https://undergroundinfrastructure.com/rss?topic=robotics",
    "https://undergroundinfrastructure.com/rss?topic=research",
    "https://undergroundinfrastructure.com/rss?topic=regulatory",
    "https://undergroundinfrastructure.com/rss?topic=project-news",
    "https://undergroundinfrastructure.com/rss?topic=magazine",
    "https://www.constructiondive.com/feeds/news/",
    "https://www.constructionenquirer.com/feed/",
    "https://www.contractormag.com/__rss/all-published-content.xml",
    "https://www.constructconnect.com/blog/rss.xml",
    "https://www.theconstructionindex.co.uk/feeds/news.xml",
    "https://www.building.co.uk/2815.rss",
    "https://www.constructionnews.co.uk/feed/",
    "https://www.autodesk.com/blogs/construction/feed/",
    "https://www.constructionspecifier.com/feed/",
    "https://ukconstructionblog.co.uk/feed/",
    "https://aec-business.com/feed/",
    "https://constructiondaily.news/feed/",
    "https://edzarenski.com/feed/",
    "https://ccr-mag.com/feed/",
    "https://feeds.feedburner.com/Archdaily",
    "https://architizer.com/blog/feed/",
    "https://www.dezeen.com/feed/",
    "https://www.archpaper.com/feed",
    "https://www.architecturalrecord.com/rss/articles",
    "https://www.pbctoday.co.uk/news/category/bim-news/feed/",
    "https://bimcorner.com/feed/",
    "https://biblus.accasoftware.com/en/feed/",
    "https://www.equipmentworld.com/feed/",
    "https://www.contractormag.com/__rss/all-published-content.xml",
    "https://feeds.feedburner.com/ConstructionJunkieBlog-ConstructionJunkie",
    "https://myconstructiontechnology.com/feed/",
    "https://www.equipmentworld.com/feed/",
    



]

unique_feeds = []
for i in RSS_FEEDS:
    if i not in unique_feeds:
        unique_feeds.append(i)

RSS_FEEDS = unique_feeds


# 1. SSL Certificate Fix (Vital for some Windows/Mac setups)
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def save_feed_entry(entry, source_name):
    """Saves a blog post if it passes the keyword filter."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 2. Extract Text (RSS feeds vary in format)
        if 'content' in entry:
            text_content = entry.content[0].value
        elif 'summary' in entry:
            text_content = entry.summary
        else:
            return False

        # 3. THE RELEVANCE FILTER
        # Only save if it mentions AI or Tech keywords
        keywords = ['ai ', 'artificial intelligence', 'machine learning', 
                    'robot', 'software', 'data', "AI", "ML", "robotics", "AR", "VR"]
        
        # We lowercase everything to be safe
        if not any(k in text_content.lower() for k in keywords):
            return False # Skip this article (It's probably about finance or law)

        # 4. Save to Database
        cursor.execute("""
            INSERT OR IGNORE INTO articles 
            (title, publication_date, source_domain, url, full_text, category_tag)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry.title,
            entry.published[:10] if hasattr(entry, 'published') else "2025-01-01",
            source_name,
            entry.link,
            text_content, 
            "Blog_RSS"
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        # print(f"Error: {e}") # Keep silent to avoid console spam
        return False

def fetch_rss():
    print("📡 Scanning Industry RSS Feeds...")
    
    total_new = 0
    for url in RSS_FEEDS:
        print(f"   Reading feed: {url}...")
        try:
            feed = feedparser.parse(url)
            
            saved_count = 0
            for entry in feed.entries:
                source_domain = urllib.parse.urlparse(url).netloc
                if save_feed_entry(entry, source_domain):
                    saved_count += 1
                    total_new += 1
            
            print(f"     -> Found {saved_count} relevant Tech articles.")
        except Exception as e:
            print(f"     -> Failed to read feed: {e}")

    print(f"🎉 RSS Scan Complete. Added {total_new} articles.")

if __name__ == "__main__":
    fetch_rss()