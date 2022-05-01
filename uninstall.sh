#!/bin/bash
# Removes doorbell.py as systemd service
# Removes all relating configurations for doorbell service

# Only allow script to be ran as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root or with sudo"
  exit
fi

# Abort uninstallation if python script is not already in /usr/local/bin
if [[ -f "/usr/local/bin/doorbell.py" ]]; then
	systemctl disable doorbell
	systemctl stop doorbell
	rm /usr/local/bin/doorbell.py
	rm /etc/systemd/system/doorbell.service
	rm /var/log/doorbell.log # Make backup if you want to keep logs, journalctl -u doorbell.service still keeps a copy though
	sed -i '\;/var/log/doorbell;d' /etc/logrotate.d/rsyslog
	sed -i '\;local5.*;d' /etc/rsyslog.conf
	systemctl daemon-reload
	systemctl reset-failed
else
	echo "Doorbell system is not installed"
	exit 0
fi