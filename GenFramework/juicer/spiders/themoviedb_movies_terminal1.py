import collections
from juicer.items import MovieItem, CrewItem, ProgramCrewItem, AvailItem, \
                         RichMediaItem, RatingItem, ReleasesItem
from juicer.hott_utils import *
from showtime_xpaths import movie_html_url



class ThemoviedbMoviesTerminal(JuicerSpider):
    name = 'themoviedb_movies_terminal1'

    def __init__(self, *args, **kwargs):
        super(ThemoviedbMoviesTerminal, self).__init__(*args, **kwargs)


    def parse(self, response):
        movie_sk = response.url.split('movie/')[-1].replace('?language=en','')
        movie_title = ''.join(response.xpath('//div[@class="title"]//h2/text()').extract())
        if movie_sk and movie_title:
            desc = ''.join(response.xpath('//div[@class="overview"]//p/text()').extract())
            duration = ''.join(response.xpath('//section[@class="facts left_column"]//strong//bdi[contains(text(),"Runtime")]//..//following-sibling::text()').extract())
            if '-' in duration:
                dur = 0
            if 'h' in duration:
                duration_in_hours = duration.split('h')[0]
                dur_hours = int(duration_in_hours) * 3600
            if 'm' in duration:
                duration_in_min = duration.split('h')[-1].replace('m','')
                dur_in_min = int(duration_in_min) * 60
            if 'h' in duration and 'm' in duration:
                dur = dur_hours + dur_in_min
            release_date = ''.join(response.xpath('//ul[@class="releases"]//li/text()').extract()).strip().replace('\n','')
            if release_date:
                rel_date = str(release_date)
            release_year = ''.join(response.xpath('//span[@class="release_date"]/text()').extract())
            mpaa_rating = ''.join(response.xpath('//div[@class="certification"]//span[@element="56901e19c3a3680f8904bce4"]/text()').extract())
            genres = '<>'.join(response.xpath('//section[@class="genres right_column"]//li//a//text()').extract())
      	    image_url = ''.join(response.xpath('//div[@class="image_content"]//img//@src').extract()).replace('_filter(blur)','')
            image_sk = image_url.split('_bestv2/')[-1].replace('.jpg','')
            img_dim = ''.join(re.findall('w\d+_and_h\d+',image_url)).replace('w','').replace('h','').replace('_and_','X')
            movieitem = MovieItem()
            movieitem.update({
                'sk':movie_sk, 'title':movie_title, 'description':desc,
                'genres':genres,'aux_info':'', 'duration':dur,
                'metadata_language':'eng', 'reference_url':response.url
                })  
            print movieitem
            yield movieitem      
            
	    richmedia_item = RichMediaItem()
            richmedia_item.update({'sk':image_sk,
                                    'program_sk':movie_sk,
                                    'program_type':'movie',
                                    'media_type':'image',
                                    'image_type':'poster',
                                    'image_url':image_url,
                                    'reference_url':response.url,
                                    'dimensions':img_dim
                                  })
            print richmedia_item
            yield richmedia_item

            if mpaa_rating:
                rating_item = RatingItem()
                rating_item.update({'program_sk':movie_sk,
                                    'program_type':'movie',
                                    'rating':mpaa_rating,
                                    'rating_type' : 'mpaa_rating'})
                print rating_item
                yield rating_item

            if release_year or release_date:
                release_item = ReleasesItem()
                release_item.update({'program_sk':movie_sk,
                                     'program_type':'movie',
                                     'release_date':rel_date,
                                     'release_year':release_year,
                                     'country' : 'us'})
                print release_item
                yield release_item
 
            if "Full Cast & Crew" in response.text:
                crew_data = ''.join(response.xpath('//p[@class="new_button"]//a/@href').extract())
                url = "https://www.themoviedb.org" + crew_data
                yield Request(url ,callback=self.parse_cast,meta={'sk':movie_sk})


    def parse_cast(self, response):
        movie_sk =response.meta.get('sk')
        urls = response.xpath('//div[@class="info"]//p//a/@href').extract()
        for url in urls:
            url_ = "https://www.themoviedb.org" + url
            yield Request(url_, callback=self.parse_crew,meta={'sk':movie_sk})

    def parse_crew(self, response):
        movie_sk = response.meta.get('sk')
        crew_title=''.join(response.xpath('//div[@class="title"]//h2/text()').extract())
        crew_sk = hashlib.md5(crew_title).hexdigest()
        rank = ''.join(response.xpath('//section[@class="facts left_column"]//strong//bdi[contains(text(),"Known Credits")]//..//following-sibling::text()').extract())
        birth_date = ''.join(response.xpath('//section[@class="facts left_column"]//strong//bdi[contains(text(),"Birthday")]//..//following-sibling::text()').extract())
        role = ''.join(response.xpath('//section[@class="facts left_column"]//strong//bdi[contains(text(),"Known For")]//..//following-sibling::text()').extract())
        place_of_birth = ''.join(response.xpath('//section[@class="facts left_column"]//strong//bdi[contains(text(),"Place of Birth")]//..//following-sibling::text()').extract())
        gender = ''.join(response.xpath('//section[@class="facts left_column"]//strong//bdi[contains(text(),"Gender")]//..//following-sibling::text()').extract())
	crew_item = CrewItem()
        crew_item['name']         = crew_title
        crew_item['sk'] = crew_title.lower()
        crew_item['gender'] = gender
        crew_item['birth_date']=birth_date
        crew_item['birth_place'] = place_of_birth
        crew_item['image'] = ''
        crew_item['reference_url'] = response.url
	print crew_item
        yield crew_item
        programcrew_item = ProgramCrewItem()
        programcrew_item['program_type'] = 'movie'
        programcrew_item['program_sk']=movie_sk
        programcrew_item['rank']= rank
        programcrew_item['role'] = role
        programcrew_item['crew_sk'] = crew_sk
        print programcrew_item
        yield programcrew_item 
