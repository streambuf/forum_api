from flask import Flask
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'drovosek'
app.config['MYSQL_DATABASE_DB'] = 'forum_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()

class Codes:
	ok = 0
	not_found = 1
	invalid_query = 2
	incorrect_query = 3
	unknown_error = 4
	user_exists = 5
