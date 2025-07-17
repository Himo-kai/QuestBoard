# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
from pathlib import Path

def load_keywords():
    """Load gear keywords from JSON configuration with validation"""
    config_path = Path(__file__).parent / "gear_keywords.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Gear keywords configuration not found at {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            keywords = json.load(f)
            
        # Validate the structure
        if not isinstance(keywords, dict):
            raise ValueError("Keywords configuration must be a dictionary")
            
        for category, data in keywords.items():
            if not isinstance(data, dict):
                logger.warning(f"Warning: Unexpected category format for {category}")
                continue
                
            if "common" in data and not isinstance(data["common"], list):
                logger.warning(f"Warning: 'common' keywords for {category} should be a list")
                
            if "specific" in data:
                if not isinstance(data["specific"], dict):
                    logger.warning(f"Warning: 'specific' section for {category} should be a dictionary")
                    continue
                for subcat, items in data["specific"].items():
                    if not isinstance(items, list):
                        logger.warning(f"Warning: Subcategory {subcat} in {category} should contain a list")
        
        return keywords
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing keywords JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading keywords: {e}")
        raise

def get_all_keywords():
    """Get all keywords from the configuration"""
    all_keywords = []
    
    # Add common keywords from all categories
    for category in gear_keywords.values():
        all_keywords.extend(category)
    
    return set(all_keywords)  # Remove duplicates

def get_category_keywords(category):
    """Get keywords for a specific category"""
    if category in gear_keywords:
        return gear_keywords[category]
    return None

def get_subcategory_keywords(category, subcategory):
    """Get keywords for a specific subcategory"""
    keywords = load_keywords()
    if category in keywords and "specific" in keywords[category]:
        return keywords[category]["specific"].get(subcategory, [])
    return []

def matches_keyword(text, category=None, subcategory=None):
    """Check if text matches any keywords in the specified category/subcategory"""
    text = text.lower()
    
    if category and subcategory:
        keywords = get_subcategory_keywords(category, subcategory)
    elif category:
        keywords = get_category_keywords(category)
    else:
        keywords = get_all_keywords()
    
    if not keywords:
        return False
    
    # Check for exact matches and partial matches
    for keyword in keywords:
        if keyword.lower() in text:
            return True
    return False
