
import requests
import time
import requests
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Access the secret key
secret_key = os.getenv("SECRET_KEY")
portal_id = os.getenv("PORTAL_ID")
form_guid = os.getenv("FORM_GUID")
url = f"https://api.hsforms.com/submissions/v3/integration/secure/submit/{portal_id}/{form_guid}"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {secret_key}"
}
payload = {
    "submittedAt": str(int(time.time() * 1000)),
    "fields": [
   
        {
            #required field
            "name": "firstname",
            "value": "Danny"
        },
        {
            #required field
            "name": "lastname",
            "value": "Haycraft"
        },
        {
            #required field
            "name": "email",
            "value": "dhcopy1@gmail.com"
        },
        {
            #required field
            "name": "phone",
            "value": "4803385396"
        },
        {
            #required field
            "name": "property_state",
            "value": "Califni"
        },
        {
            "name": "additional_notes",
            "value": "Full address goes here"
        },
    ],
    "context": {
        "pageUri": "https://3xz5u.share.hsforms.com/2ATPVMkeHSSqm_IquqiAdwA",
        "pageName": "Investor lift"
    }
}



response = requests.post(url, json=payload, headers=headers)

print(response.json())
print(response.status_code)




