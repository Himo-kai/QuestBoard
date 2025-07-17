# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from sentence_transformers import SentenceTransformer, util
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the pre-trained model
model = None
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Successfully loaded sentence transformer model")
except Exception as e:
    logger.error(f"Failed to load sentence transformer model: {e}")

# Reference descriptions for difficulty comparison
REFERENCE_TEXTS = {
    'very_easy': "A simple, quick task that requires minimal effort or skill.",
    'easy': "A straightforward task that requires basic knowledge or skills.",
    'moderate': "A task that requires some experience and may take several hours to complete.",
    'hard': "A challenging task that requires specialized skills or knowledge.",
    'very_hard': "An extremely difficult task that requires expert-level skills and significant time investment."
}

# Pre-compute reference embeddings
REFERENCE_EMBEDDINGS = {}

def get_reference_embeddings():
    """Get or compute reference embeddings for difficulty comparison."""
    global REFERENCE_EMBEDDINGS
    
    if not REFERENCE_EMBEDDINGS and model:
        try:
            for level, text in REFERENCE_TEXTS.items():
                REFERENCE_EMBEDDINGS[level] = model.encode(text)
            logger.info("Successfully computed reference embeddings")
        except Exception as e:
            logger.error(f"Error computing reference embeddings: {e}")
    
    return REFERENCE_EMBEDDINGS

def rate_difficulty_nlp(text: str) -> float:
    """
    Rate the difficulty of a quest using NLP.
    
    Args:
        text: The quest title and description
        
    Returns:
        float: A difficulty score between 0 (easiest) and 10 (hardest)
    """
    if not model:
        logger.warning("NLP model not available, falling back to default difficulty")
        return 5.0  # Default to medium difficulty if model fails
    
    try:
        # Get or compute reference embeddings
        ref_embeddings = get_reference_embeddings()
        if not ref_embeddings:
            logger.warning("Could not get reference embeddings")
            return 5.0
        
        # Encode the input text
        text_embedding = model.encode(text)
        
        # Calculate similarity with each reference text
        similarities = {}
        for level, ref_embedding in ref_embeddings.items():
            similarity = util.cos_sim(text_embedding, ref_embedding).item()
            similarities[level] = similarity
        
        # Normalize similarities to sum to 1
        total = sum(similarities.values())
        if total > 0:
            normalized = {k: v/total for k, v in similarities.items()}
        else:
            normalized = {k: 1/len(similarities) for k in similarities}
        
        # Calculate weighted difficulty score (0-10 scale)
        difficulty_weights = {
            'very_easy': 1.0,
            'easy': 3.0,
            'moderate': 5.0,
            'hard': 7.5,
            'very_hard': 9.5
        }
        
        score = sum(normalized[level] * weight 
                   for level, weight in difficulty_weights.items())
        
        # Ensure score is within bounds
        score = max(0, min(10, score))
        
        logger.debug(f"Difficulty assessment - Text: {text[:100]}... | Score: {score:.2f}")
        return round(score, 2)
        
    except Exception as e:
        logger.error(f"Error in rate_difficulty_nlp: {e}")
        return 5.0  # Fallback to medium difficulty

def extract_key_phrases(text: str, top_n: int = 3) -> list:
    """
    Extract key phrases that might indicate difficulty.
    
    Args:
        text: The input text
        top_n: Number of key phrases to return
        
    Returns:
        list: List of key phrases
    """
    # Simple implementation - split into sentences and return most important ones
    # In a production system, you might use more sophisticated NLP techniques
    import re
    from collections import Counter
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    # Simple scoring based on word importance (can be enhanced)
    word_scores = Counter()
    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence.lower())
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_scores[word] += 1
    
    # Get top phrases (simple implementation)
    top_phrases = [phrase for phrase, _ in word_scores.most_common(top_n)]
    
    return top_phrases
