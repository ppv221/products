
import threading

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Product(object):
    """
    Class that represents a Product

    This version uses an in-memory collection of products for testing
    """
    lock = threading.Lock()
    data = []
    index = 0

    def __init__(self, id=0, name='', category='', price='', description = '',color='',count=''):
        """ Initialize a Product """
        self.id = id
        self.name = name
        self.category = category
        self.price = price
        self.color = color
        self.description = description
        self.count=count
    def save(self):
        """
        Saves a Product to the data store
        """
        if self.id == 0:
            self.id = self.__next_index()
            Product.data.append(self)
            print Product.data[-1].id
        else:
            for i in range(len(Product.data)):
                if Product.data[i].id == self.id:
                    Product.data[i] = self
                    break

    def delete(self):
        """ Removes a Product from the data store """
        Product.data.remove(self)

    def serialize(self):
        """ Serializes a Product into a dictionary """
        return {"id": self.id, "name": self.name, "category": self.category, "price": self.price, "description": self.description,"color": self.color,"count":self.count}

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the Pet data
        """
        if not isinstance(data, dict):
            raise DataValidationError('Invalid product: body of request contained bad or no data')
        if data.has_key('id'):
            self.id = data['id']
        try:
            self.name = data['name']
            self.category = data['category']
            self.price = data['price']
            self.description = data['description']
            self.color = data['color']
            self.count = data['count']
        except KeyError as err:
            raise DataValidationError('Invalid product: missing ' + err.args[0])
        return

    @staticmethod
    def __next_index():
        """ Generates the next index in a continual sequence """
        with Product.lock:
            Product.index += 1
        return Product.index

    @staticmethod
    def all():
        """ Returns all of the Products in the database """
        return [p for p in Product.data]

    @staticmethod
    def available():
        """ Returns all of the Products in the database with count greater than 0"""
        return [p for p in Product.data if int(p.count) > 0]

    @staticmethod
    def remove_all():
        """ Removes all of the Products from the database """
        del Product.data[:]
        Product.index = 0
        return Product.data

    @staticmethod
    def find(product_id):
        """ Finds a Product by it's ID """
        if not Product.data:
            return None
        product = [p for p in Product.data if p.id == product_id]
        if product:
            return product[0]
        return None

    @staticmethod
    def find_by_category(category):
        """ Returns all of the Products in a category

        Args:
            category (string): the category of the Products you want to match
        """
        return [p for p in Product.data if p.category == category]

    @staticmethod
    def find_by_name(name):
        """ Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        return [p for p in Product.data if p.name == name]
