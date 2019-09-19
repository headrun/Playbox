from juicer.utils import *
from juicer.items import *

Domain = 'https://trakt.tv'
class TrackTvSpider(JuicerSpider):
    name = 'trakttv_browse'
    start_urls = ['https://trakt.tv/']

    def __init__(self, *args, **kwargs):
        super(TrackTvSpider, self).__init__(*args, **kwargs)
        self.crawl_type = kwargs.get('crawl_type') #keepup or catchup
        self.content_type = kwargs.get('content_type') 
    def parse(self, response):
        sel = Selector(response)
        content_types = sel.xpath('//ul[@class="nav navbar-nav brand-left"]//li/a/@href').extract()
        for cont_type in content_types:
            cat_link = Domain + cont_type
            if 'shows' in cat_link:
                yield Request(cat_link, callback=self.parse_shows)
            if 'movies' in cat_link:
                yield Request(cat_link, callback=self.parse_movies)

    def parse_shows(self, response):
        sel = Selector(response)
        cate = sel.xpath('//nav//div[@class="link"]//a/@href').extract()
        for categ_li in cate:
            cate_li = Domain + categ_li
            yield Request(cate_li, callback=self.parse_series_next, dont_filter=True)
    def parse_series_next(self, response):
        sel = Selector(response)
        self.content_type = 'tvshow'
        if 'page=' not in response.url:
            self.crawl_type = 'keepup'
        else:
            self.crawl_type='catchup'
        category = (response.url).split('/shows/')[-1].split('?')[0]
        series_list = sel.xpath('//div[@class="row fanarts"]//div[@data-type="show"]/@data-url').extract()
        for show in series_list:
            sk = (Domain+show).split('/shows/')[-1]
            self.get_page('trakttv_tvshows_terminal', Domain+show, sk, meta_data={'category': category})
        page_nav = extract_data(sel, '//div[@class="next"]/a/@href')
        if 'page=' in page_nav:
            yield Request(Domain + page_nav, callback=self.parse_series_next)
    def parse_movies(self, response):
        sel = Selector(response)
        cate = sel.xpath('//div[@class="link"]//a/@href').extract()
        for categ_li in cate:
            cate_li = Domain + categ_li
            yield Request(cate_li, callback=self.parse_movies_next, dont_filter=True)
    def parse_movies_next(self, response):
        sel = Selector(response)
        if 'page=' not in response.url:
            self.crawl_type = 'keepup'
        else:
            self.crawl_type='catchup'
        category = (response.url).split('/movies/')[-1].split('?')[0]
        movie_list = sel.xpath('//div[@class="row fanarts"]//div[@data-type="movie"]//meta[@itemprop="url"]//@content').extract()
        for mov_list in movie_list:
            sk = mov_list.split('/movies/')[-1]
            self.get_page('trakttv_movie_terminal', mov_list, sk, meta_data={'category': category})
        page_nav = extract_data(sel, '//div[@class="next"]/a/@href')
        if 'page=' in page_nav:
            yield Request(Domain + page_nav, callback=self.parse_movies_next)



