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
    "https://api.reliefweb.int/v1/sources?appname=" + app_name + "&limit=1",
    json=payload,
    timeout=30,
)

response_json = response.json()
print(json.dumps(response_json, indent=4))
href = response_json["data"][0]["href"]

response = requests.get(href, timeout=30)
response_json = response.json()
print(json.dumps(response_json, indent=4))
