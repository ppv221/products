""" Test cases for the Product E-Commerce Site """

import logging
import unittest
import json
from mock import MagicMock, patch
from flask_api import status    # HTTP Status Codes
import server

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################


class TestProductServer(unittest.TestCase):
    """ Product Server Tests """

    # @classmethod
    # def setUpClass(cls):
    #     """ Run once before all tests """
    #     server.app.debug = False
    #     # server.initialize_logging(logging.ERROR)

    def setUp(self):
        """ Runs before each test """
        self.app = server.app.test_client()
        server.get_product_data()
        # server.data_reset()

        # server.Product(0, 'Asus2500', 'Laptop', '234',
        #                'qerwrw', 'erwwfwf', 23).save()
        # server.Product(0, 'GE4509', 'Microwave', '34324',
        #                'wewef', 'fwfwsxdws', 12).save()
        # server.Product(0, 'Hp', 'Microwave', '960', 'Micro', 'blue', 0).save()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/ui')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # data = json.loads(resp.data)
        self.assertIn('Product', resp.data)

    def test_get_product_list(self):
        """ Get a list of Product """
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertTrue(len(resp.data) > 0)
        # self.assertEqual(len(data), 3)

    def test_list_available_products(self):
        resp = self.app.get('/products/available')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(len(data), 2)

    def test_get_product(self):
        """ Get one product """
        resp = self.app.get('/products/2')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'GE4509')

    def test_get_product_count(self):
        """ Get one product """
        resp = self.app.get('/products/3')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['count'], 0)

    def test_get_product_not_found(self):
        """ Get a Product thats not found """
        resp = self.app.get('/products/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_product(self):
        """ Create a Product """
        # save the current number of products for later comparrison
        product_count = self.get_product_count()
        # add a new product
        new_product = {'name': 'High_Sierra', 'category': 'Bag',
                       'price': '1234', 'description': 'Cool Bag',
                       'color': 'blue', 'count': 0}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'High_Sierra')
        # check that count has gone up and includes new product
        resp = self.app.get('/products')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), product_count + 1)
        self.assertIn(new_json, data)

    def test_update_product(self):
        """ Update a Product """
        upd_product = {'name': 'GE4509', 'category': 'Microwave',
                       'price': '1000', 'description': 'Dont buy',
                       'color': 'faded', 'count': 6}
        data = json.dumps(upd_product)
        resp = self.app.put('/products/2', data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/products/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['price'], '1000')

    def test_update_product_with_no_name(self):
        """ Update a Product with no name """
        new_product = {'category': 'Microwave', 'price': '1200',
                       'description': 'Dont buy', 'color': 'faded', 'count': 3}
        data = json.dumps(new_product)
        resp = self.app.put('/products/2', data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_not_found(self):
        """ Update a Product that can't be found """
        upd_product = {'name': 'GE4509', 'category': 'Microwave',
                       'price': '1000', 'description': 'Dont buy',
                       'color': 'faded', 'count': 5}
        data = json.dumps(upd_product)
        resp = self.app.put('/products/0', data=data,
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_product_unit(self):
        resp = self.app.put('/products/2/add_unit',
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/products/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['count'], 13)

    def test_add_product_unit_not_found(self):
        """ Update count of a Product that can't be found """
        resp = self.app.put('/products/0/add_unit',
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_sell_products(self):
        resp = self.app.put('/products/2/sell_products',
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.app.get('/products/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['count'], 11)

    def test_sell_products_count(self):
        """ Get one product """
        resp = self.app.put('/products/3/sell_products',
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_200_OK)

    def test_sell_products_not_found(self):
        """ Update count of a Product that can't be found """
        resp = self.app.put('/products/0/sell_products',
                            content_type='application/json')
        self.assertEquals(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """ Delete a Product that exists """
        # save the current number of products for later comparrison
        product_count = self.get_product_count()
        # delete a product
        resp = self.app.delete('/products/2', content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_product_count()
        self.assertEqual(new_count, product_count - 1)

    def test_create_product_with_no_name(self):
        """ Create a Product with the name missing """
        new_product = {'category': 'Microwave', 'price': '1000',
                       'description': 'Dont buy', 'color': 'faded', 'count': 7}
        data = json.dumps(new_product)
        resp = self.app.post('/products', data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_nonexisting_product(self):
        """ Get a Product that doesn't exist """
        resp = self.app.get('/products/5')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_query_product_list_by_category(self):
        """ Query Product by Category """
        resp = self.app.get('/products', query_string='category=Microwave')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('GE4509' in resp.data)
        self.assertFalse('Asus2500' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['category'], 'Microwave')

    def test_query_product_list_by_name(self):
        """ Query Product by Name """
        resp = self.app.get('/products', query_string='name=GE4509')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertTrue('GE4509' in resp.data)
        self.assertFalse('Asus2500' in resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['name'], 'GE4509')


######################################################################
# Utility functions
######################################################################

    def get_product_count(self):
        """ save the current number of product """
        resp = self.app.get('/products')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
