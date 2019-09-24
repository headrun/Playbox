import collections
from juicer.items import *

from juicer.hott_utils import *
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')


class ThemoviedbTvshowsTerminal(JuicerSpider):
    name = 'themoviedb_tvshows_terminal'

    def __init__(self, *args, **kwargs):
        super(ThemoviedbTvshowsTerminal, self).__init__(*args, **kwargs)


    def parse(self, response):
        sk = ''.join(re.findall('\d+',response.url.split('/movie')[-1]))
        reference_url = response.url
        url = "https://api.themoviedb.org/3/tv/" +str(sk) +"?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&append_to_response=images,videos,credits,reviews,releases,content_ratings"
        yield Request(url,callback = self.parse_next,meta={'url':reference_url})

    def parse_next(self, response):
        url  = response.meta['url']
        data = json.loads(response.text)
        desc = data.get('overview','').encode('utf-8')
        tvshow_sk = data.get('id','')
        tvshow_title = data.get('name','').encode('utf-8')
        images = data.get('poster_path','')
        original_title= data.get('original_name','')
        original_language = data.get('original_language','')
        if images == None:
            image_url = ""
	    image_sk = ""
	    img_dim = ""
        else:
            image_url = "https://image.tmdb.org/t/p/w300_and_h450_bestv2" + str(images)
	    image_sk = image_url.split('_bestv2/')[-1].replace('.jpg','')
	    img_dim = img_dim = ''.join(re.findall('w\d+_and_h\d+',image_url)).replace('w','').replace('h','').replace('_and_','X')
        genre_ = data.get('genres','')
        genres_ = []
        for genre in genre_:
            genres = genre.get('name','')
            genres_.append(genres)
        release_date = data.get('release_date','')
        release_date = data.get('release_date','')
        release_year = release_date.split('-')[0]
        try:
            mpaa_rating = data.get('releases','').get('countries','')[0].get('certification','')
        except:
            try:
                mpaa_rating = data.get('content_ratings','').get('results','')[0].get('rating','')    
                print mpaa_rating
            except:
                mpaa_rating = ""
	tvshow_item = TvshowItem()
        tvshow_item.update({
                'sk':str(tvshow_sk), 'title':str(tvshow_title),'original_title':str(original_title), 'description':normalize((str(desc))),
                'genres':'<>'.join(genres_),'aux_info':str({'reference_url':response.url}),'original_languages':original_language,
                'metadata_language':'eng', 'reference_url':url
                })  
        print tvshow_item
        yield tvshow_item

	richmedia_item = RichMediaItem()
        if image_sk:
            richmedia_item.update({'sk':image_sk,
                                    'program_sk':str(tvshow_sk),
                                    'program_type':'tvshow',
                                    'media_type':'image',
                                    'image_type':'poster',
                                    'image_url':image_url,
                                    'reference_url':response.url,
                                    'dimensions':img_dim
                                  })  
            print richmedia_item
            yield richmedia_item 
    
        if release_year or release_date:
                release_item = ReleasesItem()
                release_item.update({'program_sk':str(tvshow_sk),
                                     'program_type':'tvshow',
                                     'release_date':release_date,
                                     'release_year':release_year,
                                     'country' : 'us'})
                print release_item
                yield release_item

        if mpaa_rating:
                rating_item = RatingItem()
                rating_item.update({'program_sk':str(tvshow_sk),
                                    'program_type':'tvshow',
                                    'rating':mpaa_rating,
                                    'rating_type' : 'mpaa_rating'})
                print rating_item
                yield rating_item


        if tvshow_title and "seasons" in data:
            season_data = data.get('seasons','')
	    for data in season_data:
		sk = data.get('id','')
		season_title = data.get('name','').encode('utf-8')
		desc = data.get('overview','').encode('utf-8')
		sn_no = data.get('season_number','')
                sea_url  = "https://www.themoviedb.org/tv/" + str(tvshow_sk) + "/season/" + str(sn_no)
            	season_item = SeasonItem()
            	season_item.update({
                'title': season_title,
                'sk': str(sk), 
                'tvshow_sk': str(tvshow_sk),
                'season_number': str(sn_no),
                'description': normalize(desc),
                'metadata_language': 'us',
                'aux_info': str({'reference_url':response.url}),
                'reference_url': sea_url
                })  
                print season_item
                yield season_item
                epi_num = data.get('episode_count')
                if epi_num >= 1:
                    for i in range(1,epi_num+1):
                        url = "https://api.themoviedb.org/3/tv/"+str(tvshow_sk) + '/season/' +str(sn_no) + '/episode/' + str(i) + '?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&append_to_response=images,videos,credits,reviews,releases'
                        yield Request(url,callback=self.parse_episodes,meta={'tvshow_title':tvshow_title,'season_sk':sk,'tvshow_sk':tvshow_sk})

    def parse_episodes(self, response):
        epi_data = json.loads(response.text)
	tvshow_sk = response.meta.get('tvshow_sk','')
	tvshow_title  = response.meta.get('tvshow_title','')
	season_sk = response.meta.get('season_sk','')
        epi_item = EpisodeItem()
        epi_sk = epi_data.get('id')
	sea_num = epi_data.get('season_number')
	url = "https://www.themoviedb.org/tv/" + str(tvshow_sk) + "/season/" + str(sea_num)
        epi_title = epi_data.get('name').encode('utf-8')
        epi_num = epi_data.get('episode_number')
        epi_desc = epi_data.get('overview').encode('utf-8')
        original_lang = epi_data.get('original_language','')
	epi_image = epi_data.get('still_path')
        if epi_image == None:
            image_url = ""
	    image_sk = ""
	    img_dim = ""
        else:
            image_url = "https://image.tmdb.org/t/p/w300_and_h450_bestv2" + str(epi_image)
            image_sk = image_url.split('_bestv2/')[-1].replace('.jpg','')
            img_dim = ''.join(re.findall('w\d+_and_h\d+',image_url)).replace('w','').replace('h','').replace('_and_','X')

	epi_crew = epi_data.get('credits').get('cast','')
        epi_cast = epi_data.get('credits').get('cast','')
        genres = ""
        duration = ""
	release_date = epi_data.get('air_date')
        release_year = release_date.split('-')[0]
	epi_item.update({'sk':str(epi_sk), 'title':normalize(epi_title),
                    'tvshow_sk':str(tvshow_sk),
                    'show_title':normalize(tvshow_title),
                    'season_sk':str(season_sk), 'duration':str(duration),
                    'episode_number':str(epi_num),
                    'original_languages':original_lang,
                    'season_number':str(sea_num),
                    'genres':genres,
                    'description':normalize(epi_desc),
                    'metadata_language':'eng',
                    'aux_info':str({'json_link':normalize(response.url)}),
                    'reference_url':normalize(url)})
	print epi_item
	yield epi_item
	
	richmedia_item = RichMediaItem()
	if image_sk:
        	richmedia_item.update({'sk':image_sk,
                                    'program_sk':str(epi_sk),
                                    'program_type':'episode',
                                    'media_type':'image',
                                    'image_type':'poster',
                                    'image_url':image_url,
                                    'reference_url':response.url,
                                    'dimensions':img_dim
                                  })  
        	print richmedia_item
        	yield richmedia_item 
    
        if release_year or release_date:
                release_item = ReleasesItem()
                release_item.update({'program_sk':str(epi_sk),
                                     'program_type':'episode',
                                     'release_date':release_date,
                                     'release_year':release_year,
                                     'country' : 'us'})
                print release_item
                yield release_item


	if epi_crew:
            for details in epi_crew:
                id_ = details.get('id')
                url =  "https://api.themoviedb.org/3/person/"+str(id_)+"?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&language=en-US"
                self.get_page('themoviedb_crew_terminal',url,id_,meta_data= {'program_sk':str(epi_sk),'program_type':'episode','reference_url':normalize(url)})
        if epi_cast:
            for details in epi_cast:
                role = details.get('character','')
                rank = details.get('order','')
                id_ = details.get('id')
                url =  "https://api.themoviedb.org/3/person/"+str(id_)+"?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&language=en-US"
                self.get_page('themoviedb_crew_terminal',url,id_,meta_data= {'program_sk':str(epi_sk),'program_type':'episode','person_rank':rank,'reference_url':normalize(url)})

	
