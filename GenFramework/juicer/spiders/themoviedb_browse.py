from juicer.hott_utils import *
from juicer.items import *

class TheMovieDbBrowse(JuicerSpider):
    name = 'themoviedb_browse'

    def __init__(self, *args, **kwargs):
        super(TheMovieDbBrowse, self).__init__(*args, **kwargs)
        self.crawl_type = kwargs.get('crawl_type')
        if self.crawl_type == 'keepup':
	    self.start_urls = ['https://www.themoviedb.org/movie','https://www.themoviedb.org/tv'] 
	if self.crawl_type =='catchup':
	    self.start_urls = ['https://www.themoviedb.org/discover/tv']
            #self.start_urls = ['https://www.themoviedb.org/discover/movie','https://www.themoviedb.org/discover/tv'] 

    def add_domain(self, link):
        if "http" not in link:
            link = 'https://www.themoviedb.org/' + link.strip('/')
        return link

    def parse(self, response):
        sel = HTML(response)
        listing_pages = []
        if self.crawl_type == 'catchup':
            years = response.xpath('//select[@id="year"]//option/text()').extract()
            for year in years:
                if '/discover/movie' in response.url:
                    listing_page = 'https://www.themoviedb.org/discover/movie/remote?language=en&media_type=movie&vote_count.gte=0&list_style=1&primary_release_year='+str(year)+'&sort_by=popularity.desc'
                if  '/discover/tv' in response.url:
                    listing_page = 'https://www.themoviedb.org/discover/tv/remote?language=en&media_type=tv&vote_count.gte=0&list_style=1&first_air_date_year='+str(year)+'&sort_by=popularity.desc'
                yield Request(listing_page, callback=self.parse_listings)
        
        else:
            urls = response.xpath('//div[@class="flex"]//a[@class="title result"]/@href').extract()
            for url_ in urls:
		sk = url_.split('/')[-1]
                url = self.add_domain(url_)
                self.content_type = url.split('/')[-2]
            if self.content_type == 'movie':
                terminal = 'themoviedb_movies_terminal'
            elif self.content_type == 'tv':
                terminal = 'themoviedb_tvshows_terminal'
            self.get_page(terminal, url, sk)  
            page = ''.join(response.xpath('//a[@class="next_page"]//@href').extract())
            if page:
                pages = ''.join(re.findall('\d+',page))
                page = self.add_domain(self.content_type + '?page=' + pages)
                yield Request(page, callback=self.parse)


    def parse_listings(self, response):
        sel = HTML(response)
        program_nodes = sel.xpath('//div[@class="flex"]/a')
        for program_node in program_nodes:
            program_link = extract(program_node, './@href')
            program_sk = extract(program_node, './@id')
            program_link = self.add_domain(program_link)
            self.content_type = program_sk.split('_')[0]
            if self.content_type == 'movie':
                terminal = 'themoviedb_movies_terminal'
            elif self.content_type == 'tv':
                terminal = 'themoviedb_tvshows_terminal'
            self.get_page(terminal, program_link, program_sk)
        try:
            last_page =int(response.xpath('//a[@class="next_page"]/preceding-sibling::a')[-1].xpath('.//text()').extract_first())
        except:
            last_page = 0
            page = ''.join(response.xpath('//a[@class="next_page"]//@href').extract())
        for next_page in range(1,last_page+1):
            if '/movie' in response.url:
                page_ = re.findall('primary_release_year=\d+',response.url)
                year = ''.join(page_).replace('primary_release_year=','')
                page = 'https://www.themoviedb.org/discover/movie?language=en&list_style=1&media_type=movie&page='+str(next_page)+'&primary_release_year='+str(year)+'&sort_by=popularity.desc&vote_count.gte=0'
                yield Request(page, callback=self.parse_listings)
            if '/tv' in response.url:
                page_ = re.findall('first_air_date_year=\d+',response.url)
                year = ''.join(page_).replace('first_air_date_year=','')
                page = 'https://www.themoviedb.org/discover/tv?first_air_date_year='+str(year)+'&language=en&list_style=1&media_type=tv&page=' + str(next_page)+'&sort_by=popularity.desc&vote_count.gte=0'
                yield Request(page, callback=self.parse_listings)
