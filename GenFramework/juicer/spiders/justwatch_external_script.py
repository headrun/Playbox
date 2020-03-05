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
from juicer.utils import *
# sys.path.insert(0,r'/home/veveo/headrun/Sneha/justwatch_path/SnehaGenframework/')
#sys.path.insert(0, r'/data/veveo/justwatch_prod/Genframework/')
#sys.path.insert(0, r'/root/hplaybox/Genframework/')
#from scrapy.http import FormRequest
#from scrapy.conf import settings
#import mysql.connector as mariadb


class JustwatchExternalIds(JuicerSpider):

    def __init__(self, name=None, *args, **kwargs):
        super(JustwatchExternalIds, self).__init__(name, *args, **kwargs)
        self.spider = JuicerSpider()
        self.pipeline = JuicerPipeline()
        self.sks_query = 'select justwatch_id , json_response from Movies where is_valid=0'
        self.insert_query = 'insert into External_ids(justwatch_id,title,tmdb_id,imdb_id,created_at,modified_at)'
        self.insert_query += 'values(%s,%s,%s,%s,now(),now()) on duplicate key update modified_at = now(),tmdb_id = %s, imdb_id=%s, title = %s'

    def create_cursor(self,dbname):
        conn = MySQLdb.connect(host='localhost', user='root', passwd='e3e2b51caee03ee85232537ccaff059d167518e2',
                               db=dbname, charset='utf8', use_unicode=True)

        cur = conn.cursor()
        return cur, conn

    def main(self):
        cur, conn = self.create_cursor('JUSTWATCHRAWDB')
        cur.execute(self.sks_query)
        sks_with_data = cur.fetchall()
        for sk in sks_with_data:
            justwatch_sk, json_response = sk
            print(justwatch_sk)
            self.get_external_ids(justwatch_sk, json_response)


    def get_external_ids(self, justwatch_sk, res):
        json_data = json.loads(res)
        status_check = json_data.get('error', '')
        if not status_check:
            movie_sk = json_data.get('id', '')
            title = json_data.get('title', '')
            external_ids = json_data.get('external_ids',[])
            tmdb_id , imdb_id = '',''

            for i in external_ids:
                provider = i.get('provider','')
                if provider == 'tmdb': tmdb_id = i.get('external_id','')
                if provider == 'imdb': imdb_id = i.get('external_id','')
            values = (movie_sk,title,tmdb_id,imdb_id,tmdb_id,imdb_id,title)
            cur1, conn1 = self.create_cursor('JUSTWATCHOTTDB')
            cur1.execute(self.insert_query, values)


    def create_movie_table(self):
        show_tabl_query = 'SHOW TABLES LIKE "External_ids%%"'
        row_cnt = self.cur1.execute(show_tabl_query)
        if row_cnt:
            return
        table_query = "CREATE TABLE `External_ids` (`justwatch_id` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,`title` varchar(512) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,`tmdb_id` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,`imdb_id` varchar(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,`created_at` datetime DEFAULT '0000-00-00 00:00:00',`modified_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,PRIMARY KEY (`justwatch_id`) )ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;"
        self.cur1.execute(table_query)
        print ("Created table successfully>>>")


if '__main__' == __name__:
    JustwatchExternalIds().main()
