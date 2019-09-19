#!/usr/bin/env python
import sys
import optparse
import MySQLdb
import datetime

class CalculateDuration:
    def __init__(self, options):
        self.db     = options.db_name
        self.ip     = options.ip_address
        self.main()

    def check_options(self):
        if not self.db or not self.ip:
            print "Souce, Db and Ip cant be empty. For more check python calculate_duration.py --help"
            sys.exit(-1)


    def create_cursor(self, host, db):
        try:
            conn = MySQLdb.connect(user='root',host='localhost', db=db)
            conn.set_character_set('utf8')
            cursor = conn.cursor()
            cursor.execute('SET NAMES utf8;')
            cursor.execute('SET CHARACTER SET utf8;')
            cursor.execute('SET character_set_connection=utf8;')
        except:
            import traceback; print traceback.format_exc()
            sys.exit(-1)

        return conn, cursor

    def ensure_db_exists(self, ip, dbname):
        conn, cursor = self.create_cursor(ip, dbname)
        stmt = "show databases like '%s';" % dbname
        cursor.execute(stmt)
        result = cursor.fetchone()
        if result:
            is_existing = True
        else:
            is_existing = False

        cursor.close()
        conn.close()

        return is_existing

    def main(self):
        self.check_options()

        if not self.ensure_db_exists(self.ip, self.db):
            print 'Enter valid DB and Ip'
            pass

        conn, cursor = self.create_cursor(self.ip, self.db)
        query = 'select sk from Channel order by sk asc;'
        cursor.execute(query)
        channels  = cursor.fetchall()

        for _id in channels:
            _id = _id[0]
            query = 'select channel_sk, program_sk, program_type, start_datetime, duration from  Schedules where channel_sk = "%s" order by start_datetime asc;'
            query = query % _id
            cursor.execute(query)
            records = cursor.fetchall()

            for index, record in enumerate(records):
                channel_sk, program_sk, program_type, start_time, s_duration = record
                duration = 0

                try:
                    end_time = records[index + 1][-2]
                    duration = int((end_time - start_time).total_seconds())
                except IndexError:
                    endtime_format = str((start_time + datetime.timedelta(days = 1)).date()) + ' 00:00'
                    end_time = datetime.datetime.strptime(endtime_format, '%Y-%m-%d %H:%M')
                    duration = int((end_time - start_time).total_seconds())

                query = 'update Schedules set duration = %s, modified_at=now() where channel_sk = "%s" and program_sk =  "%s" and program_type = "%s" and start_datetime = "%s";'  % (duration, channel_sk, program_sk, program_type, start_time)
                cursor.execute(query)

        cursor.close()
        conn.close()


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-d', '--db-name', default='', help = 'dbname')
    parser.add_option('-i', '--ip-address', default='', help= 'ipaddress')
    (options, args) = parser.parse_args()
    CalculateDuration(options)
