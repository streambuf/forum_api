# -*- coding: utf-8 -*-
from flask import Flask, render_template, g
from forum.forum import forum
from forum.thread import thread
from forum.post import post
from forum.user import user
from forum.other import other
import mysql.connector

app = Flask(__name__)
app.debug = True

app.register_blueprint(forum)
app.register_blueprint(thread)
app.register_blueprint(post)
app.register_blueprint(user)
app.register_blueprint(other)

@app.before_first_request
def before_first_request():
	g.cnx_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pool",
		pool_size=10, autocommit=True, user='root',password='drovosek',host='localhost',database='forum_db')
	print "hi"

@app.route('/')
def hello():
    tml = "test.html"
    return render_template(tml)

if __name__ == '__main__':
    app.run()





