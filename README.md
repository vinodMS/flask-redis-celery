# flask-redis-celery
 
## Setup
1. Make sure you have docker installed on your computer
2. Pull the repository
3. Run `docker-compose up` from project directory
4. If all goes well, running `docker ps` should show all 3 containers up and running.

## Directory structure and file contains
- api/ -- contains flask and celery app code.
  - app.py -- flask and celery app setup.
  - tasks.py -- simple celery tasks to demontrate some mathematical operations such as addition and subtraction.
  - batch_tasks.py -- advance celery tasks that demonstrates batch calculation tasks.
  - views.py -- contains flask routes that can be accessed via the api.
  - celeryconfig.py -- self explanatory.
  - calculator.py -- calculator class with some basic operations to be used by batch celery tasks.

## Flask routes
- GET / -- Test app status
- <WIP>

## Testing
1. Use postman to test the API endpoints which will trigger celery tasks.
2. Following screenshot shows an example postman session, <img width="1544" alt="Screenshot 2021-08-13 at 09 55 02" src="https://user-images.githubusercontent.com/2227036/129304783-27217199-f4cf-42d2-ae71-95cfa06dc708.png">

