# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os
import praw
from dotenv import load_dotenv
from datetime import datetime
import re
from typing import List, Dict
import logging
from gear_keywords import matches_keyword

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Reddit API credentials
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "QuestBoard/1.0")

# Configuration
SOURCE_TAG = "[r/DoneDirtCheap]"  # Source tag for Reddit posts
INVALID_FLAIRS = ["Meta"]  # Fewer restrictions on flairs

# Task-related keywords and patterns
TASK_KEYWORDS = [
    "[task]", "[TASK]", "[Task]", 
    "[hiring]", "[HIRING]", "[Hiring]",
    "[offer]", "[OFFER]", "[Offer]",
    "wanted", "looking for", "need help with",
    "paying", "budget", "compensation"
]

REWARD_PATTERNS = [
    r"\$\s?\d+",  # Matches $50, $ 50
    r"pay\s?\$?\d+",  # Matches pay $50, pay50
    r"\d+\s?\$",  # Matches 50 $, 50$
    r"\d+\.\d+\s?\$",  # Matches 50.50 $
    r"\$\s?\d+\.\d+",  # Matches $50.50
    r"\$\d+[Kk]\b",  # Matches $50k, $50K
    r"\d+[Kk]\s?\$",  # Matches 50k$, 50K $
    r"\b\d+\s?(dollars|USD|usd)\b"  # Matches 50 dollars, 50 USD
]

# Initialize Reddit client
def init_reddit_client():
    """Initialize the Reddit API client."""
    if not REDDIT_CLIENT_ID or not REDDIT_SECRET:
        raise ValueError("Reddit API credentials not set in environment.")
    
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

def extract_reward(text: str) -> str:
    """Extract reward information from text using regex patterns."""
    for pattern in REWARD_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    return "TBD"

