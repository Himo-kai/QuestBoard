# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import pickle
import re
import requests
import logging
import traceback
from dotenv import load_dotenv
from database import get_database
from sklearn.feature_extraction.text import TfidfVectorizer

# Define tech themes for difficulty calculation
tech_themes = {
    "python", "developer", "frontend", "backend", "network", 
    "security", "automation", "api", "devops", "cloud", "database",
    "server", "container", "kubernetes", "docker", "aws", "azure", 
    "gcp", "javascript", "typescript", "react", "node", "linux", "git"
}

def configure_logging():
    """Configure logging for the application."""
    # Only configure logging once
    if hasattr(configure_logging, '_configured'):
        return
    
    # Remove all handlers associated with the root logger
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Prevent propagation to avoid duplicate logs
    root_logger.propagate = False
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # File handler
    file_handler = logging.FileHandler('questboard_debug.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add handlers to root logger if not already added
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(console_handler)
    if not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)
    
    # Configure third-party loggers
    for logger_name in ['urllib3', 'werkzeug']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    # Disable propagation for application loggers
    for logger_name in ['env_wizard', 'migrations']:
        logging.getLogger(logger_name).propagate = False
    
    # Mark as configured
    configure_logging._configured = True

# Initialize logging
configure_logging()

# Get logger for this module
logger = logging.getLogger(__name__)
from flask import Flask, request, jsonify
import utils
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer

# Load environment variables first
load_dotenv(override=True)

from reddit_source import fetch_task_posts
from env_wizard import main as run_env_setup, validate_credentials, create_env_file
from utils import print_header
from database import get_database, get_pending_quests, approve_quest, reject_quest, get_user_stats, get_quests_by_region
from gear_keywords import load_keywords, get_all_keywords, get_category_keywords, matches_keyword

# Configure logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'questboard.log')

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create file handler which logs even debug messages
file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format))

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Set log level for external libraries to WARNING to reduce noise
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('werkzeug').setLevel(logging.INFO)

# Get logger for this module
logger = logging.getLogger(__name__)
logger.info("Starting QuestBoard application")

# Check for valid credentials at startup
logger.info("Checking for valid credentials...")
if not validate_credentials():
    logger.warning("No valid credentials found. Starting setup wizard...")
    # Create empty .env file if it doesn't exist
    create_env_file()
    
    # Run setup wizard to get credentials
    try:
        logger.info("Launching setup wizard...")
        run_env_setup()
        logger.info("Setup wizard completed")
    except Exception as e:
        logger.error(f"Error in setup wizard: {str(e)}")
        raise
else:
    logger.info("Valid credentials found. Proceeding with application startup.")

app = Flask(__name__)

# --- Category and Gear Definitions ---
CATEGORIES = {
    "Tech Gigs": ["developer", "engineer", "tech", "software", "IT", "computer"],
    "Creative Gigs": ["design", "video", "photo", "art", "creative", "edit", "graphic"],
    "Labor Gigs": ["move", "labor", "yard", "paint", "clean", "wash", "lift", "furniture"],
    "Writing Gigs": ["write", "writer", "blog", "content", "copy", "editor"],
    # Add more as needed
}

GEAR_KEYWORDS = {
    "drill": ["install", "screw", "mount", "drill", "anchor", "bolt"],
    "ladder": ["high", "ceiling", "light", "sign", "gutter"],
    "dolly": ["move", "heavy", "appliance", "furniture"],
    "ratchet set": ["mechanic", "car", "vehicle", "engine"],
    "gloves": ["trash", "clean", "yard", "hazard", "dirty"],
    "multimeter": ["electrical", "wiring", "circuit", "voltage"],
    "hex keys": ["bike", "furniture", "ikea", "assemble"],
    "shop vac": ["dust", "cleanup", "debris", "removal"],
    "safety glasses": ["cutting", "grind", "saw", "danger"],
    "wifi analyzer": ["network", "router", "signal", "wifi"]
}

