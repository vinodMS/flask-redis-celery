# api/views.py
import uuid

from flask import Flask, request
from celery import chain, chord, group

from app import app
from tasks import xsum, add, sub
from batch_tasks import batch

#--------------------------- Simple celery routes ---------------------------#


@app.route('/')
def hello_world() -> str:
    # redis.incr('hits')
    return 'This is hello world'


@app.post('/basic-task')
def signature_task() -> str:
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


@app.post('/callback-task')
def callback_task() -> str:
    """ Test Callback and partials """

    x = request.form.get('x')
    y = request.form.get('y')
    z = request.form.get('z')

    if None in [x, y, z]:
        return "Please specify x,y,z values as form data"

    result = add.apply_async((int(x), int(y)), link=sub.s(int(z)))
    return 'Callback succesfully initiated, check celery log for results'


@app.post('/chain-task')
def chain_task() -> str:
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


@app.post('/simple-chord-task')
def simple_chord_task() -> str:
    """ Test Simple Chord """

    range_val = request.form.get('range')

    if range_val is None:
        return "Please specify a value for range (range=10)"

    result = chord((add.s(i, i) for i in range(int(range_val))), xsum.s())()
    return 'Running this - chord((add.s(i, i) for i in range(int(range_val))), xsum.s())() returns {0}'.format(result.get())


@app.post('/chord-task')
def chord_task() -> str:
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


#--------------------------- Advance Celery routes ---------------------------#

@app.post('/batch-start')
def batch_start() -> str:
    "Entry point to the batch call"
    start, end, step = 0, 890, 60
    batch_id = uuid.uuid1()  # Generate unique batch ID

    result = batch.s(start, end, step, batch_id.int).apply_async()
    return 'Task ID is - {0}'.format(result)
