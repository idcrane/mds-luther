import urllib2
import re
import string
import bomojo
import scraper
from bs4 import BeautifulSoup

class BOMMassScrape(bomojo.BOMojoScraper):

    def build_list_of_recent_movies(self, startingyear=2010, endingyear=2014)
        recent_movie_urls = []
        years = range(startingyear, endingyear + 1)
        for year in years:
            year = str(year)
            oneurl = self.base_url + 'yearly/chart/?page=1&view=releasedate&view2=domestic&yr=' + year + '&p=.htm'
            try:
                print oneurl
                one_page_movie_list = self.get_single_page_movie_urls(oneurl)
                for movie in one_page_movie_list:
                    recent_movie_urls.append(movie)
            except HTTPError:
                print 'Failure opening %s' % oneurl
                break
        return recent_movie_urls

    def build_list_of_all_movies(self):
        all_movie_urls = []
        for letter in string.ascii_uppercase:
            valid_num = True
            n = 1

            while valid_num:
                n = str(n)
                oneurl = ms.base_url + 'movies/alphabetical.htm?letter=' + letter + '&page=' + n + '&p=1.htm'
                try:
                    print oneurl
                    one_page_movie_list = self.get_single_page_movie_urls(oneurl)
                    if len(one_page_movie_list) == 0:
                        break
                    for movie in one_page_movie_list:
                        all_movie_urls.append(movie)
                    n = int(n) + 1
                except HTTPError:
                    print 'Failure opening %s' % oneurl
                    break

    def clean_movie_url_lists(self, alist):
        list = list(set(alist))
        return list

    def get_movie_dicts_from_URL_list_page(self, url):
        grand_movie_list = []
        problem_movie_list = []
        movie_urls = self.get_single_page_movie_urls(url)
        for num, movie_url in enumerate(movie_urls):
            print movie_url
            try:
                movie_info = self.parse_full_mojo_page(movie_url)
                grand_movie_list.append(movie_info)
                print "Parsed", movie_info['movie_title']
            except (AttributeError, TypeError):
                problem_movie_list.append(movie_url)
        return grand_movie_list, problem_movie_list


    def get_single_page_movie_urls(self, url):
        soup = self.connect(url)
        obj = soup.find_all('a', href=re.compile('/movies/\?id='))


        movie_urls = []
        for movie in obj:
            if '#1 Movie' not in movie.text:
                full_url = self.base_url + movie['href']
                movie_urls.append(full_url)
        return movie_urls

