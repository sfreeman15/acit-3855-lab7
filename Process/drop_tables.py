import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE IF EXISTS stats
          ''')



conn.commit()
conn.close()
