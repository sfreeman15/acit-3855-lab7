# create_tables.py

import sqlite3

def create_event_log_table():
    conn = sqlite3.connect('event_log.sqlite')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS event_log (
            event_id INTEGER PRIMARY KEY ASC,
            message TEXT NOT NULL,
            message_code TEXT NOT NULL,
            date_time VARCHAR(100) NOT NULL
        )
    ''')

    conn.commit()
    conn.close()