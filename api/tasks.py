# api/tasks.py

from app import app, celery


#---------------------------Simple Celery Tasks ---------------------------#
@celery.task()
def add(x, y):
    return x + y


@celery.task()
def sub(x, y):
    return x - y


@celery.task()
def xsum(results):
    # when raising an exception here, the on_error method will be invoked
    # raise Exception
    return sum(results)


@celery.task()
def on_chord_error(res):
    # print("we've hit an error %s" % res)
    app.logger.error("we've hit an error %s" % res)
    return False
