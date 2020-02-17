import logging
import calendar
import smtplib
import datetime
import MySQLdb
import sys
sys.path.insert(0, r'/root/hplaybox/Genframework/')
import re
from juicer.pipelines import JuicerPipeline
from juicer.items import *
from juicer.temp_utils import *
# sys.path.insert(0,r'/home/veveo/headrun/Sneha/justwatch_path/SnehaGenframework/')
#sys.path.insert(0, r'/data/veveo/justwatch_prod/Genframework/')
#sys.path.insert(0, r'/root/hplaybox/Genframework/')
#from scrapy.http import FormRequest
#from scrapy.conf import settings
#import mysql.connector as mariadb


class JustwatchMovieTerminal(JuicerSpider):

    def __init__(self, name=None, *args, **kwargs):
        super(JustwatchMovieTerminal, self).__init__(name, *args, **kwargs)
        self.spider = JuicerSpider()
        self.pipeline = JuicerPipeline()
        self.spider.name = "justwatch_movie_terminal"
        self.sks_query = 'select justwatch_id , json_response from Movies where is_valid=0'
        self.crew_sks = 'select justwatch_id , json_response from Crew where justwatch_id= "%s"'
        self.final_itemslist = []
        self.providers_id = []
        self.quality_dict = {}

    def create_cursor(self):
        conn = MySQLdb.connect(host='localhost', user='root', passwd='e3e2b51caee03ee85232537ccaff059d167518e2',
                               db='JUSTWATCHRAWDB', charset='utf8', use_unicode=True)

        cur = conn.cursor()
        return cur, conn

    def main(self):
        cur, conn = self.create_cursor()
        cur.execute(self.sks_query)
        sks_with_data = cur.fetchall()
        for sk in sks_with_data:
            justwatch_sk, json_response = sk
            print(justwatch_sk)
            movie_item = self.get_moviesinfo(justwatch_sk, json_response)

    def yielding_items(self, final_itemslist):
        movie_items = MovieItem()
        for i in final_itemslist:
            movie_items.update(i)
            self.pipeline.process_item(movie_items, self.spider)

    def get_moviesinfo(self, justwatch_sk, res):
        json_data = json.loads(res)
        cur, conn = self.create_cursor()
        status_check = json_data.get('error', '')
        if not status_check:
            movie_sk = json_data.get('id', '')
            title = json_data.get('title', '')
            ref_url = json_data.get('full_path', '')

            try:
                if ref_url and 'http' not in ref_url:
                    ref_url = 'https://www.justwatch.com' + ref_url
            except:
                print(movie_sk)
                '''else:
                ref_url = response.url'''
            desc = json_data.get('short_description', '')
            description = ' '.join(normalize(desc).split('\n'))
            rel_year = json_data.get('original_release_year', '')
            duration = json_data.get('runtime', '')
            if duration:
                duration = int(duration)*60
            else:
                duration = 0
            age_rating = json_data.get('age_certification', '')
            if age_rating:
                rating_type = 'age_rating'
                ratings_item = self.ratings(
                    age_rating, rating_type, str(movie_sk))
                self.pipeline.process_item(ratings_item, self.spider)
            ava_info = json_data.get('offers', '')
            org_titles = json_data.get('original_title', '')
            other_titles = json_data.get('all_titles', '')
            other_titles = '<>'.join(other_titles)
            genres = json_data.get('genre_ids', [])
            org_language = json_data.get('original_language', '')
            if genres:
                try:
                    gen_data = open(
                        "/root/hplaybox/Genframework/juicer/spiders/genre_dict", "r")
                    genre_data = json.loads(gen_data.read())
                except:
                    genre_data = {}
                genre_text = []
                for _id in genres:
                    for i in genre_data.keys():
                        if _id == int(i):
                            genre_name = genre_data.get(
                                i, {}).get('translation', '')
                            genre_text.append(genre_name)
                    gen = '<>'.join(genre_text)

            else:
                gen = ''
            if movie_sk:
                movie_item = MovieItem()
                movie_item.update({'sk': str(movie_sk),
                                   'title': normalize(title),
                                   'original_title': normalize(org_titles),
                                   'other_titles': normalize(other_titles),
                                   'description': normalize(description),
                                   'duration': duration,
                                   'original_languages': normalize(org_language),
                                   'genres': normalize(gen),
                                   'metadata_language': 'English',
                                   'reference_url': normalize(ref_url)
                                   })
                aux = {}
                json_link = "https://apis.justwatch.com/content/titles/movie/%s/locale/en_US" % str(
                    movie_sk)
                clips_sks = []
                clips = json_data.get('clips',[])
                for clip_ in clips:
                    clip_id = clip_.get('external_id','')
                    if clip_.get('provider','') == 'youtube' and 'trailer' in clip_.get('type','').lower():
                        clip_link = 'https://youtu.be/' + str(clip_id)
                        if clip_id: clips_sks.append(clip_link)
                if clips_sks:
                    aux.update({'trailer_info':clips_sks})
                slug = ref_url.strip('/').split('/')[-1]
                if slug:
                    aux.update({'slug':normalize(slug)})
                if json_link:
                    aux.update({'json_link': json_link})
                if aux:
                    movie_item.update({'aux_info': normalize(json.dumps(aux))})
                images_poster = json_data.get('poster','')
                image_sks_list = []
                if images_poster: 
                    images_poster = 'https://images.justwatch.com' + str(images_poster).replace('{profile}','s592')
                    image_sk = images_poster.strip('/').split('/')[-2]
                    image_sks_list.append((image_sk,str(movie_sk),images_poster,ref_url,'poster'))
                back_images = json_data.get('backdrops',[])
                for back in back_images:
                    back_url = back.get('backdrop_url','')
                    if back_url:
                        back_url = 'https://images.justwatch.com' + str(back_url).replace('{profile}','s1440')
                        back_sk = back_url.strip('/').split('/')[-2]
                        image_sks_list.append((back_sk,str(movie_sk),back_url,ref_url,'background'))
                self.pipeline.process_item(movie_item, self.spider)
                release_year = json_data.get('original_release_year', '')
                release_date = json_data.get('localized_release_date','')
                if not release_date:
                    release_date = json_data.get('cinema_release_date','')
                if release_year:
                    releasing_item = self.release(release_year, str(movie_sk),release_date)
                    self.pipeline.process_item(releasing_item, self.spider)
                if image_sks_list:
                    for img_tup in image_sks_list:
                        (image_sk,movie_sk,image_url,ref_url,image_type) = img_tup
                        richmediaitem =  self.richmedia(image_sk,str(movie_sk),image_url,ref_url,image_type)
                        self.pipeline.process_item(richmediaitem,self.spider)
                rating_info = json_data.get('scoring', '')
                for rating in rating_info:
                    rating_type = rating.get('provider_type', '')
                    if 'tomato:rating' in rating_type:
                        rating_type = 'rotten_tomato_rating'
                    if 'imdb:score' in rating_type:
                        rating_type = 'imdb_rating'
                    if 'tmdb:score' in rating_type:
                        rating_type = 'tmdb_rating'

                    value = str(rating.get('value', ''))
                    if rating_type and rating_type in ('tmdb_rating', 'imdb_rating', 'rotten_tomato_rating'):
                        ratings_item = self.ratings(
                            value, rating_type, str(movie_sk))
                        self.pipeline.process_item(ratings_item, self.spider)

                    elif rating_type and rating_type in ('metacritic:score', 'tomato:meter', 'tomato_userrating:meter', 'tmdb:popularity'):
                        value = round(float(value))
                        if value:
                            popularity_item = self.popularity(
                                value, str(movie_sk))
                            self.pipeline.process_item(
                                popularity_item, self.spider)
                rank = 0
                credits = json_data.get('credits', [])
                if credits:
                    for crew_dict in credits:
                        crew_id = crew_dict.get('person_id', '')
                        role = crew_dict.get('role', '')
                        rank += 1
                        role_title = crew_dict.get('character_name', '')
                        self.crew_sk_query = self.crew_sks % crew_id
                        cur.execute(self.crew_sk_query)
                        crew_data = cur.fetchall()
                        for crew in crew_data:
                            crew_sk, crew_json_data = crew
                            self.get_crewinfo(
                                movie_sk, crew_json_data, role, role_title, rank)

                avail_items = []
                avail_item = AvailItem()
                json_list, list_items = [], []
                providers_id = []
                quality_dict = {}
                for id_ in ava_info:
                    provider = id_.get('provider_id', '')
                    if provider:
                        providers_id.append(provider)
                for prov in set(providers_id):
                    qua_list = []
                    for off in ava_info:
                        if prov == off.get('provider_id', ''):
                            quality = off.get('presentation_type', '')
                            quality_key = off.get('urls', {}).get(
                                'standard_web', '')
                            quality_value = self.get_program_sk(
                                quality_key, prov)

                            if quality and quality_value:
                                qua_list.append(quality)
                                quality_dict.update({quality_value: qua_list})
                availability_list = []
                provider_avail_dict = {}
                if ava_info:
                    for ava in ava_info:
                        program_sk = ''
                        provider_id = ava.get('provider_id', '')
                        if provider_id:
                            # if provider_id == 8 or provider_id == 9:
                            if provider_id == 9 or provider_id == 8 or provider_id == 31:
                                url = ava.get('urls', {}).get(
                                    'standard_web', '')
                                program_sk = self.get_program_sk(
                                    url, provider_id)
                                provider_avail_dict.update({program_sk: ava})
                                if provider_id == 9:
                                    url = url.split('?')[0]
                                if provider_id == 31:
                                    url = ava.get('urls', {}).get(
                                        'standard_web', '')

                    if provider_avail_dict:
                        for avail in provider_avail_dict.keys():
                            provider = ''
                            provider_value = provider_avail_dict.get(avail, {})
                            provider = provider_value.get('provider_id', '')
                            if provider:
                                # if provider == 8 or provider == 9:
                                if provider == 9:
                                    self.availitem_yielding_providers(
                                        quality_dict, provider_value, avail, movie_sk, title, duration)
                                if provider == 8:
                                    self.availitem_yielding_providers(
                                        quality_dict, provider_value, avail, movie_sk, title, duration)
                                if provider == 31:
                                    self.availitem_yielding_providers(
                                        quality_dict, provider_value, avail, movie_sk, title, duration)

    def availitem_yielding_providers(self, quality_dict, provider_value, avail, movie_sk, title, duration):
        avail_items = []
        avail_item = AvailItem()
        json_list, list_items = [], []
        quality_list = quality_dict.get(avail, [])
        monetization_type, providerid, last_change_rt_price, retail_price, platform_types, audio_language, subtitle_language, currency, url = [
            '']*9
        if not quality_list:
            quality_list = ['sd']
        for quality in quality_list:
            monetization_type, providerid, last_change_rt_price, retail_price, platform_types, audio_language, subtitle_language, currency, url = self.get_availinfo(
                provider_value)
            for platform in platform_types:
                template_values, template_id = self.get_templates(
                    providerid, platform, avail)
                with_constraint, medium_type, price_type, constraints,  = self.get_othervalues(
                    providerid, retail_price)
                if not retail_price:
                    currency = ''
                scraper_args = {'type': 'movie',
                                'sk': avail, 'justwatch_id': movie_sk}
                avail_dict = {'justwatch_id': movie_sk, 'title': normalize(title), 'platform_id': platform, 'country_code': 'us', 'reference_url': url, 'template_id': template_id, 'template_values': template_values, 'duration': duration, 'last_refreshed_timestamp': str(get_ts_with_seconds().replace(
                    ' ', 'T')), 'program_type': 'movie', 'medium_type': medium_type, 'price': str(retail_price), 'subtitle_languages': subtitle_language, 'audio_languages': audio_language, 'price_type': price_type, 'price_currency': currency, 'quality': quality, 'scraper_args': scraper_args, 'with_constraint': with_constraint, 'constraints': constraints}
                json_list.append(avail_dict)
        avail_item.update({'source_id': str(providerid), 'program_sk': normalize(
            avail), 'source_availabilities': json_list})
        self.pipeline.process_item(avail_item, self.spider)

    def get_crewinfo(self, movie_sk, res, role, role_title, rank):
        i = json.loads(res)
        crew_id = i.get('id', '')
        program_type = 'movie'
        program_sk = movie_sk
        desc = i.get('short_description', '')
        description = ' '.join(normalize(desc).split('\n'))
        name = i.get('full_name', '')
        date_of_birth = i.get('date_of_birth', '')
        also_known_as = i.get('also_known_as', '')
        aux_info = {}
        tmdb_popularity = i.get('tmdb_popularity', '')
        if tmdb_popularity:
            aux_info.update({'tmdb_popularity': tmdb_popularity})
        if also_known_as:
            also_known_as = '<>'.join(also_known_as)
        reference_url = "https://apis.justwatch.com/content/titles/person/%s/locale/en_US" % crew_id
        if crew_id and program_sk:
            crew_item = CrewItem()
            crew_item.update({'sk': str(crew_id), 'name': normalize(name), 'description': normalize(description), 'aka': normalize(
                also_known_as), 'birth_date': str(date_of_birth), 'reference_url': normalize(reference_url), 'aux_info': json.dumps(aux_info)})
            self.pipeline.process_item(crew_item, self.spider)
            program_item = ProgramCrewItem()
            program_item.update({'program_sk': str(program_sk),
                                 'program_type': program_type,
                                 'crew_sk': str(crew_id),
                                 'role': normalize(role),
                                 'rank': str(rank),
                                 'role_title': normalize(role_title)
                                 })
            self.pipeline.process_item(program_item, self.spider)

    def get_othervalues(self, provider_id, price):
        if provider_id == 8:
            medium_type = 'streaming'
            constraints = ["service_subscription"]
            with_constraint = True
            if not price:
                price_type = 'free'
        if provider_id == 9:
            medium_type = 'streaming'
            constraints = ["service_subscription"]
            with_constraint = True
            if not price:
                price_type = 'free'
        if provider_id == 31:
            medium_type = 'streaming'
            constraints = ["cable_subscription"]
            with_constraint = True
            if not price:
                price_type = 'free'
        return with_constraint, medium_type, price_type, constraints

    def get_templates(self, provider_id, platform, program_sk):
        if provider_id == 8:
            if platform:
                template_id = 'netflixusa_movie_%s_jw' % platform
                template_values = {'sk': str(program_sk)}
        if provider_id == 9:

            if platform:

                template_id = 'amazonprime_movie_%s_jw' % platform
                template_values = {'char_sk': str(program_sk)}
        if provider_id == 31:
            if platform:
                template_id = 'hbogo_movie_%s_jw' % platform
                template_values = {'sk': str(program_sk)}

        return template_values, template_id

    def get_program_sk(self, url, provider_id):
        program_sk = ''
        if provider_id == 8:
            program_sk = re.findall(r'\d+', url)[0]
        if provider_id == 9:
            try:
                program_sk = url.split('?')[0].split('/')[-1]
            except:
                print("error in program sk construction for providerid 9")
        if provider_id == 31:
            program_sk = url.split(':')[-1]

        return program_sk

    def get_availinfo(self, ava):
        subtitle_language, audio_language = [], []
        monetization_type = ava.get('monetization_type', '')
        retail_price = ava.get('retail_price', '')
        subtitle_languages = ava.get('subtitle_languages', [])
        audio_languages = ava.get('audio_languages', [])
        if audio_languages:
            audio_language = ['<>'.join(audio_languages)]
        if subtitle_languages:
            subtitle_language = ['<>'.join(subtitle_languages)]
        provider_id = ava.get('provider_id', '')
        currency = ava.get('currency', '')
        last_change_rt_price = ava.get('last_change_retail_price', '')
        quality = ava.get('presentation_type', '')
        if quality == '':
            quality = 'sd'
        urls = ava.get('urls', '')
        platforms = ava.get('urls', {}).keys()
        if provider_id == 31:
            platforms = ['standard_web', 'deeplink_android', 'deeplink_ios']
        platform_types = []
        for i in platforms:
            if i == "standard_web":
                platform_types.append('pc')
            if i == "deeplink_android":
                platform_types.append('android')
            if i == "deeplink_ios":
                platform_types.append('ios')
        url = ava.get('urls', {}).get('standard_web', '')
        if provider_id == 9:
            url = url.split('?')[0]
        return monetization_type, provider_id, last_change_rt_price, retail_price, platform_types, audio_language, subtitle_language, currency, url

    def release(self, year, prog_sk,release_date):
        release_item = ReleasesItem()
        release_item.update({'program_sk': prog_sk,
                             'program_type': 'movie',
                             'release_date': release_date,
                             'release_year': year
                             })
        return release_item
    def richmedia(self,image_sk,prog_sk,image_url,ref_url,image_type):
        richmediaitem = RichMediaItem()
        richmediaitem.update({'sk': image_sk, 'program_sk': normalize(prog_sk), 'program_type': 'movie', 'media_type': 'image',
                              'image_type': image_type, 'image_url': image_url, 'reference_url': ref_url,'size':'large'})
        return richmediaitem

    def ratings(self, rating, _type, prog_sk):
        rating_item = RatingItem()
        rating_item.update({
            'program_sk': prog_sk,
            'program_type': 'movie',
            'rating': str(rating),
            'rating_type': _type
        })
        return rating_item

    def popularity(self, value, prog_sk):
        popular_item = PopularityItem()
        popular_item.update({
            'program_sk': prog_sk,
            'program_type': 'movie',
            'no_of_ratings': str(value)
        })
        return popular_item


if '__main__' == __name__:
    JustwatchMovieTerminal().main()
