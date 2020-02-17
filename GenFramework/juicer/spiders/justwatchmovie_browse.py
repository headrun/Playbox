import ast
#import MySQLdb
#from scrapy.xlib.pydispatch import dispatcher
from pydispatch import dispatcher
import datetime
from juicer.utils import *
from scrapy import signals
from scrapy.selector import Selector
from scrapy.http import Request
#from datetime import datetime
import requests
import json
import scrapy
HEADER = {
    'User-Agent': 'JustWatch Python client (github.com/dawoudt/JustWatchAPI)'}
requests = requests.Session()
null = None


class Justwatch_browse(JuicerSpider):
    name = 'justwatch_movie_browse'
    start_urls = ['https://apis.justwatch.com/content/providers/locale/en_US',
                  'https://apis.justwatch.com/content/genres/locale/en_US', 'https://apis.justwatch.com/content/age_certifications?country=US']

    def __init__(self, *args, **kwargs):
        super(Justwatch_browse, self).__init__(*args, **kwargs)
        self.crawl_type = kwargs.get('crawl_type', 'keepup')
        self.from_year = kwargs.get('from', '')
        self.to_year = kwargs.get('to', '')
        self.provider_list, self.genres_list, self.age_list = [], [], []

    def parse(self, response):
        sel = Selector(response)
        json_data = json.loads(response.body)
        #year_list = ['1900', '2020']
        data = json_data
        self.genres_list.append('null')
        for dat in data:
            if 'providers' in response.url:
                provider_name = dat.get('short_name', '')
                self.provider_list.append(provider_name)
            elif 'genres' in response.url:
                genre_name = dat.get('short_name', '')
                self.genres_list.append(genre_name)
                # self.genres_list.append('null')
            elif 'age_certifications' in response.url:
                age_cer_name = dat.get('technical_name', '')
                self.age_list.append(age_cer_name)
        if len(self.provider_list) != [] and len(self.genres_list) != [] and len(self.age_list) != []:
            now = datetime.datetime.now()
            current_year = now.year
            if self.crawl_type == "catchup":
                if self.from_year and self.to_year:
                    years_list = range(int(self.from_year),  int(self.to_year))
                elif self.from_year:
                    years_list = range(int(self.from_year),  current_year)
                else:
                    years_list = range(1900,  current_year)
                #years_list = range(1900, 2001)
                #years_list = range(2011, 2019)
                self.get_sks_from_api(years_list)
            if self.crawl_type == "keepup":

                years_list = [current_year]
                self.get_sks_from_api(years_list)

    def get_sks_from_api(self, years_list):
        for provider in self.provider_list:
            pro = provider
            payload = ''
            for year in years_list:

                for genr in self.genres_list:
                    if genr == "null":
                        payload = '{"age_certifications":null,"content_types":["movie"],"genres":null,"languages":null,"max_price":null,"min_price":null,"monetization_types":null,"page":0,"page_size":1000,"presentation_types":null,"providers":["%s"],"release_year_from":%s,"release_year_until":%s,"scoring_filter_types":null,"timeline_type":null}' % (str(pro), year, year)
                    else:
                        payload = '{"age_certifications":null,"content_types":["movie"],"genres":["%s"],"languages":null,"max_price":null,"min_price":null,"monetization_types":null,"page":0,"page_size":1000,"presentation_types":null,"providers":["%s"],"release_year_from":%s,"release_year_until":%s,"scoring_filter_types":null,"timeline_type":null}' % (genr, str(pro), year, year)
                    #api_url = 'https://api.justwatch.com/titles/en_US/popular'
                    api_url = 'https://api.justwatch.com/content/titles/en_US/popular'
                    r = requests.post(api_url, data=payload, headers=HEADER)
                    data = r.text
                    self.another(data)
                for age in self.age_list:
                    payload = '{"age_certifications":["%s"],"content_types":["movie"],"genres":null,"languages":null,"max_price":null,"min_price":null,"monetization_types":null,"page":0,"page_size":1000,"presentation_types":null,"providers":["%s"],"release_year_from":%s,"release_year_until":%s,"scoring_filter_types":null,"timeline_type":null}' % (str(age), str(pro), year, year)
                    api_url = 'https://api.justwatch.com/content/titles/en_US/popular'

                    resp = requests.post(api_url, data=payload, headers=HEADER)
                    dat = resp.text
                    self.another(dat)

    def another(self, data):
        try:
            movies_info = json.loads(data)
            _data = movies_info['items']
            for data in _data:
                ids = data.get('id', '')
                title = data.get('title')
                url = data.get('full_path', '')
                if not ids:
                    continue
                full_path = 'https://www.justwatch.com' + str(url)
                api_url = 'https://apis.justwatch.com/content/titles/movie/%s/locale/en_US' % ids
                self.get_page('justwatch_movies_terminal', api_url,
                              ids, meta_data={'movie_url': full_path})
        except:
            pass
