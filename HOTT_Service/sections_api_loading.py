import json
import MySQLdb
import datetime
from optparse import OptionParser
from ConfigParser import SafeConfigParser


_cfg = SafeConfigParser()
_cfg.read('source_sections_details.cfg')

def xcode(text, encoding='utf8', mode='strict'):
    return text.encode(encoding, mode) if isinstance(text, unicode) else text

def xcode_tuple(_tuple):
    _tuple_list = list(_tuple)
    for i in range(len(_tuple_list)):
        if isinstance(_tuple_list[i], unicode) or isinstance(_tuple_list[i], str):
            _tuple_list[i] = xcode(_tuple_list[i])
    return tuple(_tuple_list)


class LoadingSectionsAPI():

    def __init__(self, options=None):

        #self.select_sections = 'select sk, content_type from %s.%s_sections where date(created_at)>=curdate() ;'
        self.select_sections = 'select sk, content_type from %s.%s_sections where date(created_at)>=curdate()-1 ;'
        self.select_api_common = 'select id, source_id, season_id, series_id, item_type, title, episode_title, description, episode_number, season_number, release_year, release_date, expiry_date, genres, maturity_ratings, duration, purchase_info, url, image_url, directors, producers, writers, cast, categories, aux_info  from HOTT_COMMONDB.api_commontable where id="%s" and item_type="%s" and source_id="%s" and is_valid=1 limit 1;'
        query = 'insert into SECTIONS_DB.sections_api (id, source_id, season_id, series_id, item_type, title, episode_title, description, episode_number, season_number, release_year, release_date, expiry_date, genres, maturity_ratings, duration, purchase_info, url, image_url, directors, producers, writers, cast, categories, aux_info, created_at, modified_at) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", utc_timestamp(), utc_timestamp()) '
        duplcate_entry = 'on duplicate key update source_id="%s", season_id="%s", series_id="%s", item_type="%s", title="%s", episode_title="%s", description="%s", episode_number="%s", season_number="%s", release_year="%s", release_date="%s", expiry_date="%s", genres="%s", maturity_ratings="%s", duration="%s", purchase_info="%s", url="%s", image_url="%s", directors="%s", producers="%s", writers="%s", cast="%s",  categories="%s", aux_info="%s", modified_at=utc_timestamp();'
        self.insert_sections_api = query + duplcate_entry

        self.connection = MySQLdb.connect(host='localhost')
        self.connection.set_character_set('utf8')
        self.cursor = self.connection.cursor()

    def loading_sections_api(self):
        sources_list = _cfg.sections()
        for source_name in sources_list:

            sections_db = _cfg.get(source_name, 'db')
            machine_name = _cfg.get(source_name, 'machine_name')
            if '_' in source_name: source_name = source_name.split('_')[0].strip()

	    if machine_name == 'HOTT1':
            	dbServer='localhost'
	    else:
		dbServer='138.201.53.105'

	    global connection
	    global cursor
	    connection = MySQLdb.connect(host='%s' %dbServer)
	    connection.set_character_set('utf8')
	    cursor = connection.cursor()

            cursor.execute(self.select_sections %(sections_db, source_name))
            sections_result = cursor.fetchall()

            for section_rec in sections_result:
                sk, content_type = section_rec
                content_type = content_type.rstrip('s')
                cursor.execute(self.select_api_common %(sk, content_type, source_name))
                api_result = cursor.fetchall()

                for api_rec in api_result:

		    sk, source_id, season_id, series_id, item_type, title, episode_title, description, episode_number, season_number, release_year, release_date, expiry_date, genres, maturity_ratings, duration, purchase_info, url, image_url, directors, producers, writers, cast, categories, aux_info = api_rec

                    title = MySQLdb.escape_string(xcode(title))
                    episode_title = MySQLdb.escape_string(xcode(episode_title))
                    purchase_info = MySQLdb.escape_string(json.dumps(purchase_info))
                    aux_info = MySQLdb.escape_string(aux_info)

		    if description: description = MySQLdb.escape_string(xcode(description))
		    if image_url: image_url = MySQLdb.escape_string(json.dumps(image_url))
                    if genres: genres = MySQLdb.escape_string(json.dumps(genres))
                    if directors: directors = MySQLdb.escape_string(json.dumps(directors))
                    if producers: producers = MySQLdb.escape_string(json.dumps(producers))
                    if writers: writers = MySQLdb.escape_string(json.dumps(writers))
		    if cast: cast = MySQLdb.escape_string(json.dumps(cast))

		    values = xcode_tuple((sk, source_name, season_id,
			series_id, item_type, title,
                        episode_title, description,
			str(episode_number), str(season_number),
			str(release_year), str(release_date),
			str(expiry_date), genres,
                        str(maturity_ratings), str(duration),
                        purchase_info, url, image_url, directors,
                        producers, writers, cast, categories, aux_info))

		    duplcate_values = xcode_tuple((source_name,
			season_id, series_id, item_type,
			title, episode_title, description,
			str(episode_number), str(season_number),
			str(release_year), str(release_date),
			str(expiry_date), genres,
			str(maturity_ratings), str(duration),
			purchase_info, url, purchase_info,
                        directors, producers, writers,
			cast, categories, aux_info))

                    try:
                        self.cursor.execute(self.insert_sections_api % (values + duplcate_values))
                        self.connection.commit()
                    except:
			print "Exception while inserting SECTIONS API"
                        pass

        cursor.close()
        connection.close()

if __name__ == '__main__':
    """
    parser = OptionParser()
    parser.add_option('-d', '--db', default=None, help='Enter db' )
    (options, args) = parser.parse_args()

    lsa = LoadingSectionsAPI(options)
    """
    lsa = LoadingSectionsAPI()
    lsa.loading_sections_api()

