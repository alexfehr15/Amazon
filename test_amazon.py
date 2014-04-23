"""
    test_amazon.py
    April 22, 2014
    Python Programming - CIS 5930 - Spring 2014
    Amazon Assignment

    Team:
    Alex Fehr and Doug Wussler

    Run tests for amazon.py
"""

import unittest
import amazon

class TestSequenceFunctions(unittest.TestCase):
	"""Run tests for amazon.py"""

	def setUp(self):
		"""
		Sets up two objects for manipulation in tests below
		"""

		self.obj_url = amazon.Amazon(url="www.amazon.com/sampleurl")
		self.obj_url.name = "Game of Thrones"
		self.obj_url.authors = "George RR Martin"
		self.obj_url.price = 5.99
		self.obj_url.details = "Details"
		self.obj_url.reviews = "Reviews"
		self.obj_file = amazon.Amazon(file="sampledirectory/anotherdirectory")

	def tearDown(self):
		"""
		Intentionally empty
		"""

		pass

	def test_url_getter(self):
		"""
		Test if an Amazon object's url returns the correct type and data
		"""

		self.assertEqual(self.obj_url.url, "www.amazon.com/sampleurl")

	def test_file_getter(self):
		"""
		Test if an Amazon object's file returns the correct type and data
		"""

		self.assertEqual(self.obj_file.file, "sampledirectory/anotherdirectory")

	def test_name_getter(self):
		"""
		Test if an Amazon object's name returns the correct type and data
		"""

		self.assertEqual(self.obj_url.name, "Game of Thrones")

	def test_authors_getter(self):
		"""
		Test if an Amazon object's authors returns the correct type and data
		"""

		self.assertEqual(self.obj_url.authors, "George RR Martin")

	def test_price_getter(self):
		"""
		Test if an Amazon object's price returns the correct type and data
		"""

		self.assertEqual(self.obj_url.price, 5.99)

	def test_details_getter(self):
		"""
		Test if an Amazon object's details returns the correct type and data
		"""

		self.assertEqual(self.obj_url.details, "Details")

	def test_reviews_getter(self):
		"""
		Test if an Amazon object's reviews returns the correct type and data
		"""

		self.assertEqual(self.obj_url.reviews, "Reviews")

	def test_url_setter(self):
		"""
		Test if an Amazon object's url returns the correct type and data
		"""

		self.obj_url.url = "www.amazon.com/anotherurl"
		self.assertEqual(self.obj_url.url, "www.amazon.com/anotherurl")

	def test_file_setter(self):
		"""
		Test if an Amazon object's file returns the correct type and data
		"""

		self.obj_file.file = "sampledirectory/yetanotherdirectory"
		self.assertEqual(self.obj_file.file, "sampledirectory/yetanotherdirectory")

	def test_name_setter(self):
		"""
		Test if an Amazon object's name returns the correct type and data
		"""

		self.obj_file.name = "Gardens of the Moon"
		self.assertEqual(self.obj_file.name, "Gardens of the Moon")

	def test_authors_setter(self):
		"""
		Test if an Amazon object's authors returns the correct type and data
		"""

		self.obj_file.authors = "Steven Erikson"
		self.assertEqual(self.obj_file.authors, "Steven Erikson")

	def test_price_setter(self):
		"""
		Test if an Amazon object's price returns the correct type and data
		"""

		self.obj_file.price = 5.44
		self.assertEqual(self.obj_file.price, 5.44)

	def test_details_setter(self):
		"""
		Test if an Amazon object's details returns the correct type and data
		"""

		self.obj_file.details = "More Details"
		self.assertEqual(self.obj_file.details, "More Details")

	def test_reviews_setter(self):
		"""
		Test if an Amazon object's reviews returns the correct type and data
		"""

		self.obj_file.reviews = "More Reviews"
		self.assertEqual(self.obj_file.reviews, "More Reviews")

	def test_parse_command_line(self):
		"""
		Test that command line arguments are being treated correctly
		"""

		pass

if __name__ == '__main__':
	unittest.main()