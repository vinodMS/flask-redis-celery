# api/batch_tasks.py
from typing import List

from celery import chord

from app import app, celery
from calculator import Calculator


# ----------------------- Advance Celery Tasks -----------------------#


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-start",
    ignore_result=True
)
def batch(
        self,
        start: int,
        end: int,
        batch: int,
        batch_id: int
):
    # important to pass self as the first variable when bind=True
    app.logger.info("Starting calculation")

    try:
        callback = batch_run_main.s(batch_id).on_error(
            batch_failed.si(batch_id))
        header = [batch_validate_data.s(batch_id, val, batch)
                  for val in range(start, end, batch)]
        chord(header)(callback)
    except Exception as e:
        app.logger.error(f"exception raised {e}")
        celery.send_task("batch-failed", args=[batch_id, ])


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-validate-data"
)
def batch_validate_data(self, batch_id: int, start: int, batch: int):
    app.logger.info(
        "Starting batch validate task with id {0}".format(batch_id))

    return Calculator().verify_data(start, batch)


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-run_main"
)
def batch_run_main(self, results: List, batch_id: int):
    app.logger.info("Main run of batch ID {0} starts now".format(batch_id))
    app.logger.info(results)

    if False in results:
        app.logger.error("Run failed")
        celery.send_task("batch-failed", args=[batch_id, ])
    else:
        app.logger.info("Run success")
        celery.send_task("batch-finished", args=[batch_id, ])


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-failed"
)
def batch_failed(self, batch_id: int):
    app.logger.error("Calculation with batch ID {0} failed".format(batch_id))


@celery.task(
    bind=True,
    max_tries=2,
    name="batch-finished",
)
def batch_finished(self, batch_id: int):
    app.logger.info(
        "Calculation successfully completed with batch ID {0}.".format(batch_id))
