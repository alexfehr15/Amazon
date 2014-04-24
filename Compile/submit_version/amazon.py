#!/usr/bin/env python

"""
    amz_main.py
    April 23, 2014
    Alex Fehr
    Doug Wussler

    This has the code needed to parse a URL and persist the parsed book data.
    The "main" routine calls persist() and passes it parsed book data
    that has been converted to a JSON dictionary.
    persist() will add the book to the database.  It does not
    check to see if the book is already in the database so
    duplicate entries are possible.
"""

import argparse
import requests
from bs4 import BeautifulSoup
from lxml import etree
import re
import json
import os

from sqlalchemy import Column, Float, ForeignKey, Integer, \
    Table, Unicode, UnicodeText
from sqlalchemy.orm import relationship, backref, sessionmaker, joinedload
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

# Create object mappings to database tables
Base = declarative_base()

Books_authors_link = Table('books_authors_link', Base.metadata,
                           Column('book_id', Integer,
                                  ForeignKey('books.bid')),
                           Column('author_id', Integer,
                                  ForeignKey('authors.aid')))


class Books(Base):
    __tablename__ = 'books'
    bid = Column(Integer, primary_key=True)
    title = Column(Unicode)
    authors = relationship('Authors',
                           secondary=Books_authors_link)
    price_new = Column(Float)
    price_rent = Column(Float)
    details = Column(UnicodeText)
    reviews = relationship('Reviews')


class Authors(Base):
    __tablename__ = 'authors'
    aid = Column(Integer, primary_key=True)
    name = Column(Unicode)
    books = relationship('Books',
                         secondary=Books_authors_link)


class Reviews(Base):
    __tablename__ = 'reviews'
    rid = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.bid'))
    review = Column(UnicodeText)


def persist(jbook, view=False):
    engine = create_engine('sqlite:///Amazon.sqlite', echo=False)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    b = json.loads(jbook)
    new = Books(title=b['title'],
                price_new=b['price_new'],
                price_rent=b['price_rent'],
                authors=[Authors(name=a) for a in b['authors']],
                details=("~!^\n").join(b['details']),
                reviews=[Reviews(review=r) for r in b['reviews']])
    session.add(new)
    session.commit()
    #commented this out because kept giving errors

    if view:
        for b in session.query(Books).options(joinedload(Books.authors)).all():
            print("\n\n**************************")
            print(b.title, b.price_new, b.price_rent)
            print((", ").join([a.name for a in b.authors]))
            print(("\n").join(b.details.split("~!^\n")))
            try:
                print(("\n\n").join([r.review for r in b.reviews]))
            except UnicodeEncodeError as u:
                print(u)
            print("*************************\n")

    return True  # This serves no purpose at the moment


