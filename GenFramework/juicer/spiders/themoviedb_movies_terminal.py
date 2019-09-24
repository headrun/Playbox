import collections
from juicer.items import MovieItem, CrewItem, ProgramCrewItem, AvailItem, \
                         RichMediaItem, RatingItem, ReleasesItem
from juicer.hott_utils import *
import sys 
reload(sys)
sys.setdefaultencoding('utf-8')


class ThemoviedbMoviesTerminal(JuicerSpider):
    name = 'themoviedb_movies_terminal'

    def __init__(self, *args, **kwargs):
        super(ThemoviedbMoviesTerminal, self).__init__(*args, **kwargs)


    def parse(self, response):
        sk = ''.join(re.findall('\d+',response.url.split('/movie')[-1]))
        reference_url = response.url
        url = "https://api.themoviedb.org/3/movie/" +str(sk) +"?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&append_to_response=images,videos,credits,reviews,releases"
        yield Request(url,callback = self.parse_next,meta={'url':reference_url})

    def parse_next(self, response):
        url  = response.meta['url']
        data = json.loads(response.text)
        desc = data.get('overview','')
        movie_sk = data.get('id','')
        title = data.get('title','').encode('utf=8')
        images = data.get('poster_path','')
        original_title= data.get('original_title','').encode('utf-8')
        original_language =  data.get('original_language','')
        if images == None:
            image_url = ""
        else:
            image_url = "https://image.tmdb.org/t/p/w300_and_h450_bestv2" + images
        genre_ = data.get('genres','')
        genres_ = []
        for genre in genre_:
            genres = genre.get('name','')
            genres_.append(genres)
	duration_ = str(data.get('runtime',''))
	release_date = data.get('release_date','')
	release_year = release_date.split('-')[0]
        if duration_ == 'None':
            dur = 0
        else:
            dur = int(duration_) * 60
        duration = str(dur)
        mpaa_ = data.get('releases','').get('countries','')
        for rating in mpaa_:
            mpaa_release = rating.get('release_date','')
            if release_date  == mpaa_release:
                mpaa_rating = rating.get('certification','')
            
        image_sk = image_url.split('_bestv2/')[-1].replace('.jpg','')
        img_dim = ''.join(re.findall('w\d+_and_h\d+',image_url)).replace('w','').replace('h','').replace('_and_','X')
	credits   = data.get('credits', []) 
        cast = credits.get('cast','')
        crew = credits.get('crew','')
        movieitem = MovieItem()
        movieitem.update({
                'sk':str(movie_sk), 'title':str(title),'original_title':str(original_title), 'description':normalize((str(desc))),
                'genres':'<>'.join(genres_),'aux_info':str({'reference_url':response.url}),'original_languages':original_language,
                'duration':duration,'metadata_language':'eng', 'reference_url':url
                })
        print movieitem
        yield movieitem

        richmedia_item = RichMediaItem()
        richmedia_item.update({'sk':image_sk,
                                    'program_sk':str(movie_sk),
                                    'program_type':'movie',
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
                release_item.update({'program_sk':str(movie_sk),
                                     'program_type':'movie',
                                     'release_date':release_date,
                                     'release_year':release_year,
                                     'country' : 'us'})
	        print release_item
                yield release_item

	if mpaa_rating:
                rating_item = RatingItem()
                rating_item.update({'program_sk':str(movie_sk),
                                    'program_type':'movie',
                                    'rating':mpaa_rating,
                                    'rating_type' : 'mpaa_rating'})
	        print rating_item
                yield rating_item

        if crew:
                type_vs_name = {}
                for details in crew:
                    id_ = details.get('id')
                    url =  "https://api.themoviedb.org/3/person/"+str(id_)+"?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&language=en-US"
                    self.get_page('themoviedb_crew_terminal',url,id_,meta_data= {'program_sk':str(movie_sk),'program_type':'movie','reference_url':url})
        if cast:
            type_vs_name = {}
            for details in cast:
                role = details.get('character','')
                rank = details.get('order','')
                id_ = details.get('id')
                url =  "https://api.themoviedb.org/3/person/"+str(id_)+"?api_key=e3a72d3678ff1f7d7ff54ae4b0c2df0e&language=en-US"
                self.get_page('themoviedb_crew_terminal',url,id_,meta_data= {'program_sk':str(movie_sk),'program_type':'movie','person_rank':rank,'reference_url':url})
