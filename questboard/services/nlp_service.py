# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any

class NLPService:
    """Service for handling natural language processing tasks."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.tech_themes = {
            "python", "developer", "frontend", "backend", "network", 
            "security", "automation", "api", "devops", "cloud", "database",
            "server", "container", "kubernetes", "docker", "aws", "azure", 
            "gcp", "javascript", "typescript", "react", "node", "linux", "git"
        }
        self._is_fitted = False
    
    def fit(self, documents: List[str]):
        """Fit the TF-IDF vectorizer with training documents."""
        self.vectorizer.fit(documents)
        self._is_fitted = True
    
    def calculate_difficulty(self, text: str) -> float:
        """
        Calculate difficulty score for a quest based on its text.
        
        Args:
            text: The quest text to analyze
            
        Returns:
            float: Difficulty score between 1 (easiest) and 10 (hardest)
        """
        if not text:
            return 5.0
            
        # Basic text features
        word_count = len(text.split())
        char_count = len(text)
        avg_word_length = char_count / max(1, word_count)
        
        # Count technical terms
        text_lower = text.lower()
        tech_terms = sum(1 for term in self.tech_themes if term in text_lower)
        tech_density = tech_terms / max(1, word_count)
        
        # Calculate base score (1-10)
        score = 1.0
        score += min(4, word_count / 50)  # Up to 200 words
        score += min(3, avg_word_length / 5)  # Longer words = harder
        score += min(2, tech_terms * 0.5)  # More tech terms = harder
        
        return min(10.0, max(1.0, score))
    
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extract top N keywords from text."""
        if not self._is_fitted or not text.strip():
            return []
            
        tfidf_matrix = self.vectorizer.transform([text])
        feature_array = np.array(self.vectorizer.get_feature_names_out())
        tfidf_sorting = np.argsort(tfidf_matrix.toarray()).flatten()[::-1]
        
        return feature_array[tfidf_sorting][:top_n].tolist()
    
    def extract_reward(self, description: str) -> str:
        """Extract reward information from quest description."""
        if not description:
            return "Not specified"
            
        # Look for common reward patterns
        patterns = [
            r'(?i)(?:\$|€|£|¥)(\d+(?:\.\d{1,2})?)(?:\s*(?:USD|EUR|GBP|JPY))?',
            r'(?i)(?:pay(?:ing)?\s*[\w\s]*?)(\d+)(?:\s*(?:dollars|euros|pounds|yen))?',
            r'(?i)reward\s*:\s*\$?(\d+)',
            r'(?i)budget\s*:\s*\$?(\d+)',
            r'(?i)price\s*:\s*\$?(\d+)',
            r'(?i)compensation\s*:\s*\$?(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                amount = match.group(1)
                currency = "$" if "$" in match.group(0) else ""
                return f"{currency}{amount}"
                
        return "Not specified"

    def suggest_gear(self, text: str) -> List[Dict[str, Any]]:
        """
        Suggest gear based on quest description.
        
        Args:
            text: The quest description text
            
        Returns:
            List of dictionaries containing gear suggestions with categories
        """
        if not text:
            return []
            
        text_lower = text.lower()
        suggestions = []
        
        # Define gear categories and their keywords
        gear_categories = {
            "Coding": ["code", "programming", "developer", "software", "script"],
            "Hardware": ["computer", "laptop", "raspberry pi", "arduino", "circuit"],
            "Networking": ["network", "router", "switch", "firewall", "vpn"],
            "Security": ["security", "encryption", "penetration", "firewall", "vulnerability"],
            "Cloud": ["aws", "azure", "gcp", "cloud", "serverless"],
            "Tools": ["screwdriver", "pliers", "drill", "soldering", "multimeter"]
        }
        
        # Check each category
        for category, keywords in gear_categories.items():
            if any(keyword in text_lower for keyword in keywords):
                suggestions.append({
                    "category": category,
                    "confidence": 0.8,  # High confidence if keyword matches
                    "items": self._get_gear_items(category)
                })
        
        return suggestions
    
    def _get_gear_items(self, category: str) -> List[str]:
        """Get specific gear items for a category."""
        gear_items = {
            "Coding": ["Laptop", "IDE (VS Code/PyCharm)", "Git client", "Terminal", "Docker"],
            "Hardware": ["Raspberry Pi", "Arduino kit", "Multimeter", "Soldering iron", "Jumper wires"],
            "Networking": ["Ethernet cables", "Network switch", "WiFi analyzer", "Crimping tool", "Cable tester"],
            "Security": ["Kali Linux", "Wireshark", "Metasploit", "Hashcat", "Burp Suite"],
            "Cloud": ["AWS CLI", "Terraform", "Kubernetes", "Docker", "Serverless Framework"],
            "Tools": ["Screwdriver set", "Needle-nose pliers", "Wire strippers", "Multimeter", "Cable ties"]
        }
        return gear_items.get(category, [])
