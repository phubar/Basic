#!/bin/bash

sudo yum install mariadb-server
# sudo systemctl enable mariadb
sudo systemctl start mariadb
mysql_secure_installation
mysql -u user -p
