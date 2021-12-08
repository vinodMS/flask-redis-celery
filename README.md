# flask-redis-celery
 
## SETUP
1. Make sure you have docker installed on your computer
2. Pull the repository
3. Run `docker-compose up` from project directory
4. If all goes well, running `docker ps` should show all 3 containers up and running.
5. In your browser access `http://127.0.0.1:5000/`, if you see `This is hello world`, then you're all set.

## DIRECTORY STRUCTURE & FILE CONTAINS
- api/ -- contains flask and celery app code.
  - app.py -- flask and celery app setup.
  - tasks.py -- simple celery tasks to demontrate some mathematical operations such as addition and subtraction.
  - batch_tasks.py -- advance celery tasks that demonstrates batch calculation tasks.
  - views.py -- contains flask routes that can be accessed via the api.
  - celeryconfig.py -- self explanatory.
  - calculator.py -- calculator class with some basic operations to be used by batch celery tasks.

## FLASK ROUTES
|   |  HTTP Methods | URL  |  Args  | Celery Refs  |
|---|---|---|---|---|
| 1 | GET  |  / |   |  Check app status |
| 2 | POST  | /basic-task  |  **x**:int, **y**:int |  [Signature](https://docs.celeryproject.org/en/stable/userguide/canvas.html#signatures) |
| 3 |  POST |  /callback-task |  **x**:int, **y**:int, **z**:int |  [Callback](https://docs.celeryproject.org/en/stable/userguide/canvas.html#callbacks) |
| 4 |  POST |  /chain-task |  **a**:int, **x**:int, **y**:int, **z**:int |  [Chain](https://docs.celeryproject.org/en/stable/userguide/canvas.html#chains) |
| 5 |  POST |  /simple-chord-task |  **range**:int |  [Chord](https://docs.celeryproject.org/en/stable/userguide/canvas.html#chords) |
| 6 |  POST |  /chord-task |  **range**:int |  [Chord](https://docs.celeryproject.org/en/stable/userguide/canvas.html#chords) |
| 7 |  POST |  /batch-start |   |  A route that performs a calculator operation in batches |

## TESTING
1. Use postman to test the API endpoints which will trigger the celery tasks.
2. Following screenshot shows an example postman session, 
<img width="967" alt="Screenshot 2021-12-08 at 21 58 21" src="https://user-images.githubusercontent.com/2227036/145283534-44a003c6-0668-499d-8914-b5ebc4dce7c3.png">

## EXTEND & EXPERIMENT
Experimenting with a new celery task can be done in 3 steps.

### Add a celery task
```
@celery.task()
def new_celery_task(a, b):
    return a + b
```

### Add a route
```
@app.post('/new-task')
def new_route():
    x = 1
    y = 2
    result = new_celery_task.s(x, y).apply_async()
    return str(result.get())
```

### Test task
1. Restart all three docker containers to make sure the new tasks and routes are registered.
2. Call the new route using postman.


## TO:DO
1. Add an example of redis caching
2. Add unit and integration tests
