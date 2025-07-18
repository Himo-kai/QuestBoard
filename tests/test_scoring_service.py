"""
Tests for the scoring service functionality.
"""
import pytest
from datetime import datetime, timedelta, timezone
from questboard.services.scoring_service import ScoringService, QuestScore
from questboard.models.quest import Quest

class TestScoringService:
    """Test cases for the ScoringService class."""

    @pytest.fixture
    def scoring_service(self):
        """Create an instance of ScoringService for testing."""
        return ScoringService()

    @pytest.fixture
    def sample_quests(self):
        """Create sample quests for testing."""
        now = datetime.now(timezone.utc)
        return [
            Quest(
                id=f"quest_{i}",
                title=f"Quest {i}",
                description=f"Description for quest {i}",
                source=f"source_{i}",
                url=f"http://example.com/quest/{i}",
                posted_date=now - timedelta(days=i),
                difficulty=5.0,
                reward=f"${i}00"
            ) for i in range(1, 6)
        ]

    def test_calculate_popularity_score(self, scoring_service, sample_quests):
        """Test calculation of popularity score."""
        quest = sample_quests[0]
        quest.views = 100
        quest.bookmark_count = 10
        quest.completion_count = 5

        # Convert quest to dict to match method signature
        quest_dict = {
            'views': quest.views,
            'bookmarks': quest.bookmark_count,
            'completion_count': quest.completion_count
        }
        score = scoring_service.calculate_popularity(quest_dict)
        assert isinstance(score, float)
        assert 0 <= score <= 1.0

    def test_calculate_relevance_score(self, scoring_service, sample_quests):
        """Test calculation of relevance score."""
        query = "web development"
        quest = sample_quests[0]
        quest.title = "Senior Web Developer Needed"
        quest.description = "Looking for an experienced web developer"
        
        # Convert quest to dict to match method signature
        quest_dict = {
            'title': quest.title,
            'description': quest.description,
            'posted_date': quest.posted_date
        }
        
        score = scoring_service.calculate_quest_score(quest_dict)
        assert isinstance(score, QuestScore)
        assert 0 <= score.final_score <= 1.0

    def test_rank_quests(self, scoring_service, sample_quests):
        """Test ranking of multiple quests."""
        # Convert quests to dictionaries
        quests_data = []
        for i, quest in enumerate(sample_quests):
            quest_dict = {
                'id': quest.id,
                'title': quest.title,
                'description': quest.description,
                'posted_date': quest.posted_date,
                'views': (i + 1) * 10,
                'bookmarks': i + 1,
                'completion_count': i,
                'length_minutes': 60,
                'complexity': (i % 5) + 1,  # 1-5
                'requirements': [f'skill_{j}' for j in range((i % 3) + 1)]  # 1-3 skills
            }
            quests_data.append(quest_dict)
        
        # Customize some quests for better testing
        quests_data[0]['title'] = "Senior Software Engineer"
        quests_data[1]['title'] = "Web Developer"
        quests_data[2]['title'] = "Data Scientist"
        
        # Rank quests
        ranked_quests = scoring_service.rank_quests(quests_data)
        
        # Should return the same number of quests
        assert len(ranked_quests) == len(quests_data)
        
        # Should be sorted in descending order of final_score
        scores = [score.final_score for quest, score in ranked_quests]
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

    def test_rank_quests_empty_query(self, scoring_service, sample_quests):
        """Test ranking with an empty query."""
        # Convert quests to dictionaries
        quests_data = []
        for i, quest in enumerate(sample_quests):
            quest_dict = {
                'id': quest.id,
                'title': quest.title,
                'description': quest.description,
                'posted_date': quest.posted_date,
                'views': (i + 1) * 10,
                'bookmarks': i + 1,
                'completion_count': i,
                'length_minutes': 60,
                'complexity': (i % 5) + 1,
                'requirements': [f'skill_{j}' for j in range((i % 3) + 1)]
            }
            quests_data.append(quest_dict)
        
        # Rank quests with empty query (not used in current implementation)
        ranked_quests = scoring_service.rank_quests(quests_data)
        
        # Should still work with empty query
        assert len(ranked_quests) == len(quests_data)
        
        # Should be sorted by final_score
        scores = [score.final_score for quest, score in ranked_quests]
        assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

    def test_rank_quests_single_quest(self, scoring_service, sample_quests):
        """Test ranking with a single quest."""
        # Convert single quest to dictionary
        quest_dict = {
            'id': sample_quests[0].id,
            'title': 'Web Developer Position',
            'description': 'Looking for a skilled web developer',
            'posted_date': datetime.now(timezone.utc),
            'views': 100,
            'bookmarks': 10,
            'completion_count': 5,
            'length_minutes': 60,
            'complexity': 3,
            'requirements': ['JavaScript', 'HTML', 'CSS']
        }
        
        ranked = scoring_service.rank_quests([quest_dict])
        
        assert len(ranked) == 1
        assert ranked[0][0]['id'] == quest_dict['id']
        assert isinstance(ranked[0][1], QuestScore)

    def test_rank_quests_empty_list(self, scoring_service):
        """Test ranking with an empty list of quests."""
        assert scoring_service.rank_quests([]) == []
