#!/bin/sh

### For mail notifications
/usr/bin/sudo /usr/bin/apt-get install ssmtp

### For python libraries (XML file parsing)

# If you don't find problems with using pip command behin a proxy
#/usr/bin/sudo /usr/bin/apt-get install nmap python-pip libxml2-dev libxslt-dev python-dev
#/usr/bin/sudo /usr/bin/pip install lxml

# If you find problems with using pip command behin a proxy
/usr/bin/sudo /usr/bin/apt-get install python-lxml

### For python libraries

# If you don't find problems with using pip command behin a proxy
#/usr/bin/sudo /usr/bin/pip install netaddr

# If you don't find problems with using git command behin a proxy
#git clone https://github.com/drkjam/netaddr

# If you find problems with using git command behin a proxy
wget https://github.com/drkjam/netaddr/archive/rel-0.7.x.zip
unzip rel-0.7.x.zip
cd netaddr-rel-0.7.x/
/usr/bin/sudo python setup.py install
cd -
rm -rf netaddr-rel-0.7.x rel-0.7.x.zip

### Creating logs directory
/bin/mkdir logs
/bin/chmod 0770 logs
