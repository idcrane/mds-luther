import bomojo
import wikiscraper

import pickle
import dateutil.parser
import random
import urllib2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
from bs4 import BeautifulSoup


class ProjectLutherScraper(bomojo.BOMMassScrape):

    data_dir = '/Users/ian/metis/mds-luther/movies/data'
    url_list_filename = os.path.join(data_dir, 'all_movie_urls.pkl')
    movie_dict_filename = os.path.join(data_dir, 'all_movie_data.pkl')
    problem_movie_list_filename = os.path.join(data_dir, 'prob_movie_list.pkl')
    nationality_dict_filename = os.path.join(data_dir, 'nationality_dict.pkl')

    url_list = []
    movie_dict = {}
    problem_movie_urls = []
    wiki_dict = {}

    def get_data(self, forcescrape=False):
        self.url_list_data(forcescrape)
        self.movie_dict_data(forcescrape)
        self.wiki_dict_data(forcescrape)

    def dump_url_list(self):
        pickle.dump(self.url_list, open(self.url_list_filename, 'w'))

    def dump_movie_dict(self):
        pickle.dump(self.movie_dict, open(self.movie_dict_filename, 'w'))
        pickle.dump(self.problem_movie_urls, open(
                                    self.problem_movie_list_filename, 'w'))

    def dump_wiki_dict(self):
        pickle.dump(self.wiki_dict, open(self.nationality_dict_filename, 'w'))

    def url_list_data(self, scrape):
        if scrape == False:
            try:
                with open(self.url_list_filename, 'rb') as infile:
                        self.url_list = pickle.load(infile)
            except IOError:
                print "WARNING: Movie URL file does not exist"
                scrape = True
        if scrape == True:
            self.url_list = self.build_list_of_all_movies()

    def movie_dict_data(self, scrape):
        if scrape == False:
            try:
                with open(self.movie_dict_filename, 'rb') as infile:
                        self.movie_dict = pickle.load(infile)
            except IOError:
                 print "WARNING: Movie dict file does not exist"
                 scrape = True
            try:
                with open(self.problem_movie_list_filename, 'rb') as infile:
                        self.problem_movie_urls = pickle.load(infile)
            except IOError:
                print "WARNING: No problem movie file"
        if scrape == True:
            self.movie_dict, self.problem_movie_urls = self.get_movie_dicts_from_URL_list_page(self.url_list)

    def wiki_dict_data(self, scrape):
        if scrape == False:
            try:
                with open(self.nationality_dict_filename, 'rb') as infile:
                        self.wiki_dict = pickle.load(infile)
            except IOError:
                print "WARNING: Wiki dict file does not exist"
                scrape = True
        if scrape == True:
            wiki = wikiscraper.WikiScraper()
            self.wiki_dict = self.wiki_dict = wiki.actor_to_country()


    def add_actor_info(self):
        for movie in self.movie_dict:
            movie['China actors'] = 0
            movie['Hong Kong actors'] = 0
            movie['Japan actors'] = 0
            movie['South Korea actors'] = 0
            movie['Taiwan actors'] = 0

            if 'actors' in movie.keys():
                for actor in movie['actors']:
                    actor = actor.replace('*', '')
                    if actor in self.wiki_dict.keys():
                        #print actor
                        country = self.wiki_dict[actor]
                        keystring = country + ' actors'
                        #print keystring
                        movie[keystring] = movie[keystring] + 1

