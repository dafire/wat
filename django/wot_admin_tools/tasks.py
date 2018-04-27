from time import sleep

import celery
from celery.utils.log import get_logger
from django.utils import timezone

logger = get_logger(__name__)


@celery.task()
def test_task():
    logger.warn("TEST TASK 2 SEC")
    sleep(10)
    logger.warn("TEST TASK DONE")
    return {"test": "result", "1": 2, "text": str(timezone.now())}
