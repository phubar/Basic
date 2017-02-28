#!/bin/bash

# sudo yum install mariadb-server
# sudo systemctl enable mariadb
# sudo systemctl start mariadb
# mysql_secure_installation
# mysql -u user -p
# CREATE DATABASE myip;
# USE myip;
# create table iptable ( id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ip VARCHAR(20), ipdate timestamp NOT NULL );
# INSERT INTO iptable (ip) VALUES ('0.0.0.0');

# add user
# mysql> CREATE USER 'user'@'localhost' IDENTIFIED BY 'some_pass';
# mysql> GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost'
#    ->     WITH GRANT OPTION;

DB_USER='user';
DB_PASSWD='passwd';
DB_NAME='myip';
DB_TABLE='iptable';
MAIL_ADDR='your.email.com';

NEWIP=`curl -s checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//'`
LASTID=$(mysql -u$DB_USER -p$DB_PASSWD $DB_NAME -s -r -N -e "SELECT COUNT(id) FROM iptable")
CURIP=$(mysql -u$DB_USER -p$DB_PASSWD $DB_NAME -s -r -N -e "SELECT ip FROM iptable WHERE id=$LASTID")

if [ "$CURIP" != "$NEWIP" ];
then
	if [ "$NEWIP" != "" ];
	then
	echo $NEWIP | mail -s "NEW IP" $MAIL_ADDR
	mysql -u$DB_USER -p$DB_PASSWD -e "INSERT INTO myip.iptable (ip) VALUES ('$NEWIP');"
	fi
fi
