"""
Scoring service for calculating quest rankings and difficulty scores.
"""
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class QuestScore:
    """Represents the calculated scores for a quest."""
    difficulty: float
    relevance: float
    popularity: float
    final_score: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert the score to a dictionary."""
        return {
            'difficulty': self.difficulty,
            'relevance': self.relevance,
            'popularity': self.popularity,
            'final_score': self.final_score
        }

class ScoringService:
    """Service for calculating quest rankings and difficulty scores."""
    
    # Difficulty weights
    DIFFICULTY_WEIGHTS = {
        'length': 0.3,
        'complexity': 0.4,
        'requirements': 0.3
    }
    
    # Relevance weights
    RELEVANCE_WEIGHTS = {
        'recency': 0.4,
        'skills_match': 0.4,
        'location': 0.2
    }
    
    # Popularity weights
    POPULARITY_WEIGHTS = {
        'views': 0.3,
        'bookmarks': 0.4,
        'completion_rate': 0.3
    }
    
    @staticmethod
    def calculate_difficulty(quest_data: Dict) -> float:
        """
        Calculate the difficulty score of a quest.
        
        Args:
            quest_data: Dictionary containing quest data
            
        Returns:
            float: Difficulty score between 0 and 1
        """
        # Calculate length component (0-1)
        length = min(quest_data.get('length_minutes', 0) / 240, 1.0)  # Max 4 hours
        
        # Calculate complexity component (0-1)
        complexity = min(quest_data.get('complexity', 0) / 5.0, 1.0)  # Assuming 1-5 scale
        
        # Calculate requirements component (0-1)
        requirements = min(len(quest_data.get('requirements', [])) / 5.0, 1.0)  # Max 5 requirements
        
        # Calculate weighted sum
        weights = ScoringService.DIFFICULTY_WEIGHTS
        difficulty = (
            weights['length'] * length +
            weights['complexity'] * complexity +
            weights['requirements'] * requirements
        )
        
        return min(max(difficulty, 0.0), 1.0)
    
    @staticmethod
    def calculate_relevance(quest_data: Dict, user_data: Optional[Dict] = None) -> float:
        """
        Calculate the relevance score of a quest for a user.
        
        Args:
            quest_data: Dictionary containing quest data
            user_data: Optional dictionary containing user data
            
        Returns:
            float: Relevance score between 0 and 1
        """
        # Calculate recency component (0-1, higher for newer quests)
        posted_date = quest_data.get('posted_date', datetime.utcnow())
        days_old = (datetime.utcnow() - posted_date).total_seconds() / (24 * 3600)
        recency = max(0, 1 - (days_old / 30))  # Decay over 30 days
        
        # Default skills match score
        skills_match = 0.5
        
        if user_data and 'skills' in user_data and 'required_skills' in quest_data:
            # Calculate skills match (0-1)
            user_skills = set(skill.lower() for skill in user_data['skills'])
            required_skills = set(skill.lower() for skill in quest_data['required_skills'])
            
            if required_skills:
                matching_skills = user_skills.intersection(required_skills)
                skills_match = len(matching_skills) / len(required_skills)
        
        # Default location score
        location = 0.5
        
        if user_data and 'location' in user_data and 'location' in quest_data:
            # Simple location matching (0 or 1)
            location = 1.0 if user_data['location'] == quest_data['location'] else 0.0
        
        # Calculate weighted sum
        weights = ScoringService.RELEVANCE_WEIGHTS
        relevance = (
            weights['recency'] * recency +
            weights['skills_match'] * skills_match +
            weights['location'] * location
        )
        
        return min(max(relevance, 0.0), 1.0)
    
    @staticmethod
    def calculate_popularity(quest_data: Dict) -> float:
        """
        Calculate the popularity score of a quest.
        
        Args:
            quest_data: Dictionary containing quest data
            
        Returns:
            float: Popularity score between 0 and 1
        """
        # Calculate views component (0-1)
        views = min(quest_data.get('views', 0) / 1000.0, 1.0)  # Max 1000 views
        
        # Calculate bookmarks component (0-1)
        bookmarks = min(quest_data.get('bookmarks', 0) / 100.0, 1.0)  # Max 100 bookmarks
        
        # Calculate completion rate component (0-1)
        completions = quest_data.get('completions', 0)
        attempts = max(quest_data.get('attempts', 1), 1)  # Avoid division by zero
        completion_rate = min(completions / attempts, 1.0)
        
        # Calculate weighted sum
        weights = ScoringService.POPULARITY_WEIGHTS
        popularity = (
            weights['views'] * views +
            weights['bookmarks'] * bookmarks +
            weights['completion_rate'] * completion_rate
        )
        
        return min(max(popularity, 0.0), 1.0)
    
    @classmethod
    def calculate_quest_score(
        cls,
        quest_data: Dict,
        user_data: Optional[Dict] = None,
        difficulty_weight: float = 0.3,
        relevance_weight: float = 0.4,
        popularity_weight: float = 0.3
    ) -> QuestScore:
        """
        Calculate the final score for a quest.
        
        Args:
            quest_data: Dictionary containing quest data
            user_data: Optional dictionary containing user data
            difficulty_weight: Weight for difficulty component (default: 0.3)
            relevance_weight: Weight for relevance component (default: 0.4)
            popularity_weight: Weight for popularity component (default: 0.3)
            
        Returns:
            QuestScore: Object containing all score components
        """
        # Normalize weights to ensure they sum to 1.0
        total_weight = difficulty_weight + relevance_weight + popularity_weight
        difficulty_weight /= total_weight
        relevance_weight /= total_weight
        popularity_weight /= total_weight
        
        # Calculate individual scores
        difficulty = cls.calculate_difficulty(quest_data)
        relevance = cls.calculate_relevance(quest_data, user_data)
        popularity = cls.calculate_popularity(quest_data)
        
        # Calculate final score
        final_score = (
            difficulty_weight * difficulty +
            relevance_weight * relevance +
            popularity_weight * popularity
        )
        
        return QuestScore(
            difficulty=difficulty,
            relevance=relevance,
            popularity=popularity,
            final_score=min(max(final_score, 0.0), 1.0)
        )
    
    @classmethod
    def rank_quests(
        cls,
        quests: List[Dict],
        user_data: Optional[Dict] = None,
        difficulty_weight: float = 0.3,
        relevance_weight: float = 0.4,
        popularity_weight: float = 0.3
    ) -> List[Tuple[Dict, QuestScore]]:
        """
        Rank a list of quests based on their scores.
        
        Args:
            quests: List of quest dictionaries
            user_data: Optional dictionary containing user data
            difficulty_weight: Weight for difficulty component (default: 0.3)
            relevance_weight: Weight for relevance component (default: 0.4)
            popularity_weight: Weight for popularity component (default: 0.3)
            
        Returns:
            List of (quest, score) tuples, sorted by final score (descending)
        """
        # Calculate scores for all quests
        scored_quests = []
        for quest in quests:
            score = cls.calculate_quest_score(
                quest,
                user_data=user_data,
                difficulty_weight=difficulty_weight,
                relevance_weight=relevance_weight,
                popularity_weight=popularity_weight
            )
            scored_quests.append((quest, score))
        
        # Sort by final score (descending)
        return sorted(scored_quests, key=lambda x: x[1].final_score, reverse=True)
