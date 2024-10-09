# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 17:31:28 2024

@author: phoen
"""

import feedparser
import hashlib
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
import dramatiq
from redis import Redis
from dramatiq.brokers.redis import RedisBroker
from dramatiq_file import classify_article  # Import the task

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database Setup
Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = 'news_articles'
    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    pub_date = Column(DateTime)
    source_url = Column(String)
    category = Column(String)

# Database connection
engine = create_engine('postgresql://postgres:Physics@6@localhost/DramatiqNewsFeed')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Redis connection and Dramatiq setup
redis_broker = RedisBroker(url="redis://localhost:6379/0")
dramatiq.set_broker(redis_broker)

def parse_pub_date(pub_date_str):
    if 'GMT' in pub_date_str:
        # Replace 'GMT' with '+0000' for UTC timezone
        pub_date_str = pub_date_str.replace('GMT', '+0000')
    try:
        return datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        # Handle other possible formats if needed
        return None

# RSS Feed Parser
def fetch_rss_feed(feed_url):
    try:
        logging.info(f'Fetching feed from {feed_url}')
        feed = feedparser.parse(feed_url)
        if feed.bozo == 1:
            logging.error(f"Error parsing feed: {feed_url}")
        return feed
    except Exception as e:
        logging.error(f"Error fetching RSS feed {feed_url}: {e}")
        return None

# Function to generate a unique hash for deduplication
def generate_article_hash(title, content):
    return hashlib.md5(f'{title}{content}'.encode('utf-8')).hexdigest()

# Save article to the database with deduplication
def save_article(article):
    article_hash = generate_article_hash(article['title'], article['content'])
    if not session.query(NewsArticle).filter_by(id=article_hash).first():
        new_article = NewsArticle(
            id=article_hash,
            title=article['title'],
            content=article['content'],
            pub_date=article['pub_date'],
            source_url=article['source_url']
        )
        session.add(new_article)
        session.commit()
        logging.info(f'Saved article: {article["title"]}')
    else:
        logging.info(f'Duplicate article skipped: {article["title"]}')

# List of RSS feeds
feeds = [
    'http://rss.cnn.com/rss/cnn_topstories.rss', 
    'http://qz.com/feed',
    'http://feeds.foxnews.com/foxnews/politics',
    'http://feeds.reuters.com/reuters/businessNews',
    'http://feeds.feedburner.com/NewshourWorld',
    'https://feeds.bbci.co.uk/news/world/asia/india/rss.xml'
]

# Process and save articles
try:
    for feed_url in feeds:
        feed = fetch_rss_feed(feed_url)
        if feed:
            for entry in feed.entries:
                article_data = {
                    'title': entry.get('title', ''),
                    'content': entry.get('summary', ''),
                    'pub_date': parse_pub_date(entry.get('published', '')) if entry.get('published') else None,
                    'source_url': entry.get('link', '')
                    }
                
                # Convert datetime to ISO 8601 string for JSON serialization
                if article_data['pub_date']:
                    article_data['pub_date'] = article_data['pub_date'].isoformat()

                save_article(article_data)
                
                # Send to Dramatiq task for classification
                classify_article.send(article_data)  # Now you can use .send() method with the @actor decorated task
except Exception as e:
    logging.error(f"An error occurred while processing feeds: {e}")

