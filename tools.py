import MySQLdb
import random

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "mysqlpassword",
                           db = "flaskproject")
    c = conn.cursor()

    return c, conn

def randomString():
    possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.sample(possible, 6))

connection()
randomString()