def parse_task_difficulty(description: str) -> int:
    """Estimate task difficulty based on description length and complexity."""
    # Base difficulty from word count
    base_difficulty = min(3, max(1, len(description.split()) // 50))
    
    # Adjust for specific keywords
    if matches_keyword(description, category="tools", subcategory="power_tools"):
        base_difficulty += 1
    if matches_keyword(description, category="vehicles", subcategory="specialized"):
        base_difficulty += 1
    
    return min(5, max(1, base_difficulty))

def detect_required_gear(text: str) -> str:
    """Detect required gear based on keywords."""
    if matches_keyword(text, category="tools", subcategory="power_tools"):
        return "Power tools"
    elif matches_keyword(text, category="vehicles", subcategory="specialized"):
        return "Specialized vehicle"
    else:
        return "TBD"

def fetch_task_posts(limit: int = 20, subreddit: str = "DoneDirtCheap", sort: str = "new", time_filter: str = "day", 
                                after: str = None, before: str = None, filters: dict = None) -> List[Dict]:
    """Fetch tasks from Reddit with filtering and pagination support.
    
    Args:
        limit: Number of posts to fetch (default: 20)
        subreddit: Subreddit to fetch from (default: "DoneDirtCheap")
        sort: Sort order (new, hot, top) (default: "new")
        time_filter: Time filter for top posts (hour, day, week, month, year, all) (default: "day")
        after: Reddit fullname of the last post in previous batch
        before: Reddit fullname of the first post in next batch
        filters: Dictionary of additional filters (e.g., {'flair': 'Task', 'min_score': 10})
    """
    logger.info(f"Fetching up to {limit} posts from r/{subreddit} (sort: {sort}, time_filter: {time_filter})")
    
    # Validate Reddit credentials
    if not all([REDDIT_CLIENT_ID, REDDIT_SECRET, REDDIT_USER_AGENT]):
        error_msg = "Missing Reddit API credentials. Please run the .env wizard first."
        logger.error(error_msg)
        print(error_msg)
        return []
    
    try:
        reddit = init_reddit_client()
        subreddit = reddit.subreddit(subreddit)
        
        # Get posts with error handling
        posts = []
        try:
            if sort == "new":
                posts = list(subreddit.new(limit=limit))
            elif sort == "hot":
                posts = list(subreddit.hot(limit=limit))
            elif sort == "top":
                posts = list(subreddit.top(time_filter=time_filter, limit=limit))
            else:
                raise ValueError(f"Invalid sort type: {sort}")
        except praw.exceptions.APIException as e:
            logger.error(f"Reddit API error: {e}")
            return []
        except praw.exceptions.ClientException as e:
            logger.error(f"Reddit client error: {e}")
            return []
        except praw.exceptions.RedditError as e:
            logger.error(f"Reddit error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected Reddit error: {e}", exc_info=True)
            return []
        
        # Process posts
        tasks = []
        for post in posts:
            title = post.title
            description = post.selftext
            
            # Apply additional filters
            if filters:
                # Filter by flair
                if 'flair' in filters and post.link_flair_text != filters['flair']:
                    continue
                
                # Filter by score
                if 'min_score' in filters and post.score < filters['min_score']:
                    continue
                
                # Filter by creation time
                if 'min_age' in filters and post.created_utc < filters['min_age']:
                    continue
                
                # Filter by author
                if 'author' in filters and post.author and post.author.name != filters['author']:
                    continue
            
            # Skip posts with invalid flairs
            if post.link_flair_text and post.link_flair_text in INVALID_FLAIRS:
                logger.debug(f"Skipping post {post.id} due to invalid flair: {post.link_flair_text}")
                continue
            
            # More lenient task detection for r/DoneDirtCheap
            title_lower = title.lower()
            desc_lower = description.lower()
            
            # Log post details for debugging
            logger.debug(f"\n--- Processing Post ---")
            logger.debug(f"Title: {title}")
            logger.debug(f"Flair: {getattr(post, 'link_flair_text', 'None')}")
            
            # Check for common task indicators in title or description
            title_keywords = [k for k in TASK_KEYWORDS if k in title_lower]
            desc_keywords = [k for k in TASK_KEYWORDS if k in desc_lower]
            has_task_indicator = bool(title_keywords or desc_keywords)
            
            if title_keywords:
                logger.debug(f"Found task keywords in title: {title_keywords}")
            if desc_keywords:
                logger.debug(f"Found task keywords in description: {desc_keywords}")
            
            # Check for payment indicators
            payment_indicators = ["$", "usd", "dollar", "paying", "paid", "budget"]
            title_payments = [p for p in payment_indicators if p in title_lower]
            desc_payments = [p for p in payment_indicators if p in desc_lower]
            has_payment = bool(title_payments or desc_payments)
            
            if title_payments:
                logger.debug(f"Found payment indicators in title: {title_payments}")
            if desc_payments:
                logger.debug(f"Found payment indicators in description: {desc_payments}")
            
            # Check for request indicators
            request_phrases = ["looking for", "need help", "hiring", "wanted", "help with", "assistance with", "i need"]
            title_requests = [p for p in request_phrases if p in title_lower]
            desc_requests = [p for p in request_phrases if p in desc_lower]
            is_request = bool(title_requests or desc_requests)
            
            if title_requests:
                logger.debug(f"Found request phrases in title: {title_requests}")
            if desc_requests:
                logger.debug(f"Found request phrases in description: {desc_requests}")
            
            # Consider it a task if it has payment info or is a clear request
            is_task = has_payment or is_request or has_task_indicator
            
            # Skip if it's a meta post or discussion
            if post.link_flair_text and any(flair.lower() in post.link_flair_text.lower() for flair in INVALID_FLAIRS):
                logger.debug(f"Skipping post due to invalid flair: {post.link_flair_text}")
                continue
                
            logger.debug(f"Task detection - Has Payment: {has_payment}, Is Request: {is_request}, Has Task Indicator: {has_task_indicator}")
            logger.debug(f"Including as task: {is_task}")
                
            if is_task:
                try:
                    # Extract reward and calculate difficulty
                    reward = extract_reward(title + " " + description)
                    difficulty = parse_task_difficulty(description)
                    required_gear = detect_required_gear(description)
                    
                    tasks.append({
                        "title": f"{SOURCE_TAG} {title}",
                        "description": description,
                        "link": f"https://reddit.com{post.permalink}",
                        "reward": reward,
                        "difficulty": difficulty,
                        "source": "Reddit",
                        "gear_required": required_gear,
                        "author": post.author.name if post.author else "[deleted]",
                        "created_utc": post.created_utc,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "selftext": description  # Add selftext for debugging
                    })
                    logger.debug(f"Added task: {title[:50]}...")
                except Exception as e:
                    logger.error(f"Error processing Reddit post {post.id}: {e}", exc_info=True)
        
        return tasks
    except Exception as e:
        logger.error(f"Error fetching Reddit posts: {e}")
        return []
