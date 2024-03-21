from flask import Flask, abort, request, jsonify
import elasticsearch as ES
import logging

from validate import validate_args

logger = logging.getLogger(__name__)
logging.basicConfig(
    encoding='utf-8', stream=sys.stdout,
    format="{'timestamp': '%(asctime)s', 'severity': '%(levelname)s', 'application': 'flask_app', 'logger': '%(name)s', 'service': 'container', 'where':'File \"%(pathname)s\", line %(lineno)d', 'message':'%(message)s'}",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.DEBUG
)

ELASTIC_HOST = '192.168.11.128'
ELASTIC_PORT = 9200

app = Flask(__name__)
es_client = ES.Elasticsearch([{'host': ELASTIC_HOST, 'port': ELASTIC_PORT}], )

@app.route('/')
def index():
    return 'worked'

@app.route('/api/movies/')
def movie_list():
    validate = validate_args(request.args)

    if not validate['success']:
        return abort(422)

    defaults = {
        'limit': 50,
        'page': 1,
        'sort': 'id',
        'sort_order': 'asc'
    }

    # Тут уже валидно все
    for param in request.args.keys():
        defaults[param] = request.args.get(param)

    # Уходит в тело запроса. Если запрос не пустой - мультисерч, если пустой - выдает все фильмы
    body = {
        "query": {
            "multi_match": {
                "query": defaults['search'],
                "fields": ["title"]
            }
        }
    } if defaults.get('search', False) else {}

    body['_source'] = dict()
    body['_source']['include'] = ['id', 'title', 'imdb_rating']

    params = {
        # '_source': ['id', 'title', 'imdb_rating'],
        'from': int(defaults['limit']) * (int(defaults['page']) - 1),
        'size': defaults['limit'],
        'sort': [
            {
                defaults["sort"]: defaults["sort_order"]
            }
        ]
    }

    global es_client
    search_res = es_client.search(
        body=body,
        index='movies',
        params=params,
        filter_path=['hits.hits._source']
    )
    es_client.close()

    return jsonify([doc['_source'] for doc in search_res['hits']['hits']])


@app.route('/api/movies/<string:movie_id>')
def get_movie(movie_id):
    global es_client 
    if not es_client.ping():
        print('oh(')

    search_result = es_client.get(index='movies', id=movie_id, ignore=404)

    es_client.close()

    if search_result['found']:
        return jsonify(search_result['_source'])

    return abort(404)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
