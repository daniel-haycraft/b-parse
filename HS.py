import requests

PRIVATE_APP_TOKEN = "pat-na1-ff737c80-8682-455c-a55e-aba7fb175741"
OWNER_ID = "39964875"   # <- the user ID you want to look up

url = f"https://api.hubapi.com/crm/v3/owners/{OWNER_ID}"

headers = {
    "Authorization": f"Bearer {PRIVATE_APP_TOKEN}",
    "Content-Type": "application/json"
}

r = requests.get(url, headers=headers)

data = r.json()

print(data)
print("Email:", data.get("email"))
