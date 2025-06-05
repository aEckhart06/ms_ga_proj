from pymongo import MongoClient

# Connect to local MongoDB on default port 27017
client = MongoClient('mongodb+srv://aeckhart06:Andrew06@cluster0.ad6vd.mongodb.net/')

# Access a database
db = client['ms_ga_contestants']

# Access a collection
collection = db['contestants']
print(collection.delete_many({}))  # Clear the collection

# Convert cursor to list and print each document

"""
results = list(collection.find({}, sort=[("amount_raised", -1)]))
for i in range(10):
    print(results[i], "\n")

"""