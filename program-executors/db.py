import pymongo

database_name = "uftrace-data"

client = pymongo.MongoClient("mongodb://localhost:27017/")
server_client = pymongo.MongoClient("YOUR_SERVER_MONGODB_URL")
db = client[database_name]

def get_previous_parameters(collection, condition = {}, server=True):
    if server:
        items = list(server_client[database_name][collection].find(condition))
    else:
        items = list(db[collection].find(condition))
    return list(items)

def insert_to_db(collection, document):
    db[collection].insert_one(document)
    pass