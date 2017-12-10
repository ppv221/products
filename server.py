"""
Product Store Service with Swagger
Paths:
------
GET / - Displays a UI for Selenium testing
GET /products - Returns a list all of the Products
GET /products/{id} - Returns the Product with a given id number
POST /products - creates a new Product record in the database
PUT /products/{id} - updates a Product record in the database
DELETE /products/{id} - deletes a Product record in the database
"""


import os
import csv
import logging
from flask import Flask, Response, jsonify
from flask import request, json, url_for, make_response, abort
from models import Product, DataValidationError, DatabaseConnectionError, \
    BadRequestError, NotFoundError
from flask_api import status
from flask_restplus import Api, Resource, fields
import sys
from werkzeug.exceptions import NotFound


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
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Product Catalog REST API Service',
          description='This is a sample server Product store server.',
          doc='/apidocs/'
          )

# This namespace is the start of the path i.e., /products
ns = api.namespace('products', description='Product operations')

# Define the model so that the docs reflect what can be sent
product_model = api.model('Product', {

    'name': fields.String(required=True,
                          description='The name of the Product'),
    'category': fields.String(required=True,
                              description='The category of Product'),
    'price': fields.String(required=True,
                           description='The price of Product'),
    'description': fields.String(required=True,
                                 description='The description of Product'),
    'color': fields.String(required=True,
                           description='The color of Product'),
    'count': fields.Integer(readOnly=True,
                            description='The total count of Product')
})

######################################################################
# Special Error Handlers
######################################################################


@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)


@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status': 500, 'error': 'Server Error', 'message': message}, 500


@api.errorhandler(BadRequestError)
def database_connection_error(error):
    """ Handles requests that have bad or malformed data """
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status': 400, 'error': 'Bad Request', 'message': message}, 400


@api.errorhandler(NotFoundError)
def database_connection_error(error):
    """ Handles Products that cannot be found """
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status': 404, 'error': 'Not Found', 'message': message}, 404


# @api.errorhandler(400)
# def bad_request(error):
#     """ Handles requests that have bad or malformed data """
#     return jsonify(status=400, error='Bad Request', message=error.message), 400
#
#
# @api.errorhandler(404)
# def not_found(error):
#     """ Handles Products that cannot be found """
#     return jsonify(status=404, error='Not Found', message=error.message), 404
#
# #@app.errorhandler(405)
# # def method_not_supported(error):
# #    """ Handles bad method calls """
# # return jsonify(status=405, error='Method not Allowed', message='Your
# # request method is not supported. Check your HTTP method and try
# # again.'), 405
#
#
# @api.errorhandler(500)
# def internal_server_error(error):
#     """ Handles catostrophic errors """
#     return jsonify(status=500,
#                    error='Internal Server Error', message=error.message), 500

######################################################################
# GET HEALTH CHECK
######################################################################


@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200,
                                 message='Healthy'), status.HTTP_200_OK)

######################################################################
# GET INDEX
######################################################################


# @app.route('/')
# def index():
#     """ Return something useful by default
#     return jsonify(name='Product Demo REST API Service',
#                    version='1.0',
#                    url=url_for('list_product', _external=True)), HTTP_200_OK"""
#     return app.send_static_file('index.html')


