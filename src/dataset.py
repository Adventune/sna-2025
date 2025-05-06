"""
Named entity recognition (NER) on the dataset.
"""

import os
import datetime
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
        articles_with_orgs = json.load(f)
        print(f"Lengths are the same: {len(articles) == len(articles_with_orgs)}")
        print(f"Lenghts are: {len(articles)} {len(articles_with_orgs)}")
        articles = articles_with_orgs
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

earliest_date = datetime.datetime(2022, 3, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
for article in tqdm(articles):
    if "date" in article:
        article_date = datetime.datetime.fromisoformat(article["date"]["created"])
        earliest_date = min(earliest_date, article_date)

    if "organisations" in article:
        for org in article["organisations"]:
            df = pd.concat(
                [
                    df,
                    pd.DataFrame(
                        {
                            "source": [org["id"]],
                            "target": [article["id"]],
                            "created_at": [article["date"]["created"]],
                        }
                    ),
                ],
                ignore_index=True,
            )


# Split the dataframe into time frames
#  - first 7 days
#  - 8-21 days
#  - 22+ days

df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
REPORTING_START = df["created_at"].min()

df_first_7_days = df[df["created_at"] <= (REPORTING_START + datetime.timedelta(days=7))]
df_8_21_days = df[
    (df["created_at"] > REPORTING_START + datetime.timedelta(days=7))
    & (df["created_at"] <= REPORTING_START + datetime.timedelta(days=21))
]
df_22_plus_days = df[(df["created_at"] > REPORTING_START + datetime.timedelta(days=21))]

# Validation prints
print(
    df_first_7_days["created_at"].min(),
    df_first_7_days["created_at"].max(),
    len(df_first_7_days),
)
print(
    df_8_21_days["created_at"].min(),
    df_8_21_days["created_at"].max(),
    len(df_8_21_days),
)
print(
    df_22_plus_days["created_at"].min(),
    df_22_plus_days["created_at"].max(),
    len(df_22_plus_days),
)
print(
    df["created_at"].min(),
    df["created_at"].max(),
    len(df),
    len(df) == (len(df_first_7_days) + len(df_8_21_days) + len(df_22_plus_days)),
)

# Drop the created_at column from the dataframes
df_first_7_days = df_first_7_days.drop(columns=["created_at"])
df_8_21_days = df_8_21_days.drop(columns=["created_at"])
df_22_plus_days = df_22_plus_days.drop(columns=["created_at"])
df = df.drop(columns=["created_at"])

# Save the dataframes to CSV files
df_first_7_days.to_csv("data/edges_first_7_days.csv", index=False)
df_8_21_days.to_csv("data/edges_8_21_days.csv", index=False)
df_22_plus_days.to_csv("data/edges_22_plus_days.csv", index=False)

# Save the dataframe to a CSV file
df.to_csv("data/edges.csv", index=False)
