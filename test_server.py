import unittest
import json
import server

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestProductServer(unittest.TestCase):

    def setUp(self):
        server.app.debug = True
        self.app = server.app.test_client()
        server.products = { 1: {'id': 1, 'name': 'TV', 'category': 'entertainment'}, 2: {'id': 2, 'name': 'Blender', 'category': 'appliances'} }

    def test_index(self):
        resp = self.app.get('/')
        self.assertTrue ('product Demo REST API Service' in resp.data)
        self.assertTrue( resp.status_code == HTTP_200_OK )

    def test_get_product_list(self):
        resp = self.app.get('/products')
        #print 'resp_data: ' + resp.data
        self.assertTrue( resp.status_code == HTTP_200_OK )
        self.assertTrue( len(resp.data) > 0 ) 

    def test_get_product(self):
        resp = self.app.get('/products/2')
        #print 'resp_data: ' + resp.data
        self.assertTrue( resp.status_code == HTTP_200_OK )
        data = json.loads(resp.data)
        self.assertTrue (data['name'] == 'Blender')


if __name__ == '__main__':
    unittest.main()