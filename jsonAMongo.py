from pymongo import MongoClient
import json

client = MongoClient('localhost', 27017)
db = client.damedatos
collection = db.materias

with open('materias.json', 'r') as json_file:
    materias = json.load(json_file)
for materia in materias:
    materia['score'] = 0
collection.insert_many(materias)

collection.create_index({"nombre": "text"})
db.score.insert_one({'_id': 'scoreTotal', 'score': 0})

client.close()