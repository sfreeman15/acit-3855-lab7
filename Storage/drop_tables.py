import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE IF EXISTS ticket_upload
          ''')

c.execute('''
          DROP TABLE IF EXISTS ticket_purchase
          ''')

conn.commit()
conn.close()
