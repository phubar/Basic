#!/bin/bash

sudo yum install mariadb-server
# sudo systemctl enable mariadb
sudo systemctl start mariadb
mysql_secure_installation
mysql -u user -p

# example
# CREATE DATABASE myip;
# USE myip;
# create table iptable ( id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ip VARCHAR(20), ipdate timestamp NOT NULL );
# INSERT INTO iptable (ip) VALUES ('0.0.0.0');

#add user - should limit to specific db
mysql> CREATE USER 'finley'@'localhost' IDENTIFIED BY 'some_pass';
mysql> GRANT ALL PRIVILEGES ON *.* TO 'finley'@'localhost'
    ->     WITH GRANT OPTION;
