import psycopg2 as pg
import os
import re

TOKEN = os.environ['TELEGRAM_TOKEN']

DATABASE_URL = os.environ['DATABASE_URL']
parsed = re.findall('[\w\.-]+', DATABASE_URL)

username = parsed[1]
password = parsed[2]
hostname = parsed[3]
port = parsed[4]
db_name = parsed[5]

conn = pg.connect(database=db_name, user=username, password=password, host=hostname, port=port, sslmode='require')
