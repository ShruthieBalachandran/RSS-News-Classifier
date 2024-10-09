# RSS-News-Classifier

# Overview:
- RSS News Classifier is an application that collects articles from various RSS feeds, stores them in a PostgreSQL database, and classifies them into predefined categories using a simple keyword-based classification model. The classification tasks are handled asynchronously using Dramatiq, a task queue library, with Redis as the message broker. nltk (Natural Language Toolkit) is used for tokenizing the article content and removing stopwords during classification.

# Features
**RSS Feed Parsing:** Fetches articles from multiple RSS feeds.

**Article Deduplication:** Ensures no duplicate articles are saved to the database using a unique hash based on article title and content.

**Asynchronous Processing:** Uses Dramatiq to classify articles asynchronously, improving the responsiveness of the system.

**Simple Keyword-based Classification:** Articles are classified into categories like 'terrorism', 'positive', 'natural disasters', and 'others' based on keywords found in the article content, processed using nltk.

**Database Integration:** Stores fetched articles in a PostgreSQL database with fields like title, content, publication date, source URL, and category.

# Tech Stack
**Programming Language:** Python

**Database:** PostgreSQL

**Task Queue:** Dramatiq with Redis as the broker

# Libraries:
- **feedparser** for RSS parsing
- **SQLAlchemy** for ORM
- **Dramatiq** for task queues
- **nltk** for tokenizing article content and removing stopwords

# Installation

1. **Install required dependencies:**
- pip install -r requirements.txt
2. **Install nltk resources:** After installing the dependencies, you will also need to download the required nltk resources for tokenization and stopwords:
- import nltk
- nltk.download('punkt')
-  nltk.download('stopwords')
3. Set up a **PostgreSQL** database and configure the connection URL in your scripts. An example connection URL format is:
- postgresql://<username>:<password>@localhost/<database_name>
4. Set up **Redis** as a message broker for **Dramatiq**:
- Install Redis: https://redis.io/download
5. Start **Redis server**:
- redis-server
6. Run migrations to create the necessary tables in PostgreSQL:
- python RSSfeed_dramatiq.py

# Usage
1. **Run the Main Application:** This script fetches RSS feeds, saves articles to the database, and sends each article for classification.
- python RSSfeed_dramatiq.py
2. **Run the Worker for Classification:** In another terminal, run the worker that classifies the articles asynchronously:
- dramatiq article_classifier

# Example Feeds
The following RSS feeds are currently parsed by default:

- CNN: http://rss.cnn.com/rss/cnn_topstories.rss
- Quartz: http://qz.com/feed
- Fox News: http://feeds.foxnews.com/foxnews/politics
- Reuters: http://feeds.reuters.com/reuters/businessNews
- BBC: https://feeds.bbci.co.uk/news/world/asia/india/rss.xml

You can modify or add additional RSS feeds by updating the feeds list in rss_feed_collector.py.

# Database Structure
The database schema consists of a single table news_articles with the following fields:

- id: Unique hash based on the title and content.
- title: The title of the article.
- content: The summary or content of the article.
- pub_date: The publication date of the article.
- source_url: The URL where the article was originally published.
- category: The classified category for the article.

# Classification Categories
Articles are classified into the following categories based on keywords using nltk for content tokenization and stopword removal:

- Terrorism
- Political Unrest
- Protest
- Positive/uplifting
- Riot
- Natural Disasters
- Others

You can modify or extend the categories by editing the categories dictionary in article_classifier.py.

# Contributing
Contributions are welcome! Please feel free to submit a Pull Request or open an Issue for any improvements or bug fixes.
