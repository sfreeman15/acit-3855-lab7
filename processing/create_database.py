import sqlite3

conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()

c.execute('''
    CREATE TABLE stats (
        id INTEGER PRIMARY KEY ASC,
        num_tp_readings INTEGER NOT NULL,
        max_tp_readings REAL,
        num_tu_readings INTEGER NOT NULL,
        max_tu_readings REAL,
        last_updated VARCHAR(100) NOT NULL
    )
''')

conn.commit()
conn.close()
