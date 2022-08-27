# api/tasks.py

from app import app, celery


# ---------------------------Simple Celery Tasks ---------------------------#
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


# experiment with decorator arguments
@celery.task(
    name="Test-Decorator-task",
    autoretry_for=(IndexError,),
    retry_kwargs={'max_retries': 2}
)
def auto_retry_exception():
    num_array = [0, 1, 2]
    num_array[4]

