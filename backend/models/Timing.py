from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['posture-db']
timings_collection = db['timings']

class Timing:
    @staticmethod
    def create(data):
        return timings_collection.insert_one(data)
    
    @staticmethod
    def update_last(data):
        return timings_collection.find_one_and_update({}, {'$set': data}, sort=[('_id', -1)])
