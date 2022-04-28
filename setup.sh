#!/bin/bash
# Bash setup script to install doorbell.py python script as a systemd service
# Sets up rsyslog to use local5 for /var/log/doorbell.log
# Sets up logrotate to use /var/log/doorbell.log when rotating logs

# Only allow script to be ran as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root or with sudo"
  exit
fi

echo "Ex: 8591114444 (only numbers, no spaces)"
read -p "Enter phone number: " number
# Only allow 10 numbers for correct input, otherwise exit
[[ "$number" =~ ^[0-9]{10}$ ]] || { echo "Invalid phone number, please try again"; exit 1; }
echo "Pick carrier:
[1] verizon
[2] tmobile
[3] at&t
[4] boost
[5] cricket
[6] uscellular
[7] virgin"
read -p "Enter option number: " carrier
# Only allow correct option input, otherwise exit
[[ "$carrier" = '1' || "$carrier" = '2' || "$carrier" = '3' || "$carrier" = '4' || "$carrier" = '5' || "$carrier" = '6' || "$carrier" = '7' ]] || { echo "Invalid input, please try again"; exit 1; }
sed -i '\;user.*;a local5.*				/var/log/doorbell.log' /etc/rsyslog.conf
systemctl restart rsyslog
mv ./doorbell.py /usr/local/bin
sed -i '\;/var/log/messages;a /var/log/doorbell.log' /etc/logrotate.d/rsyslog
sed -i "s/recipient = ''/recipient = '$number'/" /usr/local/bin/doorbell.py
sed -i "s/carrier = ''/carrier = '$carrier'/" /usr/local/bin/doorbell.py
chmod a+x ./doorbell.service
mv ./doorbell.service /etc/systemd/system
systemctl daemon-reload
systemctl enable doorbell.service
systemctl start doorbell.service