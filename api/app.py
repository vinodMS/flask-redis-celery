import re
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
    broker=app.config['CELERY_BROKER_URL']
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
    print("we've hit an error %s" % res)
    return False


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


#--------------------------- Main Run ---------------------------#
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)