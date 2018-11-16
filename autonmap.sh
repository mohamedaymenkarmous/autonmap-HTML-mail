#!/bin/sh

DATE=`date "+%Y.%m.%d-%H.%M.%S"`

## Begin Config

# The base directory
SCRIPT_PATH=$(readlink -f "$0")
BASE_DIRECTORY=$(dirname "$SCRIPT_PATH")

# The directory for autonmap logs
LOGS_DIRECTORY="${BASE_DIRECTORY}/logs"

# The directory for autonmap logs
CONF_DIRECTORY="${BASE_DIRECTORY}/conf"

# The directory for autonmap binaries
BIN_DIRECTORY="${BASE_DIRECTORY}/bin"

# The subnets you want to scan daily, space seperated.
SCAN_SUBNETS_FILE="${CONF_DIRECTORY}/address_list.txt"
SCAN_SUBNETS_MERGED_FILE="${CONF_DIRECTORY}/do_not_touch_this_file_when_running.txt"

# The python script that will parse the xml files after the scan
XML_PARSER="${BIN_DIRECTORY}/xmlParser.py"

MERGE_SUBNETS_BIN="${BIN_DIRECTORY}/mergeSubnets.py"

# The script that will send the mail
MAIL_BIN="${BIN_DIRECTORY}/mail.sh"

# The mail body that will be generated after the scan
MAIL_CONTENT_FILE="${LOGS_DIRECTORY}/mail_output.txt"

# The full path to your chosen nmap binary
NMAP="/usr/bin/nmap"

# The path to the ndiff tool provided with nmap
NDIFF="/usr/bin/ndiff"

# DNS configuration if exists in config file
DNSServers=$(cat ${BASE_DIRECTORY}/conf/parameters.json | python -c "import sys, json; print json.load(sys.stdin)['DNSServers']" 2> /dev/null)
if [ ! -z "$DNSServers" ]
then
  DNS_SERVERS="--dns-servers=${DNSServers}"
else
  DNS_SERVERS=""
fi

# Scan parameters configuration
ScanParameters=$(cat ${BASE_DIRECTORY}/conf/parameters.json | python -c "import sys, json; print json.load(sys.stdin)['ScanParameters']" 2> /dev/null)
if [ ! -z "$ScanParameters" ]
then
  SCAN_PARAMETERS="${ScanParameters}"
else
  SCAN_PARAMETERS=""
fi

# Max logs history's file number
$HistoryFilesNumber=$(cat ${BASE_DIRECTORY}/conf/parameters.json | python -c "import sys, json; print json.load(sys.stdin)['HistoryFilesNumber']" 2> /dev/null)
if [ ! -z "$HistoryFilesNumber" ]
then
  MAX_LOGS_HISTORY_FILE_NUMBER="${HistoryFilesNumber}"
else
  MAX_LOGS_HISTORY_FILE_NUMBER="10000000000"
fi

## End config

# Ensure we can change to the run directory
cd $BASE_DIRECTORY || exit 2

# Merge subnets condition if exists in config file
MergeSubnets=$(cat ${BASE_DIRECTORY}/conf/parameters.json | python -c "import sys, json; print json.load(sys.stdin)['MergeSubnets']" 2> /dev/null)
if [ ! -z "$MergeSubnets" ] && [ "${MergeSubnets}" = "true" ]
then
  ${MERGE_SUBNETS_BIN}
  FINAL_SCAN_SUBNETS_FILE=${SCAN_SUBNETS_MERGED_FILE}
else
  FINAL_SCAN_SUBNETS_FILE=${SCAN_SUBNETS_FILE}
fi

echo "`date` - Running nmap, please wait. This may take a while." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
echo "$NMAP ${SCAN_PARAMETERS} -R -O -sV -iL ${FINAL_SCAN_SUBNETS_FILE} ${DNS_SERVERS} -oX ${LOGS_DIRECTORY}/scan-$DATE.xml" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
$NMAP ${SCAN_PARAMETERS} -R -O -sV -iL ${FINAL_SCAN_SUBNETS_FILE} ${DNS_SERVERS} -oX ${LOGS_DIRECTORY}/scan-$DATE.xml > /dev/null  | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
echo "`date` - Nmap process completed with exit code $?" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log