class Amazon():
    def __init__(self, url="someURL", filename="someFile"):
        self.__url = url
        self.__file = filename

    @property
    def url(self):
        return self.__url

    @property
    def filename(self):
        return self.__file

    @url.setter
    def url(self, url):
        self.__url = url

    @filename.setter
    def filename(self, filename):
        self.__file = filename

    def parse_url(self):
        # TESTING
        f = open('temp.txt', 'w', encoding='utf-8')

        # get data from requests
        r = requests.get(self.url)
        bsoup = BeautifulSoup(r.content)

        # TESTING
        f.write(bsoup.prettify())
        f.close()

        # create JSON object
        J = dict()

        # get the name of the book
        name = ""
        count = 0
        for tag in bsoup.find(id="fbt_x_title"):
            if count != 0:
                name += tag.string
            count += 1
            if count == 2:
                break
        J['title'] = name.strip()

        # get the author of the book
        A = []
        # method 1
        tag = bsoup.find(class_="parseasinTitle")
        if str(type(tag)) != "<class 'NoneType'>":
            tag = tag.find_parent("div")
            for item in tag.find_all("a"):
                author = item.string
                if str(type(author)) != "<class 'NoneType'>":
                    if "Visit" not in author:
                        if "search" not in author:
                            if "about" not in author:
                                A.append(author)
        # method 2
        else:
            for tag in bsoup.find_all(class_="author notFaded"):
                first = tag.a.string
                if "Visit" in first or str(type(first)) == \
                   "<class 'NoneType'>":
                    temp = tag.find("span")
                    author = temp.contents[0].strip()
                    A.append(author)
                else:
                    author = first
                    A.append(author)
        J['authors'] = A

        # get the new price
        new_price = "-1"
        tag = bsoup.find(id="buyNewSection")
        reg = re.compile("\$[0-9]*\.[0-9]*")
        reg = reg.search(str(tag))
        if str(type(reg)) != "<class 'NoneType'>":
            new_price = reg.group()
        new_price = float(new_price.replace("$", ""))

        # get the rental price
        rent_price = "-1"
        tag = bsoup.find(id="rentBuySection")
        reg = re.compile("\$[0-9]*\.[0-9]*")
        reg = reg.search(str(tag))
        if str(type(reg)) != "<class 'NoneType'>":
            rent_price = reg.group()
        rent_price = float(rent_price.replace("$", ""))

        # try something else if price is still
        counter = 0
        if new_price == -1:
            for tag in bsoup.find_all(class_="rentPrice"):
                counter += 1
                if str(type(tag.contents)) != "<class 'NoneType'>":
                    if counter == 1:
                        new_price = tag.contents[0].strip()
                        new_price = float(new_price.replace("$", ""))
                    elif counter == 2:
                        rent_price = tag.contents[0].strip()
                        rent_price = float(rent_price.replace("$", ""))

        # put prices in
        J['price_new'] = new_price
        J['price_rent'] = rent_price

        # get the product details
        D = []
        tag = bsoup.find(id="productDetailsTable")
        for item in tag.find_all("li"):
            # everything besides avg customer reviews and amazon best
            # sellers rank
            if str(item.b.string).strip() != "Average Customer Review:" \
               and str(item.b.string).strip() != "Amazon Best Sellers Rank:":
                if "Shipping Weight" in str(item.b.string).strip():
                    D.append(str(item.b.string).strip() + " " +
                             str(item.contents[1]).strip().replace("(", ""))
                else:
                    if str(item.b.string).strip() not in D:
                        D.append(str(item.b.string).strip() + " " +
                                 str(item.contents[1]).strip())
            # average customer review
            elif str(item.b.string).strip() == "Average Customer Review:":
                # get number of stars
                reg = re.compile("([0-9]|\.)* out of 5 stars")
                reg = reg.search(str(item))
                if str(type(reg)) != "<class 'NoneType'>":
                    D.append(reg.group())
                # get number of reviews
                reg = re.compile("([0-9]|,)* customer reviews")
                reg = reg.search(str(item))
                if str(type(reg)) != "<class 'NoneType'>":
                    D.append(reg.group())
            # amazon best sellers rank
            else:
                reg = re.compile("#([0-9]|,)*")
                reg = reg.search(str(item))
                if str(type(reg)) != "<class 'NoneType'>":
                    D.append(reg.group() + "in Books")
                for thing in item.find_all("a"):
                    if thing.string not in D and thing.string != "Books":
                        if thing.string != "See Top 100 in Books":
                            D.append(thing.string)
        J['details'] = D

        # get the most helpful customer reviews
        # TESTING
        f = open("out.txt", "w", encoding="utf-8")

        R = []
        for tag in bsoup.find_all(id=re.compile
                                  ("revData-dpReviewsMostHelpful")):
            item = tag.find_all("div")
            to_search = str(item[len(item)-1])
            to_search = remove_html_tags(str(to_search))
            R.append(str(to_search))
            f.write(str(to_search))
            f.write("\n")
        # method 2
        if len(R) == 0:
            for tag in bsoup.find_all(class_="mt9 reviewText"):
                f.write(str(tag.contents[1]))
                item = remove_html_tags(str(tag.contents[1]))
                R.append(item)
        J['reviews'] = R

        # TESTING
        JSO = json.dumps(J)
        # JSO = json.loads(JSO)
        f.write(str(JSO))

        # TESTING
        f.close()

        return JSO

    def parse_file(self):
        S = []
        f = open("html.txt", "w", encoding="utf-8")
        f3 = open('temp.txt', 'w', encoding='utf-8')
        f2 = open("out.txt", "w", encoding="utf-8")
        # loop through the directory (need to eliminate leading /)
        for fn in os.listdir(os.path.join(os.getcwd(), self.filename)):
            if os.path.isfile(os.path.join(os.getcwd(), self.filename, fn)):
                # convert file to soup
                test = os.path.join(os.getcwd(), self.filename, fn)
                bsoup = BeautifulSoup(open(test))

                # TESTING
                f.write(bsoup.prettify())

                # TESTING
                f3.write(bsoup.prettify())

                # create JSON object
                J = dict()

                # get the name of the book
                name = ""
                count = 0
                for tag in bsoup.find(id="fbt_x_title"):
                    if count != 0:
                        name += tag.string
                    count += 1
                    if count == 2:
                        break
                J['title'] = name.strip()

                # get the author of the book
                A = []
                # method 1
                tag = bsoup.find(class_="parseasinTitle")
                if str(type(tag)) != "<class 'NoneType'>":
                    tag = tag.find_parent("div")
                    for item in tag.find_all("a"):
                        author = item.string
                        if str(type(author)) != "<class 'NoneType'>":
                            if "Visit" not in author:
                                if "search" not in author:
                                    if "about" not in author:
                                        A.append(author)
                # method 2
                else:
                    for tag in bsoup.find_all(class_="author notFaded"):
                        first = tag.a.string
                        if "Visit" in first or str(type(first)) == \
                           "<class 'NoneType'>":
                            temp = tag.find("span")
                            author = temp.contents[0].strip()
                            A.append(author)
                        else:
                            author = first
                            A.append(author)
                J['authors'] = A

                # get the new price
                new_price = "-1"
                tag = bsoup.find(id="buyNewSection")
                reg = re.compile("\$[0-9]*\.[0-9]*")
                reg = reg.search(str(tag))
                if str(type(reg)) != "<class 'NoneType'>":
                    new_price = reg.group()
                new_price = float(new_price.replace("$", ""))

                # get the rental price
                rent_price = "-1"
                tag = bsoup.find(id="rentBuySection")
                reg = re.compile("\$[0-9]*\.[0-9]*")
                reg = reg.search(str(tag))
                if str(type(reg)) != "<class 'NoneType'>":
                    rent_price = reg.group()
                rent_price = float(rent_price.replace("$", ""))

                # try something else if price is still
                counter = 0
                if new_price == -1:
                    for tag in bsoup.find_all(class_="rentPrice"):
                        counter += 1
                        if str(type(tag.contents)) != "<class 'NoneType'>":
                            if counter == 1:
                                new_price = tag.contents[0].strip()
                                new_price = float(new_price.replace("$", ""))
                            elif counter == 2:
                                rent_price = tag.contents[0].strip()
                                rent_price = float(rent_price.replace("$", ""))

                # put prices in
                J['price_new'] = new_price
                J['price_rent'] = rent_price

                # get the product details
                D = []
                tag = bsoup.find(id="productDetailsTable")
                for item in tag.find_all("li"):
                    # everything besides avg customer reviews and
                    # amazon best sellers rank
                    if str(item.b.string).strip() != \
                       "Average Customer Review:" and str(item.b.string).\
                       strip() != "Amazon Best Sellers Rank:":
                        if "Shipping Weight" in str(item.b.string).strip():
                            D.append(str(item.b.string).strip() + " " +
                                     str(item.contents[1]).strip().
                                     replace("(", ""))
                        else:
                            if str(item.b.string).strip() not in D:
                                D.append(str(item.b.string).strip() + " " +
                                         str(item.contents[1]).strip())
                    # average customer review
                    # No matter how I try to break up the following line,
                    # pep8 gives me an "E127 Continuation line
                    # over-indented for visual indent"
                    elif str(item.b.string).strip() == "Average Customer Review:":
                        #get number of stars
                        reg = re.compile("([0-9]|\.)* out of 5 stars")
                        reg = reg.search(str(item))
                        if str(type(reg)) != "<class 'NoneType'>":
                            D.append(reg.group())
                        #get number of reviews
                        reg = re.compile("([0-9]|,)* customer reviews")
                        reg = reg.search(str(item))
                        if str(type(reg)) != "<class 'NoneType'>":
                            D.append(reg.group())
                    # amazon best sellers rank
                    else:
                        reg = re.compile("#([0-9]|,)*")
                        reg = reg.search(str(item))
                        if str(type(reg)) != "<class 'NoneType'>":
                            D.append(reg.group() + "in Books")
                        for thing in item.find_all("a"):
                            if thing.string not in D and thing.string != \
                               "Books":
                                if thing.string != "See Top 100 in Books":
                                    D.append(thing.string)
                J['details'] = D

                # get the most helpful customer reviews
                R = []
                for tag in bsoup.find_all(id=re.compile
                                          ("revData-dpReviewsMostHelpful")):
                    item = tag.find_all("div")
                    to_search = str(item[len(item)-1])
                    to_search = remove_html_tags(str(to_search))
                    R.append(str(to_search))
                    f.write(str(to_search))
                    f.write("\n")
                # method 2
                if len(R) == 0:
                    for tag in bsoup.find_all(class_="mt9 reviewText"):
                        f.write(str(tag.contents[1]))
                        item = remove_html_tags(str(tag.contents[1]))
                        R.append(item)
                J['reviews'] = R

                # TESTING
                JSO = json.dumps(J)
                # JSO = json.loads(JSO)
                S.append(JSO)
                f2.write(str(JSO))
                f2.write("\n\n\n\n")

        # TESTING
        f.close()
        f3.close()
        f2.close()

        return S


