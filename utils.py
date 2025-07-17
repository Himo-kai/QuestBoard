# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTTP Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

def get_session_with_headers():
    """Return a requests.Session with default headers."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session

def colored(text: str, color_code: str) -> str:
    """Return colored text using ANSI escape codes."""
    return f"\033[{color_code}m{text}\033[0m"

def print_colored(text: str, color_code: str = "1;34") -> None:
    """Print text with color."""
    print(colored(text, color_code))

def print_header() -> None:
    """Print a colored header for the wizard."""
    print_colored("\n⚔️  Welcome to QuestBoard's Reddit Setup Wizard ⚔️", "1;34")
    print_colored("This wizard will help you set up your Reddit API credentials.", "1;34")
    print("\nPress Enter to continue...")
    input()

def validate_quest_data(quest_data: Dict[str, Any]) -> bool:
    """Validate quest data before submission."""
    required_fields = ['title', 'description', 'source']
    for field in required_fields:
        if not quest_data.get(field):
            logger.warning(f"Missing required field: {field}")
            return False
    return True

def format_quest_for_display(quest: Dict[str, Any]) -> Dict[str, Any]:
    """Format quest data for display in the UI."""
    return {
        'id': quest.get('id'),
        'title': quest.get('title', 'Untitled Quest'),
        'description': quest.get('description', ''),
        'difficulty': quest.get('difficulty', 0),
        'reward': quest.get('reward', 'Not specified'),
        'source': quest.get('source', 'Unknown'),
        'created_at': quest.get('created_at', datetime.utcnow().isoformat()),
        'gear_required': quest.get('gear_required', 'None'),
        'region': quest.get('region', 'Unknown'),
        'submitted_by': quest.get('submitted_by', 'Anonymous')
    }

def calculate_quest_expiration(days: int = 30) -> datetime:
    """Calculate the expiration date for a quest."""
    return datetime.utcnow() + timedelta(days=days)

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and other attacks."""
    if not text:
        return text
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Escape special characters
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text

def load_config(config_path: str = 'config.json') -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def save_config(config: Dict[str, Any], config_path: str = 'config.json') -> bool:
    """Save configuration to a JSON file."""
    try:
        config_path = Path(config_path)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        return False

def get_region_from_ip(ip_address: str) -> str:
    """Get region from IP address using a free geolocation service."""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        if response.status_code == 200:
            data = response.json()
            return data.get('regionName', 'Unknown')
    except Exception as e:
        logger.warning(f"Could not get region from IP: {e}")
    return 'Unknown'

def format_difficulty_stars(difficulty: int) -> str:
    """Format difficulty as stars (1-5)."""
    if not isinstance(difficulty, (int, float)):
        return "★☆☆☆☆"
    
    # Convert to 1-5 scale if needed
    stars = min(5, max(1, int(round(difficulty / 2))))
    return "★" * stars + "☆" * (5 - stars)

def parse_duration(duration_str: str) -> Optional[timedelta]:
    """Parse a duration string (e.g., '2h 30m') into a timedelta."""
    if not duration_str:
        return None
        
    try:
        # Match patterns like '2h 30m', '1d', '45m', etc.
        time_units = {
            'd': 'days',
            'h': 'hours',
            'm': 'minutes',
            's': 'seconds'
        }
        
        parts = re.findall(r'([0-9]+[dhms])', duration_str.lower())
        if not parts:
            return None
            
        kwargs = {}
        for part in parts:
            num = int(part[:-1])
            unit = part[-1]
            if unit in time_units:
                kwargs[time_units[unit]] = num
                
        return timedelta(**kwargs) if kwargs else None
        
    except Exception as e:
        logger.warning(f"Could not parse duration '{duration_str}': {e}")
        return None
