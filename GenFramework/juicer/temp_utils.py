# Stdlib imports
import base64
import os
import re
import sys
import json
import time
import timeit
import codecs
import random
import string
import hashlib
import logging
import inspect
import MySQLdb
import datetime
import asyncore
import urllib.parse as urlparse
import traceback
import logging.handlers
#import tornado.httpclient as HT
from io import IOBase
from itertools import chain
from urllib.parse import urljoin
#from dateutil.parser import *
from collections import defaultdict
#from dateutil.relativedelta import *
from configparser import SafeConfigParser

# Scrapy related imports
from scrapy import signals
#from scrapy.conf import settings
from scrapy.spiders import Spider
from scrapy.selector import Selector
#from scrapy.xlib.pydispatch import dispatcher
from pydispatch import dispatcher
from scrapy.http import Request as ScrapyHTTPRequest, TextResponse

from juicer.scripts.robots_txt_checker import get_crawl_access
from juicer.scripts.crawl_table_queries import CRAWL_TABLE_SELECT_QUERY, CRAWL_TABLE_CREATE_QUERY
from juicer.scripts.crawl_table_queries import SECTIONS_TABLE_CREATE_QUERY
#from crawler_stats import CrawlerStats
#from vkc_schedule import VkcSchedule

BATCH_SIZE = 100
YIELD_SIZE = 500
LOAD_SIZE = 100
MYSQL_CONNECT_TIMEOUT_VALUE = 30
'''DB_HOST = settings['DB_HOST']
DB_UNAME = settings['DB_USERNAME']
DB_PASSWD = settings['DB_PASSWORD']
URLQ_DB_NAME = settings['URLQ_DATABASE_NAME']
LOGS_DIR = settings['LOGS_DIR']
PROXY_PATTERN = 'http://%s:%s'''
PROJECT_DIR = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
LOGS_DIR = '%s/logs/' % PROJECT_DIR
OUTPUT_DIR = os.path.join(os.getcwd(), 'OUTPUT')
JSON_FILES_DIR = os.path.join(OUTPUT_DIR, 'ott')
QUERY_FILES_DIR = os.path.join(OUTPUT_DIR, 'crawl_out')
QUERY_FILES_PROCESSING_DIR = os.path.join(OUTPUT_DIR, 'processing')
JSON_FILES_PROCESSED_DIR = os.path.join(OUTPUT_DIR, 'ott_processed')
REPORTS_DIR = "/home/veveo/reports/REPORTS"

