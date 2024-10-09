# RSS-News-Classifier

**Overview**
RSS News Classifier is an application that collects articles from various RSS feeds, stores them in a PostgreSQL database, and classifies them into predefined categories using a simple keyword-based classification model. The classification tasks are handled asynchronously using Dramatiq, a task queue library, with Redis as the message broker. nltk (Natural Language Toolkit) is used for tokenizing the article content and removing stopwords during classification.

Features
RSS Feed Parsing: Fetches articles from multiple RSS feeds.
Article Deduplication: Ensures no duplicate articles are saved to the database using a unique hash based on article title and content.
Asynchronous Processing: Uses Dramatiq to classify articles asynchronously, improving the responsiveness of the system.
Simple Keyword-based Classification: Articles are classified into categories like 'terrorism', 'positive', 'natural disasters', and 'others' based on keywords found in the article content, processed using nltk.
Database Integration: Stores fetched articles in a PostgreSQL database with fields like title, content, publication date, source URL, and category.
Tech Stack
Programming Language: Python
Database: PostgreSQL
Task Queue: Dramatiq with Redis as the broker
Libraries:
feedparser for RSS parsing
SQLAlchemy for ORM
Dramatiq for task queues
nltk for tokenizing article content and removing stopwords
nltk corpora like punkt and stopwords
