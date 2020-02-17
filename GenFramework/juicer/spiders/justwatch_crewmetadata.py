from juicer.utils import *
from juicer.items import *
from scrapy.http import FormRequest
import MySQLdb
import datetime
import smtplib
import calendar
import logging
import re

conn = MySQLdb.connect(host='localhost', user='root', passwd='e3e2b51caee03ee85232537ccaff059d167518e2',
                       db='JWURLQUEUE_PROD', charset='utf8', use_unicode=True)
cur = conn.cursor()


class JustwatchRaw(JuicerSpider):
    name = 'justwatch_crew_metadata'
    start_urls = []
    query = 'select distinct(sk) from justwatch_crawl where content_type = "crew" and crawl_status=0 limit 10000'
    cur.execute(query)
    sks_list = cur.fetchall()
    for sk in sks_list:
        start_url = 'https://apis.justwatch.com/content/titles/person/%s/locale/en_US' % str(
            sk[0])
        start_urls.append(start_url)

    def __init__(self, *args, **kwargs):
        super(JustwatchRaw, self).__init__(*args, **kwargs)
        self.conn1 = MySQLdb.connect(host='localhost', user='root', passwd='e3e2b51caee03ee85232537ccaff059d167518e2',
                                     db='JUSTWATCHRAWDB', charset='utf8', use_unicode=True)
        self.cur1 = self.conn1.cursor()
        #self.update_query1 = "update justwatch_crawl set crawl_status=1 where content_type='crew' and sk= %s"
        self.delete_query = 'delete from justwatch_crawl where crawl_status=1 and content_type="crew" and sk= %s'
        self.update_query1 = "update  justwatch_crawl set crawl_status=1, modified_at=now() where content_type='crew' and sk= %s"
        self.create_crew_table()

    def parse(self, response):
        sel = Selector(response)
        data = response.body
        json_data = json.loads(data)
        crew_sk = json_data.get('id', '')
        if crew_sk:
            insert_query = 'insert into Crew(justwatch_id,json_response,created_at,modified_at)'
            insert_query += 'values(%s,%s,now(),now()) on duplicate key update modified_at = now() ,json_response= %s'
            values = (crew_sk, json.dumps(json_data), json.dumps(json_data))
            self.cur1.execute(insert_query, values)
            cur.execute(self.delete_query % crew_sk)
            cur.execute(self.update_query1 % crew_sk)

    def create_crew_table(self):
        show_tabl_query = 'SHOW TABLES LIKE "Crew%%"'
        row_cnt = self.cur1.execute(show_tabl_query)
        if row_cnt:
            return

        table_query = "CREATE TABLE IF NOT EXISTS `Crew` (`justwatch_id` varchar(200) COLLATE utf8_unicode_ci NOT NULL, "
        table_query += "`json_response` longtext COLLATE utf8_unicode_ci NOT NULL, "
        table_query += "`created_at` datetime DEFAULT '0000-00-00 00:00:00', "
        table_query += "`modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, "
        table_query += "PRIMARY KEY (`justwatch_id`) "
        table_query += ") ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci "
        self.cur1.execute(table_query)
        print("Created table successfully>>>")