class JuicerSpider(Spider):

    def __init__(self, name=None, **kwargs):
        #super(JuicerSpider, self).__init__(name, **kwargs)
        self.request_headers = {}
        self.provider_list = []
        self.allow_duplicate_urls = False
        self.is_ott = False
        self.limit = kwargs.get('limit', 0) or getattr(self.__class__, 'limit', 1000)
        self.finalprovider_dict = {}
        self.movie_items_list, self.tvshow_items_list, self.season_items_list, self.episode_items_list = [], [], [], []
        self.othermedia_items_list, self.related_items_list, self.richmedia_items_list, self.rating_items_list = [], [], [], []
        self.popularity_items_list, self.crew_items_list, self.programcrew_items_list, self.awards_items_list = [], [], [], []
        self.releases_items_list, self.news_items_list, self.chart_items_list, self.boxoffice_items_list = [], [], [], []
        self.reviews_items_list, self.theater_items_list, self.theateravailability_items_list, self.primetime_items_list = [], [], [], []
        self.programcharts_items_list, self.channels_items_list, self.channelcharts_items_list, self.schedules_items_list = [], [], [], []
        self.otherlinks_items_list, self.loactions_items_list, self.lineup_items_list, self.availability_items_list = [], [], [], []
        self.avail_json_items_list = []
        self.initialize_default_variables()
        self.name = None
        #dispatcher.connect(self._spider_closed, signals.spider_closed)
    
    def __del__(self):
        self.spider__closed()


    def initialize_default_variables(self):
        self._close_called = False
        self._sks = defaultdict(set)

        self.location_file = self.lineup_file = None
        self.source = self.json_file = self.crew_file = self.avail_file = None
        self.movie_file = self.season_file = self.tvshow_file = self.episode_file = None
        self.othermedia_file = self.prgm_crew_file = self.richmedia_file = self.rating_file = None
        self.popularity_file = self.related_programs_file = self.award_file = self.release_file = None
        self.news_file = self.charts_file = self.boxoffice_file = self.reviews_file = None
        self.theater_file = self.theateravailability_file = self.primetime_file = self.prgm_charts_file = None
        self.channel_file = self.channel_charts_file = self.schedule_file = self.otherlinks_file = None
        self.custom_query_file = self.created_file = None
        self.got_page_sks_len = 0
        self.crawl_vals_set = set()
        self.section_vals_set = set()

    def create_logger_obj(self):
        cur_dt = str(datetime.datetime.now().date())
        make_dir(LOGS_DIR)
        self.log_file_name = "spider_%s.log" % (cur_dt)
        self.log = initialize_logger(os.path.join(LOGS_DIR, self.log_file_name))

    def spider__closed(self):
        '''if spider.name != self.name: return
        if self.crawl_vals_set: self.insert_crawl_tables_data()
        if '_browse' not in self.name and len(self._sks) > 0:
            self.update_urlqueue_with_resp_status()

        if "terminal" in spider.name.lower() or self.crawl_type == 'catchup':
            self.crawler_stats.stats_ends(spider, reason, self.content_type)'''
        #writing into files if LOAD_SIZE < 100 items
        if self.movie_items_list: self.write_items_into_file(self.movie_items_list, self.get_movie_file(), 'movie')
        if self.tvshow_items_list: self.write_items_into_file(self.tvshow_items_list, self.get_tvshow_file(), 'tvshow')
        if self.season_items_list: self.write_items_into_file(self.season_items_list, self.get_season_file(), 'season')
        if self.episode_items_list: self.write_items_into_file(self.episode_items_list, self.get_episode_file(), 'episode')
        if self.othermedia_items_list: self.write_items_into_file(self.othermedia_items_list, self.get_othermedia_file(),  'othermedia')
        if self.related_items_list: self.write_items_into_file(self.related_items_list, self.get_related_programs_file(), 'relatedprogram')
        if self.richmedia_items_list: self.write_items_into_file(self.richmedia_items_list, self.get_richmedia_file(), 'richmedia')
        if self.rating_items_list: self.write_items_into_file(self.rating_items_list, self.get_rating_file(), 'rating')
        if self.popularity_items_list: self.write_items_into_file(self.popularity_items_list, self.get_pop_file(), 'popularity')
        if self.crew_items_list: self.write_items_into_file(self.crew_items_list, self.get_crew_file(), 'crew')
        if self.programcrew_items_list: self.write_items_into_file(self.programcrew_items_list, self.get_program_crew_file(), 'programcrew')
        if self.awards_items_list: self.write_items_into_file(self.awards_items_list, self.get_award_file(), 'awards')
        if self.releases_items_list: self.write_items_into_file(self.releases_items_list, self.get_release_file(), 'releases')
        if self.news_items_list: self.write_items_into_file(self.news_items_list, self.get_news_file(), 'news')
        if self.chart_items_list: self.write_items_into_file(self.chart_items_list, self.get_charts_file(), 'chart')
        if self.boxoffice_items_list: self.write_items_into_file(self.boxoffice_items_list, self.get_boxoffice_file(), 'boxoffice')
        if self.reviews_items_list: self.write_items_into_file(self.reviews_items_list, self.get_reviews_file(), 'reviews')
        if self.theater_items_list: self.write_items_into_file(self.theater_items_list, self.get_theater_file(), 'theater')
        if self.theateravailability_items_list: self.write_items_into_file(self.theateravailability_items_list, \
                                                                           self.get_theater_avail_file(), 'theateravailability')
        if self.primetime_items_list: self.write_items_into_file(self.primetime_items_list, self.get_primetime_file(), 'primetime')
        if self.programcharts_items_list: self.write_items_into_file(self.programcharts_items_list, self.get_program_charts_file(), 'programcharts')
        if self.channels_items_list: self.write_items_into_file(self.channels_items_list, self.get_channel_file(), 'channels')
        if self.channelcharts_items_list: self.write_items_into_file(self.channelcharts_items_list, self.get_channel_charts_file(), 'channelcharts')
        if self.schedules_items_list: self.write_items_into_file(self.schedules_items_list, self.get_schedule_file(),  'schedules')
        if self.otherlinks_items_list: self.write_items_into_file(self.otherlinks_items_list, self.get_otherlinks_file(), 'otherlinks')
        if self.loactions_items_list: self.write_items_into_file(self.loactions_items_list, self.get_location_file(), 'loaction')
        if self.lineup_items_list: self.write_items_into_file(self.lineup_items_list, self.get_lineup_file(), 'lineup')
        '''if self.availability_items_list:
            self.finalprovider_dict = self.provider_wiselist(self.availability_items_list)
            for pro in self.finalprovider_dict.keys():
                self.availability_items = self.finalprovider_dict[pro]

                self.write_items_into_file(self.availability_items, self.get_provider_avail_file(pro), 'availability')
                #self.close_all_opened_files()
                self.close_move_avail_file()
        if self.avail_json_items_list:
            self.finalprovider_dict = self.provider_wiselist(self.avail_json_items_list)
            for pro in self.finalprovider_dict.keys():
                self.json_availability_items = self.finalprovider_dict[pro]
                self.write_json_items_into_file(self.json_availability_items, self.get_provider_json_file(pro), 'avail_json')
                #self.close_all_opened_files()
                #self.close_move_avail_file()
                self.close_move_json_file()'''
        if self.availability_items_list: 
            self.write_items_into_file(self.availability_items_list, self.get_avail_file(), 'availability')
        if self.avail_json_items_list: self.write_json_items_into_file(self.avail_json_items_list, self.get_json_file(), 'avail_json')
        self.close_all_opened_files()
        #self.close_all_opened_query_files()

        #self.close_conn()
        self.initialize_default_variables()
        #remove_logger_handler(self.log, os.path.join(LOGS_DIR, self.log_file_name))

    def provider_wiselist(self,availability_items_list):
        try: 
            for pro in self.provider_list:
                all_list = [] 
                for rec in availability_items_list:
                    #rec_match = rec.split('<>')[1].strip('#')
                    rec_match = rec.split('<>')[6].strip('#').split('_')[0].strip()
                    #all_list = []
                    if pro == rec_match:
                        all_list.append(rec)
                self.finalprovider_dict.update({pro : all_list})
        except:
            for pro in self.provider_list:
                all_list, dupli_list = [] ,[]
                for rec in availability_items_list:
                    rec1 = rec['source_availabilities'][0]['template_id'].split('_')[0].strip()
                    if pro == rec1:
                        all_list.append(rec)
                self.finalprovider_dict.update({pro : all_list})
                '''for i in set(all_list):
                    lc = [] 
                    record_match = i['source_availabilities'][0]['template_id'].split('_')[0].strip()
                    for i1 in all_list:
                        record_match2 = i1['source_availabilities'][0]['template_id'].split('_')[0].strip()
                        if record_match2 == record_match and i['source_program_id'] == i1['source_program_id']:
                            lc.append(i1)
                    dupli_list.append(lc)
                final_list,alldata_list = [],[]
                for k in dupli_list:
                    rec_dict, source_avaialabilites = {} , [] 
                    for li in k:
                        rec_dict.update({'source_id': li['source_id'],'source_program_id_space' :i['source_program_id_space'], 'source_program_id': li['source_program_id']})
                        source_avaialabilites.append(li['source_availabilities'][0])
                    rec_dict.update({'source_availabilities':source_avaialabilites})
                    final_list.append(rec_dict)
                alldata_list.extend(final_list)
                self.finalprovider_dict.update({pro : alldata_list})'''
        return self.finalprovider_dict

    def store(self, items, content_type):
        #appending items  if LOAD_SIZE == 100
        if content_type == 'movie':
            if len(self.movie_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.movie_items_list, self.get_movie_file(), content_type)
            self.movie_items_list.append(items)
        elif content_type == 'tvshow':
            if len(self.tvshow_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.tvshow_items_list, self.get_tvshow_file(), content_type)
            self.tvshow_items_list.append(items)
        elif content_type == 'season':
            if len(self.season_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.season_items_list, self.get_season_file(), content_type)
            self.season_items_list.append(items)
        elif content_type == 'episode':
            if len(self.episode_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.episode_items_list, self.get_episode_file(), content_type)
            self.episode_items_list.append(items)
        elif content_type == 'othermedia':
            if len(self.othermedia_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.othermedia_items_list, self.get_othermedia_file(), content_type)
            self.othermedia_items_list.append(items)
        elif content_type == 'relatedprogram':
            if len(self.related_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.related_items_list, self.get_related_programs_file(), content_type)
            self.related_items_list.append(items)
        elif content_type == 'richmedia':
            if len(self.richmedia_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.richmedia_items_list, self.get_richmedia_file(), content_type)
            self.richmedia_items_list.append(items)
        elif content_type == 'rating':
            if len(self.rating_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.rating_items_list, self.get_rating_file(), content_type)
            self.rating_items_list.append(items)
        elif content_type == 'popularity':
            if len(self.popularity_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.popularity_items_list, self.get_pop_file(), content_type)
            self.popularity_items_list.append(items)
        elif content_type == 'crew':
            if len(self.crew_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.crew_items_list, self.get_crew_file(), content_type)
            self.crew_items_list.append(items)
        elif content_type == 'programcrew':
            if len(self.programcrew_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.programcrew_items_list, self.get_program_crew_file(), content_type)
            self.programcrew_items_list.append(items)
        elif content_type == 'awards':
            if len(self.awards_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.awards_items_list, self.get_award_file(), content_type)
            self.awards_items_list.append(items)
        elif content_type == 'releases':
            if len(self.releases_items_list)== LOAD_SIZE:
                self.write_items_into_file(self.releases_items_list, self.get_release_file(), content_type)
            self.releases_items_list.append(items)
        elif content_type == 'news':
            if len(self.news_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.news_items_list, self.get_news_file(), content_type)
            self.news_items_list.append(items)
        elif content_type == 'chart':
            if len(self.chart_items_list) ==  LOAD_SIZE :
                self.write_items_into_file(self.chart_items_list, self.get_charts_file(), content_type)
            self.chart_items_list.append(items)
        elif content_type == 'boxoffice':
            if len(self.boxoffice_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.boxoffice_items_list, self.get_boxoffice_file(), content_type)
            self.boxoffice_items_list.append(items)
        elif content_type == 'reviews':
            if len(self.reviews_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.reviews_items_list, self.get_reviews_file(), content_type)
            self.reviews_items_list.append(items)
        elif content_type == 'theater':
            if len(self.theater_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.theater_items_list, self.get_theater_file(), content_type)
            self.theater_items_list.append(items)
        elif content_type == 'theateravailability':
            if len(self.theateravailability_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.theateravailability_items_list, self.get_theater_avail_file(), content_type)
            self.theateravailability_items_list.append(items)
        elif content_type == 'primetime':
            if len(self.primetime_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.primetime_items_list, self.get_primetime_file(), content_type)
            self.primetime_items_list.append(items)
        elif content_type == 'programcharts':
            if len(self.programcharts_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.programcharts_items_list, self.get_program_charts_file(), content_type)
            self.programcharts_items_list.append(items)
        elif content_type == 'channels':
            if len(self.channels_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.channels_items_list, self.get_channel_file(), content_type)
            self.channels_items_list.append(items)
        elif content_type == 'channelcharts':
            if len(self.channelcharts_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.channelcharts_items_list, self.get_channel_charts_file(), content_type)
            self.channelcharts_items_list.append(items)
        elif content_type == 'schedules':
            if len(self.schedules_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.schedules_items_list, self.get_schedule_file(), content_type)
            self.schedules_items_list.append(items)
        elif content_type == 'otherlinks':
            if len(self.otherlinks_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.otherlinks_items_list, self.get_otherlinks_file(), content_type)
            self.otherlinks_items_list.append(items)
        elif content_type == 'loaction':
            if len(self.loactions_items_list) == LOAD_SIZE :
                self.write_items_into_file(self.loactions_items_list, self.get_location_file(), content_type)
            self.loactions_items_list.append(items)
        elif content_type == 'lineup' :
            if len(self.lineup_items_list)  == LOAD_SIZE:
                self.write_items_into_file(self.lineup_items_list, self.get_lineup_file(), content_type)
            self.lineup_items_list.append(items)
        elif content_type == 'availability':
            if len(self.availability_items_list) == LOAD_SIZE:
                self.write_items_into_file(self.availability_items_list, self.get_avail_file(), content_type)
            self.availability_items_list.append(items)
        elif content_type == 'avail_json':
            if len(self.avail_json_items_list) == LOAD_SIZE:
                self.write_json_items_into_file(self.avail_json_items_list, self.get_json_file(), content_type)
            self.avail_json_items_list.append(items)
        '''elif content_type == 'availability':
            if len(self.availability_items_list) == LOAD_SIZE:
                self.finalprovider_dict = self.provider_wiselist(self.availability_items_list)
                for pro in self.finalprovider_dict.keys():
                    self.availability_items = self.finalprovider_dict[pro]
                     
                    self.write_items_into_file(self.availability_items, self.get_provider_avail_file(pro), 'availability')
            #self.write_items_into_file(self.availability_items_list, self.get_avail_file(), content_type)
            self.availability_items_list.append(items)
            #print len(self.availability_items_list)
            try:
                provider = items.split('<>')[6].strip('#').split('_')[0].strip()
            except:
                print ("please provider valid provider name")
                pass
            self.provider_list.append(provider)
            self.provider_list = list(set(self.provider_list))
            #print self.provider_list
           
        elif content_type == 'avail_json':
            if len(self.avail_json_items_list) == LOAD_SIZE:
                self.finalprovider_dict = self.provider_wiselist(self.avail_json_items_list)
                for pro in self.finalprovider_dict.keys():
                    self.json_availability_items = self.finalprovider_dict[pro]
                    self.write_json_items_into_file(self.json_availability_items, self.get_provider_json_file(pro), 'avail_json')
                #self.write_json_items_into_file(self.avail_json_items_list, self.get_json_file(), content_type)
            self.avail_json_items_list.append(items)'''

    def write_json_items_into_file(self, json_items, _file, content_type):
        #writing json items into file
        for json_item in json_items:
            json.dump(json_item, _file)
            _file.write('\n')
            _file.flush()
        del json_items[:]

    def write_items_into_file(self, items_list, _file, content_type):
        #writing items into respective files
        _file.write('%s\n' % ('\n'.join(items_list)))
        _file.flush()
        del items_list[:]

    def get_created_file(self):
        if self.created_file: return self.created_file

        created_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_created_%s.created" % (self.name, get_current_ts_with_ms()))
        self.created_file = open(created_queries_filename, 'w')

        return self.created_file

    def get_movie_file(self):
        if self.movie_file: return self.movie_file

        movie_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_movie_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.movie_file = open(movie_queries_filename, 'w')

        return self.movie_file

    def get_tvshow_file(self):
        if self.tvshow_file: return self.tvshow_file

        tvshow_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_tvshow_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.tvshow_file = open(tvshow_queries_filename, 'w')

        return self.tvshow_file

    def get_season_file(self):
        if self.season_file: return self.season_file

        season_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_season_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.season_file = open(season_queries_filename, 'w')

        return self.season_file

    def get_episode_file(self):
        if self.episode_file: return self.episode_file

        episode_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_episode_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.episode_file = open(episode_queries_filename, 'w')

        return self.episode_file

    def get_othermedia_file(self):
        if self.othermedia_file: return self.othermedia_file

        othermedia_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_othermedia_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.othermedia_file = open(othermedia_queries_filename, 'w')

        return self.othermedia_file

    def get_crew_file(self):
        if self.crew_file: return self.crew_file

        crew_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_crew_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.crew_file = open(crew_queries_filename, 'w')

        return self.crew_file

    def get_program_crew_file(self):
        if self.prgm_crew_file: return self.prgm_crew_file

        prgm_crew_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_programcrew_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.prgm_crew_file = open(prgm_crew_queries_filename, 'w')

        return self.prgm_crew_file

    def get_richmedia_file(self):
        if self.richmedia_file: return self.richmedia_file

        richmedia_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_richmedia_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.richmedia_file = open(richmedia_queries_filename, 'w')

        return self.richmedia_file

    def get_rating_file(self):
        if self.rating_file: return self.rating_file

        rating_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_rating_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.rating_file = open(rating_queries_filename, 'w')

        return self.rating_file

    def get_pop_file(self):
        if self.popularity_file: return self.popularity_file

        popularity_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_popularity_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.popularity_file = open(popularity_queries_filename, 'w')

        return self.popularity_file

    def get_json_file(self):
        if self.json_file: return self.json_file

        json_filename = os.path.join(JSON_FILES_DIR, "crawl_%s_%s.txt" % (self.name.split('_', 1)[0], get_current_ts_with_ms()))
        self.json_file = open(json_filename, 'w')

        return self.json_file

    def get_provider_json_file(self,provider):
        #if self.json_file: return self.json_file
        json_filename = os.path.join(JSON_FILES_DIR, "crawl_%s_%s.txt" % (provider, get_current_ts_with_ms()))
        #json_filename = os.path.join(JSON_FILES_DIR, "crawl_%s_%s.txt" % (self.name.split('_', 1)[0], get_current_ts_with_ms()))
        self.json_file = open(json_filename, 'w') 

        return self.json_file

    def get_avail_file(self):
        if self.avail_file: return self.avail_file

        avail_filename = os.path.join(QUERY_FILES_DIR, "%s_ott_avail_%s.txt" % (self.name.split('_', 1)[0], get_current_ts_with_ms()))
        #avail_filename = os.path.join(QUERY_FILES_DIR, "%s_ott_avail_%s.txt" % (provider, get_current_ts_with_ms()))
        self.avail_file = open(avail_filename, 'w')

        return self.avail_file
    def get_provider_avail_file(self,provider):
        #if self.avail_file: return self.avail_file
        avail_filename = os.path.join(QUERY_FILES_DIR, "%s_ott_avail_%s.txt" % (provider, get_current_ts_with_ms()))
        self.avail_file = open(avail_filename, 'w')
        return self.avail_file

    def get_custom_query_file(self):
        if self.custom_query_file: return self.custom_query_file

        custom_query_filename = os.path.join(QUERY_FILES_DIR, "%s_queries_%s.custom" % (self.name.split('_', 1)[0], get_current_ts_with_ms()))
        self.custom_query_file = open(custom_query_filename, 'w')

        return self.custom_query_file

    def get_related_programs_file(self):
        if self.related_programs_file: return self.related_programs_file

        related_programs_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_relatedprograms_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.related_programs_file = open(related_programs_queries_filename, 'w')

        return self.related_programs_file

    def get_award_file(self):
        if self.award_file: return self.award_file

        award_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_award_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.award_file = open(award_queries_filename, 'w')

        return self.award_file

    def get_release_file(self):
        if self.release_file: return self.release_file

        release_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_release_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.release_file = open(release_queries_filename, 'w')

        return self.release_file

    def get_news_file(self):
        if self.news_file: return self.news_file

        news_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_news_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.news_file = open(news_queries_filename, 'w')

        return self.news_file

    def get_charts_file(self):
        if self.charts_file: return self.charts_file

        charts_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_charts_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.charts_file = open(charts_queries_filename, 'w')

        return self.charts_file

    def get_boxoffice_file(self):
        if self.boxoffice_file: return self.boxoffice_file

        boxoffice_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_boxoffice_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.boxoffice_file = open(boxoffice_queries_filename, 'w')

        return self.boxoffice_file

    def get_reviews_file(self):
        if self.reviews_file: return self.reviews_file

        reviews_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_reviews_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.reviews_file = open(reviews_queries_filename, 'w')

        return self.reviews_file

    def get_theater_file(self):
        if self.theater_file: return self.theater_file

        theater_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_theater_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.theater_file = open(theater_queries_filename, 'w')

        return self.theater_file

    def get_theater_avail_file(self):
        if self.theateravailability_file: return self.theateravailability_file

        theater_avail_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_theateravailability_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.theateravailability_file = open(theater_avail_queries_filename, 'w')

        return self.theateravailability_file

    def get_primetime_file(self):
        if self.primetime_file: return self.primetime_file

        primetime_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_primetime_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.primetime_file = open(primetime_queries_filename, 'w')

        return self.primetime_file

    def get_program_charts_file(self):
        if self.prgm_charts_file: return self.prgm_charts_file

        prgm_charts_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_programcharts_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.prgm_charts_file = open(prgm_charts_queries_filename, 'w')

        return self.prgm_charts_file

    def get_channel_file(self):
        if self.channel_file: return self.channel_file

        channel_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_channel_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.channel_file = open(channel_queries_filename, 'w')

        return self.channel_file

    def get_channel_charts_file(self):
        if self.channel_charts_file: return self.channel_charts_file

        channel_charts_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_channelcharts_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.channel_charts_file = open(channel_charts_queries_filename, 'w')

        return self.channel_charts_file

    def get_schedule_file(self):
        if self.schedule_file: return self.schedule_file

        schedule_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_schedule_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.schedule_file = open(schedule_queries_filename, 'w')

        return self.schedule_file

    def get_otherlinks_file(self):
        if self.otherlinks_file: return self.otherlinks_file

        otherlinks_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_otherlinks_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.otherlinks_file = open(otherlinks_queries_filename, 'w')

        return self.otherlinks_file

    def get_location_file(self):
        if self.location_file: return self.location_file

        location_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_location_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.location_file = open(location_queries_filename, 'w')

        return self.location_file

    def get_lineup_file(self):
        if self.lineup_file: return self.lineup_file

        lineup_queries_filename = os.path.join(QUERY_FILES_DIR, "%s_lineup_%s.queries" % (self.name, get_current_ts_with_ms()))
        self.lineup_file = open(lineup_queries_filename, 'w')

        return self.lineup_file

    def move_json_file_to_ott_processed_dir(self):
        if self.json_file:
            self.json_file.flush()
            self.json_file.close()
            move_file(self.json_file.name, JSON_FILES_PROCESSED_DIR)

    def close_all_opened_query_files(self):
        files_list = [
            self.movie_file, self.season_file, self.tvshow_file, self.episode_file,
            self.othermedia_file, self.crew_file, self.prgm_crew_file, self.richmedia_file, self.rating_file,
            self.popularity_file, self.related_programs_file, self.award_file, self.release_file,
            self.news_file, self.charts_file, self.boxoffice_file, self.reviews_file,
            self.theater_file, self.theateravailability_file, self.primetime_file, self.prgm_charts_file,
            self.channel_file, self.channel_charts_file, self.schedule_file, self.otherlinks_file,
            self.location_file, self.avail_file, self.lineup_file, self.created_file
        ]
        for f in files_list:
            if not isinstance(f, IOBase): continue
            f.flush()
            f.close()
            move_file(f.name, QUERY_FILES_PROCESSING_DIR)
    def close_move_avail_file(self):
        if self.avail_file:
            self.avail_file.flush()
            self.avail_file.close()
            move_file(self.avail_file.name, QUERY_FILES_PROCESSING_DIR)

    def close_all_opened_files(self):
        if self.json_file:
            self.move_json_file_to_ott_processed_dir()
        # Call Close Open Files Function
        self.close_all_opened_query_files()
    def close_move_json_file(self):
        if self.json_file:
            self.move_json_file_to_ott_processed_dir()

    def _spider_closed(self, spider, reason):
        if spider.name != self.name: return
        if self.crawl_vals_set: self.insert_crawl_tables_data()
        if '_browse' not in self.name and len(self._sks) > 0:
            self.update_urlqueue_with_resp_status()

        if "terminal" in spider.name.lower() or self.crawl_type == 'catchup':
            #self.crawler_stats.stats_ends(spider, reason, self.content_type)
            print ('.')

        #writing into files if LOAD_SIZE < 100 items
        if self.movie_items_list: self.write_items_into_file(self.movie_items_list, self.get_movie_file(), 'movie')
        if self.tvshow_items_list: self.write_items_into_file(self.tvshow_items_list, self.get_tvshow_file(), 'tvshow')
        if self.season_items_list: self.write_items_into_file(self.season_items_list, self.get_season_file(), 'season')
        if self.episode_items_list: self.write_items_into_file(self.episode_items_list, self.get_episode_file(), 'episode')
        if self.othermedia_items_list: self.write_items_into_file(self.othermedia_items_list, self.get_othermedia_file(),  'othermedia')
        if self.related_items_list: self.write_items_into_file(self.related_items_list, self.get_related_programs_file(), 'relatedprogram')
        if self.richmedia_items_list: self.write_items_into_file(self.richmedia_items_list, self.get_richmedia_file(), 'richmedia')
        if self.rating_items_list: self.write_items_into_file(self.rating_items_list, self.get_rating_file(), 'rating')
        if self.popularity_items_list: self.write_items_into_file(self.popularity_items_list, self.get_pop_file(), 'popularity')
        if self.crew_items_list: self.write_items_into_file(self.crew_items_list, self.get_crew_file(), 'crew')
        if self.programcrew_items_list: self.write_items_into_file(self.programcrew_items_list, self.get_program_crew_file(), 'programcrew')
        if self.awards_items_list: self.write_items_into_file(self.awards_items_list, self.get_award_file(), 'awards')
        if self.releases_items_list: self.write_items_into_file(self.releases_items_list, self.get_release_file(), 'releases')
        if self.news_items_list: self.write_items_into_file(self.news_items_list, self.get_news_file(), 'news')
        if self.chart_items_list: self.write_items_into_file(self.chart_items_list, self.get_charts_file(), 'chart')
        if self.boxoffice_items_list: self.write_items_into_file(self.boxoffice_items_list, self.get_boxoffice_file(), 'boxoffice')
        if self.reviews_items_list: self.write_items_into_file(self.reviews_items_list, self.get_reviews_file(), 'reviews')
        if self.theater_items_list: self.write_items_into_file(self.theater_items_list, self.get_theater_file(), 'theater')
        if self.theateravailability_items_list: self.write_items_into_file(self.theateravailability_items_list, \
                                                                           self.get_theater_avail_file(), 'theateravailability')
        if self.primetime_items_list: self.write_items_into_file(self.primetime_items_list, self.get_primetime_file(), 'primetime')
        if self.programcharts_items_list: self.write_items_into_file(self.programcharts_items_list, self.get_program_charts_file(), 'programcharts')
        if self.channels_items_list: self.write_items_into_file(self.channels_items_list, self.get_channel_file(), 'channels')
        if self.channelcharts_items_list: self.write_items_into_file(self.channelcharts_items_list, self.get_channel_charts_file(), 'channelcharts')
        if self.schedules_items_list: self.write_items_into_file(self.schedules_items_list, self.get_schedule_file(),  'schedules')
        if self.otherlinks_items_list: self.write_items_into_file(self.otherlinks_items_list, self.get_otherlinks_file(), 'otherlinks')
        if self.loactions_items_list: self.write_items_into_file(self.loactions_items_list, self.get_location_file(), 'loaction')
        if self.lineup_items_list: self.write_items_into_file(self.lineup_items_list, self.get_lineup_file(), 'lineup')
        '''if self.availability_items_list:
            self.finalprovider_dict = self.provider_wiselist(self.availability_items_list)
            for pro in self.finalprovider_dict.keys():
                self.availability_items = self.finalprovider_dict[pro]
                
                self.write_items_into_file(self.availability_items, self.get_provider_avail_file(pro), 'availability')
                #self.close_all_opened_files()
                self.close_move_avail_file()
        if self.avail_json_items_list:
            self.finalprovider_dict = self.provider_wiselist(self.avail_json_items_list)
            for pro in self.finalprovider_dict.keys():
                self.json_availability_items = self.finalprovider_dict[pro]
                self.write_json_items_into_file(self.json_availability_items, self.get_provider_json_file(pro), 'avail_json')
                #self.close_all_opened_files()
                #self.close_move_avail_file()
                self.close_move_json_file()
        #self.close_all_opened_files()
        self.close_all_opened_query_files()

        #self.close_conn()
        self.initialize_default_variables()
        #remove_logger_handler(self.log, os.path.join(LOGS_DIR, self.log_file_name))'''
        if self.availability_items_list: 
            self.write_items_into_file(self.availability_items_list, self.get_avail_file(), 'availability')
          
        if self.avail_json_items_list: self.write_json_items_into_file(self.avail_json_items_list, self.get_json_file(), 'avail_json')

        self.close_all_opened_files()


    def spider_closed(self, spider, reason):
        pass


