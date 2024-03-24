import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE IF EXISTS event_logs
          ''')



conn.commit()
conn.close()
