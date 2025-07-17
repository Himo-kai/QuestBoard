# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""Difficulty calculation service using TF-IDF and semantic analysis."""
import pickle
import logging
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import numpy as np
from database import get_database

logger = logging.getLogger(__name__)

class DifficultyEngine:
    """Handles difficulty calculation for quests."""
    
    def __init__(self, tech_themes: set, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize the difficulty engine."""
        self.tech_themes = tech_themes
        self.vectorizer = None
        self.semantic_model = None
        self.model_name = model_name
        self._load_models()
    
    def _load_models(self):
        """Load or create the necessary ML models."""
        # Load or create TF-IDF vectorizer
        try:
            with open('tfidf_vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
        except (FileNotFoundError, EOFError):
            self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Load semantic model (lazy load when needed)
        self.semantic_model = None
    
    def _get_semantic_model(self):
        """Lazy load the semantic model."""
        if self.semantic_model is None:
            try:
                self.semantic_model = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error(f"Failed to load semantic model: {e}")
                return None
        return self.semantic_model
    
    def calculate_difficulty_scores(self, quests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate difficulty scores for quests using TF-IDF and semantic analysis.
        
        Args:
            quests: List of quest dictionaries with 'title' and 'description'
            
        Returns:
            List of quests with added 'difficulty' score (1-5)
        """
        if not quests:
            return quests
        
        try:
            # Prepare texts for processing
            texts = [f"{q['title']} {q.get('description', '')}" for q in quests]
            
            # Fit TF-IDF if not already fitted
            if not hasattr(self.vectorizer, 'vocabulary_'):
                self.vectorizer.fit(texts)
                # Save the fitted vectorizer for future use
                with open('tfidf_vectorizer.pkl', 'wb') as f:
                    pickle.dump(self.vectorizer, f)
            
            # Transform texts to TF-IDF matrix
            tfidf_matrix = self.vectorizer.transform(texts)
            
            # Get cached difficulty curves
            db = get_database()
            curves = db.get_difficulty_curves()
            curve_dict = {f"{c['category']}_{c['keyword']}": c['difficulty_score'] 
                         for c in curves}
            
            # Process each quest
            for i, quest in enumerate(quests):
                # Get non-zero features and their scores
                feature_names = self.vectorizer.get_feature_names_out()
                feature_index = tfidf_matrix[i, :].nonzero()[1]
                tfidf_scores = [(idx, tfidf_matrix[i, idx]) for idx in feature_index]
                
                # Calculate base difficulty using TF-IDF
                base_difficulty = self._calculate_tfidf_difficulty(
                    tfidf_scores, feature_names, quest['source'], curve_dict)
                
                # Calculate semantic difficulty (if model is available)
                semantic_diff = self._calculate_semantic_difficulty(
                    quest['title'] + " " + quest.get('description', ''))
                
                # Combine scores (weighted average)
                if semantic_diff is not None:
                    # 70% TF-IDF, 30% semantic
                    final_difficulty = (0.7 * base_difficulty) + (0.3 * semantic_diff)
                else:
                    final_difficulty = base_difficulty
                
                # Ensure difficulty is within 1-5 range
                final_difficulty = max(1, min(5, final_difficulty))
                quest['difficulty'] = round(final_difficulty, 1)
                
                # Cache the difficulty curve for top words
                self._cache_difficulty_curves(quest, tfidf_scores, feature_names, db)
            
            return quests
            
        except Exception as e:
            logger.error(f"Error calculating difficulty scores: {e}", exc_info=True)
            # Set default difficulty in case of error
            for quest in quests:
                quest['difficulty'] = quest.get('difficulty', 3.0)
            return quests
    
    def _calculate_tfidf_difficulty(self, tfidf_scores, feature_names, source, curve_dict):
        """Calculate difficulty based on TF-IDF scores and cached curves."""
        base_difficulty = 0.0
        total_weight = 0.0
        
        for idx, score in tfidf_scores:
            word = feature_names[idx].lower()
            word_difficulty = 0.0
            
            # Base difficulty factors
            if len(word) > 7:  # Longer words are more complex
                word_difficulty += 0.5
            if word in self.tech_themes:  # Tech-related words are more complex
                word_difficulty += 1.5
            
            # Apply cached difficulty curve if available
            key = f"{source}_{word}"
            if key in curve_dict:
                word_difficulty += curve_dict[key] * 0.1  # Scale down the curve impact
            
            # Weight by TF-IDF score
            base_difficulty += word_difficulty * score
            total_weight += score
        
        # Normalize by total weight if not zero
        if total_weight > 0:
            base_difficulty /= total_weight
        
        # Scale to 1-5 range
        return min(5.0, max(1.0, base_difficulty * 2.5))
    
    def _calculate_semantic_difficulty(self, text: str) -> Optional[float]:
        """Calculate difficulty using semantic similarity."""
        model = self._get_semantic_model()
        if not model:
            return None
        
        try:
            # Encode reference texts
            easy_ref = "Simple task that requires basic skills"
            hard_ref = "Complex technical challenge requiring specialized knowledge"
            
            # Encode all texts
            embeddings = model.encode([easy_ref, hard_ref, text])
            easy_emb, hard_emb, text_emb = embeddings
            
            # Calculate similarities
            sim_easy = util.cos_sim(text_emb, easy_emb).item()
            sim_hard = util.cos_sim(text_emb, hard_emb).item()
            
            # Convert similarity to 1-5 scale
            # Higher similarity to hard text increases difficulty
            difficulty = 3.0 + (sim_hard - sim_easy) * 2.5
            return max(1.0, min(5.0, difficulty))
            
        except Exception as e:
            logger.warning(f"Semantic difficulty calculation failed: {e}")
            return None
    
    def _cache_difficulty_curves(self, quest, tfidf_scores, feature_names, db):
        """Cache difficulty curves for top words."""
        try:
            # Get top 5 most significant words
            top_words = sorted(
                [(feature_names[idx], float(score)) for idx, score in tfidf_scores],
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Cache each word's difficulty
            for word, score in top_words:
                db.add_difficulty_curve(
                    category=quest['source'],
                    keyword=word.lower(),
                    difficulty_score=quest['difficulty']
                )
                
        except Exception as e:
            logger.warning(f"Failed to cache difficulty curves: {e}")

# Global instance
_difficulty_engine = None

def init_difficulty_engine(tech_themes: set):
    """Initialize the global difficulty engine."""
    global _difficulty_engine
    if not _difficulty_engine:
        _difficulty_engine = DifficultyEngine(tech_themes)
    return _difficulty_engine

def calculate_difficulty_scores(quests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate difficulty scores for quests."""
    global _difficulty_engine
    if not _difficulty_engine:
        # Default tech themes if not initialized
        tech_themes = {
            "python", "developer", "frontend", "backend", "network", 
            "security", "automation", "api", "devops", "cloud", "database",
            "server", "container", "kubernetes", "docker", "aws", "azure", 
            "gcp", "javascript", "typescript", "react", "node", "linux", "git"
        }
        _difficulty_engine = DifficultyEngine(tech_themes)
    
    return _difficulty_engine.calculate_difficulty_scores(quests)