class MyCounter:

    def __init__(self):
        self.counter = 0

    def increase_counter_by_1(self):
        self.counter += 1

    def reset_counter_value(self):
        self.counter = 0


class SpiderMiddleware(object):

    def process_spider_output(self, response, result, spider):
        if inspect.isgenerator(result):
            result = list(result)
            _result = []
            for r in result:
                if isinstance(r, (list, tuple)):
                    _result.extend(r)
                else:
                    _result.append(r)
            result = _result

        return result


class RandomUserAgentMiddleware(object):

    def process_request(self, request, spider):
        ua = random.choice(settings['USER_AGENT_LIST'])
        if ua:
            request.headers.setdefault('User-Agent', ua)


class _Selector:

    def select_urls(self, xpaths, response=None):
        if not isinstance(xpaths, (list, tuple)):
            xpaths = [xpaths]

        return self._get_urls(response, xpaths)

    def _get_urls(self, response, xpaths):
        urls = [self.select(xpath) for xpath in xpaths]
        urls = list(chain(*urls))
        urls = [textify(u) for u in urls]
        if response:
            urls = [urljoin(response.url, u) for u in urls]
        return urls


class HTML(Selector, _Selector):
    pass


class XML(Selector, _Selector):
    pass


def Request(url, callback=None, response=None, **kwargs):
    kwargs['callback'] = callback
    kwargs['meta'] = kwargs.get('meta', {})
    if kwargs.has_key('headers') and not kwargs['headers']:
        kwargs.pop('headers', None)

    if kwargs.has_key('dont_filter') and not kwargs['dont_filter']:
        kwargs.pop('dont_filter', None)

    if settings['PROXIES_LIST']:
        proxies_list = settings['PROXIES_LIST'] if isinstance(settings['PROXIES_LIST'], list) else eval(settings['PROXIES_LIST'])
        random_proxy = random.choice(proxies_list)
        if '#<>#' in random_proxy:
            proxies_creds_list = random_proxy.split('#<>#')
            proxy_user_pass = proxies_creds_list[1].replace('\\', '') 
            kwargs['meta']['proxy'] = proxies_creds_list[0]
            encoded_user_pass = base64.encodestring(proxy_user_pass)
            Proxy_Authorization = 'Basic ' + encoded_user_pass
            kwargs.update({'headers' : {'Proxy-Authorization' : Proxy_Authorization}})
        else:
            kwargs['meta']['proxy'] = random_proxy 

    urls = url if isinstance(url, (tuple, list)) else [url]

    do_random_scheduling = settings.get('RANDOM_SCHEDULING', True)
    response_url = '' if response is None else response.url

    out = []
    for url in urls:
        if not isinstance(url, (str, bytes)):
            url = url.extract()

        out.append(urlparse.urljoin(response_url, url))

    if do_random_scheduling and 'priority' not in kwargs:
        kwargs['priority'] = 1

    return [ScrapyHTTPRequest(u, **kwargs) for u in out]

