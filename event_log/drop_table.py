import sqlite3

conn = sqlite3.connect('event_log.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE IF EXISTS event_logs
          ''')



conn.commit()
conn.close()
