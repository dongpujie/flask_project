import logging

from flask import session

# 可以用来指定 session 保存的位置
from flask_migrate import Migrate, MigrateCommand

from flask_script import Manager

from info import create_app, db


app = create_app("development")

manager = Manager(app)

# 将 app 与 db 关联
Migrate(app, db)
# 将迁移命令添加到manager中
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    session["project"] = "flask"

    # 测试打印日志
    logging.debug('测试debug')
    logging.warning('测试warning')
    logging.error('测试error')
    logging.fatal('测试fatal')

    return 'index'


if __name__ == '__main__':
    manager.run()
