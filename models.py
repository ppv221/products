import os
import json
import logging
import pickle
from redis import Redis
from cerberus import Validator
from redis.exceptions import ConnectionError


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass


class Product(object):
    """
    Class that represents a Product
    This version uses an in-memory collection of products for testing
    """
    #lock = threading.Lock()
    #data = []
    #index = 0
    logger = logging.getLogger(__name__)
    redis = None
    schema = {
        'id': {'type': 'integer'},
        'name': {'type': 'string', 'required': True},
        'category': {'type': 'string', 'required': True},
        'price': {'type': 'integer', 'required': True},
        'description': {'type': 'string', 'required': True},
        'color': {'type': 'string', 'required': True},
        'count': {'type': 'integer', 'required': True}
        }
    __validator = Validator(schema)

    def __init__(self, id=0, name='', category='',
                 price='', description='', color='', count=''):
        """ Initialize a Product """
        self.id = int(id)
        self.name = name
        self.category = category
        self.price = price
        self.color = color
        self.description = description
        self.count = count

    def save(self):
        """
        Saves a Product to the data store
        """
        if self.id == 0:
            self.id = Product.__next_index()
        # Product.data.append(self)

        Product.redis.set(self.id, pickle.dumps(self.serialize()))
        # print Product.data[-1].id
        # else:
        # for i in range(len(Product.data)):
        #    if Product.data[i].id == self.id:
        #        Product.data[i] = self
        #        break

    def delete(self):
        """ Removes a Product from the data store """
        # Product.data.remove(self)
        Product.redis.delete(self.id)

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {"id": self.id, "name": self.name, "category": self.category,
                "price": self.price, "description": self.description,
                "color": self.color, "count": self.count}

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary
        Args:
            data (dict): A dictionary containing the Product data
        """
        # if not isinstance(data, dict):
        #    raise DataValidationError('Invalid product: body of request contained bad or no data')
        # if data.has_key('id'):
        #    self.id = data['id']
        try:
            self.name = data['name']
            self.category = data['category']
            self.price = data['price']
            self.description = data['description']
            self.color = data['color']
            self.count = data['count']
        except KeyError as err:
            raise DataValidationError(
                'Invalid product: missing ' + err.args[0])
        except TypeError as error:
            raise DataValidationError(
                'Invalid product: body of request contained bad or no data')
        return self

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        # with Product.lock:
        #    Product.index += 1
        # return Product.index
        return Product.redis.incr('index')

    @staticmethod
    def all():
        """ Returns all of the Products in the database """
        # return [p for p in Product.data]
        results = []
        for key in Product.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Product.redis.get(key))
                product = Product(data['id']).deserialize(data)
                results.append(product)
        return results

    @staticmethod
    def available():
        """ Returns all of the Products in the database 
        with count greater than 0"""
        results = []

        for key in Product.redis.keys():
            if key != 'index':  # filer out our id index
                data = pickle.loads(Product.redis.get(key))
                product = Product(data['id']).deserialize(data)

                if product.count > 0:
                    results.append(product)
        return results

    @staticmethod
    def remove_all():
        """ Removes all of the Products from the database """
        #del Product.data[:]
        #Product.index = 0
        # return Product.data
        Product.redis.flushall()

    @staticmethod
    def find(product_id):
        """ Finds a Product by it's ID """
        # if not Product.data:
        #    return None
        #product = [p for p in Product.data if p.id == product_id]
        # if product:
        #    return product[0]
        # return None
        if Product.redis.exists(product_id):
            data = pickle.loads(Product.redis.get(product_id))
            product = Product(data['id']).deserialize(data)
            return product
        return None

    @staticmethod
    def __find_by(attribute, value):
        """ Generic Query that finds a key with a specific value """
        Product.logger.info('Processing %s query for %s', attribute, value)
        #if isinstance(value, str):
        search_criteria = value.lower()  # make case insensitive
        #else:
        #print ("INFB")
        #print (value)
        search_criteria = value
        results = []
        for key in Product.redis.keys():
            if key != 'index':  # filer out our id index
                # print("Key:" + key)
                data = pickle.loads(Product.redis.get(key))
                #print(data[attribute])
                # perform case insensitive search on strings
                #if isinstance(data[attribute], str):
                test_value = data[attribute].lower()
                #else:
                #test_value = data[attribute]
                # print(search_criteria, test_value)
                if test_value == search_criteria:
                    results.append(Product(data['id']).deserialize(data))
        return results

    @staticmethod
    def find_by_category(category):
        """ Returns all of the Products in a category
        Args:
            category (string): the category of the Products you want to match
        """
        #print ("IN FBC")
        return Product.__find_by('category', category)
        # return [p for p in Product.data if p.category == category]

    @staticmethod
    def find_by_name(name):
        """ Returns all Products with the given name
        Args:
            name (string): the name of the Products you want to match
        """
        # return [p for p in Product.data if p.name == name]
        return Product.__find_by('name', name)

    @staticmethod
    def connect_to_redis(hostname, port, password):
        """ Connects to Redis and tests the connection """
        Product.logger.info("Testing Connection to: %s:%s", hostname, port)
        Product.redis = Redis(host=hostname, port=port, password=password)
        try:
            Product.redis.ping()
            Product.logger.info("Connection established")
        except ConnectionError:
            Product.logger.info("Connection Error from: %s:%s", hostname, port)
            Product.redis = None
        return Product.redis

    @staticmethod
    def init_db(redis=None):
        """
        Initialized Redis database connection
        This method will work in the following conditions:
          1) In Bluemix with Redis bound through VCAP_SERVICES
          2) With Redis running on the local server as with Travis CI
          3) With Redis --link in a Docker container called 'redis'
          4) Passing in your own Redis connection object
        Exception:
        ----------
          redis.ConnectionError - if ping() test fails
        """
        if redis:
            Product.logger.info("Using client connection...")
            Product.redis = redis
            try:
                Product.redis.ping()
                Product.logger.info("Connection established")
            except ConnectionError:
                Product.logger.error("Client Connection Error!")
                Product.redis = None
                raise ConnectionError('Could not connect to the Redis Service')
            return
        # Get the credentials from the Bluemix environment
        if 'VCAP_SERVICES' in os.environ:
            Product.logger.info("Using VCAP_SERVICES...")
            vcap_services = os.environ['VCAP_SERVICES']
            services = json.loads(vcap_services)
            creds = services['rediscloud'][0]['credentials']
            Product.logger.info("Conecting to Redis on host %s port %s",
                                creds['hostname'], creds['port'])
            Product.connect_to_redis(creds['hostname'], creds[
                                     'port'], creds['password'])
        else:
            Product.logger.info(
                "VCAP_SERVICES not found, checking localhost for Redis")
            Product.connect_to_redis('127.0.0.1', 6379, None)
            if not Product.redis:
                Product.logger.info(
                    "No Redis on localhost, looking for redis host")
                Product.connect_to_redis('redis', 6379, None)
        if not Product.redis:
            # if you end up here, redis instance is down.
            Product.logger.fatal(
                '*** FATAL ERROR: Could not connect to the Redis Service')
            raise ConnectionError('Could not connect to the Redis Service')
