#!/bin/bash
yum install kvm virt-manager libvirt virt-install qemu-kvm xauth dejavu-lgc-sans-fonts
virt-install --connect qemu:///system -n centos7 --ram 1024 --disk /var/lib/libvirt/images/centos7.img,size=8 --vcpus 1 --os-type linux --os-variant Centos7.0 --graphics none --console pty,target_type=serial --location /var/lib/libvirt/images/CentOS-7-x86_64-Minimal-1511.iso --extra-args='console=ttyS0'


