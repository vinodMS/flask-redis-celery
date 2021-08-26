# api/batch_tasks.py

from celery import chord

from app import app, celery
from calculator import Calculator

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
    start = 0
    end = 890
    batch = 60
    try:
        callback = batch_run_main.s(batch_id).on_error(
            batch_failed.si(batch_id))
        header = [batch_validate_data.s(batch_id, val, batch)
                  for val in range(start, end, batch)]
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
def batch_validate_data(self, batch_id, start, batch):
    app.logger.info(
        "Starting batch validate task with id {0}".format(batch_id))

    return Calculator().verify_data(start, batch)


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


# @celery.task(
#     bind=True,
#     max_tries=2,
#     name="batch-validate-data"
# )
# def batch_validate_data(self, batch_id, val):
#     """
#         Checks if the given number is an odd/even number.
#         Returns false if it's an odd number, as we are
#         expecting even number.

#     Parameters
#     ----------
#     batch_id : int
#         unique batch id to identify the full run
#     val : int
#         value to be checked

#     Returns
#     -------
#     bool
#         True if it's an even number
#     """

#     app.logger.info(
#         "Starting batch validate task with id {0}".format(batch_id))
#     return val % 2 == 0
