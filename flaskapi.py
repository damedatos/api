from modelo import recomendador

from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request

from pymongo import MongoClient
from bson.regex import Regex

from datetime import datetime
import json, csv

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
client = MongoClient('localhost', 27017)
col_materias = client.damedatos.materias
col_score = client.damedatos.score
col_analytics = client.damedatos.analytics

with open('autorizados.json', 'r') as json_file:
    autorizados = json.load(json_file)

scoreMax = 1000

def resetScore(k):
    col_materias.update_many({}, {'$set': {'score': 0}})
    suma = col_materias.aggregate([{'$group': {'_id': None, 'suma': {'$sum': '$score'}}}])
    suma = suma.next()['suma']
    col_score.update_one({'_id': 'scoreTotal'}, {'$set': {'score': suma}})

def materiasPorIDs(ids):
    return list(col_materias.find({'_id': {'$in': ids}}))

@app.route('/api/materias/buscar', methods=['GET'])
def buscar():
    busqueda = request.args.get('q', '').lower()
    pattern = f".*{busqueda}.*"
    results = list(col_materias.find({'nombre': {'$regex': Regex(pattern, 'i')}}))
    return results

@app.route('/api/materias/recomendar', methods=['POST'])
def recomendar():
    data = request.get_json()
    recs = recomendador(data['materias'])
    if data['auth'] in autorizados:
        return materiasPorIDs(recs[:min(10, len(recs))])
    return []

@app.route('/api/log', methods=['POST'])
def logger():
    try:
        data = json.loads(request.data)
        for materia in data['materias']:
            col_materias.update_one({'_id': materia['_id']}, {'$inc': {'score': 1}})
            col_score.update_one({'_id': 'scoreTotal'}, {'$inc': {'score': 1}})
        print(col_score.find_one({'_id': 'scoreTotal'})['score'])
        if col_score.find_one({'_id': 'scoreTotal'})['score'] > scoreMax:
            resetScore(25)
        
        data['tiempo'] = datetime.now()
        col_analytics.insert_one(data)
        return '200'

    except:
        return '500'

if __name__ == '__main__':
    app.run(debug=True, port = 8000)