def get_ts_with_seconds():
    ts = datetime.datetime.utcnow()
    st = ts.strftime('%Y-%m-%d %H:%M:%S') + 'Z'
    return st


'''def get_request_url(response):
    if response.meta.get('redirect_urls', []):
        resp_url = response.meta.get('redirect_urls')[0]
    else:
        resp_url = response.url

    return resp_url

def get_mysql_connection(server=DB_HOST, db_name=URLQ_DB_NAME, cursorclass=""):
    try:
        from MySQLdb.cursors import Cursor, DictCursor, SSCursor, SSDictCursor
        cursor_dict = {'dict': DictCursor, 'ssdict': SSDictCursor, 'ss': SSCursor}
        cursor_class = cursor_dict.get(cursorclass, Cursor)

        conn = MySQLdb.connect(
                    host=server, user=DB_UNAME, passwd=DB_PASSWD, db=db_name,
                    connect_timeout=MYSQL_CONNECT_TIMEOUT_VALUE, cursorclass=cursor_class,
                    charset="utf8", use_unicode=True
        )
        if db_name: conn.autocommit(True)
        cursor = conn.cursor()

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception:
        conn, cursor = None, None

    return conn, cursor

def execute_query(cursor, query, values=''):
    try:
        if values:
            cursor.execute(query, values)

        cursor.execute(query)
    except:
        traceback.print_exc()'''

