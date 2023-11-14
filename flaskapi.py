from modelo import recomendador
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, request
from datetime import datetime
import json, csv

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

with open('materias.json', 'r') as json_file:
    materias = json.load(json_file)
for materia in materias:
    materia['score'] = 0

scoreTotal = 0

def materiaPorID(id):
    for materia in materias:
        if materia['id'] == id:
            return materia
    return None

def materiasPorIDs(ids):
    results = [materiaPorID(id) for id in ids]
    return results

@app.route('/api/materias/buscar', methods=['GET'])
def buscar():
    busqueda = request.args.get('q', '').lower()
    results = [materia for materia in materias if busqueda in materia['nombre'].lower()]
    return results

@app.route('/api/materias/recomendar', methods=['POST'])
def recomendar():
    data = request.get_json()
    recs = recomendador(data['materias'])
    return materiasPorIDs(recs[:min(10, len(recs))])

@app.route('/api/log', methods=['POST'])
def logger():
    global scoreTotal
    try:
        data = json.loads(request.data)
        for materia in data:
            materias[materia['id']]['score'] += 1
            scoreTotal += 1
        if scoreTotal >= 100:
            scoreTotal = 0
        
        data.insert(0, datetime.now())
        with open('analytics.csv', 'a') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(data)
        return '200'

    except:
        return '500'

if __name__ == '__main__':
    app.run(debug=True, port = 8000)
