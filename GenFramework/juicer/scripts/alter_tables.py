#!/usr/bin/env python
#print sks[0]

import os
import sys
import optparse
import MySQLdb
import traceback
import datetime
import smtplib
from ssh_utils import *
from inspect import getframeinfo, stack

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders


class CreateTables:
    def __init__(self, options):
        self.source = options.source
        self.db     = options.db_name
        self.ip     = options.ip_address
        self.username = options.username
        self.password = options.password
        self.tables = ['channels', 'locations', 'lineup']
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%s')
        self.mail_server = server = '10.4.1.112'
        self.to      = ['epg@headrun.com']
        self.fro = 'headrun@veveo.net'
        self.cc = ['rovi_team@headrun.com']
        self.bcc = []
        self.main()

    def check_options(self):
        if not self.db or not self.ip:
            print "Souce, Db and Ip cant be empty. For more check python create_epg_tables.py --help"
            sys.exit(-1)


    def create_cursor(self, host, db='', user='root'):
        try:
            conn = MySQLdb.connect(host=host, user=user, db=db)
            conn.set_character_set('utf8')
            cursor = conn.cursor()
            cursor.execute('SET NAMES utf8;')
            cursor.execute('SET CHARACTER SET utf8;')
            cursor.execute('SET character_set_connection=utf8;')
            print 'created cursor'
        except:
            print traceback.format_exc()
            sys.exit(-1)

        return conn, cursor

    def ensure_db_exists(self, ip, dbname):
        conn, cursor = self.create_cursor(ip)
        stmt = "SHOW DATABASES LIKE '%s';" % dbname
        cursor.execute(stmt)
        result = cursor.fetchone()
        if result:
            is_existing = True
            print 'valid DB'
        else:
            is_existing = False

        if not is_existing:
            is_existing = False

        cursor.close()
        conn.close()

        return is_existing

    def sendmail(self, text, subject, files=[]):
        '''Actual mail function '''
        files   = []

        assert type(self.to)     == list
        assert type(files)       == list
        assert type(self.cc)     == list
        assert type(self.bcc)    == list

        message             = MIMEMultipart()
        message['From']     = self.fro
        message['To']       = COMMASPACE.join(self.to)
        message['Date']     = formatdate(localtime=True)
        message['Subject']  = subject
        message['Cc']       = COMMASPACE.join(self.cc)
        message.attach(MIMEText(text, 'html'))

        for f in files:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(f, 'rb').read())
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            message.attach(part)

        addresses = []
        for x in self.to:
            addresses.append(x)
        for x in self.cc:
            addresses.append(x)
        for x in self.bcc:
            addresses.append(x)


        try:
            smtp = smtplib.SMTP(self.mail_server)
            smtp.sendmail(self.fro, addresses, message.as_string())
            smtp.close()
        except:
            raise

    def send_stats_mail(self):
        subject = "CLU %s Crawler Status" % self.source.capitalize()
        message = ''
        html = '<html><head><link href="http://getbootstrap.com/dist/css/bootstrap.css" rel="stylesheet"></head>'
        final_report = '<table border="1" style="border-collapse:collapse;" cellpadding="3px" cellspacing="3px"><tr><th>Table Name</th><th> Count</th></tr>'
        message = ''

        for table in self.tables:
            count  = self.today_stats.get(table, 0)
            message += '<tr><td>%s</td><td>%s</td></tr></br>' %(table.capitalize(), str(count))

        final_report = html + final_report + message + '</table></html>'
        self.sendmail(final_report, subject)

    def send_error_mail(self, status_msg):
        if not isinstance(status_msg, list):
            status_msg = [status_msg]

        caller = getframeinfo(stack()[1][0])
        subject = "CLU %s crawler failed with an Exception" % self.source.capitalize()
        message = []
        span_tag = '<span style="%s">%s</span>'
        style    = 'font-family: courier new,monospace;'
        br_tag   = '<br><br>'
        bold_tag = '<b style="color: black;">%s</b>'
        for index, msg in enumerate(status_msg):
            if index == 0:
                style += 'color: #e74c3c;'
            else:
                style += 'color: #34495e;'
            message.append(span_tag % (style, msg))

        self.sendmail(br_tag.join(message), subject)




    def main(self):
        self.check_options()
        if not self.ensure_db_exists(self.ip, self.db):
            print 'Enter valid DB and Ip'
            pass

        conn, cursor = self.create_cursor(self.ip, db=self.db)

        cmd = "alter table Crew add column `age` int(4) DEFAULT '0' after `gender`;"
        try:cursor.execute(cmd)
        except: import traceback; traceback.format_exc()
        cmd = "alter table Crew add column `original_name` varchar(512) COLLATE utf8_unicode_ci NOT NULL after `name`"
        try:cursor.execute(cmd)
        except: import traceback; traceback.format_exc()
        cmd = "alter table OtherMedia add column `original_title` varchar(512) COLLATE utf8_unicode_ci NOT NULL after `title`"
        try: cursor.execute(cmd)
        except: import traceback; traceback.format_exc()

        cmd = "alter table OtherMedia add column `other_titles` varchar(512) COLLATE utf8_unicode_ci NOT NULL after `original_title`"
        try: cursor.execute(cmd)
        except: import traceback; traceback.format_exc()

        cmd = "alter table OtherMedia add column  `category` text COLLATE utf8_unicode_ci after `sub_genres`"
        try: cursor.execute(cmd)
        except: import traceback; traceback.format_exc()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-s', '--source', default='', help='source_name')
    parser.add_option('-d', '--db-name', default='', help = 'dbname')
    parser.add_option('-i', '--ip-address', default='', help= 'ipaddress')
    parser.add_option('', '--username', default='veveo', help= 'Remote Machine Username Ex: root, Default is veveo')
    parser.add_option('', '--password', default='veveo123', help= 'Remote Machiens User Password Ex: oneoneone, Default is veveo123')
    (options, args) = parser.parse_args()
    CreateTables(options)
