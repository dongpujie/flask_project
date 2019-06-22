from flask import render_template, current_app

from info import redis_store

from info.modules.index import index_blu


@index_blu.route('/')
def index():
    # redis_store.set("qqq", "dddddpjjjpppp")
    return render_template("news/index.html")


# 在打开网页的时候，浏览器会默认去请求根路径+favicon.ico作网站标签的小图标
# send_static_file 是 flask 去查找指定的静态文件所调用的方法
# @index_blu.route('/favicon.ico')
# def favicon():
#     return current_app.send_static_file('news/favicon.ico')
