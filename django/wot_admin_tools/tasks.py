import os
import subprocess
import tempfile
from time import sleep
from urllib.parse import urlencode, quote_plus

import celery
from celery.utils.log import get_logger
from django.conf import settings
from django.core.signing import TimestampSigner
from django.urls import reverse
from django.utils import timezone

logger = get_logger(__name__)


@celery.shared_task()
def database_backup():
    tempdir = settings.MEDIA_ROOT
    if not tempdir:
        tempdir = tempfile.gettempdir()
    destination = tempfile.NamedTemporaryFile(dir=tempdir, delete=False, suffix=".dbbackup")
    dbsettings = settings.DATABASES['default']
    command = ['pg_dump', '-Fc', '--dbname=%s' % settings.DATABASE_URL]
    subprocess.call(command, stdout=destination)
    filename = destination.name[len(tempdir) + 1:]
    logger.info("created backup: %s", filename)
    remove_database_backup.apply_async((destination.name,), countdown=120)
    s = TimestampSigner()
    return {
        "browse": "%s?%s" % (
            reverse('wot_admin_tools:download-backup'),
            urlencode({"file": s.sign(filename.encode()).decode()}, quote_via=quote_plus)
        )
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
