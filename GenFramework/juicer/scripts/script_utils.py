import os
import re
import sys
import MySQLdb
import logging
import traceback
import ConfigParser
import logging.handlers
from subprocess import Popen, PIPE

from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

DB_USER     = "root"
DB_PASSWD     = ""
LOCAL_IP        = 'localhost'

MYSQL_CONNECT_TIMEOUT_VALUE = 5

PYLINT_PATTERNS = [
    '.*Bad indentation.*',
    'Unused import .*',
    '.*Operator not followed by a space.*\n.*',
    '.*Comma not followed by a space.*\n.*',
    '.*Operator not preceded by a space.*\n.*',
    '.*Unused variable.*'
]

PAR_DIR = os.path.abspath(os.pardir)
OUTPUT_DIR = os.path.join(PAR_DIR, 'spiders/output')
PROCESSING_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processing')
PROCESSED_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'processed')
UNPROCESSED_QUERY_FILES_PATH = os.path.join(OUTPUT_DIR, 'un-processed')
URL_FILES_PROCESSING_DIR = os.path.join(OUTPUT_DIR, 'urls_processing')
URL_FILES_PROCESSED_DIR = os.path.join(OUTPUT_DIR, 'urls_processed')
INVALID_JSON_FILES_DIR = os.path.join(OUTPUT_DIR, 'invalid_jsons')
LOGS_DIR = os.path.join(os.getcwd(), 'logs')

def init_logger(filename, level=''):
   if not os.path.isdir(LOGS_DIR):
        os.mkdir(LOGS_DIR)

   file_name = os.path.join(LOGS_DIR, filename)
   log = logging.getLogger(file_name)
   handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=524288000, backupCount=5)
   formatter = logging.Formatter('%(asctime)s.%(msecs)d: %(filename)s: %(lineno)d: %(funcName)s: %(levelname)s: %(message)s', "%Y%m%dT%H%M%S")
   handler.setFormatter(formatter)
   log.addHandler(handler)
   log.setLevel(logging.DEBUG)

   return log

def get_mysql_connection(server=LOCAL_IP, user=DB_USER, passwd=DB_PASSWD, db_name="", cursorclass=''):
    try:
        from MySQLdb.cursors import Cursor, DictCursor, SSCursor, SSDictCursor
        cursor_dict = {'dict': DictCursor, 'ssdict': SSDictCursor, 'ss': SSCursor }
        cursor_class = cursor_dict.get(cursorclass, Cursor)

        conn = MySQLdb.connect(host=server, user=user, passwd=passwd, db=db_name, connect_timeout=MYSQL_CONNECT_TIMEOUT_VALUE,
                    charset='utf8', use_unicode=True, cursorclass=cursor_class)
        cursor = conn.cursor()

    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        conn, cursor = None, None

    return conn, cursor

def execute_query(cursor, query):
    status = cursor.execute(query)
    return status

def fetchall(cursor, query):
    status = execute_query(cursor, query)
    data = cursor.fetchall()

    return data

def fetchone(cursor, query):
    status = execute_query(cursor, query)
    data = cursor.fetchone()

    return data

def close_mysql_connection(conn, cursor):
    if cursor: cursor.close()
    if conn: conn.close()

def execute_shell_cmd(cmd):
    status, text = 1, ''

    try:
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        status, text = 0, (out or err)
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        traceback.print_exc()

    return status, text

def check_with_pylint(file_name):
    errors = []

    cmd = "pylint %s" % file_name
    status, text = execute_shell_cmd(cmd)
    rating = ''.join(re.findall('Your code has been rated at (.*?)/10 \(', text))
    prev_rating = ''.join(re.findall('\(previous run: (.*)/10', text))

    for pattern in PYLINT_PATTERNS:
        matched_data = re.findall(pattern, text)
        errors.extend(matched_data)

    return rating, prev_rating, "\n".join(errors)

def parse_config_file(config_file):
    _cfg = ConfigParser.SafeConfigParser()
    _cfg.read(config_file)

    return _cfg

def move_file(source, dest=PROCESSED_QUERY_FILES_PATH):
    cmd = "mv %s %s" % (source, dest)
    os.system(cmd)

def remove_empty_files(_dir=UNPROCESSED_QUERY_FILES_PATH, pattern='queries'):
    if os.listdir(_dir):
        cmd = "find %s/*.%s -size 0 -type f -delete" % (_dir, pattern)
        os.system(cmd)
    else:
        print "No Files Found"

def send_html_mail(server, sender, receivers, subject, text, html, image=''):
    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('mixed')
    msgRoot['Subject'] = subject
    msgRoot['From'] = sender
    msgRoot['To'] = ', '.join(receivers)
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText(text, 'text')
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(html, 'html')
    msgAlternative.attach(msgText)

    # This example assumes the image is in the current directory
    if image:
        fp = open(image, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        msgRoot.attach(msgImage)

    # Send the email (this example assumes SMTP authentication is required)
    import smtplib
    smtp = smtplib.SMTP()
    smtp.connect(server)
    #smtp.login('exampleuser', 'examplepass')
    smtp.sendmail(sender, receivers, msgRoot.as_string())
    smtp.quit()

def send_mail(subject, body, to=''):
    msg_body = "<html><body>" + body + "</body></html>"
    subject    = subject
    server     = '10.4.1.112'
    sender     = 'headrun@veveo.net'
    receivers  = to or ['ott@headrun.com', 'karthik@headrun.com']

    send_html_mail(server, sender, receivers, subject, '', msg_body, '')

def get_system_load_avg():
    load_avg = os.getloadavg()
    load_avg_str = ', '.join([str(i) for i in load_avg])

    if load_avg[-1] > 10:
        return  load_avg_str, 0

    return load_avg_str, 1

def check_system_load_avg(file_name='', setup=''):
    load_avg, load_status = get_system_load_avg()
    if not load_status:
        print "Load Avg: %s - Status: %s" % (load_avg, load_status)
        print "Killed the process: File: %s - Setup: %s" % (file_name, setup)
        sys.exit(0)
