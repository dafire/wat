#!/usr/bin/env bash

./manage.py test

codecov --commit=${CI_COMMIT_ID}
