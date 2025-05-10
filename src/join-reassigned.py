"""
Helper script to join reassigned orgs with the original orgs.
"""

import json

original_orgs = {}
reassigned_orgs = {}

with open("data/filtered_organisations_with_types.json", "r") as f:
    original_orgs = json.load(f)
with open("data/reassigned_organisations_with_types.json", "r") as f:
    reassigned_orgs = json.load(f)

for org_id, org in reassigned_orgs.items():
    original_orgs[org_id]["type"] = org["type"]

# Save the filtered data to a new json file
with open("data/organisations_with_types_reassigned.json", "w") as f:
    json.dump(original_orgs, f, indent=4)
