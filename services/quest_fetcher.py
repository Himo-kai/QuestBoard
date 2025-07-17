# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Quest fetching service for multiple sources."""
import time
import logging
from typing import List, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import praw
from config import Config

logger = logging.getLogger(__name__)

class QuestFetcher:
    """Handles fetching quests from various sources."""
    
    def __init__(self, config: Config):
        """Initialize with configuration."""
        self.config = config
        self.reddit = None
        self.driver = None
        
    def init_reddit(self):
        """Initialize Reddit API client."""
        if not self.config.REDDIT_CLIENT_ID or not self.config.REDDIT_CLIENT_SECRET:
            logger.warning("Reddit credentials not configured")
            return False
            
        self.reddit = praw.Reddit(
            client_id=self.config.REDDIT_CLIENT_ID,
            client_secret=self.config.REDDIT_CLIENT_SECRET,
            user_agent=self.config.REDDIT_USER_AGENT
        )
        return True
        
    def init_webdriver(self):
        """Initialize Selenium WebDriver."""
        if not self.driver:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            try:
                self.driver = webdriver.Chrome(
                    executable_path=self.config.WEBDRIVER_PATH,
                    options=options
                )
                self.driver.set_page_load_timeout(30)
                return True
            except Exception as e:
                logger.error(f"Failed to initialize WebDriver: {e}")
                return False
        return True
        
    def fetch_from_reddit(self, subreddit: str = 'forhire', limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch quests from Reddit."""
        if not self.reddit and not self.init_reddit():
            return []
            
        try:
            quests = []
            for submission in self.reddit.subreddit(subreddit).new(limit=limit):
                if submission.stickied:
                    continue
                    
                quest = {
                    'title': submission.title,
                    'description': submission.selftext,
                    'link': f"https://reddit.com{submission.permalink}",
                    'source': 'reddit',
                    'date_posted': submission.created_utc,
                    'location': 'Remote'  # Default, can be parsed from title
                }
                quests.append(quest)
                
            return quests
            
        except Exception as e:
            logger.error(f"Error fetching from Reddit: {e}", exc_info=True)
            return []
    
    def fetch_from_craigslist(self, query: str = 'gig', limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch gigs from Craigslist."""
        if not self.init_webdriver():
            return []
            
        url = f"{self.config.CRAIGSLIST_BASE_URL}/search/ggg?query={query}&sort=date"
        quests = []
        
        try:
            self.driver.get(url)
            
            # Wait for results to load
            wait = WebDriverWait(self.driver, 10)
            results = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.result-row'))
            )
            
            for result in results[:limit]:
                try:
                    title_elem = result.find_element(By.CLASS_NAME, 'result-title')
                    title = title_elem.text
                    link = title_elem.get_attribute('href')
                    
                    # Get additional details
                    price_elem = result.find_element(By.CLASS_NAME, 'result-price')
                    location_elem = result.find_element(By.CLASS_NAME, 'result-hood')
                    
                    quest = {
                        'title': title,
                        'description': '',  # Will be fetched in detail view
                        'link': link,
                        'source': 'craigslist',
                        'price': price_elem.text if price_elem else 'Negotiable',
                        'location': location_elem.text if location_elem else 'Location not specified'
                    }
                    
                    # Fetch full description
                    try:
                        self.driver.get(link)
                        desc_elem = wait.until(
                            EC.presence_of_element_located((By.ID, 'postingbody'))
                        )
                        quest['description'] = desc_elem.text
                    except TimeoutException:
                        logger.warning(f"Timeout fetching description for {link}")
                        quest['description'] = 'Description not available'
                    
                    quests.append(quest)
                    
                except Exception as e:
                    logger.error(f"Error processing Craigslist result: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error fetching from Craigslist: {e}", exc_info=True)
            
        return quests
    
    def close(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None

# Singleton instance
_quest_fetcher = None

def init_quest_fetcher(app):
    """Initialize the quest fetcher with app context."""
    global _quest_fetcher
    if not _quest_fetcher:
        _quest_fetcher = QuestFetcher(app.config)
    return _quest_fetcher

def fetch_gigs() -> List[Dict[str, Any]]:
    """Fetch gigs from all sources."""
    global _quest_fetcher
    if not _quest_fetcher:
        logger.error("QuestFetcher not initialized. Call init_quest_fetcher() first.")
        return []
    
    try:
        # Fetch from all sources in parallel (in a real app, use ThreadPoolExecutor)
        reddit_quests = _quest_fetcher.fetch_from_reddit()
        craigslist_quests = _quest_fetcher.fetch_from_craigslist()
        
        # Combine and deduplicate quests
        seen_links = set()
        all_quests = []
        
        for quest in reddit_quests + craigslist_quests:
            if quest['link'] not in seen_links:
                seen_links.add(quest['link'])
                all_quests.append(quest)
        
        return all_quests
        
    except Exception as e:
        logger.error(f"Error fetching gigs: {e}", exc_info=True)
        return []
    finally:
        if _quest_fetcher:
            _quest_fetcher.close()
