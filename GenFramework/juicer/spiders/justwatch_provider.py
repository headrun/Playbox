import requests
import json
import MySQLdb
from datetime import datetime
header = {
    'User-Agent': 'JustWatch Python client (github.com/dawoudt/JustWatchAPI)'}
requests = requests.Session()


class Provider(object):
    def main(self):
        print ("started____")
        null = None
        conn = MySQLdb.connect(host='localhost', user='root', passwd='e3e2b51caee03ee85232537ccaff059d167518e2',
                               db="JUSTWATCHOTTDB", charset="utf8", use_unicode=True)
        cursor = conn.cursor()
        locale = 'en_US'
        api_url = 'https://apis.justwatch.com/content/providers/locale/{}'.format(
            locale)
        r = requests.get(api_url, headers=header)
        #r = requests.post(api_url, json=eval(payload), headers=HEADER)
        data = json.loads(r.text)
        insert_query = 'insert into Provider_info(id, source_id , provider_name,full_name,short_name,profile_id,slug,icon_url, created_at, modified_at)  values(%s,%s, %s,%s, %s, %s, %s,%s, now(), now()) on duplicate key update modified_at=now()'
        for i in data:
            provider_id = i.get('id', '')
            provider_name = i.get('technical_name', '')
            if provider_name == 'netflix':
                source_id = 'netflixusa'
            elif provider_name == 'play':
                source_id = 'googleplay'
            else:
                source_id = provider_name
            full_name = i.get('clear_name', '')
            short_name = i.get('short_name', '')
            profile_id = i.get('profile_id', '')
            slug = i.get('slug', '')
            icon_url = i.get('icon_url','')
            if icon_url:
                icon_url = 'https://images.justwatch.com' + str(icon_url).replace('{profile}','s100') 
            if provider_id:
                values = (provider_id, source_id, provider_name,
                          full_name, short_name, profile_id, slug,icon_url)
                cursor.execute(insert_query, values)
                conn.commit()


if '__main__' == __name__:
    Provider().main()
