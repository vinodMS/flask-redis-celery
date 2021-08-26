# api/app.py

from re import I
from flask import Flask
from celery import Celery
from flask.wrappers import Response
# from redis import Redis


#--------------------------- App Setup ---------------------------#
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'


celery = Celery(
    app.name,
    include=[
        "tasks",
        "batch_tasks",
    ],
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL'],
)
celery.config_from_object("celeryconfig")
celery.conf.update(app.config)

# redis = Redis(host='redis', port=6379)


#--------------------------- Main Run ---------------------------#
if __name__ == '__main__':
    from views import *
    app.run(host="0.0.0.0", debug=True)
