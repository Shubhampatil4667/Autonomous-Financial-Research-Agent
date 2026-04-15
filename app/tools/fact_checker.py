from typing import Dict, Any
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download NLTK data if needed
try:
    nltk.data.find('punkt')
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def fact_checker(statement: str, context: str) -> Dict[str, Any]:
    """
    Advanced fact checking using semantic similarity and keyword analysis
    """
    try:
        # Preprocess texts
        statement_clean = preprocess_text(statement)
        context_clean = preprocess_text(context)

        # Calculate semantic similarity
        semantic_score = calculate_semantic_similarity(statement, context)

        # Calculate keyword overlap
        keyword_score = calculate_keyword_overlap(statement_clean, context_clean)

        # Check for numerical consistency
        numerical_score = check_numerical_consistency(statement, context)

        # Combine scores with weights
        overall_confidence = (semantic_score * 0.4 + keyword_score * 0.4 + numerical_score * 0.2)

        # Determine verification status
        verified = overall_confidence > 0.6

        # Generate supporting evidence
        evidence = generate_evidence(statement, context, semantic_score, keyword_score, numerical_score)

        return {
            "statement": statement,
            "verified": verified,
            "confidence": round(overall_confidence, 3),
            "semantic_similarity": round(semantic_score, 3),
            "keyword_overlap": round(keyword_score, 3),
            "numerical_consistency": round(numerical_score, 3),
            "supporting_evidence": evidence
        }

    except Exception as e:
        # Fallback to basic implementation
        return _basic_fact_check(statement, context)

def preprocess_text(text: str) -> str:
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    # Tokenize and remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(filtered_tokens)

def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity using TF-IDF"""
    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except:
        return 0.0

def calculate_keyword_overlap(text1: str, text2: str) -> float:
    """Calculate keyword overlap score"""
    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1:
        return 0.0

    overlap = len(words1.intersection(words2))
    return overlap / len(words1)

def check_numerical_consistency(statement: str, context: str) -> float:
    """Check if numerical values in statement appear in context"""
    # Extract numbers from both texts
    stmt_numbers = extract_numbers(statement)
    context_numbers = extract_numbers(context)

    if not stmt_numbers:
        return 1.0  # No numbers to check

    matches = 0
    for num in stmt_numbers:
        # Check if number appears in context (with some tolerance)
        if any(abs(num - ctx_num) / max(abs(num), abs(ctx_num)) < 0.01 for ctx_num in context_numbers):
            matches += 1

    return matches / len(stmt_numbers)

def extract_numbers(text: str) -> list:
    """Extract numerical values from text"""
    # Find all numbers (integers and decimals)
    numbers = re.findall(r'\d+\.?\d*', text)
    return [float(num) for num in numbers]

def generate_evidence(statement: str, context: str, semantic: float, keyword: float, numerical: float) -> str:
    """Generate human-readable evidence"""
    evidence_parts = []

    if semantic > 0.7:
        evidence_parts.append("High semantic similarity between statement and context")
    elif semantic > 0.4:
        evidence_parts.append("Moderate semantic similarity found")
    else:
        evidence_parts.append("Low semantic similarity detected")

    if keyword > 0.5:
        evidence_parts.append(f"Strong keyword overlap ({keyword:.1%})")
    elif keyword > 0.2:
        evidence_parts.append(f"Moderate keyword overlap ({keyword:.1%})")

    if numerical == 1.0:
        evidence_parts.append("All numerical values consistent")
    elif numerical > 0.5:
        evidence_parts.append("Most numerical values consistent")
    elif numerical > 0:
        evidence_parts.append("Some numerical values consistent")

    return "; ".join(evidence_parts)

def _basic_fact_check(statement: str, context: str) -> Dict[str, Any]:
    """Fallback basic fact checking"""
    statement_words = set(statement.lower().split())
    context_words = set(context.lower().split())

    overlap = len(statement_words.intersection(context_words))
    confidence = min(overlap / len(statement_words), 1.0) if statement_words else 0.0

    return {
        "statement": statement,
        "verified": confidence > 0.3,
        "confidence": confidence,
        "supporting_evidence": f"Found {overlap} matching terms in context"
    }