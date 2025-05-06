import requests
import json

app_name = "rwint-user-0"

payload = {
    "filter": {"field": "status", "value": "active"},
    "fields": ["shortname"],
    "preset": "latest",
    "profile": "list",
}
response = requests.get(
    "https://api.reliefweb.int/v1/sources?appname=" + app_name + "&limit=10",
    json=payload,
    timeout=30,
)

response_json = response.json()
print(json.dumps(response_json, indent=4))
data = response_json["data"]

for organisation in data:
    response = requests.get(organisation["href"], timeout=30)
    response_json = response.json()
    print(json.dumps(response_json["data"][0]["fields"]["type"], indent=4))
