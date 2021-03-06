import scraper
import urllib2
import itertools
from bs4 import BeautifulSoup
from urllib2 import HTTPError


class WikiScraper(scraper.Scraper):

    base_url = 'https://en.wikipedia.org'
    category_string = '/wiki/Category:'
    east_asian_countries = ['China', 'Hong Kong', 'Japan', 'Macau', 'South Korea', 'Mongolia', 'Taiwan']

    nationality_category_pages = {
            'China': ['Chinese_film_actresses', 'Film_actresses_from_Anhui', 'Film_actresses_from_Beijing', 'Film_actresses_from_Chongqing', 'Film_actresses_from_Fujian', 'Film_actresses_from_Guangdong', 'Film_actresses_from_Guizhou', 'Film_actresses_from_Hebei', 'Film_actresses_from_Heilongjiang', 'Film_actresses_from_Henan', 'Film_actresses_from_Hubei', 'Film_actresses_from_Hunan', 'Film_actresses_from_Jiangsu', 'Film_actresses_from_Jilin', 'Film_actresses_from_Liaoning', 'Film_actresses_from_Shandong', 'Film_actresses_from_Shanghai', 'Film_actresses_from_Sichuan', 'Film_actresses_from_Zhejiang', 'Male_film_actors_from_Beijing', 'Chinese_male_film_actors', 'Male_film_actors_from_Chongqing', 'Male_film_actors_from_Fujia', 'Male_film_actors_from_Guangdong', 'Male_film_actors_from_Hebei', 'Male_film_actors_from_Heilongjiang', 'Male_film_actors_from_Henan', 'Male_film_actors_from_Liaoning', 'Male_film_actors_from_Shandong', 'Male_film_actors_from_Shanghai',
            'Male_film_actors_from_Zhejiang' ],
            'Hong Kong': ['Hong_Kong_film_actresses', 'Hong_Kong_male_film_actors'],
            'Japan': ['Japanese_male_film_actors', 'Japanese_film_actresses'],
            'Macau': [],
            'South Korea': ['South_Korean_film_actresses'],
            'Mongolia': ['Mongolian_actors'],
            'Taiwan': ['Taiwanese_male_film_actors', 'Taiwanese_film_actresses']}


    special_nationality_pages = {'China':[],
            'Hong Kong': ['data/hong_kong_female_2.html'],
            'Japan': ['data/japan_male_2.html', 'data/japan_female_2.html'],
            'Macau': [],
            'South Korea': ['data/south_korea_female_2.html'],
            'Mongolia':[],
            'Taiwan':[] }

    def actor_to_country(self):
        country_to_actor = self.build_lists_of_actor_nationalities()
        actor_to_country = {}
        for country in country_to_actor.keys():
            actor_to_single_country = {actor: country for actor in country_to_actor[country]}
            actor_to_country.update(actor_to_single_country)
        return actor_to_country

    def build_lists_of_actor_nationalities(self):
        actor_nationalities = {}
        for country in self.east_asian_countries:
            country_actor_list = []
            for category_stub in self.nationality_category_pages[country]:
                try:
                    url = self.base_url+self.category_string+category_stub
                    soup = self.connect(url)
                    country_actor_list.append(self.get_names_of_category_elements(soup))
                    if self.get_names_of_category_elements(soup) == []:
                        print 'No names gathered!!!!!!!!', url
                except HTTPError:
                    print 'HTTP Error for', url
            for htmlfile in self.special_nationality_pages[country]:
                with open(htmlfile, 'r') as infile:
                    soup = BeautifulSoup(infile)
                    country_actor_list.append(self.get_names_of_category_elements(soup))
            actor_nationalities[country] = list(set(list(itertools.chain.from_iterable(country_actor_list))))
        return actor_nationalities

    def get_names_of_category_elements(self, soup):
        xs = soup.find('a', id='Pages_in_category').find_parent().findNextSibling().findNextSibling().find_all('a')
        if len(xs) == 0:
            xs = soup.find('a', id='Pages_in_category').find_parent().findNextSibling().findNextSibling().findNextSibling().find_all('a')
        if len(xs) == 0:
            xs = soup.find('h3', text='A').find_parent().find_parent().find_all('a')
        element_list = [element.text.split('(')[0] for element in xs]
        return element_list

