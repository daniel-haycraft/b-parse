import requests

r = requests.get(
    "https://webapp.forecasa.com/api/v1/transactions",
    params={
        "api_key": "IBFP-FDUlIyAnY_mJuzIjg",
        "q[property_address_cont]": "4747 Nome Street, Dallas, Texas 75216",
    }
)
print(r.status_code)
print(r.text[:500])
