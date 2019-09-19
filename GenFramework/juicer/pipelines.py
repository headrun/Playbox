import re
import json
import datetime
import MySQLdb
from copy import deepcopy
from juicer.items import *

from json_validator import validate_json_record


SOURCES_LIST = {}


class JuicerPipeline(object):

    def get_source(self, spider):
        return spider.name.split('_', 1)[0].strip()

    def write_item_into_avail_file(self, item, spider, content_type):
        source = self.get_source(spider)

        if SOURCES_LIST.has_key(source):
            SOURCES_LIST[source](item, spider.get_avail_file(), spider.get_json_file())

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
        if item.has_key('is_3d') and item['is_3d']:
            item.pop('is_3d')
        if item.has_key('content_start_timestamp') and item['content_start_timestamp']:
            cur_dt = str(datetime.datetime.now().date())
            avail_dt = ''.join(re.findall('(\d{4}-\d{2}-\d{2})', item['content_start_timestamp']))
            if avail_dt > cur_dt:
                availabilities.remove(item)

        return availabilities

    def write_record_into_json_file(self, spider, avails):
        source_id, source_program_id, source_program_id_space, availabilities = avails

        for availability in availabilities:
            if availability.has_key('json_content_type'):
                availability['content_form'] = availability.pop('json_content_type', 'other')
            else:
                availability['content_form'] = ["other", "full"][availability['program_type'] in ['movie', 'tvshow', 'episode', 'season']]
            availability.pop('program_type')
            availability.pop('content_start_timestamp', None)
            availability.pop('content_type', None)
            if availability.has_key('purchase_type') and not availability['purchase_type']:
                availability.pop('purchase_type')

            if availability.has_key('price') and str(availability['price']) == '0':
                availability['price'] = ''
            if availability.has_key('is_3d'):
                availability.pop('is_3d')

            if availability.has_key('duration'):
                availability['content_runtime_s'] = availability.pop('duration')

        avail_dict = {
            'source_id': source_id,
            'source_program_id': source_program_id,
            'source_program_id_space': source_program_id_space,
            'source_availabilities': availabilities
        }

        status = validate_json_record(avail_dict)
        if status:
            json.dump(avail_dict, spider.get_json_file())
            spider.get_json_file().write('\n')
            spider.get_json_file().flush()

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
                item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')), item.get('reference_url', '')
            ])
            spider.get_movie_file().write('%s\n' % movie_values)
            spider.get_movie_file().flush()

            self.write_item_into_avail_file(item, spider, 'movie')

        if isinstance(item, TvshowItem):
            if not item.get('title', ''):
                self.write_rec_into_json_file(spider, item, spider.get_avail_file(), spider.get_json_file())
                return item

            tvshow_values = '#<>#'.join([
                item['sk'], item['title'], item.get('original_title', ''), item.get('other_titles', ''),
                item.get('description', ''), item.get('genres', ''), item.get('sub_genres', ''),
                item.get('category', ''), str(item.get('duration', 0)), item.get('languages', ''),
                item.get('original_languages', ''), item.get('metadata_language', ''), item.get('aka', ''),
                item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')), item.get('reference_url', '')
            ])

            spider.get_tvshow_file().write('%s\n' % tvshow_values)
            spider.get_tvshow_file().flush()
        if isinstance(item, SeasonItem):
            season_values = '#<>#'.join([
                item['sk'], item['tvshow_sk'], item['title'], item.get('original_title', ''), item.get('other_titles', ''),
                item.get('description', ''), str(item.get('season_number', 0)), item.get('genres', ''),
                item.get('sub_genres', ''), item.get('category', ''), str(item.get('duration', 0)),
                item.get('languages', ''), item.get('original_languages', ''), item.get('metadata_language', ''),
                item.get('aka', ''), item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')),
                item.get('reference_url', '')
            ])
            spider.get_season_file().write('%s\n' % season_values)
            spider.get_season_file().flush()

            # Netflixusa Specific Condition
            if item.get('avail_data', {}).get('type', '') == "netflixusa":
                self.write_item_into_avail_file(item, spider, 'season')

        if isinstance(item, EpisodeItem):
            if not item.get('title', ''):
                self.write_rec_into_json_file(spider, item, spider.get_avail_file(), spider.get_json_file())
                return item

            episode_values = '#<>#'.join([
                item['sk'], item.get('season_sk', ''), item.get('tvshow_sk',''), item['title'], item.get('show_title',''),
                item.get('original_title', ''), item.get('other_titles', ''), item.get('description', ''),
                str(item.get('episode_number', 0)), str(item.get('season_number', 0)), item.get('genres', ''),
                item.get('sub_genres', ''), item.get('category', ''), str(item.get('duration', 0)),
                item.get('languages', ''), item.get('original_languages', ''), item.get('metadata_language', ''),
                item.get('aka', ''), item.get('production_country', ''), MySQLdb.escape_string(item.get('aux_info', '')), 
                item.get('reference_url', '')
            ])

            spider.get_episode_file().write('%s\n' % episode_values)
            spider.get_episode_file().flush()

            self.write_item_into_avail_file(item, spider, 'episode')

        if isinstance(item, OtherMediaItem):
            other_media_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['program_type'], item['media_type'], item['title'], 
                item.get('original_title', ''), item.get('other_titles', ''), item.get('description', ''), 
                item.get('genres', ''), item.get('sub_genres', ''),item.get('category', ''),
                str(item.get('duration', 0)), item.get('languages', ''), item.get('original_languages', ''),
                item.get('metadata_language', ''), item.get('aka', ''), item.get('production_country', ''),
                MySQLdb.escape_string(item.get('aux_info', '')), item.get('reference_url', '')
            ])

            spider.get_othermedia_file().write('%s\n' % (other_media_values))
            spider.get_othermedia_file().flush()

        if isinstance(item, RelatedProgramItem):
            rel_prgm_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['related_sk'], str(item.get('related_rank', '0'))
            ])

            spider.get_related_programs_file().write('%s\n' % rel_prgm_values)
            spider.get_related_programs_file().flush()

        if isinstance(item, RichMediaItem):
            rich_media_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['program_type'], item['media_type'], item['image_type'],
                item.get('size', ''), item.get('dimensions', ''), item.get('description', ''), item.get('image_url', ''),
                item.get('reference_url', ''), MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_richmedia_file().write('%s\n' % (rich_media_values))
            spider.get_richmedia_file().flush()

        if isinstance(item, RatingItem):
            rating_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['rating'], item['rating_type'], item.get('rating_reason', '')
            ])
            spider.get_rating_file().write('%s\n' % (rating_values))
            spider.get_rating_file().flush()

        if isinstance(item, PopularityItem):
            pop_values = '#<>#'.join([
                item['program_sk'], item['program_type'], str(item.get('no_of_views', 0)), str(item.get('no_of_ratings', 0)),
                str(item.get('no_of_reviews', 0)), str(item.get('no_of_comments', 0)), str(item.get('no_of_likes', 0)),
                str(item.get('no_of_dislikes', 0)), MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_pop_file().write('%s\n' % (pop_values))
            spider.get_pop_file().flush()

        if isinstance(item, CrewItem): 
            crew_values = '#<>#'.join([
                item['sk'], item['name'], item.get('original_name', ''), item.get('description', ''), item.get('aka', ''), item.get('gender', ''),item.get('age', ''),
                item.get('blood_group', ''), item.get('birth_date', ''), item.get('birth_place', ''), item.get('death_date', ''),
                item.get('death_place', ''), item.get('constellation', ''), item.get('country', ''), item.get('occupation', ''),
                item.get('biography', ''), item.get('height', ''), item.get('weight', ''), item.get('rating', ''),
                item.get('top_rated_works', ''), str(item.get('no_of_ratings', 0)), item.get('family_members', ''),
                item.get('recent_films', ''), item.get('image', ''), item.get('videos', ''), item.get('reference_url', ''),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_crew_file().write('%s\n' % (crew_values))
            spider.get_crew_file().flush()

        if isinstance(item, ProgramCrewItem):
            prgm_crew_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['crew_sk'], item.get('role', ''),
                item.get('description', ''), item.get('role_title', ''), str(item.get('rank', 0)),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_program_crew_file().write('%s\n' % prgm_crew_values)
            spider.get_program_crew_file().flush()

        if isinstance(item, AwardsItem):
            award_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['award_name'], item['award_category'], str(item.get('year', 0)),
                item.get('winner', ''), item.get('winner_sk', ''), item.get('winner_type', ''), item.get('winner_flag', ''),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_award_file().write('%s\n' % (award_values))
            spider.get_award_file().flush()

        if isinstance(item, ReleasesItem):
            release_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item.get('company_name',''), item.get('region', ''), item.get('relation',''),
                item.get('company_rights', ''), item.get('release_date', '0000-00-00'), str(item.get('release_year', 0)),
                item.get('country', ''), item.get('studio', ''), str(item.get('is_imax', 0)),
                item.get('is_giant_screens', ''), MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_release_file().write('%s\n' % (release_values))
            spider.get_release_file().flush()

        if isinstance(item, NewsItem):
            news_values = '#<>#'.join([
                item['sk'], item.get('source', ''),item.get('program_sk', ''),item['program_type'], item['title'], str(item.get('description', '')),
                item.get('published_at', '0000-00-00 00:00:00'), item.get('reference_url', ''),item.get('tags', ''),item.get('keywords', ''),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_news_file().write('%s\n' % (news_values))
            spider.get_news_file().flush()

        if isinstance(item, ChartItem):
            chart_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['chart_type'], str(item.get('program_rank', 0)),
                str(item.get('week_number', 0)), str(item.get('crawl_epoc_time', '')), item.get('week_end_date', '0000-00-00'), str(item.get('no_of_weeks', 0)),
                item.get('currency', ''), item.get('present_week_units', ''), item.get('total_units', ''),
                item.get('present_week_spending', ''), item.get('total_spending', ''), item.get('market_share', ''),
                item.get('reference_url', ''), MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_charts_file().write('%s\n' % (chart_values))
            spider.get_charts_file().flush()

        if isinstance(item, BoxofficeItem):
            boxoffice_values = '#<>#'.join([
                item['program_sk'], item.get('program_rank',''), str(item.get('weekend_gross', 0)), str(item.get('total_gross', 0)),
                str(item.get('opening_gross', 0)), str(item.get('top_ten_gross', 0)), str(item.get('avg_gross', 0)),
                item.get('currency', ''), item.get('location', ''), str(item.get('no_of_locations', 0)), item.get('gross_type', ''),
                str(item.get('year', 0)), item.get('month', ''), item.get('quarter', ''), item.get('date', '0000-00-00'),
                item.get('weekday', ''), str(item.get('day_number', 0)), str(item.get('week_number', 0)),
                str(item.get('tickets_sold', 0)), str(item.get('visitors', 0)), item.get('release_strategy', '')
            ])
            spider.get_boxoffice_file().write('%s\n' % (boxoffice_values))
            spider.get_boxoffice_file().flush()

        if isinstance(item, ReviewsItem):
            review_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['title'], item.get('reviewed_on', '0000-00-00 00:00:00'),
                item.get('reviewed_by', ''), str(item.get('rating', 0)), item.get('review', ''), item.get('review_url', '')
            ])
            spider.get_reviews_file().write('%s\n' % (review_values))
            spider.get_reviews_file().flush()


        if isinstance(item, TheaterItem):
            theater_values = '#<>#'.join([
                item['sks'], item['name'], item['screen'], item['location'], item.get('firm_name', ''),
                str(item.get('is_3d', 0)), str(item.get('no_of_rooms', 0)), str(item.get('no_of_seats', 0)),
                item.get('contact_numbers', ''), str(item.get('zipcode', 0)), str(item.get('latitude', '0.00')),
                str(item.get('longitude', '0.00')), item.get('address', ''), item.get('theater_url', '')
            ])
            spider.get_theater_file().write('%s\n' % (theater_values))
            spider.get_theater_file().flush()

        if isinstance(item, TheaterAvailabilityItem):
            theater_avail_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['theater_sk'], str(item.get('show_time', '0000-00-00 00:00:00')),
                item.get('ticket_booking_link', ''), str(item.get('is_3d', 0))
            ])
            spider.get_theater_avail_file().write('%s\n' % (theater_avail_values))
            spider.get_theater_avail_file().flush()

        if isinstance(item, PrimetimeItem):
            primetime_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['program_title'], str(item.get('report_date', '0000-00-00')),
                item.get('scope', ''), str(item.get('viewers_count', 0)), str(item.get('market_share', 0.00)),
                item.get('reference_url', '')
            ])
            spider.get_primetime_file().write('%s\n' % (primetime_values))
            spider.get_primetime_file().flush()

        if isinstance(item, ProgramChartsItem):
            prgm_charts_values = '#<>#'.join([
                item['program_sk'], item['program_type'], item['channel_sk'], item['program_title'], str(item.get('hour', 0)),
                str(item.get('minute', 0)), str(item.get('rank', 0)), str(item.get('no_of_views', 0)), str(item.get('votes', 0)),
                str(item.get('rating', 0.0)), item.get('weekday', ''), item.get('week', ''), item.get('month', ''),
                str(item.get('year', 0)), item.get('reference_url')
            ])
            spider.get_program_charts_file().write('%s\n' % (prgm_charts_values))
            spider.get_program_charts_file().flush()

        if isinstance(item, ChannelItem):
            channel_values = '#<>#'.join([
                item['sk'], item['title'], item.get('description', ''), item.get('genres', ''), item.get('sub_genres', ''),
                item.get('image', ''), item.get('timezone_offset', ''), item.get('reference_url', '')
            ])
            spider.get_channel_file().write('%s\n' % (channel_values))
            spider.get_channel_file().flush()

        if isinstance(item, ChannelChartsItem):
            channel_chart_values = '#<>#'.join([
                item['channel_sk'], item['chart_type'], str(item.get('daily_reach_count', 0)),
                str(item.get('daily_reach_count_in_percentage', 0.0)), str(item.get('weekly_reach_count', 0)),
                str(item.get('weekly_reach_count_in_percentage', 0.0)), str(item.get('avg_pp_weekly_viewing', 0)),
                str(item.get('share', 0)), item.get('week', ''), item.get('month', ''), str(item.get('year', 0)),
                item.get('reference_url')
            ])
            spider.get_channel_charts_file().write('%s\n' % (channel_chart_values))
            spider.get_channel_charts_file().flush()

	if isinstance(item, LastfmChartsItem):
            lastfm_chart_values = '#<>#'.join([
                item['chart'], str(item.get('region', '')), item['type'],
                str(item.get('week', '')), str(item.get('tag', '')),
                str(item.get('entity_id', '')), str(item.get('song_sk', '')), str(item.get('artist_sk', '')),str(item['rank']),
            ])
            spider.get_lastfm_charts_file().write('%s\n' % (lastfm_chart_values))
            spider.get_lastfm_charts_file().flush()

	if isinstance(item, LastfmArtistGenreItem):
            channel_chart_values = '#<>#'.join([
                item['artist_id'], item['genre'], item.get('weight', 0)
            ])
            spider.get_lastfm_artistgenre_file().write('%s\n' % (channel_chart_values))
            spider.get_lastfm_artistgenre_file().flush()

	if isinstance(item, LastfmArtistSimilarItem):
            channel_chart_values = '#<>#'.join([
                item['artist_id'], item['similar_id'], item.get('similarity','')
            ])
            spider.get_lastfm_artistsimilar_file().write('%s\n' % (channel_chart_values))
            spider.get_lastfm_artistsimilar_file().flush()


	if isinstance(item, LastfmBiographyItem):
            channel_chart_values = '#<>#'.join([
                item['id'], item['language'], item.get('biography','')
            ])
            spider.get_lastfm_biography_file().write('%s\n' % (channel_chart_values))
            spider.get_lastfm_biography_file().flush()

        if isinstance(item, LastfmSongsItem):
            lastfm_songs_values = '#<>#'.join([
                str(item['id']),item['uri_sk'],item['title'],str(item.get('listeners', 0)),str(item.get('scrobbles', 0)),
                item.get('overview', ''), item.get('genres', ''), str(item.get('runtime', '')), MySQLdb.escape_string(item.get('aux_info', '')), str(item.get('is_valid', 1)), item.get('song_crawled', ''), str(item.get('crawl_status', '1'))
            ])
            spider.get_lastfm_songs_file().write('%s\n' % (lastfm_songs_values))
            spider.get_lastfm_songs_file().flush()

        if isinstance(item, LastfmAlbumItem):
            lastfm_album_values = '#<>#'.join([
                str(item['id']),item['uri_sk'],item['title'],str(item.get('listeners', 0)),str(item.get('scrobbles', 0)),
                item.get('label', ''),item.get('genres', ''),item.get('release_date', '0000-00-00'), str(item.get('runtime', '')),
                item.get('overview', ''), item.get('image', ''), str(item.get('num_tracks', 0)), MySQLdb.escape_string(item.get('aux_info', '')),
                str(item.get('is_valid', 1)),  item.get('album_crawled', ''), str(item.get('crawl_status', ''))
            ])
            spider.get_lastfm_album_file().write('%s\n' % (lastfm_album_values))
            spider.get_lastfm_album_file().flush()


        if isinstance(item, LastfmArtistItem):
	    channel_chart_values = '#<>#'.join([
                str(item['id']),item['uri_sk'],item['title'],str(item.get('listeners', 0)),str(item.get('scrobbles', 0)),
                item.get('overview', ''), item.get('genres', ''), str(item.get('image', '')), str(item.get('is_valid', 1)), item.get('similar_artists_crawled', ''),
                item .get('albumfully_crawled', ''), item.get('is_bio_crawled', '')
            ])
            spider.get_lastfm_artist_file().write('%s\n' % (channel_chart_values))
            spider.get_lastfm_artist_file().flush()

        if isinstance(item, SpotifyAlbumItem):
            channel_chart_values = '#<>#'.join([
                item['artist_id'], item['album_id'], item.get('album_name',''), str(item.get('released', 0)), item.get('availability',''), 
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_spotify_album_file().write('%s\n' % (channel_chart_values))
            spider.get_spotify_album_file().flush()

        if isinstance(item, SpotifyArtistItem):
            channel_chart_values = '#<>#'.join([
                item['artist_id'], item.get('artist_name',''), str(item.get('artist_popularity', 0)), MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_spotify_artist_file().write('%s\n' % (channel_chart_values))
            spider.get_spotify_artist_file().flush()

        if isinstance(item, SpotifyArtistsCrawledItem):
            channel_chart_values = '#<>#'.join([
                item['artist_name'], item.get('scrobbles',''), str(item.get('is_crawled', 0))
            ])
            spider.get_spotify_artistscrawled_file().write('%s\n' % (channel_chart_values))
            spider.get_spotify_artistscrawled_file().flush()

        if isinstance(item, SpotifyTracksItem):
            channel_chart_values = '#<>#'.join([
                item['artist_id'], item['album_id'], item['track_id'], item.get('track_name', ''), str(item.get('track_number', 0)),
                item.get('track_available',''), str(item.get('track_length', 0)), str(item.get('track_popularity', 0)),
                MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_spotify_tracks_file().write('%s\n' % (channel_chart_values))
            spider.get_spotify_tracks_file().flush()

        if isinstance(item, TwitterArtistItem):
            channel_chart_values = '#<>#'.join([
            item['sk'], item.get('gid', ''), item.get('title', ''), str(item.get('friends_count', 0)), str(item.get('followers_count', 0)),
            item.get('reference_url', ''), MySQLdb.escape_string(item.get('aux_info', ''))
            ])
            spider.get_twitter_artist_file().write('%s\n' % (channel_chart_values))
            spider.get_twitter_artist_file().flush()
        
        if isinstance(item, TwitterRelatedArtistsItem):
            channel_chart_values = '#<>#'.join([
            item['artist_sk'], item['related_sk'], item.get('related_gid', ''), item.get('related_title', '')
            ])
            spider.get_twitter_relatedartists_file().write('%s\n' % (channel_chart_values))
            spider.get_twitter_relatedartists_file().flush()

        if isinstance(item, ScheduleItem):
            schedule_values = '#<>#'.join([
                item['channel_sk'], item['program_sk'], item['program_type'], str(item.get('start_datetime', '000-00-00 00:00:00')),
                str(item.get('duration', 0)), item.get('attributes', '')
            ])
            spider.get_schedule_file().write('%s\n' % (schedule_values))
            spider.get_schedule_file().flush()

        if isinstance(item, OtherLinksItem):
            otherlinks_values = '#<>#'.join([
                item['sk'], item['program_sk'], item['program_type'], item['url_type'], item['url'], item.get('domain','')
            ])
            spider.get_otherlinks_file().write('%s\n' % (otherlinks_values))
            spider.get_otherlinks_file().flush()

        if isinstance(item, LocationItem):
            location_values = '#<>#'.join([
                item['sk'], item['country'], item['state'], item['region'], item['sub_region'],
                int(item('zipcode', 0)), item.get('other_id', ''), item.get('reference_url', '')
            ])
            spider.get_location_file().write('%s\n' % (location_values))
            spider.get_location_file().flush()

        if isinstance(item, LineupItem):
            lineup_values = '#<>#'.join([
                item['channel_sk'], item['location_sk'], item['stream_quality'], item['tuner_number']
            ])
            spider.get_lineup_file().write('%s\n' % (lineup_values))
            spider.get_lineup_file().flush()

        if isinstance(item, AvailItem):
            source_id = item['source_id']
            program_sk = item['program_sk']
            source_program_id_space = item.get('source_program_id_space', '')
            availabilities = deepcopy(item['source_availabilities'])

            for avail in item['source_availabilities']:
                if avail.has_key('title') and not avail.get('title', ''):
                    availabilities.remove(avail)
                    continue

                self.remove_future_content_ts_recs(avail, availabilities)
                if avail.has_key('is_3d'):
                    avail.pop('is_3d')

                avail_values = '#<>#'.join([
                    program_sk, avail['program_type'], avail['country_code'], avail['platform_id'], avail['template_id'],
                    str(avail['template_values']),str(avail['with_subscription']).lower(), avail.get('subscription_type', ''),
                    avail['medium_type'], avail['price_type'], avail.get('purchase_type', ''), avail['price'], avail['price_currency'],
                    str(avail.get('duration', '')), avail['quality'], str(avail.get('audio_languages', '')), str(avail.get('subtitle_languages', '')),
                    str(avail.get('is_3d', '')).lower(), avail.get('content_start_timestamp', ''), avail.get('content_expiry_timestamp', ''),
                    avail['last_refreshed_timestamp'], avail['reference_url'], str(avail['scraper_args']), '1'

                ])
                spider.get_avail_file().write('%s\n' % avail_values)
                spider.get_avail_file().flush()

            if availabilities:
                avails = (source_id, program_sk, source_program_id_space, availabilities)
                self.write_record_into_json_file(spider, avails)

        return item
