import csv
import os
from threading import Lock
from flask import Flask, Response, jsonify, request, json

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

# Lock for thread-safe counter increment
lock = Lock()

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    # return "Reached Here"
    products_url = request.base_url + "products"
    return jsonify(name='product Demo REST API Service',
                   version='1.0',
                   url=products_url
                   ), HTTP_200_OK

######################################################################
# LIST ALL products
######################################################################
@app.route('/products', methods=['GET'])
def list_products():

    results = products.values()
    category = request.args.get('category')
    if category:
        results = []
        for key, value in products.iteritems():
            if value['category'] == category:
                results.append(products[key])

    # print(results)

    return reply(list(results), HTTP_200_OK)

######################################################################
# RETRIEVE A product
######################################################################
@app.route('/products/<int:id>', methods=['GET'])
def get_products(id):

    if id in products:
        message = products[id]
        rc = HTTP_200_OK
    else:
        message = { 'error' : 'product with id: %s was not found' % str(id) }
        rc = HTTP_404_NOT_FOUND

    return reply(message, rc)


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def reply(message, rc):

    response = Response(json.dumps(message))
    response.headers['Content-Type'] = 'application/json'
    response.status_code = rc
    return response

def is_valid(data):
    valid = False
    try:
        name = data['name']
        category = data['category']
        valid = True
    except KeyError as err:
        app.logger.error('Missing parameter error: %s', err)
    return valid

PRODUCTS_DATA_SOURCE_FILE = 'sample_products.csv'

def get_product_data():
    prod_data = {}
    with open(PRODUCTS_DATA_SOURCE_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            prod_data[int(row['id'])] = { 'id':int(row['id']), 'name':row['name'], 'category':row['category']   }
    return prod_data

######################################################################
#   M A I N
######################################################################
products = {}
if __name__ == "__main__":
    products = get_product_data();
    print(products)
    # Pull options from environment
    debug = (os.getenv('DEBUG', 'False') == 'True')
    port = os.getenv('PORT', '5000')
    app.run(debug=debug)
    # app.run()