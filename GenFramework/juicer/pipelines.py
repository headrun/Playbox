import json
import datetime
import MySQLdb
from copy import deepcopy
from juicer.items import *
from .json_validator import validate_json_record

class JuicerPipeline(object):
    def get_source(self, spider):
        return spider.name.split('_', 1)[0].strip()

    def write_rec_into_json_file(self, spider, item, avail_file_obj, json_file_obj):
        source = self.get_source(spider)

        json_data = {
            'source_id': source,
            'source_program_id': item['sk'],
            'source_program_id_space': '',
            'source_availabilities': []
        }

        json.dump(json_data, json_file_obj)
        json_file_obj.write('\n')
        json_file_obj.flush()

    def remove_future_content_ts_recs(self, item, availabilities):
        if item.__contains__('is_3d') and item['is_3d']:
            item.pop('is_3d')
        if item.__contains__('content_start_timestamp') and item['content_start_timestamp']:
            cur_dt = str(datetime.datetime.now().date())
            avail_dt = ''.join(re.findall('(\d{4}-\d{2}-\d{2})', item['content_start_timestamp']))
            if avail_dt > cur_dt:
                availabilities.remove(item)

        return availabilities

    def write_record_into_json_file(self, spider, avails):
        source_id, source_program_id, source_program_id_space, availabilities = avails

        for availability in availabilities:
            if availability.__contains__('json_content_type'):
                availability['content_form'] = availability.pop('json_content_type', 'other')
            else:
                availability['content_form'] = ["other", "full"][availability['program_type'] in ['movie', 'tvshow', 'episode', 'season']]
            availability.pop('program_type')
            availability.pop('content_start_timestamp', None)
            availability.pop('content_type', None)
            if availability.__contains__('purchase_type') and not availability['purchase_type']:
                availability.pop('purchase_type')

            if availability.__contains__('price') and str(availability['price']) == '0':
                availability['price'] = ''
            if availability.__contains__('is_3d'):
                availability.pop('is_3d')

            if availability.__contains__('duration'):
                availability['content_runtime_s'] = availability.pop('duration')

            if availability['with_constraint'] == True and availability['price_type'] == 'free' and availability.get('purchase_type') == 'buy':
                availability['purchase_type'] = 'buy'
            elif availability['with_constraint'] == True and availability['price_type'] == 'free':
                availability['purchase_type'] = 'rent'

        avail_dict = {
            'source_id': source_id,
            'source_program_id': source_program_id,
            'source_program_id_space': source_program_id_space,
            'source_availabilities': availabilities
        }
        status = validate_json_record(avail_dict)
        if status:
            spider.store(avail_dict, 'avail_json')

    def process_item(self, item, spider):
        if isinstance(item, MovieItem):
            if not item.get('title', ''):
                self.write_rec_into_json_file(spider, item, spider.get_avail_file(), spider.get_json_file())
                return item
            movie_values = '#<>#'.join([
                item['sk'], item['title'], item.get('original_title', ''), item.get('other_titles', ''),
                item.get('description', ''), item.get('genres', ''), item.get('sub_genres', ''),
                item.get('category', ''), str(item.get('duration', 0)), item.get('languages', ''),
                item.get('original_languages', ''), item.get('metadata_language', ''), item.get('aka', ''),
                item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8"), item.get('reference_url', '')
            ])

            movie_created_values = '#<>#'.join([item['sk'], 'movie'])
            #spider.crawler_stats.stats["Movies"] += 1
            spider.store(movie_values, 'movie')
            spider.get_created_file().write('%s\n' % movie_created_values)
            spider.get_created_file().flush()

        if isinstance(item, TvshowItem):
            if not item.get('title', ''):
                self.write_rec_into_json_file(spider, item, spider.get_avail_file(), spider.get_json_file())
                return item

            tvshow_values = '#<>#'.join([
                item['sk'], item['title'], item.get('original_title', ''), item.get('other_titles', ''),
                item.get('description', ''), item.get('genres', ''), item.get('sub_genres', ''),
                item.get('category', ''), str(item.get('duration', 0)), item.get('languages', ''),
                item.get('original_languages', ''), item.get('metadata_language', ''), item.get('aka', ''),
                item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8"), item.get('reference_url', '')
            ])

            tvshow_created_values = '#<>#'.join([item['sk'], 'tvshow'])
            #spider.crawler_stats.stats["Tvshows"] += 1
            spider.store(tvshow_values, 'tvshow')
            spider.get_created_file().write('%s\n' % tvshow_created_values)
            spider.get_created_file().flush()


        if isinstance(item, SeasonItem):
            season_values = '#<>#'.join([
                item['sk'], item['tvshow_sk'], item['title'], item.get('original_title', ''), item.get('other_titles', ''),
                item.get('description', ''), str(item.get('season_number', 0)), item.get('genres', ''),
                item.get('sub_genres', ''), item.get('category', ''), str(item.get('duration', 0)),
                item.get('languages', ''), item.get('original_languages', ''), item.get('metadata_language', ''),
                item.get('aka', ''), item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8"),
                item.get('reference_url', '')
            ])

            season_created_values = '#<>#'.join([item['sk'], 'season'])
            #spider.crawler_stats.stats["Seasons"] += 1
            spider.store(season_values, 'season')
            spider.get_created_file().write('%s\n' % season_created_values)
            spider.get_created_file().flush()

        if isinstance(item, EpisodeItem):
            if not item.get('title', ''):
                self.write_rec_into_json_file(spider, item, spider.get_avail_file(), spider.get_json_file())
                return item

            episode_values = '#<>#'.join([
                item['sk'], item['season_sk'], item['tvshow_sk'], item['title'], item.get('show_title',''),
                item.get('original_title', ''), item.get('other_titles', ''), item.get('description', ''),
                str(item.get('episode_number', 0)), str(item.get('season_number', 0)), item.get('genres', ''),
                item.get('sub_genres', ''), item.get('category', ''), str(item.get('duration', 0)),
                item.get('languages', ''), item.get('original_languages', ''), item.get('metadata_language', ''),
                item.get('aka', ''), item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8"), 
                item.get('reference_url', '')
            ])

            episode_created_values = '#<>#'.join([item['sk'], 'episode'])
            #spider.crawler_stats.stats["Episodes"] += 1
            spider.store(episode_values, 'episode')
            spider.get_created_file().write('%s\n' % episode_created_values)
            spider.get_created_file().flush()


        if isinstance(item, OtherMediaItem):
            other_media_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['program_type'], item['media_type'], item['title'], 
                item.get('original_title', ''), item.get('other_titles', ''), item.get('description', ''), 
                item.get('genres', ''), item.get('sub_genres', ''),item.get('category', ''),
                str(item.get('duration', 0)), item.get('languages', ''), item.get('original_languages', ''),
                item.get('metadata_language', ''), item.get('aka', ''), item.get('production_country', ''),
                MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8"), item.get('reference_url', '')
            ])

            othermedia_created_values = '#<>#'.join([item['sk'], 'othermedia'])

            spider.store(other_media_values, 'othermedia')
            spider.get_created_file().write('%s\n' % othermedia_created_values)
            spider.get_created_file().flush()


        if isinstance(item, RelatedProgramItem):
            rel_prgm_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['related_sk'], str(item.get('related_rank', '0'))
            ])

            spider.store(rel_prgm_values, 'relatedprogram')

        if isinstance(item, RichMediaItem):
            rich_media_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['program_type'], item['media_type'], item['image_type'],
                item.get('size', ''), item.get('dimensions', ''), item.get('description', ''), item.get('image_url', ''),
                item.get('reference_url', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8")
            ])

            spider.store(rich_media_values, 'richmedia')

        if isinstance(item, RatingItem):
            rating_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['rating'], item['rating_type'], item.get('rating_reason', '')
            ])

            spider.store(rating_values, 'rating')

        if isinstance(item, PopularityItem):
            pop_values = '#<>#'.join([
                item['program_sk'], item['program_type'], str(item.get('no_of_views', 0)), str(item.get('no_of_ratings', 0)),
                str(item.get('no_of_reviews', 0)), str(item.get('no_of_comments', 0)), str(item.get('no_of_likes', 0)),
                str(item.get('no_of_dislikes', 0)), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8")
            ])

            spider.store(pop_values, 'popularity')

        if isinstance(item, CrewItem):
            crew_values = '#<>#'.join([
                item['sk'], item['name'], item.get('original_name', ''), item.get('description', ''), item.get('aka', ''), item.get('gender', ''),item.get('age', ''),
                item.get('blood_group', ''), item.get('birth_date', ''), item.get('birth_place', ''), item.get('death_date', ''),
                item.get('death_place', ''), item.get('constellation', ''), item.get('country', ''), item.get('occupation', ''),
                item.get('biography', ''), item.get('height', ''), item.get('weight', ''), item.get('rating', ''),
                item.get('top_rated_works', ''), str(item.get('no_of_ratings', 0)), item.get('family_members', ''),
                item.get('recent_films', ''), item.get('image', ''), item.get('videos', ''), item.get('reference_url', ''),
                MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8")
            ])

            spider.store(crew_values, 'crew')

        if isinstance(item, ProgramCrewItem):
            prgm_crew_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['crew_sk'], item.get('role', ''),
                item.get('description', ''), item.get('role_title', ''), str(item.get('rank', 0))
            ])

            spider.store(prgm_crew_values, 'programcrew')

        if isinstance(item, AwardsItem):
            award_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['award_name'], item['award_category'], str(item.get('year', 0)),
                item.get('winner', ''), item.get('winner_sk', ''), item.get('winner_type', ''), item.get('winner_flag', ''),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])

            spider.store(award_values, 'awards')

        if isinstance(item, ReleasesItem):
            release_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item.get('company_name',''), item.get('region', ''), item.get('relation',''),
                item.get('company_rights', ''), item.get('release_date', '0000-00-00'), str(item.get('release_year', 0)),
                item.get('country', ''), item.get('studio', ''), str(item.get('is_imax', 0)),
                item.get('is_giant_screens', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8")
            ])

            spider.store(release_values, 'releases')

        if isinstance(item, NewsItem):
            news_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['title'], item.get('description', ''),
                item.get('published_at', '0000-00-00 00:00:00'), item.get('reference_url', ''),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])

            spider.store(news_values, 'news')

        if isinstance(item, ChartItem):
            chart_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['chart_type'], str(item.get('program_rank', 0)),
                str(item.get('week_number', 0)), item.get('week_end_date', '0000-00-00'), str(item.get('no_of_weeks', 0)),
                item.get('currency', ''), item.get('present_week_units', ''), item.get('total_units', ''),
                item.get('present_week_spending', ''), item.get('total_spending', ''), item.get('market_share', ''),
                item.get('reference_url', ''), MySQLdb.escape_string(item.get('aux_info', '')).decode("utf-8")
            ])

            spider.store(chart_values, 'chart')

        if isinstance(item, BoxofficeItem):
            boxoffice_values = '#<>#'.join([
                item['program_sk'], item.get('program_rank',''), str(item.get('weekend_gross', 0)), str(item.get('total_gross', 0)),
                str(item.get('opening_gross', 0)), str(item.get('top_ten_gross', 0)), str(item.get('avg_gross', 0)),
                item.get('currency', ''), item.get('location', ''), str(item.get('no_of_locations', 0)), item.get('gross_type', ''),
                str(item.get('year', 0)), item.get('month', ''), item.get('quarter', ''), item.get('date', '0000-00-00'),
                item.get('weekday', ''), str(item.get('day_number', 0)), str(item.get('week_number', 0)),
                str(item.get('tickets_sold', 0)), str(item.get('visitors', 0)), item.get('release_strategy', '')
            ])

            spider.store(boxoffice_values, 'boxoffice')

        if isinstance(item, ReviewsItem):
            review_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['title'], item.get('reviewed_on', '0000-00-00 00:00:00'),
                item.get('reviewed_by', ''), str(item.get('rating', 0)), item.get('review', ''), item.get('review_url', '')
            ])

            spider.store(review_values, 'reviews')

        if isinstance(item, TheaterItem):
            theater_values = '#<>#'.join([
                item['sks'], item['name'], item['screen'], item['location'], item.get('firm_name', ''),
                str(item.get('is_3d', 0)), str(item.get('no_of_rooms', 0)), str(item.get('no_of_seats', 0)),
                item.get('contact_numbers', ''), str(item.get('zipcode', 0)), str(item.get('latitude', '0.00')),
                str(item.get('longitude', '0.00')), item.get('address', ''), item.get('theater_url', '')
            ])

            spider.store(theater_values, 'theater')

        if isinstance(item, TheaterAvailabilityItem):
            theater_avail_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['theater_sk'], str(item.get('show_time', '0000-00-00 00:00:00')),
                item.get('ticket_booking_link', ''), str(item.get('is_3d', 0))
            ])

            spider.store(theater_avail_values, 'theateravailability')

        if isinstance(item, PrimetimeItem):
            primetime_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['program_title'], str(item.get('report_date', '0000-00-00')),
                item.get('scope', ''), str(item.get('viewers_count', 0)), str(item.get('market_share', 0.00)),
                item.get('reference_url', '')
            ])

            spider.store(primetime_values, 'primetime')

        if isinstance(item, ProgramChartsItem):
            prgm_charts_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['channel_sk'], item['program_title'], str(item.get('hour', 0)),
                str(item.get('minute', 0)), str(item.get('rank', 0)), str(item.get('no_of_views', 0)), str(item.get('votes', 0)),
                str(item.get('rating', 0.0)), item.get('weekday', ''), item.get('week', ''), item.get('month', ''),
                str(item.get('year', 0)), item.get('reference_url')
            ])

            spider.store(prgm_charts_values, 'programcharts')

        if isinstance(item, ChannelItem):
            channel_values = '#<>#'.join([
                item['sk'], item['title'], item.get('description', ''), item.get('genres', ''), item.get('sub_genres', ''),
                item.get('image', ''), item.get('timezone_offset', ''), item.get('reference_url', '')
            ])

            spider.store(channel_values, 'channels')

        if isinstance(item, ChannelChartsItem):
            channel_chart_values = '#<>#'.join([
                item['channel_sk'], item['chart_type'], str(item.get('daily_reach_count', 0)),
                str(item.get('daily_reach_count_in_percentage', 0.0)), str(item.get('weekly_reach_count', 0)),
                str(item.get('weekly_reach_count_in_percentage', 0.0)), str(item.get('avg_pp_weekly_viewing', 0)),
                str(item.get('share', 0)), item.get('week', ''), item.get('month', ''), str(item.get('year', 0)),
                item.get('reference_url')
            ])

            spider.store(channel_chart_values, 'channelcharts')

        if isinstance(item, ScheduleItem):
            schedule_values = '#<>#'.join([
                item['channel_sk'], item['program_sk'], item['program_type'], str(item.get('start_datetime', '000-00-00 00:00:00')),
                str(item.get('duration', 0)), item.get('attributes', '')
            ])

            spider.store(schedule_values, 'schedules')

        if isinstance(item, OtherLinksItem):
            otherlinks_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['program_type'], item['url_type'], item['url']
            ])

            spider.store(otherlinks_values, 'otherlinks')

        if isinstance(item, LocationItem):
            location_values = '#<>#'.join([
                item['sk'], item['country'], item['state'], item['region'], item['sub_region'],
                int(item('zipcode', 0)), item.get('other_id', ''), item.get('reference_url', '')
            ])

            spider.store(location_values, 'loaction')

        if isinstance(item, LineupItem):
            lineup_values = '#<>#'.join([
                item['channel_sk'], item['location_sk'], item['stream_quality'], item['tune_number']
            ])

            spider.store(lineup_values, 'lineup')

        if isinstance(item, AvailItem):
            source_id = item['source_id']
            program_sk = item['program_sk']
            if len(program_sk) > 100:
                program_sk = program_sk[:100]
            source_program_id_space = item.get('source_program_id_space', '')
            availabilities = deepcopy(item['source_availabilities'])
            for avail in item['source_availabilities']:
                if avail.__contains__('title') and not avail['title']:
                    availabilities.remove(avail)
                    continue
                self.remove_future_content_ts_recs(avail, availabilities)
                if avail.__contains__('is_3d'):
                    avail.pop('is_3d')

                if avail.__contains__('price') and (str(avail['price']) == '0' or str(avail['price']) == '0.0' or str(avail['price']).lower() == 'free'):
                    avail['price'] = ''
                    avail['price_type'] = 'free'
                    avail['price_currency'] = ''
                if avail['with_constraint'] == True and avail['price_type'] == 'free' and avail.get('purchase_type') == 'buy':
                    avail['purchase_type'] = 'buy'
                elif avail['with_constraint'] == True and avail['price_type'] == 'free':
                    avail['purchase_type'] = 'rent'
                avail_values = '#<>#'.join([
                    str(avail['justwatch_id']), source_id, program_sk,avail['program_type'], avail['country_code'], avail['platform_id'], avail.get('template_id',''), str(avail['template_values']), str(avail['with_constraint']).lower(), str(avail.get('constraints', '')),
                    avail['medium_type'], avail['price_type'], avail.get('purchase_type', ''), avail['price'], avail['price_currency'],
                    str(avail.get('duration', '')), avail.get('quality', ''), str(avail.get('audio_languages', '')),
                    str(avail.get('subtitle_languages', '')),
                    str(avail.get('is_3d', '')).lower(), avail.get('content_start_timestamp', ''), avail.get('content_expiry_timestamp', ''),
                    avail['last_refreshed_timestamp'], avail['reference_url'], str(avail['scraper_args']), '1'

                ])
                spider.store(avail_values, 'availability')

                #self.provider_list.append(source_id)
                #spider.self.providers_list = list(set(spider.self.providers_list))
            avail_created_values = '#<>#'.join([item['program_sk'], 'availability'])
            spider.get_created_file().write('%s\n' % avail_created_values)
            spider.get_created_file().flush()
            if availabilities:
                for i in availabilities:
                    i.pop('justwatch_id')
                #source_id = availabilities[0]['source_availabilities'][0]['template_id'].split('_')[0].strip()
                source_id = availabilities[0].get('template_id','').split('_')[0].strip()
                avails = (source_id, program_sk, source_program_id_space, availabilities)
                self.write_record_into_json_file(spider, avails)

        return item
