import requests
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Access the secret key
secret_key = os.getenv("SECRET_KEY")

PRIVATE_APP_TOKEN = secret_key
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
