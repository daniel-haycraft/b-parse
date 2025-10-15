
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://dhcopy1:TvPYheHq1zKWa3ax@rural.iwmki4d.mongodb.net/?retryWrites=true&w=majority&appName=Rural"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

if __name__ == "__main__":
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")

    except Exception as e:
        print(e)
        app.run(host="localhost", port =3001)