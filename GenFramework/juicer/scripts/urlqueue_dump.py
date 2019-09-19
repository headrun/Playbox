import MySQLdb
import re
import json

DB_NAME = 'SINEMATURKOBDB'
DB_IP = '10.4.18.108'

def get_cursor(DB_IP, DB_NAME):
    conn       = MySQLdb.connect(host=DB_IP, user="root", db=DB_NAME, charset="utf8")
    cursor = conn.cursor()
    return conn, cursor

def main():
    cursor = get_cursor(DB_IP, DB_NAME)
    query = 'select sk, reference_url from Movie;'
    conn, cursor = get_cursor(DB_IP, DB_NAME)
    cursor.execute(query)
    records = cursor.fetchall()

    conn, cursor = get_cursor(DB_IP, 'urlqueue_dev')
    for record in records:
        sk, reference_url  = record

        query = 'insert into sinematurk_crawl(sk, url, crawl_type, content_type, created_at, modified_at)'
        query += 'values (%s, %s, %s, %s, now(), now())on duplicate key update modified_at=now()'
        values = (sk, reference_url, 'keepup', 'movie')
        try:
            cursor.execute(query, values)
            conn.commit()
        except:
            import traceback; traceback.format_exc()


if __name__ == "__main__":
    main()

