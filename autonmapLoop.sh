#!/bin/sh

# The base directory
SCRIPT_PATH=$(readlink -f "$0")
BASE_DIRECTORY=$(dirname "$SCRIPT_PATH")

if [ `ps -aux | grep autonmap.sh | grep -v 'grep autonmap.sh' | wc -l` -eq 0 ]
then
  while true; do
    cd ${BASE_DIRECTORY}
    ./autonmap.sh
  done
fi
