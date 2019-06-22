from flask import render_template

from info import redis_store

from info.modules.index import index_blu


@index_blu.route('/')
def index():
    # redis_store.set("qqq", "dddddpjjjpppp")
    return render_template("news/index.html")


