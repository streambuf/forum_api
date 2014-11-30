# -*- coding: utf-8 -*-
from flask import Flask, render_template, g
from forum.forum import forum
from forum.thread import thread
from forum.post import post
from forum.user import user
from forum.other import other

app = Flask(__name__)
app.debug = True

app.register_blueprint(forum)
app.register_blueprint(thread)
app.register_blueprint(post)
app.register_blueprint(user)
app.register_blueprint(other)


@app.route('/')
def hello():
    tml = "test.html"
    return render_template(tml)

if __name__ == '__main__':
    app.run() 


