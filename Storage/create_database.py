import sqlite3
import pymysql
import mysql.connector

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE ticket_purchase
          (id INTEGER PRIMARY KEY ASC, 
           ticket_id VARCHAR(250) NOT NULL,
           seat_number VARCHAR(250) NOT NULL,
           concert_name VARCHAR(250) NOT NULL,
           date VARCHAR(100) NOT NULL,
           venue VARCHAR(250) NOT NULL,
           price REAL NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL)
          ''')


c.execute('''
          CREATE TABLE ticket_upload
          (id INTEGER PRIMARY KEY ASC, 
           ticket_id VARCHAR(250) NOT NULL,
           seller_name VARCHAR(250) NOT NULL,
           seat_number VARCHAR(250) NOT NULL,
           concert_name varchar (250) NOT NULL,
           date VARCHAR(100) NOT NULL,
           venue VARCHAR(250) NOT NULL,
           price REAL NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(250) NOT NULL)
          ''')

conn.commit()
conn.close()