def remove_html_tags(data):
    p = re.compile("<.*?>")
    return p.sub('', data)


def parse_command_line():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", type=str,
                       help="directory containing html files to parse")
    group.add_argument("-u", type=str,
                       help="url for specified web page")
    parser.add_argument("-o", choices=["html", "xml", "csv"],
                        help="output format")
    return parser.parse_args()


class TableHandler(object):
    # Produce Table header
    def header(self, hdata):
        pass

    # Produce single row of output
    def row(self, rdata, hdata):
        pass


class HTMLTableHandler(TableHandler):
    def header(self, hdata):
        print("<!DOCTYPE HTML>\n<html>\n<head>")
        print("<title>Amazon Book Results</title>\n</head>")
        print("<body>")
        print("<table border=\"1\" style=\"300px\">")
        print("\t<tr>")
        for h in hdata:
            try:
                print("\t\t<th>{0}</th>".format(h))
            except UnicodeEncodeError as u:
                print("***encoding error***", end='')
        print("\t</tr>")

    def row(self, rdata, hdata):
        print("\t<tr>")
        for r in rdata:
            try:
                print("\t\t<td>{0}</td>".format(str(r).strip()))
            except UnicodeEncodeError as u:
                print("***encoding error***", end='')
        print("\t</tr>")
        print("</table>\n</body>\n</html>")


