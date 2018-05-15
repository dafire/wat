#!/usr/bin/env bash

curl -L https://codeclimate.com/downloads/test-reporter/test-reporter-latest-linux-amd64 > "$/usr/local/bin/cc-test-reporter" && chmod +x "/usr/local/bin/cc-test-reporter"

cc-test-reporter before-build

coverage run --source='.' ./manage.py test

cc-test-reporter after-build --exit-code $?

codecov