# If this is not the first time autonmap has run, we can check for a diff. Otherwise skip this section, and tomorrow when the link exists we can diff.
if [ -e ${LOGS_DIRECTORY}/scan-prev.xml ]
then
    echo "`date` - Running ndiff..." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    # Run ndiff with the link previous scan and current scan
    DIFF=`$NDIFF ${LOGS_DIRECTORY}/scan-prev.xml ${LOGS_DIRECTORY}/scan-$DATE.xml --xml | tee ${LOGS_DIRECTORY}/ndiff-$DATE.xml`

    # Create the link from the current report to scan-prev so it can be used later for diff.
    # The link can't be created before the diff to prevent from loosing the previous scan file
    echo "`date` - Linking current scan report to logs/scan-prev.xml" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    ln -sf ${LOGS_DIRECTORY}/scan-$DATE.xml ${LOGS_DIRECTORY}/scan-prev.xml

    # Create the link from the current differences to ndiff-prev so it can be used later for diff.
    echo "`date` - Linking current differences report to logs/ndiff-prev.xml" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    ln -sf ${LOGS_DIRECTORY}/ndiff-$DATE.xml ${LOGS_DIRECTORY}/ndiff-prev.xml

    echo "`date` - Checking ndiff output" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    # There is always three lines of difference; the run header that has the time/date in. So we can discount that.
    if [ `echo -n "$DIFF" | wc -l` -gt 3 ]
    then
            echo "`date` - Differences Detected. Sending mail." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
            echo "`date` - AutoNmap found differences." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
            echo "`date` - Parsing the nmap report..." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
            ${XML_PARSER} | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
            if [ `cat $MAIL_CONTENT_FILE | wc -l` -gt 5 ]
            then
                echo "`date` - Sending differences by mail." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
                $MAIL_BIN $MAIL_CONTENT_FILE | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
                echo "`date` - Mail sent" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
            else
                echo "`date` - After inspection, there is no differences detected. skipping mail." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
            fi
    else
            echo "`date` - No differences, skipping mail." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    fi

else
    echo "`date` - First scan operation." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log

    # Create the link from the current report to scan-prev so it can be used later for diff.
    # The link can't be created before the diff to prevent from loosing the previous scan file. Even if there is no diff in this situation
    echo "`date` - Linking current scan report to logs/scan-prev.xml" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    ln -sf ${LOGS_DIRECTORY}/scan-$DATE.xml ${LOGS_DIRECTORY}/scan-prev.xml

    echo "`date` - Parsing the nmap report..." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    ${XML_PARSER} | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    echo "`date` - Sending new discovered hosts by mail." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    $MAIL_BIN $MAIL_CONTENT_FILE | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
    echo "`date` - Mail sent." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
fi

# Copy the scan report to the web directory so it can be viewed later.
#echo "`date` - Copying XML to web directory." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
#cp scan-$DATE.xml $WEB_DIRECTORY

# Create the link from today's report to scan-prev so it can be used tomorrow for diff.
#echo "`date` - Linking todays scan to scan-prev.xml" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
#ln -sf ${LOGS_DIRECTORY}/scan-$DATE.xml ${LOGS_DIRECTORY}/scan-prev.xml
#ln -sf ${LOGS_DIRECTORY}/ndiff-$DATE.xml ${LOGS_DIRECTORY}/ndiff-prev.xml

echo "`date` - Purging previous logs and keeping the ${MAX_LOGS_HISTORY_FILE_NUMBER} last files" | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
ls -1rth ${LOGS_DIRECTORY}/ndiff-* 2> /dev/null | grep -v prev | head -n -${MAX_LOGS_HISTORY_FILE_NUMBER} | xargs rm 2> /dev/null
ls -1rth ${LOGS_DIRECTORY}/scan-* 2> /dev/null | grep -v prev | head -n -${MAX_LOGS_HISTORY_FILE_NUMBER} | xargs rm 2> /dev/null

echo "`date` - AutoNmap is complete." | tee -a ${LOGS_DIRECTORY}/logs-$DATE.log
exit 0
