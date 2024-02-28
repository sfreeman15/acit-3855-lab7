import mysql.connector


db_conn = mysql.connector.connect(host="acit-3855-lab6a.westus3.cloudapp.azure.com", user="user",
password="password", database="events")

db_cursor = db_conn.cursor()
db_cursor.execute('''
                DROP TABLE ticket_purchase, ticket_upload
                ''')
db_conn.commit()
db_conn.close()

