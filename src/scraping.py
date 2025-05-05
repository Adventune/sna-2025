"""
Scrapes the ReliefWeb articles for the given disaster
"""

import datetime
import sys
import json
import tqdm
from rwapi import ReliefWebAPICaller

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


# Restructure the articles
formatted_articles = []
for article in article_contents.values():
    try:
        data = article["data"][0]
        fields = data["fields"]
        article_id = fields["id"]
        title = fields["title"]
        body = fields["body"]
        if "headline" in fields:
            headline_title = fields["headline"]["title"]
            headline_summary = fields["headline"]["summary"]
        else:
            headline_title = ""
            headline_summary = ""
        sources = []
        for source in fields["source"]:
            sources.append(
                {
                    "shortname": source.get("shortname", ""),
                    "longname": source.get("longname", ""),
                    "type": source.get("type", ""),
                }
            )
        date = fields["date"]

        # Construct the new object
        formatted_article = {
            "id": article_id,
            "title": title,
            "body": body,
            "headline_title": headline_title,
            "headline_summary": headline_summary,
            "sources": sources,
            "date": date,
        }
        formatted_articles.append(formatted_article)
    except KeyError as e:
        print(f"KeyError: {e} for article {article_id}")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing article {article_id}: {e}")
        sys.exit(1)


# Save the articles to a file
with open(f"data/articles_{DISASTER_ID}.json", "w", encoding="utf-8") as f:
    json.dump(formatted_articles, f, indent=2)
