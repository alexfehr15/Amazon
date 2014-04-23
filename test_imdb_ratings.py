"""
    test_imdb_ratings.py
    April 9, 2014
    Python Programming - CIS 5930 - Spring 2014
    IMDB Assignment

    Team:
    Alex Fehr and Doug Wussler

    Run tests for imdb_ratings
"""

import unittest
import imdb_ratings


class TestSequenceFunctions(unittest.TestCase):
    """Run tests for imbd_ratings"""

    def setUp(self):
        self.mlist = imdb_ratings. \
            GroupMovieByElements(year=2013, votes=15000, rank=9.7)

    def tearDown(self):
        pass

    def test_movie_meets_condition(self):
        """Test if a movie meets the given condition"""
        tmovie = ("Grand Theft Auto V", 2013, 15425, 9.8)
        mmovie = (self.mlist).movies[0]
        self.assertEqual(tmovie, mmovie)

    def test_movie_not_meet_condition(self):
        """Test if a movie does not meet the given condition"""
        tmovie = ("12 Years a Slave", 2013, 155029, 8.3)
        mmovie = self.mlist.movies
        assert tmovie not in mmovie

    def test_title_accessor(self):
        """Test if a movie's title returns the correct type and data"""
        self.assertEqual(self.mlist.title, None)

    def test_year_accessor(self):
        """Test if a movie's year returns the correct type and data"""
        self.assertEqual(self.mlist.year, 2013)

    def test_votes_accessor(self):
        """Test if a movie's votes returns the correct type and data"""
        self.assertEqual(self.mlist.votes, 15000)

    def test_rank_accessor(self):
        """Test if a movie's rank returns the correct type and data"""
        self.assertEqual(self.mlist.rank, 9.7)

if __name__ == '__main__':
    unittest.main()
