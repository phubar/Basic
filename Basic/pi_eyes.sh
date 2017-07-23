#!/bin/bash

sudo raspi-config (localization)
systemctl enable ssh
systemcrl start ssh
sudo vi /etc/wpa_supplicant/wpa_supplicant.confcountry=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
        ssid="ssid"
        psk="password"
}
apt-get update
apt-get upgrade
curl -O https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/pi-eyes.sh
sudo bash pi-eyes.sh
