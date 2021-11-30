import psycopg2 as pg
import os

TOKEN = os.environ['TELEGRAM_TOKEN']

db_name = os.environ['DB_NAME']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
hostname = os.environ['HOSTNAME']
port = os.environ['PORT']

conn = pg.connect(database=db_name, user=username, password=password, host=hostname, port=port)
