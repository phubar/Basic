#crappy centos6 on vps

#install git python2.7
rpm -ivh https://rhel6.iuscommunity.org/ius-release.rpm
yum --enablerepo=ius install git python27 python27-devel python27-pip python27-setuptools python27-virtualenv -y

#install letsecrypt
git clone https://github.com/letsencrypt/letsencrypt
letsencrypt/letsencrypt-auto --text --agree-tos --email info@x.net certonly --renew-by-default --webroot --webroot-path /home/x/public_html/ -d x.net -d x.x.net -d x.x.net

#cert files in /etc/letsencrypt/live/X
#copy and paste into crappy WHM http://domain:2086 interface: cert.pem and privkey.pem
