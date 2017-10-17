# Test cases can be run with:
# nosetests
# coverage report -m

""" Test cases for Product Model """

import unittest
from models import Product, DataValidationError

######################################################################
#  T E S T   C A S E S
######################################################################
class TestPets(unittest.TestCase):
    """ Test Cases for Pets """

    def setUp(self):
        Product.remove_all()

    def test_create_a_pet(self):
        """ Create a pet and assert that it exists """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf')
        self.assertTrue(p != None)
        self.assertEqual(p.id, 0)
        self.assertEqual(p.name, "Asus2500")
        self.assertEqual(p.category, "Laptop")

    def test_add_a_pet(self):
        """ Create a pet and add it to the database """
        p = Product.all()
        self.assertEqual(p, [])
        p = Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf')
        self.assertTrue(p != None)
        self.assertEqual(p.id, 0)
        p.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(p.id, 1)
        pets = Product.all()
        self.assertEqual(len(pets), 1)

    def test_update_a_pet(self):
        """ Update a Pet """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf')
        p.save()
        self.assertEqual(p.id, 1)
        # Change it an save it
        p.category = "gaming_laptop"
        p.save()
        self.assertEqual(p.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Product.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].category, "gaming_laptop")

    def test_delete_a_pet(self):
        """ Delete a Pet """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf')
        p.save()
        self.assertEqual(len(Product.all()), 1)
        # delete the pet and make sure it isn't in the database
        p.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_serialize_a_pet(self):
        """ Test serialization of a Pet """
        p = Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf')
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
        self.assertEqual(data['description'], "erwwfwf")
        self.assertIn('color', data)
        self.assertEqual(data['color'], "qerwrw")

    def test_deserialize_a_pet(self):
        """ Test deserialization of a Pet """
        data = {"id": 1, "name": "Asus2500", "category": "Laptop","price": "232434", "description": "qerwrw", "color": "erwwfwf"}
        pet = Product()
        pet.deserialize(data)
        self.assertNotEqual(pet, None)
        self.assertEqual(pet.id, 1)
        self.assertEqual(pet.name, "Asus2500")
        self.assertEqual(pet.category, "Laptop")
        self.assertEqual(pet.price, "232434")
        self.assertEqual(pet.description, "qerwrw")
        self.assertEqual(pet.color, "erwwfwf")


    def test_deserialize_with_no_name(self):
        """ Deserialize a Pet without a name """
        pet = Product()
        data = {"id":0, "category": "Laptop"}
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Pet with no data """
        pet = Product()
        self.assertRaises(DataValidationError, pet.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserailize a Pet with bad data """
        pet = Product()
        self.assertRaises(DataValidationError, pet.deserialize, "data")

    def test_find_pet(self):
        """ Find a Pet by ID """
        Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf').save()
        Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
        pet = Product.find(2)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, 2)
        self.assertEqual(pet.name, "GE4509")

    def test_find_with_no_pets(self):
        """ Find a Pet with no Pets """
        pet = Product.find(1)
        self.assertIs(pet, None)

    def test_pet_not_found(self):
        """ Test for a Pet that doesn't exist """
        Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf').save()
        #Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
        pet = Product.find(2)
        self.assertIs(pet, None)

    def test_find_by_category(self):
        """ Find Pets by Category """
        Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf').save()
        Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
        pets = Product.find_by_category("Laptop")
        self.assertNotEqual(len(pets), 0)
        self.assertEqual(pets[0].category, "Laptop")
        self.assertEqual(pets[0].name, "Asus2500")

    def test_find_by_name(self):
        """ Find a Pet by Name """
        Product(0, 'Asus2500', 'Laptop', '234', 'qerwrw', 'erwwfwf').save()
        Product(0, 'GE4509', 'Microwave','34324', 'wewef', 'fwfwsxdws' ).save()
        pets = Product.find_by_name("Asus2500")
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].category, "Laptop")
        self.assertEqual(pets[0].name, "Asus2500")


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestPets)
    # unittest.TextTestRunner(verbosity=2).run(suite)
