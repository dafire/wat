#!/bin/bash
echo "" >> /src/config/default.env
echo "PROJECT_VERSION=${CI_COMMIT_ID:0:7}" >> /src/config/default.env