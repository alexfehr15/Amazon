#!/usr/bin/env python

"""
Amazon Assignment
"""

import argparse
import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import json
import os

class Amazon():

	"""
	class Description
	"""

	def __init__(self, url="someURL", filename="someFile"):
		"""
		Method Description
		"""

		self.__url = url
		self.__file = filename

	@property
	def url(self):
		"""
		Getter for the book url
		"""

		return self.__url

	@property
	def filename(self):
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

	@filename.setter
	def filename(self, filename):
		"""
		Getter for directory to look in for html files
		"""

		self.__file = filename

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

	def parse_file(self):
		"""
		Parse local html files
		"""

		pass

	def parse_url(self):
		"""
		Parse using requests
		"""

		#TESTING
		f = open('temp.txt', 'w', encoding='utf-8')

		#get data from requests
		r = requests.get(self.url)
		bsoup = BeautifulSoup(r.content)

		#TESTING	
		f.write(bsoup.prettify())
		f.close()

		#create JSON object
		J = dict()

		#get the name of the book
		name = ""
		count = 0
		for tag in bsoup.find(id="fbt_x_title"):
			if count != 0:
				name += tag.string
			count += 1
			if count == 2:
				break
		print(name.strip())
		J['title'] = name.strip()

		#get the author of the book
		A = []
		#method 1
		tag = bsoup.find(class_="parseasinTitle")
		if str(type(tag)) != "<class 'NoneType'>":
			tag = tag.find_parent("div")
			for item in tag.find_all("a"):
				author = item.string
				A.append(author)
				print(author)
		#method 2
		else:
			for tag in bsoup.find_all(class_="author notFaded"):
				temp = tag.find("span")
				author = temp.string
				A.append(author)
				print(temp.contents[0].strip())
		J['authors'] = A

		#get the new price
		new_price = "-1"
		tag = bsoup.find(id="buyNewSection")
		reg = re.compile("\$[0-9]*\.[0-9]*")
		reg = reg.search(str(tag))
		if str(type(reg)) != "<class 'NoneType'>":
			new_price = reg.group()
			print("New " + new_price)
		new_price = new_price.replace("$", "")
		J['price_new'] = float(new_price)

		#get the rental price
		rent_price = "-1"
		tag = bsoup.find(id="rentBuySection")
		reg = re.compile("\$[0-9]*\.[0-9]*")
		reg = reg.search(str(tag))
		if str(type(reg)) != "<class 'NoneType'>":
			rent_price = reg.group()
			print("Rent " + rent_price)
		rent_price = float(rent_price.replace("$", ""))
		J['price_rent'] = float(rent_price)

		#get the product details
		D = []
		tag = bsoup.find(id="productDetailsTable")
		for item in tag.find_all("li"):
			#everything besides avg customer reviews and amazon best sellers rank
			if str(item.b.string).strip() != "Average Customer Review:" and str(item.b.string).strip() != "Amazon Best Sellers Rank:":
				D.append(str(item.b.string).strip() + " " + str(item.contents[1]).strip())
				print(str(item.b.string).strip() + " " + str(item.contents[1]).strip())
			#average customer review
			elif str(item.b.string).strip() == "Average Customer Review:":
				#get number of stars
				reg = re.compile("([0-9]|\.)* out of 5 stars")
				reg = reg.search(str(item))
				if str(type(reg)) != "<class 'NoneType'>":
					D.append(reg.group())
					print(reg.group())
				#get number of reviews 
				reg = re.compile("([0-9]|,)* customer reviews")
				reg = reg.search(str(item))
				if str(type(reg)) != "<class 'NoneType'>":
					D.append(reg.group())
					print(reg.group())
			#amazon best sellers rank
			else:
				reg = re.compile("#([0-9]|,)*")
				reg = reg.search(str(item))
				if str(type(reg)) != "<class 'NoneType'>":
					D.append(reg.group())
					print(reg.group())
				for thing in item.find_all("a"):
					D.append(thing.string)
					print(thing.string)
		J['details'] = D

		#get the most helpful customer reviews
		#TESTING
		f = open("out.txt", "w", encoding="utf-8")

		R = []
		for tag in bsoup.find_all(id=re.compile("revData-dpReviewsMostHelpful")):
			item = tag.find_all("div")
			to_search = str(item[len(item)-1])
			to_search = remove_html_tags(str(to_search))
			R.append(str(to_search))
			f.write(str(to_search))
			f.write("\n")
		J['reviews'] = R

		#TESTING
		JSO = json.dumps(J)
		#JSO = json.loads(JSO)
		f.write(str(type(JSO)))
		f.write(str(JSO))

		#TESTING
		f.close()

		return JSO

	def parse_file(self):
		"""
		Parse from html files in current directory
		"""
		S = []
		f = open("html.txt", "w", encoding="utf-8")
		f3 = open('temp.txt', 'w', encoding='utf-8')
		f2 = open("out.txt", "w", encoding="utf-8")
		#loop through the directory (need to eliminate leading /)
		for fn in os.listdir(os.path.join(os.getcwd(), self.filename)):
			if os.path.isfile(os.path.join(os.getcwd(), self.filename, fn)):
				#TESTING
				print(fn)

				#convert file to soup
				test = os.path.join(os.getcwd(), self.filename, fn)
				bsoup = BeautifulSoup(open(test))

				#TESTING
				f.write(bsoup.prettify())

				#TESTING	
				f3.write(bsoup.prettify())

				#create JSON object
				J = dict()

				#get the name of the book
				name = ""
				count = 0
				for tag in bsoup.find(id="fbt_x_title"):
					if count != 0:
						name += tag.string
					count += 1
					if count == 2:
						break
				print(name.strip())
				J['title'] = name.strip()

				#get the author of the book
				A = []
				for tag in bsoup.find_all(class_="author notFaded"):
					author = tag.a.string
					A.append(author)
					print(tag.a.string)
				J['authors'] = A

				#get the new price
				price_new = ""
				tag = bsoup.find(id="buyNewSection")
				reg = re.compile("\$[0-9]*\.[0-9]*")
				reg = reg.search(str(tag))
				if str(type(reg)) != "<class 'NoneType'>":
					new_price = reg.group()
					print("New " + new_price)
				J['price_new'] = new_price

				#get the rental price
				rent_price = ""
				tag = bsoup.find(id="rentBuySection")
				reg = re.compile("\$[0-9]*\.[0-9]*")
				reg = reg.search(str(tag))
				if str(type(reg)) != "<class 'NoneType'>":
					rent_price = reg.group()
					print("Rent " + rent_price)
				J['price_rent'] = rent_price

				#get the product details
				D = []
				tag = bsoup.find(id="productDetailsTable")
				for item in tag.find_all("li"):
					#everything besides avg customer reviews and amazon best sellers rank
					if str(item.b.string).strip() != "Average Customer Review:" and str(item.b.string).strip() != "Amazon Best Sellers Rank:":
						D.append(str(item.b.string).strip() + " " + str(item.contents[1]).strip())
						print(str(item.b.string).strip() + " " + str(item.contents[1]).strip())
					#average customer review
					elif str(item.b.string).strip() == "Average Customer Review:":
						#get number of stars
						reg = re.compile("([0-9]|\.)* out of 5 stars")
						reg = reg.search(str(item))
						if str(type(reg)) != "<class 'NoneType'>":
							D.append(reg.group())
							print(reg.group())
						#get number of reviews 
						reg = re.compile("([0-9]|,)* customer reviews")
						reg = reg.search(str(item))
						if str(type(reg)) != "<class 'NoneType'>":
							D.append(reg.group())
							print(reg.group())
					#amazon best sellers rank
					else:
						reg = re.compile("#([0-9]|,)*")
						reg = reg.search(str(item))
						if str(type(reg)) != "<class 'NoneType'>":
							D.append(reg.group())
							print(reg.group())
						for thing in item.find_all("a"):
							D.append(thing.string)
							print(thing.string)
				J['details'] = D

				#get the most helpful customer reviews


				R = []
				for tag in bsoup.find_all(id=re.compile("revData-dpReviewsMostHelpful")):
					item = tag.find_all("div")
					to_search = str(item[len(item)-1])
					to_search = remove_html_tags(str(to_search))
					R.append(str(to_search))
					f.write(str(to_search))
					f.write("\n")
				J['reviews'] = R

				#TESTING
				JSO = json.dumps(J)
				#JSO = json.loads(JSO)
				S.append(JSO)
				f2.write(str(type(JSO)))
				f2.write(str(JSO))
				f2.write("\n\n\n\n")

		#TESTING
		f.close()
		f3.close()
		f2.close()

		return S


def remove_html_tags(data):
	p = re.compile("<.*?>")
	return p.sub('', data)

def parse_command_line():
	"""
	Parses the command line arguments and returns them
	"""

	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-d", type=str, help="directory containing html files to parse")
	group.add_argument("-u", type=str, help="url for specified web page")
	parser.add_argument("-o", choices=["html", "xml", "csv"], help="output format")
	return parser.parse_args()

if __name__ == "__main__":
	#parse command line arguments
	args = parse_command_line()

	#create Amazon object with filename or url
	if args.d:
		obj = Amazon(filename=args.d)
	elif args.u:
		obj = Amazon(url=args.u)

	#get what the output type is
	if args.o:
		output_type = args.o
	else:
		output_type = "no_output"

	#call parsing function and storing json object
	if args.d:
		JSON = obj.parse_file()
	elif args.u:
		JSON = obj.parse_url()
