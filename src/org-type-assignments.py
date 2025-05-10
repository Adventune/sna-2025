"""
Helper script for assigning more specific org types to the orgs in the dataset.
"""

import json
import os
import requests

current_orgs = {}
with open("data/filtered_organisations_with_types.json", "r") as f:
    current_orgs = json.load(f)

org_metadata = {}
with open("cache/organisations.json", "r") as f:
    org_metadata = json.load(f)

# Filter only orgs with type['id'] == 272 (IO) or 274 (NGO)

filtered_orgs = {k: v for k, v in current_orgs.items() if v["type"]["id"] in [272, 274]}

print(f"Filtered orgs: {len(filtered_orgs)}")

specified_types = [
    {"id": 1, "name": "Emergency Response"},
    {"id": 2, "name": "Medical"},
    {"id": 3, "name": "Food and Shelter"},
    {"id": 4, "name": "Reconstruction"},
    {"id": 5, "name": "Child-focused"},
    {"id": 6, "name": "Faith-based"},
    {"id": 7, "name": "Logistics"},
    {"id": 8, "name": "Advocacy and Policy"},
    {"id": 9, "name": "UN Agencies"},
    {"id": 10, "name": "Multilateral Financial Institutions"},
    {"id": 11, "name": "Regional Organizations"},
    {"id": 12, "name": "Specialized Technical Bodies"},
    {"id": 13, "name": "Peacekeeping/Protection Bodies"},
    {"id": 14, "name": "Humanitarian aid"},
    {"id": 15, "name": "Information and Communication"},
    {"id": 16, "name": "Media"},
    {"id": 17, "name": "Research and Development"},
    {"id": 18, "name": "Donor & financial"},
    {"id": 19, "name": "Other"},
]

reassigned_orgs = {}
if os.path.exists("data/reassigned_organisations_with_types.json"):
    with open("data/reassigned_organisations_with_types.json", "r") as f:
        reassigned_orgs = json.load(f)


i = 0
for org_id, org in filtered_orgs.items():
    if org_id in reassigned_orgs:
        continue
    os.system("clear")
    print(f"{len(reassigned_orgs)}/{len(filtered_orgs)}")
    org_url = f"https://api.reliefweb.int/v1/sources/{org_id}?appname=rwint-user-0"
    response = requests.get(org_url)
    if response.status_code != 200:
        print(f"Error getting organisation {org_id}: {response.status_code}")
        continue
    org_json = response.json()
    # Get the description
    description = org_json["data"][0]["fields"].get("description", "")

    print(f"Organisation: {org['name']}, \n\n Description: {description}\n")
    # Print options
    print("Options:")
    for i, org_type in enumerate(specified_types):
        print(f"{i + 1}: {org_type['name']}")
    print("0: Skip")
    # Get user input
    selected_type = input("Select type: ")
    # If 0, skip
    if selected_type == "0":
        continue
    # If not 0, assign the type
    selected_type = int(selected_type) - 1
    if selected_type < 0 or selected_type >= len(specified_types):
        print("Invalid selection, skipping...")
        continue
    # Assign the type
    selected_type = specified_types[selected_type]
    reassigned_orgs[org_id] = {
        "name": org["name"],
        "type": {
            "id": selected_type["id"],
            "name": selected_type["name"],
        },
    }
    # Save to json
    with open("data/reassigned_organisations_with_types.json", "w") as f:
        json.dump(reassigned_orgs, f, indent=4)
