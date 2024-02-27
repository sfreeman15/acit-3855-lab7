import mysql.connector


db_conn = mysql.connector.connect(host="acit-3855-kafka.westus3.cloudapp.azure.com", user="user",
password="", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
        CREATE TABLE ticket_purchase
        (id INT NOT NULL AUTO_INCREMENT,
        ticket_id VARCHAR(250) NOT NULL,
        seat_number VARCHAR(250) NOT NULL,
        concert_name VARCHAR(250) NOT NULL,
        artist VARCHAR(250) NOT NUll,
        date VARCHAR(100) NOT NULL,
        venue VARCHAR(250) NOT NULL,
        price REAL NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        CONSTRAINT ticket_id PRIMARY KEY (id))
    ''')
db_cursor.execute('''
        CREATE TABLE ticket_upload
        (id INT NOT NULL AUTO_INCREMENT,
        ticket_id VARCHAR(250) NOT NULL,
        seller_name VARCHAR(250) NOT NULL, 
        seat_number VARCHAR(250) NOT NULL,
        concert_name varchar(250) NOT NULL,
        artist VARCHAR(250) NOT NUll,
        date VARCHAR(100) NOT NULL,
        venue VARCHAR(250) NOT NULL,
        price REAL NOT NULL,
        trace_id VARCHAR(250) NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        CONSTRAINT ticket_upload_pk PRIMARY KEY (id))
        ''')
db_conn.commit()
db_conn.close()