def fetchone(cursor, query):
    execute_query(cursor, query)
    recs = cursor.fetchone()

    return recs[0]

def fetchall(cursor, query):
    execute_query(cursor, query)
    recs = cursor.fetchall()

    return recs

def close_mysql_connection(conn, cursor):
    if cursor: cursor.close()
    if conn: conn.close()

def get_current_ts_with_ms():
    dt = datetime.datetime.now().strftime("%Y%m%dT%H%M%S%f")

    return dt

def make_dir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

def make_dir_list(dir_list, par_dir=OUTPUT_DIR):
    make_dir(par_dir)

    for dir_name in dir_list:
        make_dir(os.path.join(par_dir, dir_name))

def copy_file(source, dest):
    cmd = "cp %s %s" % (source, dest)
    os.system(cmd)

def move_file(source, dest):
    cmd = "mv %s %s" % (source, dest)
    os.system(cmd)

def get_compact_traceback(e=''):
    except_list = [asyncore.compact_traceback()]
    return "Error: %s Traceback: %s" % (str(e), str(except_list))

def set_logger_log_level(logger, log_level_list):
    if not log_level_list:
        logger.setLevel(logging.INFO)

    log_str = string.join(log_level_list, ":")

    if log_str.find("DEBUG_") != -1:
        logger.setLevel(logging.DEBUG)
        return

    if "INFO" in log_level_list:
        logger.setLevel(logging.INFO)

    return

