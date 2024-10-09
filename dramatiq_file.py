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
        categories = {'terrorism': ['terrorism', 'protest', 'political unrest', 'riot'],
                      'positive': ['positive', 'uplifting', 'good news'],
                      'natural_disasters': ['earthquake', 'flood', 'hurricane', 'natural disaster'],
                      'others': []
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
