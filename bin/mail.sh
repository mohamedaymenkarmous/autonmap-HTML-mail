#!/bin/sh

# The base directory
SCRIPT_PATH=$(readlink -f "$0")
BASE_DIRECTORY=$(dirname "$SCRIPT_PATH")

if [ "$1" != "" ]; then
    From=$(cat ${BASE_DIRECTORY}/../conf/parameters.json | python -c "import sys, json; print json.load(sys.stdin)['From']")
    To=$(cat ${BASE_DIRECTORY}/../conf/parameters.json | python -c "import sys, json; print json.load(sys.stdin)['To']")
    cat $1 | /usr/sbin/ssmtp -v -f"${From}" ${To}
else
    echo "Usage : mail.sh <mail_content_file_name>"
    echo "Example : mail.sh mail_content_file_name.html"
    exit 1
fi

