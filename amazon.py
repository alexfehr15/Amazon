"""
Amazon Assignment
"""

import argparse

class Amazon():

	"""
	class Description
	"""

	def __init__(self, url="someURL", file="someFile"):
		"""
		Method Description
		"""

		self.__url = url
		self.__file = file

	@property
	def url(self):
		"""
		Getter for the book url
		"""

		return self.__url

	@property
	def file(self):
		"""
		Getter for directory to look in for html files
		"""

		return self.__file

	@property
	def name(self):
		"""
		Getter for the name of the book
		"""

		return self.__name

	@property
	def authors(self):
		"""
		Getter for the author(s) of the book
		"""

		return self.__authors

	@property
	def price(self):
		"""
		Getter for the price of the book
		"""

		return self.__price

	@property
	def details(self):
		"""
		Getter for the product details of the book
		"""

		return self.__details

	@property
	def reviews(self):
		"""
		Getter for the most helpful customer reviews of the book
		"""

		return self.__reviews

	@url.setter
	def url(self, url):
		"""
		Getter for the book url
		"""

		self.__url = url

	@file.setter
	def file(self, file):
		"""
		Getter for directory to look in for html files
		"""

		self.__file = file

	@name.setter
	def name(self, name):
		"""
		Getter for the name of the book
		"""

		self.__name = name

	@authors.setter
	def authors(self, authors):
		"""
		Getter for the author(s) of the book
		"""

		self.__authors = authors

	@price.setter
	def price(self, price):
		"""
		Getter for the price of the book
		"""

		self.__price = price

	@details.setter
	def details(self, details):
		"""
		Getter for the product details of the book
		"""

		self.__details = details

	@reviews.setter
	def reviews(self, reviews):
		"""
		Getter for the most helpful customer reviews of the book
		"""

		self.__reviews = reviews

def parse_command_line():
	"""
	Parses the command line arguments and returns them
	"""

	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-d", help="directory containing html files to parse")
	group.add_argument("-u", help="url for specified web page")
	parser.add_argument("-o", choices=["html", "xml", "csv"], help="output format")
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_command_line()
	if args.d:
		obj = Amazon(file=args.d)
	elif args.u:
		obj = Amazon(url=args.u)
	if args.o:
		output_type = args.o
	else:
		output_type = "no_output"

	#testing
	if args.d:
		print(obj.file)
	elif args.u:
		print(obj.url)
	print(output_type)
