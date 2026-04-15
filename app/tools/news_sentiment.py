import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any
from app.models.schemas import NewsItem
from datetime import datetime

# Download NLTK data if needed
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

def news_sentiment(news_articles: List[str]) -> List[NewsItem]:
    """
    Analyze sentiment of news articles
    """
    sia = SentimentIntensityAnalyzer()
    results = []

    for article in news_articles:
        sentiment = sia.polarity_scores(article)
        results.append(NewsItem(
            title=article[:50] + "...",
            content=article,
            sentiment=sentiment['compound'],
            date=datetime.now()
        ))

    return results