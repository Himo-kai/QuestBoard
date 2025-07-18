"""
Tests for the NLP service functionality.
"""
import inspect
import pytest
import numpy as np
from questboard.services.nlp_service import NLPService

class TestNLPService:
    """Test cases for the NLPService class."""

    @pytest.fixture
    def nlp_service(self):
        """Create an instance of NLPService for testing."""
        return NLPService()

    def test_extract_keywords_simple(self, nlp_service):
        """Test keyword extraction with a simple test case."""
        print("\n" + "="*80)
        print("TEST - Starting test_extract_keywords_simple")
        
        # Test data
        text = "Fix broken website UI"
        expected_keywords = ["fix", "broken", "website", "ui"]
        
        print(f"TEST - Input text: {text!r}")
        print(f"TEST - Expected keywords: {expected_keywords}")
        
        # Print method info
        method = getattr(nlp_service, 'extract_keywords', None)
        print(f"\nDEBUG - extract_keywords method: {method}")
        if method:
            print(f"  Source file: {inspect.getfile(method.__code__) if hasattr(method, '__code__') else 'Unknown'}")
            try:
                source = inspect.getsource(method)
                print(f"  Source code:\n{source}")
            except Exception as e:
                print(f"  Could not get source: {e}")
        
        # Call the method
        print("\nDEBUG - Calling extract_keywords...")
        result = nlp_service.extract_keywords(text)
        
        # Print the result
        print("\nDEBUG - Method call result:")
        print(f"  Type: {type(result).__name__}")
        print(f"  Value: {result!r}")
        
        # Check if result is a list
        if isinstance(result, list):
            print("  List items:")
            for i, item in enumerate(result):
                print(f"    {i}: {item!r} (type: {type(item).__name__})")
        
        # Check type assertions
        assert isinstance(result, list), f"Expected list, got {type(result).__name__}"
        assert all(isinstance(kw, str) for kw in result), \
            f"Not all items are strings: {[type(kw).__name__ for kw in result]}"
        
        # Check for missing keywords
        missing = [kw for kw in expected_keywords if kw not in result]
        if missing:
            print(f"TEST - Missing keywords: {missing}")
        
        # Final assertion with detailed error message
        assert all(kw in result for kw in expected_keywords), \
            f"Expected keywords {expected_keywords} not found in result {result}"
        
        print("\nTEST - All assertions passed!")
        print("="*80)

    @pytest.mark.parametrize('text,expected_difficulty', [
        ("simple task", 2.0),
        ("moderate complexity task", 5.0),
        ("very complex and challenging project", 8.0),
    ])
    def test_calculate_difficulty(self, nlp_service, text, expected_difficulty):
        """Test difficulty calculation."""
        result = nlp_service.calculate_difficulty(text)
        assert isinstance(result, float)
        # Allow some tolerance in the result
        assert abs(result - expected_difficulty) <= 3.0

    def test_similarity_score(self, nlp_service):
        """Test text similarity scoring."""
        text1 = "web development project"
        text2 = "website development task"
        text3 = "completely different topic"
        
        # Similar texts should have higher similarity
        score_similar = nlp_service.similarity_score(text1, text2)
        # Different texts should have lower similarity
        score_different = nlp_service.similarity_score(text1, text3)
        
        assert 0 <= score_similar <= 1.0
        assert 0 <= score_different <= 1.0
        assert score_similar > score_different

    def test_suggest_gear(self, nlp_service):
        """Test gear suggestion based on quest description."""
        description = "I need to build a website with a database backend"
        suggestions = nlp_service.suggest_gear(description)
        
        assert isinstance(suggestions, list)
        assert all(isinstance(item, str) for item in suggestions)
        assert len(suggestions) > 0

    def test_fit_vectorizer(self, nlp_service, tmp_path):
        """Test fitting the TF-IDF vectorizer with custom data."""
        # Create a temporary directory for the test
        vectorizer_path = tmp_path / "test_vectorizer.pkl"
        
        # Test data
        documents = [
            "web development project",
            "mobile app development",
            "data analysis task"
        ]
        
        # Fit the vectorizer
        nlp_service.fit_vectorizer(documents, str(vectorizer_path))
        
        # Check if the vectorizer file was created
        assert vectorizer_path.exists()
        
        # Test if the vectorizer can transform new text
        vector = nlp_service.vectorizer.transform(["new web project"])
        assert vector.shape[0] == 1  # One document
        assert vector.shape[1] > 0   # At least one feature

    def test_load_vectorizer(self, nlp_service, tmp_path):
        """Test loading a pre-trained vectorizer."""
        # First, create and save a vectorizer
        vectorizer_path = tmp_path / "test_vectorizer.pkl"
        documents = ["test document"]
        nlp_service.fit_vectorizer(documents, str(vectorizer_path))
        
        # Create a new instance and load the vectorizer
        new_service = NLPService()
        new_service.load_vectorizer(str(vectorizer_path))
        
        # Test if the loaded vectorizer works
        vector = new_service.vectorizer.transform(["test"])
        # The vectorizer creates 3 features for the input "test document"
        assert vector.shape == (1, 3)  # One document and three features
