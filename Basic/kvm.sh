#!/bin/bash
yum install kvm virt-manager libvirt virt-install qemu-kvm xauth dejavu-lgc-sans-fonts
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
#ifcfg-br0
DEVICE=br0
TYPE=Bridge
BOOTPROTO=static
ONBOOT=yes
STP=on
IPADDR=
NETMASK=
GATEWAY=
DNS1=
# comment out IP on eth0 ; add BRIDGE=br0
sysctl -p /etc/sysctl.conf
virt-install --connect qemu:///system -n centos7 --ram 1024 --disk /var/lib/libvirt/images/centos7.img,size=8 --vcpus 1 --os-type linux --os-variant Centos7.0 --graphics none --console pty,target_type=serial --location /var/lib/libvirt/images/CentOS-7-x86_64-Minimal-1511.iso --extra-args='console=ttyS0'