def add_logger_handler(logger, file_name, log_level_list=[]):
    success_cnt, handler = 3, None

    for i in xrange(success_cnt):
        try:
            handler = logging.FileHandler(file_name)
            break
        except (KeyboardInterrupt, SystemExit):
            raise
        except: pass

    if not handler: return

    formatter = logging.Formatter('%(asctime)s.%(msecs)d: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s', "%Y%m%d%H%M%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    set_logger_log_level(logger, log_level_list)

    if handler.stream:
        set_close_on_exec(handler.stream)

def remove_logger_handler(logger, file_name='', log_level_list=[]):
    for handler in logger.handlers:
        if handler.baseFilename == file_name:
            handler.close()
            logger.removeHandler(handler)

def initialize_logger(file_name, log_level_list=[]):
    logger = logging.getLogger()
    try:
        add_logger_handler(logger, file_name, log_level_list)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        e = sys.exc_info()[2]
        time_str = time.strftime("%Y%m%dT%H%M%S", time.localtime())
        exception_str = "%s: %s: Exception: %s" % (time_str, sys.argv, get_compact_traceback(e))
        #print exception_str

    return logger

def set_close_on_exec(fd):
    import fcntl
    st = fcntl.fcntl(fd, fcntl.F_GETFD)
    fcntl.fcntl(fd, fcntl.F_SETFD, st | fcntl.FD_CLOEXEC)

def textify(nodes, sep=' '):
    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]

    def _t(x):
        if isinstance(x, (str, unicode)):
            return [x]

        if hasattr(x, 'xmlNode'):
            if not x.xmlNode.get_type() == 'element':
                return [x.extract()]
        else:
            if isinstance(x.root, (str, unicode)):
                return [x.root]

        return (n.extract() for n in x.select('.//text()'))

    nodes = chain(*(_t(node) for node in nodes))
    nodes = (node.strip() for node in nodes if node.strip())

    return sep.join(nodes)

