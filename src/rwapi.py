"""
API methods for ReliefWeb
"""

import os
import datetime
import json
import requests


class ReliefWebAPICaller:
    """
    Exception class for ReliefWeb API errors
    """

    def __init__(self, app_name, disaster_id, use_cache=True):
        """
        Initializes the ReliefWebAPICaller class
        :param app_name: The name of the api app
        :param disaster_id: The id of the disaster
        :param use_cache: Whether to use cache for articles
        """
        self.app_name = app_name
        self.disaster_id = disaster_id
        self.api_url = f"https://api.reliefweb.int/v1/reports?appname={app_name}"
        self.use_cache = use_cache

        os.makedirs("cache/articles", exist_ok=True)

    def list_articles(self, start=None, end=None):
        """
        Gets the articles for the given disaster id
        """

        if os.path.exists("cache/articles.json") and self.use_cache:
            print("Cache found, loading articles from cache")
            with open("cache/articles.json", "r", encoding="utf-8") as f:
                articles = json.load(f)
            return (len(articles), articles)

        payload = {
            "offset": 0,
            "limit": 0,  # Maximum that ReliefWeb allows is 1000
            "filter": {
                "conditions": [
                    {"field": "disaster.id", "value": self.disaster_id},
                    {"field": "format.id", "value": "10"},  # Only situation reports
                ],
                "operator": "AND",
            },
            "preset": "latest",
            "profile": "list",
        }
        # Post request
        response = requests.post(self.api_url, json=payload, timeout=30)
        response_json = response.json()

        total_articles = response_json["totalCount"]
        articles = []

        print(f"Total articles: {total_articles}")

        for i in range(0, total_articles, 1000):
            payload["offset"] = i
            payload["limit"] = min(1000, total_articles - i)

            print(f"Getting articles {i} to {i + payload['limit']}")

            response = requests.post(self.api_url, json=payload, timeout=5)
            response_json = response.json()

            for article in response_json["data"]:
                article_date = article["fields"]["date"]["created"]
                # Convert "2024-11-26T15:18:57+00:00" format to datetime
                article_date = datetime.datetime.strptime(
                    article_date, "%Y-%m-%dT%H:%M:%S%z"
                )
                if start and start.date() > article_date.date():
                    continue
                if end and end.date() < article_date.date():
                    continue

                articles.append(
                    {
                        "id": article["id"],
                        "title": article["fields"]["title"],
                        "date": article["fields"]["date"],
                        "countries": [
                            country["name"] for country in article["fields"]["country"]
                        ],
                        "primary_country": article["fields"]["primary_country"]["name"],
                        "article_url": article["fields"]["url"],
                        "api_url": article["href"],
                    }
                )

        # Save articles to cache
        if self.use_cache:
            with open("cache/articles.json", "w", encoding="utf-8") as f:
                json.dump(articles, f, ensure_ascii=False, indent=4)

        return (len(articles), articles)

    def get_article(self, article_id):
        """
        Gets the article for the given article id
        :param article_id: The id of the article
        """
        if os.path.exists(f"cache/articles/{article_id}.json") and self.use_cache:
            with open(f"cache/articles/{article_id}.json", "r", encoding="utf-8") as f:
                return json.load(f)

        response = requests.get(
            f"https://api.reliefweb.int/v1/reports/{article_id}?appname={self.app_name}",
            timeout=30,
        )
        response_json = response.json()

        # Save article to cache
        if self.use_cache:
            with open(f"cache/articles/{article_id}.json", "w", encoding="utf-8") as f:
                json.dump(response_json, f, ensure_ascii=False, indent=4)

        return response_json

    def list_organisations(self):
        """
        Lists the organisations
        """
        cached_organisations = {}
        if os.path.exists("cache/organisations.json") and self.use_cache:
            with open("cache/organisations.json", "r", encoding="utf-8") as f:
                cached_organisations = json.load(f)

        payload = {
            "filter": {"field": "status", "value": "active"},
            "preset": "latest",
            "profile": "list",
        }
        response = requests.post(
            "https://api.reliefweb.int/v1/sources?appname="
            + self.app_name
            + "&limit=0",
            json=payload,
            timeout=30,
        )
        response_json = response.json()

        total_organisations = response_json["totalCount"]
        organisations = {}

        j = 0
        with open("cache/organisations.json", "w", encoding="utf-8") as f:
            for i in range(0, total_organisations, 1000):
                response = requests.post(
                    "https://api.reliefweb.int/v1/sources?appname="
                    + self.app_name
                    + "&limit=1000&offset="
                    + str(i),
                    json=payload,
                    timeout=30,
                )
                response_json = response.json()

                for organisation in response_json["data"]:
                    j += 1
                    if j % 10 == 0:
                        print(f"Getting organisations {j} of {total_organisations}")
                    org_id = organisation["id"]
                    if org_id in cached_organisations:
                        organisations[org_id] = cached_organisations[org_id]
                        continue

                    href = organisation["href"]

                    response = requests.get(href, timeout=30)
                    if response.status_code != 200:
                        raise Exception(
                            f"Error getting organisation {org_id}: {response.status_code}"
                        )

                    org_json = response.json()
                    shortname = org_json["data"][0]["fields"]["shortname"]

                    organisations[org_id] = {
                        "name": organisation["fields"]["name"],
                        "shortname": shortname,
                        "type": org_json["data"][0]["fields"]["type"],
                    }

                    # Dump to cache
                    f.seek(0)
                    json.dump(
                        organisations,
                        f,
                        ensure_ascii=False,
                        indent=4,
                    )

        return response_json
