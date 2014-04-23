"""
    imdb_ratings.py
    April 9, 2014
    Python Programming - CIS 5930 - Spring 2014
    IMDB Assignment

    Team:
    Alex Fehr and Doug Wussler

    This module provides a class for parsing and filtering the IMDB
    by year, votes and rank, and then the ability to query
    the filtered data for specific titles.
"""

import re
import sys


class TableHandler(object):
    # Produce Table header
    def header(self, hdata):
        pass

    # Produce single row of output
    def row(self, rdata):
        pass


class TextTableHandler(TableHandler):
    def header(self, hdata):
        for h in hdata:
            print("{0:>10s}".format(h), end='')
        print("\n" + "-" * 79)

    def row(self, rdata):
        for r in rdata:
            print("{0!s:>10s}".format(r), end='')
        print()


class HTMLTableHandler(TableHandler):
    def header(self, hdata):
        print("<!DOCTYPE HTML>\n<html>\n<head>")
        print("<title>IMDB Movie Resutls</title>\n</head>")
        print("<body>")
        print("<table border=\"1\" style=\"300px\">")
        print("\t<tr>")
        for h in hdata:
            print("\t\t<th>{0}</th>".format(h))
        print("\t</tr>")

    def row(self, rdata):
        print("\t<tr>")
        for r in rdata:
            print("\t\t<td>{0}</td>".format(str(r).strip()))
        print("\t</tr>")


class XMLTableHandler(TableHandler):
    def header(self, hdata):
        print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        print("<IMDB>")

    def row(self, rdata):
        L = ["Votes", "Rating", "Year", "Title"]
        print("\t<Movie>")
        for i in range(0, len(rdata)):
            print("\t\t<{0}>{1}</{0}>".format(
                L[i], str(rdata[i]).strip().replace("&", "&amp;")))
        print("\t</Movie>")


class CSVTableHandler(TableHandler):
    def header(self, hdata):
        for i in range(0, len(hdata)):
            if i == len(hdata) - 1:
                print(hdata[i], end='')
            else:
                print("{0}, ".format(hdata[i]), end='')
        print()

    def row(self, rdata):
        for i in range(0, len(rdata)):
            if i == len(rdata) - 1:
                print(str(rdata[i]).strip(), end='')
            else:
                print("{0}, ".format(str(rdata[i]).strip()), end='')
        print()


class MoviePrinter(object):
    def __init__(self, handler):
        self.handler = handler

    def print_movie_table(self, mlist):
        # print header
        self.handler.header(["Votes", "Rating", "Year", "Title"])

        # print movie data
        for m in mlist:
            try:
                self.handler.row([m[2], m[3], m[1], "     " + m[0]])
            except UnicodeEncodeError as u:
                print("     *** encoding error ***")


class GroupMovieByElements():

    """
    This class parses an exported instance of the IMDB.  It filters on
    the arguments passed in at instantiation.  The default filters are:

        Year  =   2010
        Votes >  1,000
        Rank  >=   8.0

    For each film that passes the filter, the title, year, votes
    and rank are captured.  Duplicate film titles for the same year
    are removed.  If the duplicates had a conflict in rank, the higher
    rank is preserved.

    The list of films is then sorted by title and printed in this format:

    Rank     Votes  Title

    The film titles can then be queried for matching strings.

    """

    def __init__(self, year=2010, votes=1000, rank=8.0, title=None):
        """
        The IMDB will be filtered according to the keyword
        arguments passed to this function.  Thus, this object works
        with at most one year's worth of films at a time.

        Duplicates are removed and the films are printed in
        alphabetical order by title.

        """
        self.__movie_file = "ratings.list"
        self.__title = title
        self.__year = year
        self.__votes = votes
        self.__rank = rank
        self.__movies = []
        self.__parse_movies()

        # Eliminate duplicates but preserve the higher ranking
        self.__movies.sort(key=lambda s: s[3], reverse=True)
        self.__movie_set = set()
        titles = set()
        for m in self.__movies:
            if m[0] not in titles:
                titles.add(m[0])
                self.__movie_set.add(m)

        # Now sort
        self.__movies = list(self.__movie_set)
        self.__movies.sort(key=lambda s: s[0].strip('"').lower())

    """  Getter methods """
    @property
    def title(self):
        return self.__title

    @property
    def year(self):
        return self.__year

    @property
    def votes(self):
        return self.__votes

    @property
    def rank(self):
        return self.__rank

    @property
    def movies(self):
        return self.__movies

    def __parse_movies(self):
        """
        This function captures and filters data from the IMDB and
        returns a list of films.

        """
        regex = re.compile(r" {6}[.0-9]{10} +"        # Don't care
                           r"(?P<v>[0-9]+)"           # Votes
                           r"   (?P<r>[0-9].[0-9])"   # Rank
                           r" +(?P<t>.*) "            # Title
                           r"\((?P<y>[0-9]{4})\) *"   # Year
                           r"(\{(?P<e>.*)\(.*\)\})?"  # Optional Episode
                           )
        imdb = open(self.__movie_file, "r")
        for m in imdb.readlines():
            movie = regex.search(m)
            if movie and int(movie.group("y")) == self.__year and \
               int(movie.group("v")) > self.__votes and \
               float(movie.group("r")) >= self.__rank:
                if movie.group("e"):
                    title = movie.group("t") + " - " + movie.group("e")
                else:
                    title = movie.group("t")
                self.__movies.append((title,
                                      int(movie.group("y")),
                                      int(movie.group("v")),
                                      float(movie.group("r")))
                                     )
        imdb.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        style = "text"
    else:
        style = sys.argv[1].lower()

    if style == "text":
        handler = TextTableHandler()
    elif style == "csv":
        handler = CSVTableHandler()
    elif style == "html":
        handler = HTMLTableHandler()
    elif style == "xml":
        handler = XMLTableHandler()
    else:
        print("\nError: invalid print format:", sys.argv[1])
        print("Supported print formats: text, html, xml, csv")
        exit(1)

    m = GroupMovieByElements()
    printer = MoviePrinter(handler)
    printer.print_movie_table(m.movies)

    if style == "html":
        print("</table>\n</body>\n</html>")
    elif style == "xml":
            print("</IMDB>")
