from time import sleep

import celery
from celery.utils.log import get_logger
from django.utils import timezone

logger = get_logger(__name__)


@celery.task()
def test_task():
    logger.warn("TEST TASK DONE")
    return {"test": "result", "1": 2, "text": str(timezone.now())}


@celery.task(rate_limit=0.1)
def test_task2():
    sleep(5)
    logger.warn("TEST TASK SLOW DONE")
    return {"test": "result", "2": 2, "text": str(timezone.now())}


@celery.task()
def test_task3():
    logger.warn("TEST TASK 3 SEC")
    sleep(5)
    logger.warn("TEST TASK DONE")
    return {"test": "result", "3": 2, "text": str(timezone.now())}
