"""
Scrapes the ReliefWeb articles for the given disaster
"""

import datetime
from rwapi import ReliefWebAPICaller
import tqdm

# Scraper configuration
DISASTER_ID = "47733"  # Cyclone Idai
DISASTER_NAME = "Cyclone Idai"
APP_NAME = "rwint-user-0"  # From ReliefWebs "Search to API query converter"
DISASTER_START = datetime.datetime(
    2019, 3, 1, 0, 0, 0
)  # Cyclone Idai start date - 3 days
DISASTER_END = DISASTER_START + datetime.timedelta(days=60)  # Start date + 60 days
USE_CACHE = True  # Use cache for articles

print(
    f"Scraping articles for {DISASTER_NAME} ({DISASTER_ID}) from {DISASTER_START} to {DISASTER_END}"
)

rwapi_caller = ReliefWebAPICaller(APP_NAME, DISASTER_ID, use_cache=USE_CACHE)

count, articles = rwapi_caller.list_articles(start=DISASTER_START, end=DISASTER_END)

print(f"Recieived total of {count} articles from the API after filtering")

# Get all article content
article_contents = {}
for article in tqdm.tqdm(articles):
    article_id = article["id"]
    article_content = rwapi_caller.get_article(article_id)
    article_contents[article_id] = article_content
