from socket import CAN_BCM_TX_READ
from gpiozero import LED,Button
from picamera import PiCamera
import smtplib
import time

reed = Button(12, bounce_time = 0.25)   # GPIO 12
button = Button(26, bounce_time = 0.25) # GPIO 26
camera = PiCamera()

path='/home/pi/scripts/group_project/pic.jpg'

def reedDisconnect(pictureTaken):      # When reed is open
    if pictureTaken == False:
        capturePicture()
        print('Reed disconnected')
        pictureTaken = True

def capturePicture():
    camera.capture(path) # Use path variable for file location

def doorbell():
    if not rang:
        epoch_time = int(time.time())
        finish_time = epoch_time + 30
        rang = True
    if rang == True:
    capturePicture()
    print('ding dong')

def main():
    pictureTaken = False
    while True:
        if reed.value == 0:
            reedDisconnect(pictureTaken)
        if button.value == 1:
            doorbell()
        if pictureTaken == True and reed.value == 1:
            pictureTaken = False
            print('resetting pictureTaken to False')
        print(reed.value)
        time.sleep(1)
if __name__ == '__main__': # Call the main function
    main()