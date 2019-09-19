from juicer.utils import *
from juicer.items import *
import json
Domain = 'https://trakt.tv'
class TrackTvAPISpider(JuicerSpider):
    name = 'trakttvapi_browse'
    start_urls = ['https://trakt.tv']
    def parse(self, response):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer f44b9f99aeaa3a0d8ecf421508ff983585e966497b2cfb77b7b8cda4412b869c',
            'trakt-api-version': '2',
            'trakt-api-key': '4403c635e068424536af745657c97aa12f245faa84cdee30d01ad73b79b5dcd2',
            'X-Pagination-Page':'2',
            'X-Pagination-Limit':'10',
            'X-Pagination-Page-Count':'10'
        }
        #url = 'https://api.trakt.tv/calendars/all/movies/2014-09-01/2000'
        #url = 'https://api.trakt.tv/movies/trending?page=1&limit=100'
        #url = 'https://api.trakt.tv/movies/trending?extended=full&page=1&limit=100&networks'
        url = 'https://api.trakt.tv/movies/cars-2006/lists/trending'
        #url = 'https://api.trakt.tv/watchnow/8856321'
        #url = 'https://api.trakt.tv/movies/trending?networks'
        #url='https://api.trakt.tv/movies/trending?extended=metadata&page=1' 
        #url='https://private-anon-991fd93c57-trakt.apiary-proxy.com/calendars/my/movies/2014-09-01/7'
        #url='https://api.trakt.tv/movies/trending?page=1&limit=100'
        yield Request(url, self.parse_next, headers=headers)
    def parse_next(self, response):
        json_data = json.loads(response.body)        
        for data in json_data: 
            print data
            import pdb;pdb.set_trace()
            '''first_aired = data['first_aired']
            show = data['show']
            show_title = show['title']
            episode = data['episode']
            sea_num = episode['season']
            epi_num = episode['number']
            epi_title = episode['title']
            show_ids = show['ids']
            trakt_show = show_ids['trakt']  
            tvdb_show = show_ids['tvdb']
            imdb_show = show_ids['imdb']
            tmdb_show = show_ids['tmdb']
            tvrage_show = show_ids['tvrage']
            slug_show = show_ids['slug']
            episode_ids = show['ids']
            trakt_epi = episode_ids['trakt']
            tvdb_epi = episode_ids['tvdb']
            imdb_epi = episode_ids['imdb']
            tmdb_epi = episode_ids['tmdb']
            tvrage_epi = episode_ids['tvrage']
            slug_epi = episode_ids['slug']'''
