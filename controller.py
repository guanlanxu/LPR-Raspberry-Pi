#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
from datetime import datetime
from PCF8574 import PCF8574_GPIO 
from Adafruit_LCD1602 import Adafruit_CharLCD
from picamera import PiCamera
import subprocess

PCF8574_address = 0x27 # I2C address of the PCF8574 chip. 
PCF8574A_address = 0x3F # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter. 
try: 
    mcp = PCF8574_GPIO(PCF8574_address) 
except: 
    try: 
        mcp = PCF8574_GPIO(PCF8574A_address) 
    except: 
        print ('I2C Address Error !') 
        exit(1) 

# Create LCD, passing in MCP GPIO adapter. 
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

redLEDPin = 37 # GPIO26
redButtonPin = 40 # GPIO21
greenLEDPin = 35 # GPIO19
greenButtonPin = 22 # GPIO25
buzzerPin = 11 # GPIO17

camera = PiCamera()

def take_picture_with_camera():
    image_path = '/home/pi/hackathon/photos/image_%s.jpg' % int(round(time.time() * 1000))
    camera.capture(image_path)
    return image_path

def get_time_now(): # get system time 
    return datetime.now().strftime(' %H:%M:%S')

def setup():
    GPIO.setmode(GPIO.BOARD) # use PHYSICAL GPIO Numbering
    GPIO.setup(redLEDPin, GPIO.OUT) # set ledPin to OUTPUT mode
    GPIO.setup(greenLEDPin, GPIO.OUT) # set ledPin to OUTPUT mode
    GPIO.setup(redButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # set buttonPin to PULL UP INPUT mode
    GPIO.setup(greenButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # set buttonPin to PULL UP INPUT mode
    GPIO.setup(buzzerPin, GPIO.OUT) # set buzzerPin to OUTPUT mode

def lpr(imagePath):
    print(imagePath)
    result = subprocess.run(['alpr','-c', 'us', imagePath], capture_output=True)
    out = result.stdout.decode().split("\n");
    print(out)
    
    
    firstNumber = out[1].replace("- ","").strip().split(" ")
    print(firstNumber)
    if len(firstNumber) < 3 :
        return ("No License", "0")
    else :
        return (firstNumber[0].strip(),firstNumber[2].strip())
    
def loop():
    while True:
        if GPIO.input(greenButtonPin)==GPIO.LOW:
            
            lcd.clear()
            
            imagePath = take_picture_with_camera()
            result = lpr(imagePath)
            
            lcd.setCursor(0,0)
            lcd.message(result[0] + '\n')
            lcd.message(result[1] + '%')
            
            if float(result[1]) > 75:
                
                GPIO.output(greenLEDPin,GPIO.HIGH) 
                GPIO.output(buzzerPin,GPIO.HIGH)
                time.sleep(0.5)
                GPIO.output(buzzerPin,GPIO.LOW)
                GPIO.output(greenLEDPin,GPIO.LOW)
            
            else :
                GPIO.output(redLEDPin,GPIO.HIGH)
                GPIO.output(buzzerPin,GPIO.HIGH)
                time.sleep(3)
                GPIO.output(buzzerPin,GPIO.LOW)
            
        if GPIO.input(redButtonPin)==GPIO.LOW: 
            GPIO.output(redLEDPin,GPIO.LOW) 
            #print ('red LED turned on >>>') 
        else : 
            GPIO.output(redLEDPin,GPIO.LOW)
            

def destroy():
    lcd.clear()
    GPIO.output(buzzerPin,GPIO.LOW)
    GPIO.output(greenLEDPin,GPIO.LOW) 
    GPIO.output(redLEDPin,GPIO.LOW)
    GPIO.cleanup() # Release GPIO resource

if __name__ == '__main__': # Program entrance
    print ('Program is starting...')
    setup()
    try:
        mcp.output(3,1) # turn on LCD backlight
        lcd.begin(16,2) # set number of LCD lines and columns
        loop()
    except KeyboardInterrupt: # Press ctrl-c to end the program.
        destroy()
