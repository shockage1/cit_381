# CIT 381 - Spring 2022
# Raspberry Pi Final Project
# Author: Derek Disibio
# Created: April 13, 2022
# Raspberry Pi script for doorbell system using reed and button in Python
# Logs are outputted in /var/log/doorbell.log and in journalctl -u doorbell.service

# ***USE SETUP.SH TO CONFIGURE SCRIPT***

from gpiozero import LED,Button
from picamera import PiCamera
import smtplib
import time
import datetime
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import subprocess

reed = Button(12, bounce_time = 0.25)   # GPIO 12
button = Button(26, bounce_time = 0.25) # GPIO 26
camera = PiCamera()

path='/tmp/'
ext='.jpg'

# Email/texting variable configurations
gmail_user = 'disibiod1pi@gmail.com'
gmail_password = 'ppkdrassajquzozy'
recipient = '' # configured from setup.sh
carrier = '' # configured from setup.sh
# Map carrier to respective gateway domain in dictionary
carrier_map = {
    "1": "@vzwpix.com", # verzion
    "2": "@tmomail.net", # tmobile
    "3": "@mms.att.net", # at&t
    "4": "@myboostmobile.com", # boost
    "5": "@mms.cricketwireless.net", # cricket
    "6": "@mms.uscc.net", # uscellular
    "7": "@vmpix.com", # virgin
}

finish_time = int(time.time()) # Initialize for first iteration of debounce

def log(level, topic, data): # Use rsyslog to log events
    # Level denotes severity of log, topic is environment of log, data is log text
    subprocess.run(['logger', '-p', 'local5.'+level, '-t', topic, data]) # Subprocess to make things easy

def reedDisconnect():
    log('info', 'Door', 'Reed disconnected')
    capturePicture('Door opened') # Pass trigger type to text msg later

def doorbell():
    log('info', 'Doorbell', 'Doorbell rung')
    capturePicture('Doorbell rung') # Pass trigger type to text msg later

def capturePicture(text):
    global finish_time
    epoch_time = int(time.time())
    # Use UNIX epoch time to prevent multiple pictures being taken
    # Keeps detecting button presses or reed disconnect for logging
    if epoch_time > finish_time: 
        finish_time = epoch_time + 60 # Reset debounce
        picturepath = path + str(datetime.datetime.now()) + ext # timestamp the capture
        try:
            camera.capture(picturepath)
        except:
            log('error', 'Camera', "Picture couldn't be taken")
        else:
            log('info', 'Camera', 'Picture taken')
        sendText(picturepath, text) # pass our capture location and our alarm type
        os.remove(picturepath)
    else:
        log('warning', 'System', 'Camera capture is on cooldown for %s seconds' % (finish_time - epoch_time))

def sendText(picturepath, alarmtype):
    global gmail_user,gmail_password,recipient,carrier,carrier_map
    with open(picturepath, 'rb') as capture:
        img_data = capture.read()
    msg = MIMEMultipart() # Initialize MIME object
    msg['Subject'] = 'Doorbell Alert'
    msg['From'] = gmail_user
    msg['To'] = recipient+carrier_map[carrier]
    text = MIMEText(alarmtype)
    # Assemble the email
    msg.attach(text)
    image = MIMEImage(img_data, name=os.path.basename(picturepath)) # Create MIMEImage object with our capture
    msg.attach(image)
    log('info', 'Text', 'Notifying %s of %s' % (recipient,alarmtype))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com',465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient+carrier_map[carrier], msg.as_string())
        server.close()
    except:
        log('error', 'Text', 'Something went wrong with sending the text message')

def main():
    log('info', 'System', 'Doorbell system successfully started')
    while True:
        if reed.value == 0:
            reedDisconnect()
        if button.value == 1:
            doorbell()
        time.sleep(1) # Prevent main loop from executing too fast

if __name__ == '__main__': # Call the main function
    main()