def xcode(text, encoding='utf8', mode='strict'):
    return text.encode(encoding, mode) if isinstance(text, bytes) else text

def compact(text, level=0):
    if text is None: return ''

    if level == 0:
       # text = text.replace("\n", " ")
        text = text.replace("\r", " ")

    compacted = re.sub("\s\s(?m)", " ", text)
    if compacted != text:
        compacted = compact(compacted, level+1)

    return compacted.strip()

def clean(text):
    if not text: return text

    value = text
    value = re.sub("&amp;", "&", value)
    value = re.sub("&lt;", "<", value)
    value = re.sub("&gt;", ">", value)
    value = re.sub("&quot;", '"', value)
    value = re.sub("&apos;", "'", value)

    return value

def normalize(text):
    return clean(compact(xcode(text)))

def extract(sel, xpath, sep=' '):
    return clean(compact(textify(sel.xpath(xpath).extract(), sep)))

def extract_data(data, path, delem=''):
   return delem.join(i.strip() for i in data.xpath(path).extract() if i).strip()

def extract_list_data(data, path):
   return data.xpath(path).extract()

def get_nodes(data, path):
   return data.xpath(path)

def md5(x):
    return hashlib.md5(xcode(x)).hexdigest()

def validate_year(self, year):
        is_valid = False
        if year and isinstance(year, int):
            if year >= 1900 and year <= 2020:
                is_valid = True
        return is_valid

