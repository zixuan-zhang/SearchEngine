#!/bin/bash
#
# This scripts is used for installing project.
# This scripts is required for all projects.
#

python setup.py -q build

SCRIPT_DIR=`dirname $0`
PROJECT=news_spider

if [ "$1" = "checkdeps" ] ; then

    if [ -f "${SCRIPT_DIR}/install_deps.sh" ]; then
        ${SCRIPT_DIR}/install_deps.sh
    fi
fi

if [ -f "${SCRIPT_DIR}/setup_conf.sh" ]; then
    ${SCRIPT_DIR}/setup_conf.sh
fi

PTH_FILE='news_spider.pth'
if [ "$2" = "lib" ] ; then
    sudo python setup.py -q install
else
    pwd > ${PTH_FILE}
    sudo python scripts/install.py
fi

echo Installing service...
[ -z `grep "^news_spider:" /etc/passwd` ] && sudo useradd -r news_spider -M -N

mkdir -p /var/app/${PROJECT}
sudo cp -r ./* /var/app/${PROJECT}/

ln -sf /var/app/${PROJECT}/scripts/news_spider-init.sh /etc/init.d/news_spider
update-rc.d news_spider defaults
