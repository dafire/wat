import os
import subprocess
import tempfile
from time import sleep

import celery
from celery.utils.log import get_logger
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from itsdangerous import Signer

logger = get_logger(__name__)

BACKUP_PATH = '/tmp'


@celery.shared_task()
def database_backup():
    destination = tempfile.NamedTemporaryFile(delete=False, prefix="db_", suffix="_backup")
    dbsettings = settings.DATABASES['default']
    ps = subprocess.Popen(
        ['pg_dump', '-h', dbsettings['HOST'], '-U', dbsettings['USER'], '-Fc', dbsettings['NAME']],
        stdout=destination
    )
    destination.close()
    logger.info("created backup %s", destination.name)
    remove_database_backup.apply_async((destination.name,), countdown=120)
    s = Signer(settings.SECRET_KEY)
    return {
        "download": reverse('download-backup') + s.sign(destination.name)
    }


@celery.shared_task()
def remove_database_backup(filename):
    os.unlink(filename)
    logger.info("deleted backup %s", filename)


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
