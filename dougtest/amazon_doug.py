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
    #TESTING (changed print below to f.write to avoid encoding issue)
    #also changed all commas to plus below so that would run write
    """
    f = open("persist_test.txt", "w", encoding="utf-8")
    if view:
        for b in session.query(Books).options(joinedload(Books.authors)).all():
            f.write(b.title + b.price_new + b.price_rent + "\n" +
                  (", ").join([str(a.name) for a in b.authors]) + "\n")
            for x in b.details:
                f.write(("\n").join(str(x)) + "\n")
                  #("\n").join(b.details.split("~!^\n")) + "\n" +
            f.write(("\n\n").join([r.review for r in b.reviews]))
    session.close()
    #TESTING
    f.close()
    """
    return True  # This serves no purpose at the moment


class Amazon():
    def __init__(self, url="someURL", file="someFile"):
        self.__url = url
        self.__file = file

    @property
    def url(self):
        return self.__url

    @property
    def file(self):
        return self.__file

    @property
    def name(self):
        return self.__name

    @property
    def authors(self):
        return self.__authors

    @property
    def price(self):
        return self.__price

    @property
    def details(self):
        return self.__details

    @property
    def reviews(self):
        return self.__reviews

    @url.setter
    def url(self, url):
        self.__url = url

    @file.setter
    def file(self, file):
        self.__file = file

    @name.setter
    def name(self, name):
        self.__name = name

    @authors.setter
    def authors(self, authors):
        self.__authors = authors

    @price.setter
    def price(self, price):
        self.__price = price

    @details.setter
    def details(self, details):
        self.__details = details

    @reviews.setter
    def reviews(self, reviews):
        self.__reviews = reviews

    def parse_file(self):
        pass

    def parse_url(self):
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
        for tag in bsoup.find_all(class_="author notFaded"):
            author = tag.a.string
            A.append(author)
            print(tag.a.string)
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
        J['price_rent'] = rent_price

        #get the product details
        D = []
        tag = bsoup.find(id="productDetailsTable")
        for item in tag.find_all("li"):
            # everything besides avg customer reviews and amazon best
            # sellers rank
            if str(item.b.string).strip() != "Average Customer Review:" \
            and str(item.b.string).strip() != "Amazon Best Sellers Rank:":
                D.append(str(item.b.string).strip() + " " +
                         str(item.contents[1]).strip())
                print(str(item.b.string).strip() + " " +
                      str(item.contents[1]).strip())
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
        for tag in bsoup.find_all(id=re.compile
                                  ("revData-dpReviewsMostHelpful")):
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


def remove_html_tags(data):
    p = re.compile("<.*?>")
    return p.sub('', data)


def parse_command_line():
    """
    Parses the command line arguments and returns them
    """

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", type=str,
                       help="directory containing html files to parse")
    group.add_argument("-u", type=str,
                       help="url for specified web page")
    parser.add_argument("-o", choices=["html", "xml", "csv"],
                        help="output format")
    return parser.parse_args()


if __name__ == "__main__":
    #parse command line arguments
    args = parse_command_line()

    #create Amazon object with file or url
    if args.d:
        obj = Amazon(file=args.d)
    elif args.u:
        obj = Amazon(url=args.u)

    #get what the output type is
    if args.o:
        output_type = args.o
    else:
        output_type = "no_output"

    #call parsing function and storing json object
    if args.d:
        pass
    elif args.u:
        JSON_book = obj.parse_url()
    result = persist(JSON_book, True)
