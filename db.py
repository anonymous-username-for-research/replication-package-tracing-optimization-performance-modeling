import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['uftrace-data']

def get_previous_parameters(collection):
    items = db[collection].find()
    return [item['parameters'] for item in items]

def insert_to_db(collection, document):
    db[collection].insert_one(document)
    # pass