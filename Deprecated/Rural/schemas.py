from typing import TypedDict
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from bson import ObjectId
from db import client

db = client["my_database"]
zip_codes = db["zip_codes"]

class Zipcode:
    def __init__(self, _id: int, State: str, ZipType: str, POName: str, PrimR: int, SecondR: float):
        self._id = _id
        self.State = State
        self.ZipType = ZipType
        self.POName=POName
        self.PrimR=PrimR
        self.SecondR=SecondR

    @classmethod
    def create(cls, zipp: int, State: str, ZipType: str, POName: str, PrimR: int, SecondR: float):
        zip_doc: ZipcodeDict = {
            "Zip": zipp,  # match the index name
            "State": State,
            "ZipType": ZipType,
            "POName": POName,
            "PrimR": PrimR,
            "SecondR": SecondR
        }
        zip_code_id = zip_codes.insert_one(zip_doc).inserted_id
         
        @classmethod
        def search(cls, zipp: int):
            return zip_codes.find_one({zipp: int})
        

