from flask import Flask
from flaskext.mysql import MySQL
import mysql.connector


conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool",
		pool_size=10, autocommit=True, user='root',password='drovosek',host='localhost',database='forum_db')

class Codes:
	ok = 0
	not_found = 1
	invalid_query = 2
	incorrect_query = 3
	unknown_error = 4
	user_exists = 5


	
