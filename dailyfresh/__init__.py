from __future__ import absolute_import

from celery_tasks.tasks import app as celery_app
import pymysql
pymysql.version_info = (1, 4, 13, "final", 0)
pymysql.install_as_MySQLdb()  # 使用pymysql代替mysqldb连接数据库