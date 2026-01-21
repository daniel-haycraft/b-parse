import requests
import json
def main(event):
  url = "https://staging.capitalfund1.com/api/integrations/hubspot/create-caps-entities"
  firstName = event["inputFields"]["firstName"]
  lastName = event["inputFields"]["lastName"]
  email = event["inputFields"]["email"]
  phoneNumber = event["inputFields"]["phoneNumber"]
  mailingAddress = event["inputFields"]["mailingAddress"]
  mailingCity = event["inputFields"]["mailingCity"]
  mailingState = event["inputFields"]["mailingState"]
  mailingZip = event["inputFields"]["mailingZip"]
  customerType = event["inputFields"]["customerType"]
  originalSource = event["inputFields"]["originalSource"]
  loanType = event["inputFields"]["loanType"]
  transactionType = event["inputFields"]["transactionType"]
  purchaseType = event["inputFields"]["purchaseType"]
  propertyType = event["inputFields"]["propertyType"]
  dwellingType = event["inputFields"]["dwellingType"]
  exitStrategy = event["inputFields"]["exitStrategy"]
  targetCloseDate = event["inputFields"]["targetCloseDate"]
  createDate = event["inputFields"]["createDate"]
  dealOwner = event["inputFields"]["dealOwner"]
  dealOwnerEmail = event["inputFields"]["dealOwnerEmail"]
  propertyAddress = event["inputFields"]["propertyAddress"]
  propertyCity = event["inputFields"]["propertyCity"]
  propertyState = event["inputFields"]["propertyState"]
  propertyZipCode = event["inputFields"]["propertyZipCode"]
  propertyCounty = event["inputFields"]["propertyCounty"]
  preRehabSQFT = event["inputFields"]["preRehabSQFT"]
  postRehabSQFT = event["inputFields"]["postRehabSQFT"]
  loanRequestAmount = event["inputFields"]["loanRequestAmount"]
  existingLoanAmount = event["inputFields"]["existingLoanAmount"]
  purchasePrice = event["inputFields"]["purchasePrice"]
  rehabBudget = event["inputFields"]["rehabBudget"]
  costOfImprovementsToDate = event["inputFields"]["costOfImprovementsToDate"]
  borrowerARV = event["inputFields"]["borrowerARV"]


  
  payload = {
    "contacts": [
      {
        "firstName": firstName,
        "lastName": lastName,
        "email": email,
        "phoneNumber": phoneNumber,
        "mailingAddress": mailingAddress,
        "mailingCity": mailingCity,
        "mailingState": mailingState,
        "mailingZip": mailingZip,
        "customerType": customerType,
        "originalSource": originalSource
      }
    ],
    "dealProperty": {
      "loanType": loanType,
      "transactionType": transactionType,
      "purchaseType": purchaseType,
      "propertyType": propertyType,
      "dwellingType": dwellingType,
      "exitStrategy": exitStrategy,
      "targetCloseDate": targetCloseDate,
      "createDate": createDate,
      "dealOwner": dealOwner,
      "dealOwnerEmail": dealOwnerEmail,
      "propertyAddress": propertyAddress,
      "propertyCity": propertyCity,
      "propertyState": propertyState,
      "propertyZipCode": propertyZipCode,
      "propertyCounty": propertyCounty,
      "preRehabSQFT": preRehabSQFT,
      "postRehabSQFT": postRehabSQFT,
      "loanRequestAmount": loanRequestAmount,
      "existingLoanAmount": existingLoanAmount,
      "purchasePrice": purchasePrice,
      "rehabBudget": rehabBudget,
      "costOfImprovementsToDate": costOfImprovementsToDate,
      "borrowerARV": borrowerARV
    }


  headers = {
    "Content-Type": "application/json"
    response = requests.post(
    url,
    headers=headers,
    json=payload
  )

  print(response.json())