def get_year_from_string(text):
    import re
    cleaned_text, year = '', ''
    re_match = re.search('\((\d{4})\)', text) or re.search('\s(\d{4})$', text) or re.search('\s(\d{4})\s', text) or re.search('\[(\d{4})\]', text)
    if re_match:
        year_info    = re_match.re.findall(text)
        if year_info:
            final_year = int(year_info[0])
            if validate_year(final_year):
                cleaned_text = re_match.re.sub('', text).strip()
                year         = final_year
    return cleaned_text, year

def get_rating_val(self, rating, mul=0):
        rating = get_digit(rating)
        if mul > 1:
            rating = rating * mul
        return rating

def get_response(reference_url, logger=''):
    start_time = timeit.default_timer()
    USER_AGENT = "Mozilla/5.0 (Linux; Veveobot; + http://corporate.veveo.net/contact/) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0"

    http_client = HT.HTTPClient()
    try:
        r =  http_client.fetch(reference_url, user_agent=USER_AGENT)
        res = TextResponse(url=reference_url, headers=r.headers, body=r.body)
        status = res.status
        end_time = timeit.default_timer()
        logger.info("URL Response Time: %s - Reference URL: %s", (end_time - start_time), reference_url)

        start_time = timeit.default_timer()
        sel = Selector(res)
        end_time = timeit.default_timer()
        logger.info("DOM Construction Time: %s  - Reference URL: %s", (end_time - start_time), reference_url)

    except Exception as e:
        status, sel = 404, ''
        logger.error(get_compact_traceback(e))

    return (status, sel)



def get_response_by_passing_headers(reference_url, logger, headers={}, conn_timeout=0, req_timeout=0):
    USER_AGENT = "Mozilla/5.0 (Linux; Veveobot; + http://corporate.veveo.net/contact/) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0"
    conn_timeout = conn_timeout or 1800.0
    req_timeout = req_timeout or 1800.0

    start_time = timeit.default_timer()
    http_client = HT.HTTPClient()

    if headers.has_key('User-Agent'):
        USER_AGENT = headers['User-Agent']
    headers['User-Agent'] = USER_AGENT

    try:
        request = HT.HTTPRequest(reference_url, headers=headers, connect_timeout=conn_timeout, request_timeout=req_timeout)
        response = http_client.fetch(request)
        status, body = response.code, response.body
        end_time = timeit.default_timer()
        logger.info("URL Response Time: %s - Reference URL: %s", (end_time - start_time), reference_url)

    except Exception as e:
        logger.error(get_compact_traceback(e))
        status, body = 404, ''
    return status, body


def get_xml_response(reference_url, logger=''):
    start_time = timeit.default_timer()

    http_client = HT.HTTPClient()

    try:
        r =  http_client.fetch(reference_url)
        res = XmlResponse(url=reference_url, headers=r.headers, body=r.body)
        status = res.status

        end_time = timeit.default_timer()
        logger.info("URL Response Time: %s - Reference URL: %s", (end_time - start_time), reference_url)

        start_time = timeit.default_timer()
        sel = Selector(res)
        end_time = timeit.default_timer()
        logger.info("DOM Construction Time: %s  - Reference URL: %s", (end_time - start_time), reference_url)

    except Exception as e:
        status, sel = 404, ''
        logger.error(get_compact_traceback(e))

    return (status, sel)

def get_response_body(reference_url, logger=''):
    start_time = timeit.default_timer()

    http_client = HT.HTTPClient()
    try:
        r   = http_client.fetch(reference_url)
        sel = r.body
        res = TextResponse(url=reference_url, headers=r.headers, body=r.body)
        status = res.status
        end_time = timeit.default_timer()
        logger.info("URL Response Time: %s - Reference URL: %s", (end_time - start_time), reference_url)
    except HT.HTTPError as e:
        status, sel = 404, ''
        logger.error(get_compact_traceback(e))

    return (status, sel)

def parse_date(data, dayfirst=False):
    if not 'ago' in data and 'Yesterday' not in data:
        return parse(data, dayfirst=dayfirst, fuzzy=True)
    elif 'Yesterday' in data:
        return parse(data, dayfirst=dayfirst, fuzzy=True)+relativedelta(days=-1)
    else:
        DEFAULT = datetime.datetime.utcnow()
        dat = re.findall('\d+', data)
        if len(dat)==1 : dat.append(0)
        if 'years' in data:
            return DEFAULT + relativedelta(years=-int(dat[0]), months=-int(dat[1]))
        elif 'months' in data:
            return DEFAULT + relativedelta(months=-int(dat[0]), weeks=-int(dat[1]))
        elif 'week' in data:
            return DEFAULT + relativedelta(weeks=-int(dat[0]))
        elif 'day' in data:
            return DEFAULT + relativedelta(days=-int(dat[0]), hours=-int(dat[1]))
        elif 'hour' in data or 'hrs' in data or 'hr' in data:
            return DEFAULT + relativedelta(hours=-int(dat[0]), minutes=-int(dat[1]))
        elif 'minute' in data or 'mins' in data:
            return DEFAULT + relativedelta(minutes=-int(dat[0]))

def get_digit(self, value):
    if value.isdigit():
        value = int(value)
    else:
        try:
            value = float(value)
        except ValueError:
            value = 0
    return value

def convert_str_to_dict_obj(text):
    conv_text = json.loads(text)

    return conv_text

def convert_dict_to_str_obj(text):
    conv_text = json.dumps(text)

    return conv_text

def get_datetime(epoch):
    t = time.gmtime(epoch)
    dt = datetime.datetime(*t[:6])

    return dt

def parse_genframework_config_file(section='', sub_section=''):
    cfg_file_path = os.path.join(os.path.abspath(os.path.pardir), 'genframework.cfg')
    parser = SafeConfigParser()
    parser.read(cfg_file_path)

    sections = parser.sections()
    if not sections: return {}

    cfg_data = {}
    for section in sections:
        for key, value in parser.items(section):
            cfg_data.setdefault(section, {}).update({key: json.loads(value)})

    if section and sub_section:
        return cfg_data[section][sub_section]
    elif section:
        return cfg_data[section]

    return cfg_data

