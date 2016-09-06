import pymysql
import os

def connection():
    conn = pymysql.connect(host="localhost",
                user = os.environ.get('USER'), password = os.environ.get('PASSWORD'), db = os.environ.get('DB'))

    c = conn.cursor()

    return c, conn
