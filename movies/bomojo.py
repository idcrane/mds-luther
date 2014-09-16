import sys
import re
import urllib2
import scraper
import dateutil.parser
import urlparse
import string
import numpy as np
from bs4 import BeautifulSoup
from urllib2 import HTTPError


class BOMojoScraper(scraper.Scraper):

    base_url = "http://www.boxofficemojo.com/"
    search_url = base_url + "search/?q=%s"
    east_asian_countries = ['China', 'Hong Kong', 'Japan', 'Macau', 'South Korea', 'Mongolia', 'Taiwan']

    def full_movie_dict_from_title(self,movie_name):
        return self.parse_full_mojo_page(self.get_full_page_url_from_title(movie_name))

    def get_full_page_url_from_title(self,movie_name):
        search_soup = self.search(movie_name)
        found_matches = search_soup.find(text=re.compile("Movie Matches"))
        if found_matches:
            matches_table = found_matches.parent.find_next_sibling("table")
            result_row = matches_table.find_all('tr')[1]
            full_page_url = urlparse.urljoin(self.base_url,result_row.find('a')['href'])

            return full_page_url

        # if we end up here without returning anything, we did not hit a match
        log_message = "[LOG: No match found for %s]" % movie_name
        print >> sys.stderr, log_message
        return -1

    def parse_full_mojo_page_foreign(self, full_page_url):
        try:
            soup_foreign = self.connect(self.get_foreign_info_URL(full_page_url))
            countries_dictionary = {}
            for country in self.east_asian_countries:
                country_line = soup_foreign.find(text=re.compile(country))
                if country_line != None:
                    country_release_date = country_line.find_parent('td').findNextSibling().findNextSibling()
                    country_gross_string = country_release_date.findNextSibling().findNextSibling().findNextSibling()
                    if country_release_date.text != '-':
                        date = dateutil.parser.parse(country_release_date.text)
                    else:
                        date = np.nan
                    try:
                        if country_gross_string.text == '-':
                            return np.nan
                        else:
                            if country_gross_string.text == 'Final':
                                country_gross_string = country_release_date.findNextSibling().findNextSibling()
                            gross = self.money_to_int(country_gross_string.text)
                    except ValueError:
                        return np.nan
                    country_dict = {country+'_release date': date, country+' total_gross': gross}
                    countries_dictionary.update(country_dict)
            return countries_dictionary
        except HTTPError:
            return {}


    def parse_full_mojo_page(self,full_page_url):
        try:
            soup = self.connect(full_page_url)


            release_date = self.to_date(
                self.get_movie_value(soup,'Release Date'))
            domestic_total_gross_string = self.get_movie_value(soup, 'Domestic Total Gross')
            try:
                domestic_total_gross = self.money_to_int(domestic_total_gross_string)
            except AttributeError:
                domestic_total_gross_string = self.deal_with_gross_total_problems(soup)
                domestic_total_gross = self.money_to_int(domestic_total_gross_string)

            runtime = self.runtime_to_minutes(self.get_movie_value(soup,'Runtime'))
            director = self.get_movie_value(soup,'Director')
            rating = self.get_movie_value(soup,'MPAA Rating')
            budget = self.budget_to_int(self.get_movie_value(soup, 'Production Budget'))
            actors = self.get_actors(soup)
            genre = self.get_genre(soup)

            movie_dict = {
                'movie_title':self.get_movie_title(soup),
                'release_date':release_date,
                'domestic_total_gross':domestic_total_gross,
                'runtime':runtime,
                'director':director,
                'rating':rating,
                'budget':budget,
                'actors':actors,
                'genre':genre
            }

            foreign_dict = self.parse_full_mojo_page_foreign(full_page_url)
            movie_dict.update(foreign_dict)

            return movie_dict
        except (HTTPError, UnicodeEncodeError):
            return {}

    def get_movie_value(self,soup,value_name):
        '''
        takes a string attribute of a movie on the page and
        returns the string in the next sibling object (the value for that attribute)
        '''
        obj = soup.find(text=re.compile(value_name))
        if obj == None:
            return None

        # this works for most of the values
        next_sibling = obj.findNextSibling()
        if next_sibling:
            return next_sibling.text

        # this next part works for the director
        elif obj.find_parent('td'):
            sibling_cell = obj.find_parent('tr').findNextSibling()
            if sibling_cell:
                return sibling_cell.text
                # # Code to put directors into lists
                # director_list = []
                # messy_director_list = sibling_cell.find_all(
                        # 'a', href=re.compile('/\?view=Director'))
                # for director in messy_director_list:
                    # director_list.append(director.text)
                # if director_list == []:
                    # director_list = None
                # return director_list

        # this works for movies with estimated totals
        else:
            return -1


    def get_foreign_info_URL(self, url):
        url = url.split('?')
        return url[0] + '?page=intl&' + url[1]


    def deal_with_gross_total_problems(self,soup):
        try:
            obj = soup.find(text-re.compile('Estimate'))
            obj = obj.split('(')[0]
            return obj
        except:
            obj = soup.find(text=re.compile('Domestic'))
            obj = obj.find_parent('font').findNextSibling().text
            obj = obj.split('(')[0]
            return obj

    def get_actors(self, soup):
        quoted = re.compile('>[A-Za-z ]+<')
        obj = str(soup.find('a', href=re.compile('/people/\?view=Actor')).find_parent('tr').findNextSibling())
        out = re.findall(quoted, obj)
        return [element.replace('>', '').replace('<', '') for element in out]

    def get_genre(self, soup):
        genre_string = soup.find(text=re.compile('Genre: ')).find_parent().text.split(': ')
        return genre_string[1]

    def get_movie_title(self,soup):
        title_tag = soup.find('title')
        movie_title = title_tag.text.split('(')[0].strip()
        return movie_title

    def to_date(self,datestring):
        return dateutil.parser.parse(datestring)

    def money_to_int(self,moneystring):
        return int(moneystring.replace('$','').replace(',',''))

    def runtime_to_minutes(self,runtimestring):
        if runtimestring == 'N/A':
            return np.nan
        rt = runtimestring.split(' ')
        return int(rt[0])*60 + int(rt[2])

    def budget_to_int(self, budgetstring):
        if budgetstring == 'N/A':
            return np.nan
        budgetstring = budgetstring.replace('$','').replace(',','').split(' ')
        if len(budgetstring) == 1:
            return float(budgetstring[0])
        else:
            budget = float(budgetstring[0])*int(self.mag_dict[budgetstring[1].lower()])
            return budget



class BOMMassScrape(BOMojoScraper):

    mag_dict = {'thousand': 1000, 'million': 1000000, 'billion': 1000000000}

    def build_list_of_recent_movies(self, startingyear=2014, endingyear=2014):
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
        return self.clean_movie_url_lists(recent_movie_urls)


    def build_list_of_all_movies(self):
        all_movie_urls = []

        for letter in ['NUM'] + list(string.ascii_uppercase):
            valid_num = True
            n = 1

            while valid_num:
                n = str(n)
                oneurl = self.base_url + 'movies/alphabetical.htm?letter=' + letter + '&page=' + n + '&p=1.htm'
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
        return self.clean_movie_url_lists(all_movie_urls)

    def clean_movie_url_lists(self, alist):
        alist = list(set(alist))
        return alist

    def get_movie_dicts_from_URL_list_page(self, urllist):
        grand_movie_list = []
        problem_movie_list = []
        for num, movie_url in enumerate(urllist):
            try:
                print "Parsing", movie_url
                movie_info = self.parse_full_mojo_page(movie_url)
                grand_movie_list.append(movie_info)
            except:  #(AttributeError, TypeError):
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

