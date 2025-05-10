import json
import pandas as pd

# load the json file
data = None
with open("data/organisations_with_types.json", "r") as f:
    data = json.load(f)

# load edge data
edge_data = pd.read_csv("data/edges.csv")

# Get all unique org ids "source"

org_ids = edge_data["source"].unique().tolist()
# As string
org_ids = [str(org_id) for org_id in org_ids]

# From data, filter any keys that are not in org_ids
filtered_data = {}
for key in data:
    if key in org_ids:
        filtered_data[key] = data[key]

print(len(filtered_data), len(data), len(org_ids))
# Save the filtered data to a new json file
with open("data/filtered_organisations_with_types.json", "w") as f:
    json.dump(filtered_data, f, indent=4)


with open("cache/articles.json", "r") as f:
    articles = json.load(f)
    print(len(articles))
