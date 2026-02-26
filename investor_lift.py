
import requests
import time
PRIVATE_APP_TOKEN = "pat-na1-6f6fe850-0217-4155-833c-ee421f749fff"

portal_id = "6624066"
form_guid ="ab791219-4b31-4711-ac54-18b876f55b4b"

url = f"https://api.hsforms.com/submissions/v3/integration/secure/submit/{portal_id}/{form_guid}"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {PRIVATE_APP_TOKEN}"
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




