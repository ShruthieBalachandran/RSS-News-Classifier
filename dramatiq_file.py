# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 17:59:34 2024

@author: phoen
"""

import hashlib
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging
import dramatiq

# Database Setup (should match the setup in your main script)
engine = create_engine('postgresql://postgres:Physics@6@localhost/DramatiqNewsFeed')
Session = sessionmaker(bind=engine)

# Function to generate a unique hash for deduplication
def generate_article_hash(title, content):
    return hashlib.md5(f'{title}{content}'.encode('utf-8')).hexdigest()

# Task Worker for Dramatiq Queue
@dramatiq.actor
def classify_article(article_data):
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        nltk.download('punkt')
        nltk.download('stopwords')

        # Define categories and keywords
        categories = {
    "Terrorism": [
        "terrorism", "terrorist", "attack", "bombing", "extremism",
        "militant", "insurgent", "jihad", "radicalization", "violence",
        "threat", "hostage", "act of terror", "security", "conspiracy", "fundamentalism", "plot", "sabotage"
    ],
    "Protest": [
        "protest", "demonstration", "rally", "march", "sit-in", "advocacy",
        "campaign", "gathering", "public display", "activism", "dissent",
        "petition", "social movement", "awareness", "outcry", "mobilization",
        "collective action", "peaceful assembly"
    ],
    "Political Unrest": [
        "political unrest", "turmoil", "chaos", "discontent", "civil strife",
        "revolt", "rebellion", "civil war", "instability", "uprising",
        "reform movement", "power struggle", "government dissatisfaction",
        "policy conflict", "overthrow", "resistance", "insurrection", "judge"
    ],
    "Riot": [
        "riot", "mob", "civil disorder", "unrest", "chaos", "violence",
        "clashes", "fighting", "looting", "vandalism", "insurrection",
        "disturbance", "aggression", "mayhem", "brawl", "street fight",
        "violent protest"
    ],
    "Positive/Uplifting": [
        "happy", "joy", "positive", "good", "uplifting", "success",
        "achievement", "celebration", "hope", "love", "progress",
        "inspiration", "encouragement", "smile", "community", "gratitude",
        "kindness", "support", "unity", "wellness", "beneficial", 
        "optimistic", "bright", "joyful", "promising", "victory"
    ],
    "Natural Disasters": [
        "earthquake", "flood", "hurricane", "storm", "disaster",
        "wildfire", "tsunami", "landslide", "avalanche", "drought",
        "calamity", "severe weather", "catastrophe", "emergency", 
        "rescue", "evacuation", "damage", "devastation", 
        "natural calamity", "crisis", "heatwave", "famine", 
        "tornado", "blizzard", "mudslide", "hazard"
    ],
    "Others": []
}
        
        stop_words = set(stopwords.words('english'))

        # Tokenize and clean article content
        word_tokens = word_tokenize(article_data['content'].lower())
        filtered_content = [w for w in word_tokens if w not in stop_words]

        # Simple keyword matching for classification
        article_category = 'others'
        for category, keywords in categories.items():
            if any(keyword in filtered_content for keyword in keywords):
                article_category = category
                break

        # Update article category in the database
        session = Session()
        article_in_db = session.query(NewsArticle).filter_by(id=generate_article_hash(article_data['title'], article_data['content'])).first()
        if article_in_db:
            article_in_db.category = article_category
            session.commit()
            logging.info(f'Article classified as {article_category}: {article_data["title"]}')
        session.close()

    except Exception as e:
        logging.error(f"Error classifying article: {article_data['title']}, Error: {str(e)}")