# --- Helper Functions ---
def fetch_gigs():
    """Fetch gigs from both Craigslist and Reddit sources."""
    logger.info("Fetching gigs from all sources...")
    all_gigs = []
    
    # Fetch from Craigslist
    logger.info("=== Starting Craigslist fetch ===")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        logger.info("Setting up Selenium WebDriver...")
        
        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Initialize WebDriver
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"Error initializing Chrome WebDriver: {e}")
            logger.info("Falling back to default Chrome WebDriver")
            driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Load cookies if available
            cookie_file = os.getenv("CRAIGSLIST_COOKIE_FILE")
            if cookie_file and os.path.exists(cookie_file):
                logger.info(f"Loading cookies from {cookie_file}")
                try:
                    driver.get("https://craigslist.org")
                    with open(cookie_file, "r") as f:
                        for line in f:
                            line = line.strip()
                            if not line or line.startswith("http") or "=" not in line:
                                continue
                            name, value = line.split("=", 1)
                            cookie = {
                                'name': name.strip(),
                                'value': value.strip(),
                                'domain': '.craigslist.org'
                            }
                            driver.add_cookie(cookie)
                except Exception as e:
                    logger.error(f"Error loading cookies: {e}")
            
            # Try to fetch from Craigslist
            url = "https://lasvegas.craigslist.org/search/ggg"
            logger.info(f"Fetching Craigslist gigs from {url}")
            driver.get(url)
            
            # Wait for page to load
            import time
            time.sleep(3)
            
            # Save page source for debugging
            page_source = driver.page_source
            with open('craigslist_rendered.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Try different selectors for gigs
            gigs = []
            selectors = [
                "li.cl-search-result",
                "li.result-row",
                "div.cl-search-result",
                "li[class*='result']"
            ]
            
            for selector in selectors:
                gigs = soup.select(selector)
                if gigs:
                    logger.info(f"Found {len(gigs)} gigs using selector: {selector}")
                    break
            
            # Process found gigs
            processed_gigs = 0
            for gig in gigs:
                try:
                    # Extract gig information
                    title_elem = gig.select_one('.title, a.result-title, .posting-title')
                    title = title_elem.get_text(strip=True) if title_elem else 'No title'
                    
                    link = None
                    if title_elem and title_elem.get('href'):
                        link = title_elem['href']
                        if not link.startswith('http'):
                            link = f"https://lasvegas.craigslist.org{link if link.startswith('/') else '/' + link}"
                    
                    price_elem = gig.select_one('.price, .result-price, .posting-price')
                    price = price_elem.get_text(strip=True) if price_elem else 'N/A'
                    
                    location_elem = gig.select_one('.result-hood, .posting-location, .meta')
                    location = location_elem.get_text(strip=True).strip('()') if location_elem else 'Location not specified'
                    
                    # Create gig data
                    gig_data = {
                        'title': title,
                        'link': link or '#',
                        'price': price,
                        'location': location,
                        'source': 'Craigslist',
                        'description': f"{price} - {location}",
                        'date': 'Recent',
                        'id': f"cl_{abs(hash(link)) if link else id(gig)}"
                    }
                    
                    all_gigs.append(gig_data)
                    processed_gigs += 1
                    
                except Exception as e:
                    logger.error(f"Error processing Craigslist gig: {e}", exc_info=True)
            
            logger.info(f"Processed {processed_gigs} Craigslist gigs")
            
        except Exception as e:
            logger.error(f"Error in Craigslist fetch: {e}", exc_info=True)
        finally:
            try:
                driver.quit()
                logger.info("Closed WebDriver")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    except Exception as e:
        logger.error(f"Failed to initialize Selenium: {e}")
    
    # Fetch from Reddit
    logger.info("=== Starting Reddit fetch ===")
    try:
        from reddit_source import fetch_task_posts
        
        try:
            logger.debug("Fetching from Reddit...")
            reddit_tasks = fetch_task_posts(limit=20)  # Get 20 most recent tasks
            
            if not reddit_tasks:
                logger.warning("No tasks found from Reddit. This might be normal if there are no recent matching posts.")
            else:
                logger.info(f"Fetched {len(reddit_tasks)} tasks from Reddit")
                # Log some details about the tasks we found
                logger.debug(f"First few task titles: {[t.get('title', 'No title')[:50] + '...' for t in reddit_tasks[:3]]}")
                
                for task in reddit_tasks:
                    try:
                        title = task.get('title', 'Untitled Task')
                        logger.debug(f"Processing Reddit task: {title[:50]}...")
                        
                        gig_data = {
                            "title": f"[Reddit] {title}",
                            "description": task.get('description', task.get('selftext', 'No description')),
                            "link": task.get('url', ''),
                            "reward": task.get('reward', 'TBD'),
                            "difficulty": task.get('difficulty', 5),  # Default to medium difficulty
                            "source": "Reddit",
                            "gear_required": ", ".join(suggest_gear(
                                f"{title} {task.get('description', '')} {task.get('selftext', '')}"
                            ) or ["TBD"]),
                            "date": task.get('created', 'Recent'),
                            "id": f"rd_{task.get('id', str(id(task)))}",
                            "raw_task": task  # Keep the raw task data for debugging
                        }
                        all_gigs.append(gig_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing Reddit task: {e}", exc_info=True)
                        continue
                        
        except Exception as e:
            logger.error(f"Error in fetch_task_posts: {e}", exc_info=True)
            
    except ImportError as e:
        logger.error(f"Failed to import reddit_source: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in Reddit fetch: {e}", exc_info=True)
    
    logger.info(f"Successfully fetched {len(all_gigs)} gigs from all sources")
    return all_gigs

def cache_quest(quest):
    """Cache a quest in the database."""
    db = get_database()
    db.cache_quest(quest)

def remove_old_quests(days_old):
    """Remove old quests from the cache."""
    db = get_database()
    db.remove_old_quests(days_old)

def calculate_difficulty_scores(quests):
    """
    Calculate difficulty scores for quests using TF-IDF and cached curves.
    
    Args:
        quests (list): List of quest dictionaries containing 'title' and 'description'
        
    Returns:
        list: Updated list of quests with 'difficulty' scores
    """
    if not quests:
        return quests
    
    # Extract text content
    texts = [f"{q['title']} {q['description']}" for q in quests]
    
    try:
        # Load or create vectorizer
        vectorizer = None
        try:
            with open('tfidf_vectorizer.pkl', 'rb') as f:
                vectorizer = pickle.load(f)
        except FileNotFoundError:
            vectorizer = TfidfVectorizer()
            vectorizer.fit(texts)  # Fit on all available data
            with open('tfidf_vectorizer.pkl', 'wb') as f:
                pickle.dump(vectorizer, f)
        
        # Transform texts to TF-IDF matrix
        tfidf_matrix = vectorizer.transform(texts)
        
        # Get cached difficulty curves
        db = get_database()
        curves = db.get_difficulty_curves()
        curve_dict = {f"{c['category']}_{c['keyword']}": c['difficulty_score'] for c in curves}
        
        # Process each quest
        for i, quest in enumerate(quests):
            # Get non-zero features and their scores
            feature_names = vectorizer.get_feature_names_out()
            feature_index = tfidf_matrix[i, :].nonzero()[1]
            tfidf_scores = [(idx, tfidf_matrix[i, idx]) for idx in feature_index]
            
            # Calculate base difficulty based on word complexity
            base_difficulty = 0
            word_scores = []
            
            for idx, score in tfidf_scores:
                word = feature_names[idx].lower()
                word_difficulty = 0
                
                # Increase difficulty for complex words
                if len(word) > 7:  # Longer words are more complex
                    word_difficulty += score * 0.5
                if word in tech_themes:  # Tech-related words are more complex
                    word_difficulty += score * 1.5
                
                base_difficulty += word_difficulty
                word_scores.append((word, word_difficulty))
            
            # Adjust difficulty based on cached curves
            adjusted_difficulty = base_difficulty
            for word, score in word_scores:
                key = f"{quest['source']}_{word}"
                if key in curve_dict:
                    adjusted_difficulty += curve_dict[key] * score
            
            # Ensure difficulty is within 1-5 range
            final_difficulty = min(5, max(1, int(adjusted_difficulty * 2)))
            quest['difficulty'] = final_difficulty
            
            # Cache the difficulty curve for top words
            for word, score in sorted(word_scores, key=lambda x: x[1], reverse=True)[:5]:
                try:
                    db.add_difficulty_curve(
                        category=quest['source'],
                        keyword=word,
                        difficulty_score=final_difficulty
                    )
                except Exception as e:
                    logger.warning(f"Failed to cache difficulty curve for {word}: {e}")
        
        return quests
        
    except Exception as e:
        logger.error(f"Error calculating difficulty scores: {e}", exc_info=True)
        # Set default difficulty in case of error
        for quest in quests:
            quest['difficulty'] = quest.get('difficulty', 3)  # Default to medium difficulty
        return quests
    
    return quests

# Load gear keywords when the module is imported
gear_keywords = load_keywords()

def suggest_gear(text):
    """
    Suggest gear based on the quest description.
    Returns a list of suggested gear categories and specific items.
    """
    if not text:
        return []
        
    text = text.lower()
    suggestions = set()
    
    for category, data in gear_keywords.items():
        # Check common keywords for this category
        common_keywords = data.get('common', [])
        for keyword in common_keywords:
            if keyword.lower() in text:
                suggestions.add(category)
                break
                
        # Check specific subcategories
        specific_keywords = data.get('specific', {})
        for subcategory, keywords in specific_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    suggestions.add(f"{category} - {subcategory}")
    
    # Return top 3 matches
    return list(suggestions)[:3]

import re

def extract_reward(description):
    matches = re.findall(r'\$\s?(\d+(?:,\d{3})*(?:\.\d{1,2})?)', description)
    if matches:
        rewards = [float(m.replace(',', '')) for m in matches]
        return sum(rewards) / len(rewards) if len(rewards) > 1 else rewards[0]
    return 0.0

def rate_difficulty(text):
    """
    Rate the difficulty of a quest based on its text content.
    Uses NLP-based analysis for more accurate difficulty assessment.
    
    Args:
        text (str): The quest title and description
        
    Returns:
        float: A difficulty score between 1 (easiest) and 10 (hardest)
    """
    if not text:
        return 3.0  # Default to medium difficulty if no text provided
    
    try:
        # Try using the NLP-based difficulty rating first
        from nlp_utils import rate_difficulty_nlp
        difficulty = rate_difficulty_nlp(text)
        
        # Ensure the difficulty is within bounds (1-10)
        difficulty = max(1, min(10, difficulty))
        
        # Round to 1 decimal place for consistency
        return round(difficulty, 1)
        
    except Exception as e:
        # Fall back to simple keyword-based difficulty if NLP fails
        logger.warning(f"NLP difficulty rating failed, falling back to simple method: {e}")
        text = text.lower()
        difficulty = 1
    if any(word in text for word in ["lift", "install", "tools", "truck", "heavy", "construction", "mount", "assemble"]):
        difficulty += 2
    if any(word in text for word in ["climb", "ladder", "roof", "racking", "equipment"]):
        difficulty += 1
    return min(difficulty, 5)

def render_questboard(quests):
    """Render the questboard HTML with scrollable tabs."""
    # Group quests by source
    quests_by_source = {}
    for quest in quests:
        source = quest['source']
        if source not in quests_by_source:
            quests_by_source[source] = []
        quests_by_source[source].append(quest)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>QuestBoard</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
                background-color: #f5f5f5;
            }
            
            .tabs-container {
                width: 100%;
                overflow-x: auto;
                white-space: nowrap;
                background: #fff;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                border-radius: 5px;
                margin-bottom: 20px;
                padding: 10px 0;
            }
            
            .tabs {
                display: flex;
                padding: 0;
                margin: 0;
                list-style: none;
            }
            
            .tab {
                padding: 10px 20px;
                cursor: pointer;
                background: #f1f1f1;
                margin-right: 5px;
                border-radius: 5px 5px 0 0;
                transition: all 0.3s ease;
                white-space: nowrap;
            }
            
            .tab:hover {
                background: #e0e0e0;
            }
            
            .tab.active {
                background: #4CAF50;
                color: white;
            }
            
            .tab-content {
                display: none;
                padding: 20px;
                background: white;
                border-radius: 0 0 5px 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .tab-content.active {
                display: block;
            }
            
            .quest-card { 
                border: 1px solid #e0e0e0; 
                padding: 15px; 
                margin-bottom: 15px; 
                border-radius: 5px; 
                background: white;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .quest-card:hover { 
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            
            .source-tag { 
                background-color: #4CAF50; 
                color: white; 
                padding: 3px 8px; 
                border-radius: 12px; 
                font-size: 0.75em;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .quest-card h2 {
                margin: 10px 0;
                color: #333;
                font-size: 1.25em;
            }
            
            .quest-card p {
                color: #666;
                line-height: 1.5;
                margin: 10px 0;
            }
            
            .quest-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
                padding-top: 10px;
                border-top: 1px solid #eee;
            }
            
            .difficulty { 
                color: #f44336; 
                font-weight: bold;
                background: #ffebee;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.85em;
            }
            
            .reward { 
                color: #2196F3; 
                font-weight: bold;
                background: #e3f2fd;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.85em;
            }
            
            .bookmarked { 
                border-left: 4px solid #FFD700;
                position: relative;
            }
            
            .bookmarked:before {
                content: '★';
                position: absolute;
                left: -15px;
                top: 10px;
                color: #FFD700;
            }
            
            .quest-actions {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 15px;
            }
            
            .view-details {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                text-decoration: none;
                font-size: 0.9em;
                transition: background 0.3s ease;
            }
            
            .view-details:hover {
                background: #45a049;
            }
            
            .bookmark-btn { 
                background: #f5f5f5;
                border: 1px solid #ddd;
                color: #666;
                cursor: pointer;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 0.9em;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .bookmark-btn:hover { 
                background: #e0e0e0;
                color: #333;
            }
            
            .bookmark-btn.bookmarked {
                background: #fff3cd;
                color: #856404;
                border-color: #ffeeba;
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #888;
                border-radius: 10px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
        </style>
    </head>
    <body>
        <h1 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">QuestBoard</h1>
        
        <div class="tabs-container">
            <ul class="tabs" id="sourceTabs">
                <li class="tab active" onclick="showTab('all')">All Quests</li>
    """
    
    # Add a tab for each source
    for source in sorted(quests_by_source.keys()):
        html += f'<li class="tab" onclick="showTab(\'{source}\')">{source} ({len(quests_by_source[source])})</li>'
    
    html += """
            </ul>
        </div>
        
        <!-- All Quests Tab -->
        <div id="all" class="tab-content active">
            <div class="quest-list">
    """
    
    # Add all quests to the 'All' tab
    for quest in quests:
        html += _render_quest_card(quest)
    
    html += """
            </div>
        </div>
    """
    
    # Add a tab content section for each source
    for source, source_quests in quests_by_source.items():
        html += f"""
        <div id="{source}" class="tab-content">
            <div class="quest-list">
        """
        for quest in source_quests:
            html += _render_quest_card(quest)
        html += """
            </div>
        </div>
        """
    
    html += """
        <script>
            function showTab(tabName) {
                // Hide all tab contents
                const tabContents = document.getElementsByClassName('tab-content');
                for (let i = 0; i < tabContents.length; i++) {
                    tabContents[i].classList.remove('active');
                }
                
                // Deactivate all tabs
                const tabs = document.getElementsByClassName('tab');
                for (let i = 0; i < tabs.length; i++) {
                    tabs[i].classList.remove('active');
                }
                
                // Show the selected tab content and activate the tab
                document.getElementById(tabName).classList.add('active');
                const activeTab = Array.from(tabs).find(tab => tab.textContent.startsWith(tabName));
                if (activeTab) activeTab.classList.add('active');
                
                // Special case for 'All' tab
                if (tabName === 'all') {
                    document.querySelector('.tab:first-child').classList.add('active');
                }
            }
            
            async function toggleBookmark(link) {
                try {
                    const response = await fetch(`/bookmark/${encodeURIComponent(link)}`, {
                        method: 'POST'
                    });
                    if (response.ok) {
                        // Refresh the page to update the UI
                        location.reload();
                    }
                } catch (error) {
                    console.error('Error toggling bookmark:', error);
                    alert('Failed to toggle bookmark. Please try again.');
                }
            }
        </script>
    </body>
    </html>
    """
    return html

def _render_quest_card(quest):
    """Render a single quest card."""
    bookmark_class = "bookmarked" if quest['bookmarked'] else ""
    return f"""
    <div class="quest-card {bookmark_class}">
        <span class="source-tag">{quest['source']}</span>
        <h2>{quest['title']}</h2>
        <p>{quest['description']}</p>
        <div class="quest-meta">
            <span class="difficulty">Difficulty: {quest['difficulty']}</span>
            <span class="reward">Reward: {quest['reward']}</span>
        </div>
        <div class="quest-actions">
            <a href="{quest['link']}" target="_blank" class="view-details">View Details</a>
            <button onclick="toggleBookmark('{quest['link']}')" class="bookmark-btn {'bookmarked' if quest['bookmarked'] else ''}">
                { '★' if quest['bookmarked'] else '☆' } { 'Unbookmark' if quest['bookmarked'] else 'Bookmark' }
            </button>
        </div>
    </div>
    """

@app.route("/")
def index():
    """Main page with quest listings."""
    try:
        logger.info("=== Starting index route ===")
        logger.debug("Attempting to load quests for homepage...")
        
        try:
            logger.debug("Calling fetch_gigs()...")
            quests = fetch_gigs()  # This is where it probably dies
            logger.info(f"Loaded {len(quests)} quests.")
            
            if not quests:
                logger.warning("No quests were fetched from any source")
            
            try:
                logger.debug("Calculating difficulty scores...")
                quests = calculate_difficulty_scores(quests)
                logger.debug(f"Calculated difficulty for {len(quests)} quests")
            except Exception as e:
                logger.error(f"Error calculating difficulty scores: {e}", exc_info=True)
                logger.info("Continuing without difficulty scores...")
                # Add default difficulty if calculation failed
                for quest in quests:
                    quest.setdefault('difficulty', 3)
            
            try:
                logger.debug("Getting bookmarked quests...")
                db = get_database()
                bookmarks = db.get_bookmarked_quests()
                bookmarked_ids = {b[0] for b in bookmarks}
                logger.debug(f"Found {len(bookmarked_ids)} bookmarked quests")
                
                # Add bookmark status to quests
                for quest in quests:
                    quest['bookmarked'] = quest.get('link', '') in bookmarked_ids
            except Exception as e:
                logger.error(f"Error processing bookmarks: {e}", exc_info=True)
                logger.info("Continuing without bookmark status...")
                for quest in quests:
                    quest['bookmarked'] = False
        except Exception as e:
            logger.error(f"Error in main quest processing: {e}", exc_info=True)
            logger.info("Attempting to continue with empty quest list...")
            quests = []
        
        logger.info("Rendering questboard...")
        return render_questboard(quests)
        
    except Exception as e:
        logger.critical(f"Critical error in index route: {e}", exc_info=True)
        return (
            "<h1>Error Loading Quests</h1>"
            "<p>We encountered an error while loading quests. The development team has been notified.</p>"
            "<p>Please try refreshing the page or check back later.</p>"
            "<p>Error details have been logged for investigation.</p>",
            500
        )

@app.route("/bookmark/<quest_id>", methods=["POST"])
def toggle_bookmark(quest_id):
    """Toggle bookmark status for a quest."""
    try:
        db = get_database()
        # Check if quest is already bookmarked
        bookmarks = db.get_bookmarked_quests()
        bookmarked_ids = {b[0] for b in bookmarks}
        
        if quest_id in bookmarked_ids:
            db.remove_bookmark(quest_id)
            return jsonify({"status": "removed", "message": "Quest unbookmarked"})
        else:
            # Find the quest to get its details
            quests = fetch_gigs()
            quest = next((q for q in quests if q['link'] == quest_id), None)
            if quest:
                db.bookmark_quest(quest_id, quest['title'], quest['source'])
                return jsonify({"status": "added", "message": "Quest bookmarked"})
            else:
                return jsonify({"error": "Quest not found"}), 404
    except Exception as e:
        logger.error(f"Error toggling bookmark: {e}")
        return jsonify({"error": "Failed to toggle bookmark"}), 500

@app.route('/guildhall/review', methods=['GET', 'POST'])
def guildhall_review():
    """Admin interface for reviewing and approving quests."""
    if request.method == 'POST':
        quest_id = request.form.get('quest_id')
        action = request.form.get('action')
        if action == 'approve':
            try:
                approve_quest(quest_id)
                return jsonify({'status': 'success', 'message': 'Quest approved'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 400
        elif action == 'reject':
            try:
                reject_quest(quest_id)
                return jsonify({'status': 'success', 'message': 'Quest rejected'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 400
    
    # For GET requests, return pending quests
    quests = get_pending_quests()
    return jsonify(quests)

@app.route('/submit', methods=['POST'])
def submit_quest():
    """Handle user-submitted quests."""
    try:
        quest = request.get_json()
        if not quest:
            return jsonify({'status': 'error', 'message': 'No quest data provided'}), 400
        
        # Set default values
        quest['source'] = 'User'
        quest['approved'] = None  # Needs admin approval
        quest['submitted_by'] = request.headers.get('X-User-Id', 'anonymous')
        
        # Calculate difficulty if not provided
        if 'difficulty' not in quest or not quest['difficulty']:
            quest['difficulty'] = rate_difficulty(
                f"{quest.get('title', '')} {quest.get('description', '')}"
            )
        
        # Suggest gear if not provided
        if 'gear_required' not in quest or not quest['gear_required']:
            quest['gear_required'] = suggest_gear(
                f"{quest.get('title', '')} {quest.get('description', '')}"
            )
        
        # Cache the quest (will be pending approval)
        cache_quest(quest)
        return jsonify({
            'status': 'success', 
            'message': 'Quest submitted and pending approval',
            'quest': quest
        }), 201
    except Exception as e:
        logger.error(f"Error submitting quest: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to submit quest: {str(e)}'
        }), 500

@app.route('/guildcard/<user_id>')
def guild_card(user_id):
    """Get guild card statistics for a user."""
    try:
        stats = get_user_stats(user_id)
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting guild card for user {user_id}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get guild card: {str(e)}'
        }), 500

@app.route('/quests/region/<region>')
def quests_by_region(region):
    """Get quests filtered by region."""
    try:
        quests = get_quests_by_region(region)
        return jsonify({
            'status': 'success',
            'region': region,
            'count': len(quests),
            'quests': quests
        })
    except Exception as e:
        logger.error(f"Error getting quests for region {region}: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get quests for region {region}: {str(e)}'
        }), 500

def create_app():
    # Configure the Flask app
    app = Flask(__name__)
    
    # Ensure the database has the latest schema
    try:
        from migrations import run_migration
        run_migration()
    except Exception as e:
        logger.warning(f"Could not run migrations: {e}")
    
    return app

if __name__ == "__main__":
    import os
    import sys
    import argparse
    
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Run the QuestBoard application')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the application on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    args = parser.parse_args()
    
    # Create and run the application
    app = create_app()
    app.run(host='0.0.0.0', port=args.port, debug=args.debug, use_reloader=False)