class XMLTableHandler(TableHandler):
    def header(self, hdata):
        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        print("<Amazon>")

    def row(self, rdata, hdata):
        print("\t<Book>")
        for i in range(0, len(rdata)):
            try:
                print("\t\t<{0}>{1}</{0}>".format(
                    hdata[i], str(rdata[i]).strip().replace("&", "&amp;")))
            except UnicodeEncodeError as u:
                print("***encoding error***", end='')
        print("\t</Book>")
        print("</Amazon>")


class CSVTableHandler(TableHandler):
    def header(self, hdata):
        #TESTING
        f = open("csv.txt", "w", encoding="utf-8")
        for i in range(0, len(hdata)):
            if i == len(hdata) - 1:
                try:
                    print(hdata[i], end='')
                except UnicodeEncodeError as u:
                    print("***encoding error***", end='')
            else:
                try:
                    print("{0}, ".format(hdata[i]), end='')
                except UnicodeEncodeError as u:
                    print("***encoding error***, ", end='')
        print()
        f.close()

    def row(self, rdata, hdata):
        for i in range(0, len(rdata)):
            if i == len(rdata) - 1:
                try:
                    print(str(rdata[i]).strip(), end='')
                except UnicodeEncodeError as u:
                    print("***encoding error***", end='')
            else:
                try:
                    print("{0}, ".format(str(rdata[i]).strip()), end='')
                except UnicodeEncodeError as u:
                    print("***encoding error***, ", end='')
        print()


class MoviePrinter(object):
    def __init__(self, handler):
        self.handler = handler

    def print_movie_table(self, J):
        # print header
        L = []
        B = []
        for key in J:
            if str(type(J[key])) == "<class 'list'>":
                for k in J[key]:
                    if key == "details":
                        if ":" in k:
                            L.append(k.split(":")[0])
                            B.append(k.split(":")[1].strip())
                        else:
                            L.append("details")
                            B.append(k)
                    elif key == "reviews":
                        for i in J[key]:
                            L.append(key)
                            B.append(i)
                        break
                    elif key == "authors":
                        for i in J[key]:
                            L.append(key)
                            B.append(i)
                        break
            else:
                L.append(key)
                B.append(J[key])
        self.handler.header(L)

        # print movie data
        self.handler.row(B, L)

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
    SQLAlchemy_Logging = False
    if args.d:
        JSON_book = obj.parse_file()
        for x in JSON_book:
            result = persist(x, SQLAlchemy_Logging)
    elif args.u:
        JSON_book = obj.parse_url()
        result = persist(JSON_book, SQLAlchemy_Logging)

    #turn into JSON object
    if args.u:
        JSON_book = json.loads(JSON_book)

    #produce output of desired type
    if output_type == "csv":
        handler = CSVTableHandler()
    elif output_type == "html":
        handler = HTMLTableHandler()
    elif output_type == "xml":
        handler = XMLTableHandler()
    else:
        handler = output_type

    printer = MoviePrinter(handler)
    if args.d:
        for x in JSON_book:
            if handler != "no_output":
                printer.print_movie_table(json.loads(x))
    else:
        if handler != "no_output":
            printer.print_movie_table(JSON_book)
