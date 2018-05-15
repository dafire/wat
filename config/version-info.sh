#!/bin/bash
echo "# default.env" > /src/tmp/artifacts/default.env
echo "PROJECT_VERSION=${CI_COMMIT_DESCRIPTION}" >> /src/tmp/artifacts/default.env