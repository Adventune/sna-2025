"""
Named entity recognition (NER) on the dataset.
"""

import os
import json
from tqdm import tqdm
import pandas as pd

organisations = None
articles = None

with open("data/organisations.json", "r", encoding="utf-8") as f:
    organisations = json.load(f)

with open("data/articles_47733.json", "r", encoding="utf-8") as f:
    articles = json.load(f)

if os.path.exists("data/articles_47733_with_organisations.json"):
    with open(
        "data/articles_47733_with_organisations.json", "r", encoding="utf-8"
    ) as f:
        articles = json.load(f)
else:
    for article in tqdm(articles):
        article_text = (
            article["title"]
            + " "
            + article["headline_title"]
            + " "
            + article["headline_summary"]
            + " "
            + article["body"]
            + " "
            + " ".join(
                [
                    source["shortname"] + " " + source["longname"]
                    for source in article["sources"]
                ]
            )
        ).lower()

        for org_id, values in organisations.items():

            if values["name"].lower() in article_text:
                if "organisations" not in article:
                    article["organisations"] = []
                article["organisations"].append(
                    {"id": org_id, "name": values["shortname"]}
                )
            # Else if any of the space separated words in the article text is the shortname
            elif any(
                word == values["shortname"].lower() for word in article_text.split()
            ):
                if "organisations" not in article:
                    article["organisations"] = []
                article["organisations"].append(
                    {"id": org_id, "name": values["shortname"]}
                )

    # Save the updated articles to a new JSON file
    with open(
        "data/articles_47733_with_organisations.json", "w", encoding="utf-8"
    ) as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)


# Pandas edge dataset
df = pd.DataFrame(columns=["source", "target"])

for article in tqdm(articles):
    if "organisations" in article:
        for org in article["organisations"]:
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "source": [org["id"]],
                            "target": [article["id"]],
                        }
                    ),
                ],
                ignore_index=True,
            )


# Save the dataframe to a CSV file
df.to_csv("data/edges.csv", index=False)
