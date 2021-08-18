import re
import uuid

from flask import Flask, request
from celery import Celery, chain, chord, group
from flask.wrappers import Response
# from redis import Redis


#--------------------------- App Setup ---------------------------#
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(
    app.name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL'],
)
celery.config_from_object("celeryconfig")
celery.conf.update(app.config)

# redis = Redis(host='redis', port=6379)


#--------------------------- Celery Tasks ---------------------------#
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


#----------------------- Advance Celery Tasks -----------------------#
@celery.task(
    bind=True,
    max_tries=2,
    name="batch-start",
    ignore_result=True
)
def batch(self, start, end, step, batch_id):
    # important to pass self as the first variable when bind=True
    app.logger.info("Starting calculation")
    try:
        callback = batch_run_main.s(batch_id).on_error(
            batch_failed.si(batch_id))
        header = [batch_validate_data.s(batch_id, val)
                  for val in range(start, end, step)]
        chord(header)(callback)
    except Exception as e:
        app.logger.error("exception raised")
        # TODO: send task currently fails, as the task is not found
        # celery.send_task(batch_failed(batch_id))


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-validate-data"
)
def batch_validate_data(self, batch_id, val):
    """
        Checks if the given number is an odd/even number. 
        Returns false if it's an odd number, as we are 
        expecting even number. 

    Parameters
    ----------
    batch_id : int
        unique batch id to identify the full run
    val : int
        value to be checked

    Returns
    -------
    bool
        True if it's an even number
    """

    app.logger.info(
        "Starting batch validate task with id {0}".format(batch_id))
    return val % 2 == 0


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-run_main"
)
def batch_run_main(self, results, batch_id):
    app.logger.info("Main run of batch ID {0} starts now".format(batch_id))
    app.logger.info(results)

    if False in results:
        app.logger.error("Run failed, odd number found")
        # TODO: send task currently fails, as the task is not found
        # celery.send_task(batch_failed(batch_id))
    else:
        # TODO: before we do another chord, we can do some grouped or chained tasks here. 
        callback = batch_finished.si(batch_id).on_error(
            batch_failed.si(batch_id))
        # header = [batch_validate_data.s(batch_id, val)
        #           for val in range(start, end, step)]
        # chord(header)(callback)
        app.logger.info("continue further")


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-failed"
)
def batch_failed(self, batch_id):
    app.logger.error("Calculation with batch ID {0} failed".format(batch_id))


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-finished",
)
def batch_finished(self, batch_id):
    app.logger.info(
        "Calculation succesfully completed with batch ID {0}.".format(batch_id))


#--------------------------- Flask routes ---------------------------#
@app.route('/')
def hello_world():
    # redis.incr('hits')
    return 'This is hello world'


@app.route('/sig_task')
def signature_task():
    """ Test Signatures """

    x = request.form.get('x')
    y = request.form.get('y')

    if None in [x, y]:
        return "Please specify x,y values as form data"

    # result = add.delay(4, 4)
    # result = add.s(2, 2)()
    # result = add.apply_async((2, 2), countdown=1) same as below
    result = add.signature((int(x), int(y)), countdown=1).apply_async()

    return '{0} + {1} is {2}'.format(x, y, result.get())


@app.route('/callback_task')
def callback_task():
    """ Test Callback and partials """

    x = request.form.get('x')
    y = request.form.get('y')
    z = request.form.get('z')

    if None in [x, y, z]:
        return "Please specify x,y,z values as form data"

    result = add.apply_async((int(x), int(y)), link=sub.s(int(z)))
    return 'Callback succesfully initiated, check celery log for results'


@app.route('/chain_task')
def chain_task():
    """ Test Chainback """

    a = request.form.get('a')
    x = request.form.get('x')
    y = request.form.get('y')
    z = request.form.get('z')

    if None in [a, x, y, z]:
        return "Please specify a, x,y,z values as form data"

    # () at the end means that the chain will execute the task inline in the current process:
    result = chain(add.s(int(a), int(x)), add.s(int(y)), add.s(int(z)))()
    # result = (add.s(int(a), int(x)) | add.s(int(y)) | add.s(int(z)))().get() same as above
    return 'Running this - chain(add.s({0}, {1}), add.s({2}), add.s({3}))() returns {4}'.format(a, x, y, z, result.get())


@app.route('/simple_chord_task')
def simple_chord_task():
    """ Test Simple Chord """

    range_val = request.form.get('range')

    if range_val is None:
        return "Please specify a value for range (range=10)"

    result = chord((add.s(i, i) for i in range(int(range_val))), xsum.s())()
    return 'Running this - chord((add.s(i, i) for i in range(int(range_val))), xsum.s())() returns {0}'.format(result.get())


@app.route('/chord_task')
def chord_task():
    """ Test Chord and on error """

    range_val = request.form.get('range')

    if range_val is None:
        return "Please specify a value for range (range=10)"

    callback = xsum.s()
    header = [add.s(i, i) for i in range(int(range_val))]
    result = chord(header)(callback)

    # result = (group(add.s(i, i) for i in range(int(range_val)))
    #           | xsum.s().on_error(on_chord_error.s())).delay()

    return 'Result is {0}'.format(result.get())


@app.route('/batch')
def batch_start() -> str:
    "Entry point to the batch call"
    start, end, step = 0, 10, 2
    batch_id = uuid.uuid1()  # Generate unique batch ID

    result = batch.s(start, end, step, batch_id.int).apply_async()
    return 'Task ID is - {0}'.format(result)


#--------------------------- Main Run ---------------------------#
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
