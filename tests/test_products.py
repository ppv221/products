""" Test cases for Product Model """
import os
import json
import unittest
from mock import patch
from redis import Redis, ConnectionError
from models import Product, DataValidationError,DatabaseConnectionError,BadRequestError,NotFoundError


VCAP_SERVICES = {
    'rediscloud': [
        {'credentials': {
            'password': '',
            'hostname': '127.0.0.1',
            'port': '6379'
        }
        }
    ]
}

######################################################################
#  T E S T   C A S E S
######################################################################


class TestProduct(unittest.TestCase):
    """ Test Cases for Products """

    def setUp(self):
        """ Initialize the db"""
        Product.init_db()
        Product.remove_all()

    def test_create_a_product(self):
        """ Create a product and assert that it exists """
        p = Product(0, 'Asus2500', 'Laptop', '34', 'laptop', 'blue', 4)
        self.assertTrue(p != None)
        self.assertEqual(p.id, 0)
        self.assertEqual(p.name, "Asus2500")
        self.assertEqual(p.category, "Laptop")

    def test_add_a_product(self):
        """ Create a product and add it to the database """
        p = Product.all()
        self.assertEqual(p, [])
        p = Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4)
        self.assertTrue(p != None)
        self.assertEqual(p.id, 0)
        p.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(p.id, 1)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_update_a_product(self):
        """ Update a Product """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4)
        p.save()
        self.assertEqual(p.id, 1)
        # Change it an save it
        p.category = "gaming_laptop"
        p.save()
        self.assertEqual(p.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category, "gaming_laptop")

    def test_delete_a_product(self):
        """ Delete a Product """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4)
        p.save()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        p.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_product(self):
        """ Test serialization of a Product """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4)
        data = p.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], 0)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "Asus2500")
        self.assertIn('category', data)
        self.assertEqual(data['category'], "Laptop")
        self.assertIn('price', data)
        self.assertEqual(data['price'], "234")
        self.assertIn('description', data)
        self.assertEqual(data['description'], "laptop")
        self.assertIn('color', data)
        self.assertEqual(data['color'], "blue")
        self.assertIn('count', data)
        self.assertEqual(data['count'], 4)

    def test_deserialize_a_product(self):
        """ Test deserialization of a Product """
        data = {"id": 1, "name": "Asus2500", "category": "Laptop",
                "price": "234", "description": "laptop",
                "color": "blue", 'count': 4}
        products = Product(data['id'])
        products.deserialize(data)

        self.assertNotEqual(products, None)
        self.assertEqual(products.id, 1)
        self.assertEqual(products.name, "Asus2500")
        self.assertEqual(products.category, "Laptop")
        self.assertEqual(products.price, "234")
        self.assertEqual(products.description, "laptop")
        self.assertEqual(products.color, "blue")
        self.assertEqual(products.count, 4)

    def test_deserialize_with_no_name(self):
        """ Deserialize a Product without a name """
        products = Product()
        data = {"id": 0, "category": "Laptop"}
        self.assertRaises(DataValidationError, products.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Product with no data """
        products = Product()
        self.assertRaises(DataValidationError, products.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Product with bad data """
        products = Product()
        self.assertRaises(DataValidationError, products.deserialize, "data")

    def test_available(self):
        Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4).save()
        Product(0, 'GE4509', 'Microwave', '34324',
                'microwave', 'black', 0).save()

        products = Product.available()

        self.assertEqual(len(products), 1)
        self.assertIsNot(products[0], None)
        self.assertEqual(products[0].id, 1)
        self.assertEqual(products[0].name, "Asus2500")

    def test_find_product(self):
        """ Find a Product by ID """
        Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4).save()
        Product(0, 'GE4509', 'Microwave', '34324',
                'microwave', 'black', 4).save()
        products = Product.find(2)

        self.assertIsNot(products, None)
        self.assertEqual(products.id, 2)
        self.assertEqual(products.name, "GE4509")

    def test_find_with_no_product(self):
        """ Find a Product with no products """
        products = Product.find(1)
        self.assertIs(products, None)

    def test_product_not_found(self):
        """ Test for a Product that doesn't exist """
        Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4).save()
        #Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
        products = Product.find(2)
        self.assertIs(products, None)

    def test_find_by_category(self):
        """ Find Products by Category """
        Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4).save()
        Product(0, 'GE4509', 'Microwave', '34324',
                'microwave', 'black', 4).save()
        products = Product.find_by_category("Laptop")
        self.assertNotEqual(len(products), 0)
        self.assertEqual(products[0].category, "Laptop")
        self.assertEqual(products[0].name, "Asus2500")

    def test_find_by_name(self):
        """ Find a Product by Name """
        Product(0, 'Asus2500', 'Laptop', '234', 'laptop', 'blue', 4).save()
        Product(0, 'GE4509', 'Microwave', '34324',
                'microwave', 'black', 4).save()
        products = Product.find_by_name("Asus2500")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].category, "Laptop")
        self.assertEqual(products[0].name, "Asus2500")

    def test_passing_connection(self):
        """ Pass in the Redis connection """
        Product.init_db(Redis(host='127.0.0.1', port=6379))
        self.assertIsNotNone(Product.redis)

    def test_passing_bad_connection(self):
        """ Pass in a bad Redis connection """
        self.assertRaises(ConnectionError, Product.init_db,
                          Redis(host='127.0.0.1', port=6300))
        self.assertIsNone(Product.redis)

    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        Product.init_db()
        self.assertIsNotNone(Product.redis)

    @patch('redis.Redis.ping')
    def test_redis_connection_error(self, ping_error_mock):
        """ Test a Bad Redis connection """
        ping_error_mock.side_effect = ConnectionError()
        self.assertRaises(ConnectionError, Product.init_db)
        self.assertIsNone(Product.redis)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
