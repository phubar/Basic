#!/bin/bash

#quick install
# yum update
# yum -y groups install "Gnome Desktop"
# systemctl set-default graphical.target
#/etc/hostname
#/etc/resolv.conf
# echo "blacklist pcspkr" >> /etc/modprobe.d/pcspkr.conf
# usermod -aG wheel "USER" #if admin req

# ssh
# disable root login and specify protocol 2 /etc/ssh/sshd_config

# fail2ban
# add epel repo and install fail2ban
# yum install -y epel-release
# yum install -y fail2ban fail2ban-systemd
# systemctl mask firewalld.service
# systemctl enable iptables.service
# systemctl enable ip6tables.service
# systemctl stop firewalld.service
# systemctl start iptables.service
# systemctl start ip6tables.service
# Add to /etc/fail2ban/jail.d/sshd.local
# [ssh-iptables]
# enabled  = true
# filter   = sshd
# action   = iptables[name=SSH, port=ssh, protocol=tcp]
# logpath  = /var/log/secure
# maxretry = 5
# bantime = 86400

# systemctl enable fail2ban
# systemctl start fail2ban

#mount cifs
mount -t cifs -o username=x,password=x //host/share /mnt/share

#github config
# su - "user"
# git config --global user.name "USER"
# git config --global user.email "YOUR EMAIL ADDRESS"
# ssh-keygen -t rsa -C "your_email@example.com"
# eval "$(ssh-agent -s)"
# ssh-add ~/.ssh/id_rsa
# git init .
# git pull http://github.com/phubar/Basic
# git push http://github.com/phubar/Basic
# git config --global push.default simple
# git push --set-upstream http://github.com/phubar/Basic master
# git commit -a
# git push

#check public IP
# curl -s checkip.dyndns.org | sed -e 's/.*Current IP Address: //' -e 's/<.*$//'
# 5551234567@vtext.com
#| mail -s "Test" an@email.com

#postfix config for gmail
# echo "smtp.gmail.com    smtp_user:smtp_passwd" > /etc/postfix/sasl_passwd
# postmap hash:/etc/postfix/sasl_passwd
# append to main.cf
# smtp_sasl_auth_enable = yes
# smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
# smtp_sasl_security_options = noanonymous
## Secure channel TLS with exact nexthop name match.
# smtp_tls_security_level = secure
# smtp_tls_mandatory_protocols = TLSv1
# smtp_tls_mandatory_ciphers = high
# smtp_tls_secure_cert_match = nexthop
# smtp_tls_CAfile = /etc/pki/tls/certs/ca-bundle.crt
# relayhost = smtp.gmail.com:587

# postfix reload

# vi /etc/aliases # add external mail address
# newaliases
