from multiprocessing.dummy import Array
from fastapi.encoders import jsonable_encoder
from typing import Any, List
from datetime import date, datetime
from uuid import uuid4

import dotenv
from pydantic import BaseModel, Field
from pymongo import MongoClient


class User(BaseModel):
    name: str = Field(...)
    email: str = Field(...)
    initials: str = Field(...)
    id: str = Field(alias="_id", default=None)
    number: int = Field(default=0)
    createdDate: datetime = Field(default=datetime.now())

class CareersUserManager(object):

    def __init__(self):
        self.config = dotenv.dotenv_values(".env")
        self.mongo_client = MongoClient(self.config["DB_URL"])
        self.database = self.mongo_client["careers"]
        self.database["users"].create_index('name')
        self.collection = self.database["users"]

    def createUser(self, user: User) -> User:
        user.id = uuid4()
        self.collection.insert_one(jsonable_encoder(user))

        return user
    
    def getUserByUserId(self, userId: str) -> User:
        return self.collection.find_one({"_id": userId})
    
    def deleteUser(self, userId: str):
        self.collection.delete_one({"_id": userId})

    def updateUser(self, user: User):
        self.collection.update_one({"_id": user['_id']}, {"$set": {'number': user["number"]}})