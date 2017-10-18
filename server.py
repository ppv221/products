import os
import csv
import logging
from flask import Flask, Response, jsonify, request, json, url_for, make_response
from models import Product, DataValidationError
import mock

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Create Flask application
app = Flask(__name__)

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    return jsonify(status=400, error='Bad Request', message=error.message), 400

# @app.errorhandler(404)
# def not_found(error):
#     """ Handles Products that cannot be found """
#     return jsonify(status=404, error='Not Found', message=error.message), 404
#
# @app.errorhandler(405)
# def method_not_supported(error):
#     """ Handles bad method calls """
#     return jsonify(status=405, error='Method not Allowed',
#                    message='Your request method is not supported.' \
#                    ' Check your HTTP method and try again.'), 405

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles catostrophic errors """
    return jsonify(status=500, error='Internal Server Error', message=error.message), 500

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Return something useful by default """
    return jsonify(name='Product Demo REST API Service',
                   version='1.0',
                   url=url_for('list_product', _external=True)), HTTP_200_OK

######################################################################
# LIST ALL products
######################################################################
@app.route('/Products', methods=['GET'])
def list_product():
    """ Retrieves a list of products from the database """
    results = []
    category = request.args.get('category')
    #print category
    name = request.args.get('name')
    if category:
        results = Product.find_by_category(category)
    elif name:
        results = Product.find_by_name(name)
    else:
        results = Product.all()

    return jsonify([p.serialize() for p in results]), HTTP_200_OK

######################################################################
# LIST AVAILABLE Products
######################################################################
@app.route('/Products/available', methods=['GET'])
def list_available_products():
    """ Retrieves a list of available products from the database """
    results = []
    results = Product.available()
    return jsonify([p.serialize() for p in results]), HTTP_200_OK

######################################################################
# RETRIEVE A PRODUCT
######################################################################
@app.route('/Products/<int:id>', methods=['GET'])
def get_products(id):
    """ Retrieves a Product with a specific id """
    product = Product.find(id)
    if product:
        message = product.serialize()
        return_code = HTTP_200_OK
        if product.count == 0:
            message['Understocked'] = 'Product out of Stock'
    else:
        message = {'error' : 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route('/Products', methods=['POST'])
def create_product():
    """ Creates a Product in the datbase from the posted database """
    payload = request.get_json(force=True)
    product = Product()
    #print payload
    product.deserialize(payload)
    #print (product.id,product.name)
    product.save()
    message = product.serialize()
    response = make_response(jsonify(message), HTTP_201_CREATED)
    response.headers['Location'] = url_for('get_products', id=product.id, _external=True)
    return response

######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################
@app.route('/Products/<int:id>', methods=['PUT'])
def update_products(id):
    """ Updates a Products in the database fom the posted database """
    product = Product.find(id)
    if product:
        payload = request.get_json()
        product.deserialize(payload)
        product.save()
        message = product.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error' : 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

@app.route('/Products/add_unit/<int:id>', methods=['PUT'])
def add_product_unit(id):
    """ Updates a Product in the database fom the posted database """
    product = Product.find(id)
    if product:
        product.count = int(product.count) + 1
        message = product.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error' : 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

@app.route('/Products/sell_products/<int:id>', methods=['PUT'])
def sell_products(id):
    """ Updates a Product in the database fom the posted database """
    product = Product.find(id)
    if product:
        if product.count == 0:
            message = {'error' : 'Product with id: %s is out of Stock' % str(id)}
        else:
            product.count = int(product.count) - 1
            message = product.serialize()

        return_code = HTTP_200_OK
    else:
        message = {'error' : 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return jsonify(message), return_code

######################################################################
# DELETE A Product
######################################################################
@app.route('/Products/<int:id>', methods=['DELETE'])
def delete_product(id):
    """ Removes a Product from the database that matches the id """
    product = Product.find(id)
    if product:
        product.delete()
    return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# GET PRODUCT DATA
######################################################################
def get_product_data():

    with open("sample_products.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Product(0, row['Name'], row['Category'], row['Price'], row['Description'], row['Color'], int(row['Count'])).save()

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    # dummy data for testing
    # Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf').save()
    # Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
    get_product_data()
    app.run(host='0.0.0.0',debug=False)
    #port = int(os.environ.get('PORT', 5000))
    #socketio.run(app, host='0.0.0.0', port=port)
