#!/bin/bash
#
# This scripts is used to stop the application.
#
#
# Author : chzhong 
#

PID_FILE=/var/run/news_spider.pid
SERVICE_NAME="News Spider Service"

service news_spider stop

if [ -f "${PID_FILE}" ]; then
    echo "Stopping ${SERVICE_NAME}..."
    export PID=`cat ${PID_FILE}`
    kill -9 ${PID}
    echo "${SERVICE_NAME}(pid ${PID}) stopped."
fi
