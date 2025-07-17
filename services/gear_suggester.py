# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Gear suggestion service for quests."""
import re
import logging
from typing import List, Dict, Any, Set, Tuple

logger = logging.getLogger(__name__)

class GearSuggester:
    """Handles gear suggestions based on quest content."""
    
    def __init__(self):
        """Initialize with default gear categories and mappings."""
        self.gear_categories = {
            'laptop': {'keywords': ['laptop', 'notebook', 'macbook', 'surface', 'thinkpad'], 'priority': 1},
            'smartphone': {'keywords': ['iphone', 'android', 'smartphone', 'mobile', 'tablet'], 'priority': 2},
            'camera': {'keywords': ['camera', 'dslr', 'mirrorless', 'gopro', 'drone'], 'priority': 3},
            'tools': {'keywords': ['screwdriver', 'hammer', 'wrench', 'pliers', 'drill'], 'priority': 4},
            'safety': {'keywords': ['helmet', 'gloves', 'goggles', 'mask', 'vest'], 'priority': 5},
            'outdoor': {'keywords': ['tent', 'backpack', 'hiking', 'camping', 'sleeping bag'], 'priority': 6},
            'vehicle': {'keywords': ['car', 'truck', 'van', 'bike', 'scooter'], 'priority': 7},
            'software': {'keywords': ['photoshop', 'adobe', 'microsoft', 'autocad', 'sketch'], 'priority': 8},
            'audio': {'keywords': ['microphone', 'headphones', 'speaker', 'mixer', 'recorder'], 'priority': 9},
            'misc': {'keywords': [], 'priority': 99}  # Default category
        }
        
        # Specific gear items that map to categories
        self.gear_items = {
            'camera': ['Canon EOS R5', 'Sony A7 IV', 'DJI Mavic 3', 'GoPro Hero 10'],
            'laptop': ['MacBook Pro 16"', 'Dell XPS 15', 'Lenovo ThinkPad X1', 'Microsoft Surface Laptop 4'],
            'smartphone': ['iPhone 14 Pro', 'Samsung Galaxy S23', 'Google Pixel 7', 'OnePlus 11'],
            'tools': ['DeWalt Drill Set', 'Stanley Tool Kit', 'Makita Impact Driver', 'Klein Tools Multimeter'],
            'safety': ['3M Respirator', 'Honeywell Safety Glasses', 'Carhartt Work Gloves', 'MCR Safety Vest'],
            'outdoor': ['REI Co-op Half Dome Tent', 'Osprey Backpack', 'Yeti Cooler', 'Black Diamond Headlamp'],
            'vehicle': ['Hitch Cargo Carrier', 'Bike Rack', 'Car Roof Box', 'Trailer Hitch'],
            'software': ['Adobe Creative Cloud', 'Microsoft 365', 'AutoCAD', 'Figma'],
            'audio': ['Shure SM7B', 'Sony WH-1000XM5', 'Rode VideoMic', 'Focusrite Scarlett']
        }
        
        # Initialize regex patterns for each category
        self.patterns = {
            category: re.compile(r'\b(?:' + '|'.join(map(re.escape, data['keywords'])) + r')\b', re.IGNORECASE)
            for category, data in self.gear_categories.items()
            if data['keywords']  # Only create patterns for categories with keywords
        }
    
    def suggest_gear(self, text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Suggest gear based on the quest description.
        
        Args:
            text: The quest description text to analyze
            limit: Maximum number of gear suggestions to return
            
        Returns:
            List of dictionaries containing gear suggestions with 'category', 'items', and 'confidence'
        """
        if not text or not isinstance(text, str):
            return []
        
        try:
            # Find matching categories
            matched_categories = self._find_matching_categories(text)
            
            # Get gear suggestions for matched categories
            suggestions = []
            for category, confidence in matched_categories:
                if category in self.gear_items:
                    suggestions.append({
                        'category': category,
                        'items': self.gear_items[category][:3],  # Top 3 items per category
                        'confidence': confidence
                    })
            
            # Sort by confidence (highest first) and then by category priority
            suggestions.sort(key=lambda x: (-x['confidence'], 
                                         self.gear_categories.get(x['category'], {}).get('priority', 99)))
            
            # Limit the number of suggestions
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error suggesting gear: {e}", exc_info=True)
            return []
    
    def _find_matching_categories(self, text: str) -> List[Tuple[str, float]]:
        """Find categories that match the text with confidence scores."""
        matches = []
        total_matches = 0
        
        # Count matches for each category
        for category, pattern in self.patterns.items():
            match_count = len(pattern.findall(text))
            if match_count > 0:
                matches.append((category, match_count))
                total_matches += match_count
        
        # Calculate confidence scores (normalized by total matches)
        if total_matches == 0:
            # No matches found, return default suggestions
            return [('misc', 0.1)]
        
        # Return categories with confidence scores
        return [(cat, count / total_matches) for cat, count in matches]
    
    def get_gear_categories(self) -> List[Dict[str, Any]]:
        """Get all available gear categories with their details."""
        return [
            {
                'id': cat_id,
                'name': ' '.join(word.capitalize() for word in cat_id.split('_')),
                'keywords': data['keywords'],
                'priority': data['priority']
            }
            for cat_id, data in self.gear_categories.items()
        ]

# Global instance
_gear_suggester = None

def get_gear_suggester() -> GearSuggester:
    """Get the global gear suggester instance."""
    global _gear_suggester
    if _gear_suggester is None:
        _gear_suggester = GearSuggester()
    return _gear_suggester

def suggest_gear(text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Suggest gear based on the given text."""
    return get_gear_suggester().suggest_gear(text, limit)

def get_gear_categories() -> List[Dict[str, Any]]:
    """Get all available gear categories."""
    return get_gear_suggester().get_gear_categories()
