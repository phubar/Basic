#!/bin/bash

sudo yum install mariadb-server
# sudo systemctl enable mariadb
sudo systemctl start mariadb
mysql_secure_installation
mysql -u user -p

# example
# CREATE DATABASE myip;
# USE myip;
# create table iptable ( id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ip VARCHAR(20), ipdate DATE);
# INSERT INTO iptable (ip,ipdate) VALUES ('0.0.0.0', '1970-01-01');
