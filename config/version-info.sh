#!/bin/bash
echo "\nPROJECT_VERSION=${CI_COMMIT_ID:0:7}" >> /src/config/default.env