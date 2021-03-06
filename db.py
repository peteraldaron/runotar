import os, pymongo
from pymongo import MongoClient

class DataBase:
    def __init__(self):
        #definitions:
        self.dbName = 'runotar';
        self.port = 27017;
        self.host = 'localhost';
        #set up:
        self.db = self.getDataBase();

    def getDataBase(self):
        client = MongoClient(self.host, self.port);
        return client[self.dbName];

    def getCollection(self, collectionName):
        if self.db == None:
            self.db = self.getDataBase();
        return self.db[collectionName];

    def insertOneToCollection(self, document, collectionName, collection=None):
        if collection == None:
            collection = self.getCollection(collectionName);
        return collection.insert_one(document);

    def upsertOneToCollection(self, document, query, collectionName, collection=None):
        if collection == None:
            collection = self.getCollection(collectionName);
        return collection.find_and_modify(query, update=document, upsert=True)

    def getAllVisitedTitles(self, collectionName, collection=None):
        if collection == None:
            collection = self.getCollection(collectionName);
        #TODO: consider using mongo's aggregation calls
        return map(lambda x: x["title"], collection.find({}, {"title": 1, "_id": 0}))

    def insertManyIntoCollection(self, documents, collectionName, collection=None):
        if collection == None:
            collection = self.getCollection(collectionName);
        return collection.insert_many(documents)