######################################################################
#  PATH: /products/{id}
######################################################################
@ns.route('/<int:products_id>')
@ns.param('products_id', 'The Product identifier')
class ProductResource(Resource):
    """
    ProductResource class
    Allows the manipulation of a single Product
    GET /products{id} - Returns a Product with the id
    PUT /products{id} - Update a Product with the id
    DELETE /products{id} -  Deletes a Product with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    #------------------------------------------------------------------
    @ns.doc('get_products`')
    @ns.response(404, 'Product not found')
    @ns.marshal_with(product_model)
    #@app.route('/products/<int:id>', methods=['GET'])
    def get(self, products_id):
        """
        Retrieve a single Product
        This endpoint will return a Product based on it's id
        """
        app.logger.info(
            "Request to Retrieve a product with id [%s]", products_id)
        product = Product.find(products_id)
        if product:
            message = product.serialize()
            return_code = HTTP_200_OK
            return product.serialize(), status.HTTP_200_OK
            if product.count == 0:
                #message['Understocked'] = 'Product out of Stock'
                raise NotFound("Product is Understocked.")

        else:
            raise NotFound(
                "Product with id '{}' was not found.".format(products_id))
            #message = {'error': 'Product with id: %s was not found' % str(products_id)}
            #return_code = HTTP_404_NOT_FOUND

        # return product.serialize(), status.HTTP_200_OK
        # #make_response(jsonify(message), return_code)

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    #------------------------------------------------------------------
    @ns.doc('update_products')
    @ns.response(404, 'Product not found')
    @ns.response(400, 'The posted Product data was not valid')
    @ns.expect(product_model)
    @ns.marshal_with(product_model)
    def put(self, products_id):
        """
        Update a Product
        This endpoint will update a Product based the body that is posted
        """
        app.logger.info(
            'Request to Update a product with id [%s]', products_id)
        check_content_type('application/json')
        product = Product.find(products_id)
        if not product:
            #api.abort(404, "Pet with id '{}' was not found.".format(pet_id))
            raise NotFound(
                'Product with id [{}] was not found.'.format(products_id))
        #data = request.get_json()
        data = api.payload
        app.logger.info(data)
        product.deserialize(data)
        product.id = products_id
        product.save()
        return product.serialize(), status.HTTP_200_OK
        # app.logger.info('Request to Update a product with id [%s]', products_id)
        # product = Product.find(products_id)
        # if product:
        #     payload = request.get_json()
        #     product.deserialize(payload)
        #     product.save()
        #     message = product.serialize()
        #     return_code = HTTP_200_OK
        #     return product.serialize(), status.HTTP_200_OK#make_response(jsonify(message), return_code)
        # else:
        #     raise NotFound("Product with id '{}' was not found.".format(products_id))
        #     #message = {'error': 'Product with id: %s was not found' % str(products_id)}
        #     #return_code = HTTP_404_NOT_FOUND

        # return product.serialize(),
        # status.HTTP_200_OK#make_response(jsonify(message), return_code)

     #------------------------------------------------------------------
    # DELETE A PRODUCT
    #------------------------------------------------------------------
    @ns.doc('delete_products')
    @ns.response(204, 'Product deleted')
    def delete(self, products_id):
        """
        Delete a Product
        This endpoint will delete a Product based the id specified in the path
        """
        app.logger.info(
            'Request to Delete a product with id [%s]', products_id)
        product = Product.find(products_id)
        if product:
            product.delete()
        return '', HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products
######################################################################
@ns.route('/', strict_slashes=False)
class ProductCollection(Resource):
    """ Handles all interactions with collections of Products """
    #------------------------------------------------------------------
    # LIST ALL PRODUCTS
    #------------------------------------------------------------------
    @ns.doc('list_products')
    @ns.param('category', 'List Product by category')
    @ns.marshal_list_with(product_model)
    def get(self):
        """ Returns all of the Products """
        app.logger.info('Request to list Products...')
        results = []
        category = request.args.get('category')
        #print (category)
        name = request.args.get('name')
        if category:
            # print("Category is " + category)
            results = Product.find_by_category(str(category).lower())
        elif name:
            results = Product.find_by_name(str(name).lower())
        else:
            results = Product.all()
        app.logger.info('[%s] Products returned', len(results))
        # return make_response(jsonify([p.serialize() for p in results]),
        #                     HTTP_200_OK)
        resultsUpd = [prod.serialize() for prod in results]
        return resultsUpd, status.HTTP_200_OK

#------------------------------------------------------------------
    # ADD A NEW PRODUCT
#------------------------------------------------------------------
    @ns.doc('create_products')
    @ns.expect(product_model)
    @ns.response(400, 'The posted data was not valid')
    @ns.response(201, 'Product created successfully')
    @ns.marshal_with(product_model, code=201)
    def post(self):
        """
        Creates a Product
        This endpoint will create a Product based the data in the body that is posted
        """

        app.logger.info('Request to Create a Product')
        check_content_type('application/json')
        prod = Product()
        app.logger.info('Payload = %s', api.payload)
        prod.deserialize(api.payload)
        prod.save()
        app.logger.info('Product with new id [%s] saved!', prod.id)
        location_url = api.url_for(
            ProductResource, products_id=prod.id, _external=True)
        return prod.serialize(), status.HTTP_201_CREATED, \
            {'Location': location_url}

        # app.logger.info('Request to Create a Product')
        # data = {}
        # # Check for form submission data
        # if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        #
        #     #app.logger.info('Getting data from form submit')
        #     data = {
        #         'name': request.form['name'],
        #         'category': request.form['category'],
        #         "color": request.form['color'],
        #         "count": request.form['count'],
        #         "price": request.form['price'],
        #         "description": request.form['description']
        #         }
        # else:
        #     #app.logger.info('Getting data from API call')
        #     """ Creates a Product in the datbase from the posted database """
        #     payload = request.get_json(force=True)
        #     product = Product()
        #     # print payload
        #     product.deserialize(payload)
        #     #print (product.id,product.name)
        #     product.save()
        #     message = product.serialize()
        #     #response = make_response(jsonify(message), HTTP_201_CREATED)
        #     #response.headers['Location'] = url_for(
        #     #    'get_products', products_id=product.id, _external=True)
        #     app.logger.info('Product with new id [%s] saved!', product.id)
        #     location_url = api.url_for(ProductResource, products_id=product.id, _external=True)
        #
        #     return message, status.HTTP_201_CREATED, {'Location': location_url}
        # #return response

#=============================================================================

######################################################################
# LIST ALL products
######################################################################


# @app.route('/products', methods=['GET'])
# def list_product():
#     """ Retrieves a list of products from the database """
#     results = []
#     category = request.args.get('category')
#     #print (category)
#     name = request.args.get('name')
#     if category:
#         # print("Category is " + category)
#         results = Product.find_by_category(str(category).lower())
#     elif name:
#         results = Product.find_by_name(str(name).lower())
#     else:
#         results = Product.all()
#
#     return make_response(jsonify([p.serialize() for p in results]),
#                          HTTP_200_OK)

######################################################################
# LIST AVAILABLE Products
######################################################################


@app.route('/products/available', methods=['GET'])
def list_available_products():
    """ Retrieves a list of available products from the database """
    results = []
    results = Product.available()
    return make_response(jsonify([p.serialize() for p in results]),
                         HTTP_200_OK)

######################################################################
# RETRIEVE A PRODUCT
######################################################################


# @app.route('/products/<int:id>', methods=['GET'])
# def get_products(id):
#     """ Retrieves a Product with a specific id """
#     product = Product.find(id)
#     if product:
#         message = product.serialize()
#         return_code = HTTP_200_OK
#         if product.count == 0:
#             message['Understocked'] = 'Product out of Stock'
#     else:
#         message = {'error': 'Product with id: %s was not found' % str(id)}
#         return_code = HTTP_404_NOT_FOUND
#
#     return make_response(jsonify(message), return_code)

######################################################################
# ADD A NEW PRODUCT
######################################################################


# @app.route('/products', methods=['POST'])
# def create_product():
#     data = {}
#     # Check for form submission data
#     if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
#
#         app.logger.info('Getting data from form submit')
#         data = {
#             'name': request.form['name'],
#             'category': request.form['category'],
#             "color": request.form['color'],
#             "count": request.form['count'],
#             "price": request.form['price'],
#             "description": request.form['description']
#         }
#     else:
#         app.logger.info('Getting data from API call')
#         """ Creates a Product in the datbase from the posted database """
#         payload = request.get_json(force=True)
#         product = Product()
#         # print payload
#         product.deserialize(payload)
#         #print (product.id,product.name)
#         product.save()
#         message = product.serialize()
#         response = make_response(jsonify(message), HTTP_201_CREATED)
#         response.headers['Location'] = url_for(
#             'get_products', id=product.id, _external=True)
#     return response

######################################################################
# UPDATE AN EXISTING PRODUCT
######################################################################


# @app.route('/products/<int:id>', methods=['PUT'])
# def update_products(id):
#     """ Updates a Products in the database fom the posted database """
#     product = Product.find(id)
#     if product:
#         payload = request.get_json()
#         product.deserialize(payload)
#         product.save()
#         message = product.serialize()
#         return_code = HTTP_200_OK
#     else:
#         message = {'error': 'Product with id: %s was not found' % str(id)}
#         return_code = HTTP_404_NOT_FOUND
#
#     return make_response(jsonify(message), return_code)


@app.route('/products/<int:id>/add_unit', methods=['PUT'])
def add_product_unit(id):
    """ Updates a Product in the database fom the posted database """
    product = Product.find(id)
    if product:
        product.count = int(product.count) + 1
        product.save()
        message = product.serialize()
        return_code = HTTP_200_OK
    else:
        message = {'error': 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return make_response(jsonify(message), return_code)


@app.route('/products/<int:id>/sell_products', methods=['PUT'])
def sell_products(id):
    """ Updates a Product in the database fom the posted database """
    product = Product.find(id)
    if product:
        if product.count == 0:
            message = {
                'error': 'Product with id: %s is out of Stock' % str(id)}
        else:
            product.count = int(product.count) - 1
            product.save()
            message = product.serialize()

        return_code = HTTP_200_OK
    else:
        message = {'error': 'Product with id: %s was not found' % str(id)}
        return_code = HTTP_404_NOT_FOUND

    return make_response(jsonify(message), return_code)

######################################################################
# DELETE A Product
######################################################################


# @app.route('/products/<int:id>', methods=['DELETE'])
# def delete_product(id):
#     """ Removes a Product from the database that matches the id """
#     product = Product.find(id)
#     if product:
#         product.delete()
#     return make_response('', HTTP_204_NO_CONTENT)

######################################################################
# DELETE ALL PRODUCT DATA (for testing only)
######################################################################


@app.route('/products/reset', methods=['DELETE'])
def products_reset():
    print("REACHED HERE")
    """ Removes all products from the database """
    Product.remove_all()
    print("LEAVING HERE")
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


# load sample data
def data_load(payload):
    """ Loads a Product into the database """
    Product(0, 'Asus2500', 'Laptop', '234',
            'Working Condition', 'Black', 23).save()
    Product(0, 'GE4509', 'Microwave', '45',
            'Open Box', 'Black', 12).save()
    Product(0, 'Hp', 'Microwave', '960', 'Brand New', 'Blue', 0).save()


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s',
                     request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
          'Content-Type must be {}'.format(content_type))


######################################################################
# GET PRODUCT DATA
######################################################################


@app.before_first_request
def init_db(redis=None):
    """ Initlaize the model """
    Product.init_db(redis)


def data_reset():
    """ Removes all Products from the database """
    Product.remove_all()


def get_product_data():

    # with open("sample_products.csv") as csvfile:
    #     reader = csv.DictReader(csvfile)
    #     for row in reader:
    #         Product(0, row['Name'], row['Category'], row['Price'], row[
    #                 'Description'], row['Color'], int(row['Count'])).save()
    init_db()
    data_reset()

    Product(0, 'Asus2500', 'Laptop', '234',
            'Working Condition', 'Black', 23).save()
    Product(0, 'GE4509', 'Microwave', '45',
            'Open Box', 'Black', 12).save()
    Product(0, 'Hp', 'Microwave', '960', 'Brand New', 'Blue', 0).save()


def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')


######################################################################
#   M A I N  F U N C T I O N
######################################################################
if __name__ == "__main__":
    # dummy data for testing
    # product = Product(0, 'Asus2500', 'Laptop', '299',
    #                   'In Great Condition', 'Black', 10)
    # product.save()
    # product2 = Product(0, 'GE4509', 'Microwave', '50', 'Working', 'Red', 20)
    # product2.save()
    get_product_data()

    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
    # get_product_data()
    #port = int(os.environ.get('PORT', 5000))
    #socketio.run(app, host='0.0.0.0', port=port)
