#!/bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/var/app/news_spider
NAME=news_spider
DESC="News Spider Service"
PROJECT=news_spider

if [ -f /etc/default/news_spider ]; then
	. /etc/default/news_spider
fi

function stop_service()
{
	if [ -f "/var/run/news_spider.pid" ]; then
        pushd /var/app/${PROJECT}/
        python runcrawler.py stop
        popd
	fi
}

function start_service()
{
    pushd /var/app/${PROJECT}/
    python runcrawler.py start
    popd
}

function restart_service()
{
    pushd /var/app/${PROJECT}/
    python runcrawler.py restart
    popd
}

set -e

. /lib/lsb/init-functions

case "$1" in
	start)
		echo "Starting $DESC..."
		start_service
		echo "Done."				
		;;
	stop)
		echo "Stopping $DESC..."
		stop_service
		echo "Done."
		;;

	restart)
		echo "Restarting $DESC..."
		restart_service
		echo "Done."
		;;
	*)
		echo "Usage: $NAME {start|stop|restart}" >&2
		exit 1
		;;
esac

exit 0

