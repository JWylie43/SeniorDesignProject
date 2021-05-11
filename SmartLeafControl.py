import serial
import array as arr
import time
import csv
import RPi.GPIO as GPIO
from rpi_lcd import LCD


lcd = LCD()

#Button Setup
GPIO.setmode(GPIO.BCM)   # Specify We Want to reference Physical pins

# Raspberry Pi pin configuration:
pump_relay = 21
light_relay = 20

LED_blue = 13
LED_red = 19

GPIO.setup(pump_relay, GPIO.OUT)
GPIO.setup(light_relay, GPIO.OUT)

GPIO.setup(LED_blue, GPIO.OUT)
GPIO.setup(LED_red, GPIO.OUT)

#reset value
x = 0

#temp values, will change with testing
luxVLow = 800
luxLow = 1000
luxNormal = 1500
luxHigh = 2000
luxVHigh = 2500

def Relay_control(waterLevel,luxAvg):
    if int(time.strftime("%M")) >= 0 and int(time.strftime("%M")) < 15 and int(waterLevel) == 1:#Pump will run for the first 15 minutes of every hour.
        GPIO.output(pump_relay, GPIO.HIGH)
        print("Pump relay ON")
    else:
    #if int(time.strftime("%M")) > 15:                    #Pump will turn off after running for 15 minutes.
        GPIO.output(pump_relay, GPIO.LOW)
        print("Pump relay OFF")
        
    if int(time.strftime("%H")) >= 8 and int(time.strftime("%H")) < 17: #and lightOnTracker == 0: #lightOn/OffTracker so we only execute these two statements once per day (mainly to not clutter the cmd out with relay on 
        GPIO.output(light_relay, GPIO.HIGH)
        print("Light relay ON")

    #if int(time.strftime("%H")) < 8 and int(time.strftime("%H")) > 17 and lightOffTracker == 0: #Start considering turning the lights off after 5PM
    else:
        if int(float(luxAvg)) > luxVHigh: #If lux is very high, turn off imediately 
            GPIO.output(light_relay, GPIO.LOW)
            print("Light relay OFF")
            #lightOffTracker = 1 #make it so you dont go back into the after 5pm block again
        elif int(time.strftime("%H")) >= 17 and int(time.strftime("%M")) >= 30 and int(float(luxAvg)) > luxHigh: #check next condition after 30 minutes
            GPIO.output(light_relay, GPIO.LOW)
            print("Light relay OFF")
            #lightOffTracker = 1
        elif int(time.strftime("%H")) >= 18 and int(float(luxAvg)) > luxNormal: #check next condition after 30 minutes
            GPIO.output(light_relay, GPIO.LOW)
            print("Light relay OFF")
            #lightOffTracker = 1
        elif int(time.strftime("%H")) >= 18 and int(time.strftime("%M")) >= 30 and int(float(luxAvg)) > luxLow: #another 30
            GPIO.output(light_relay, GPIO.LOW)
            print("Light relay OFF")
            #lightOffTracker = 1
        elif int(time.strftime("%H")) >= 19 and int(float(luxAvg)) > luxVLow: #one more time
            GPIO.output(light_relay, GPIO.LOW)
            print("Light relay OFF")
            #lightOffTracker = 1
        elif int(time.strftime("%H")) > 19 and int(time.strftime("%M")) > 30: #ok fuck it just turn em off
            GPIO.output(light_relay, GPIO.LOW)
            print("Light relay OFF")
            #lightOffTracker = 1
        else:
            print("Light relay ON")
            
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=5)
data_split = [1]
while len(data_split) != 4:
    ser.flush()
    while ser.in_waiting == 0:
        time.sleep(.5)
    if ser.in_waiting > 0:
        time.sleep(.1)
        serial_data = ser.readline().decode('utf-8').strip()
        print(serial_data)
        data_split = serial_data.split("|")
        time.sleep(.5)
while(x < 1):
    print(data_split)
    pH = data_split[0]
    temp = data_split[1]
    waterLevel = data_split[2]
    avgLux = data_split[3]
    
    print("pH: ",pH)
    lcd.clear()
    lcd.text('pH:'+ str(pH),1)
    if float(pH) < 7 and float(pH) > 5:
        GPIO.output(LED_red, GPIO.LOW)
        GPIO.output(LED_blue, GPIO.HIGH)
        lcd.text('Good',2)
        pH_flag = 0
    elif float(pH) >= 7:
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
        lcd.text('pH too high',2)
        pH_flag = 1
    elif float(pH) <= 5:
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
        lcd.text('pH too low',2)
        pH_flag = 1
    time.sleep(2)
        
    print("C: ",temp)
    #display Temp value in C
    lcd.clear()
    lcd.text('Temp(C):'+temp,1)
    if float(temp) < 25 and float(temp) > 20:
        GPIO.output(LED_red, GPIO.LOW)
        GPIO.output(LED_blue, GPIO.HIGH)
        lcd.text('Good',2)
        temp_flag = 0
    elif float(temp) >= 25:
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
        lcd.text('Too high',2)
        temp_flag = 1
    elif float(temp) <= 20:
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
        lcd.text('Too low',2)
        temp_flag = 1
    time.sleep(2)

    print("Water Level: ",waterLevel)
    #display Temp value in C
    lcd.clear()
    lcd.text('Water Level:',1)
    if (waterLevel == '1'):     
        lcd.text('Good',2)
        GPIO.output(LED_blue, GPIO.HIGH)
        GPIO.output(LED_red, GPIO.LOW)
        level_flag = 0
    else: #(data_split[3] == 0):
        lcd.text('Low',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
        level_flag = 1
    time.sleep(2)

    print("Average Lux: ",avgLux)
    GPIO.output(LED_blue, GPIO.HIGH)
    GPIO.output(LED_red, GPIO.LOW)
    lcd.clear()
    lcd.text('Avg Lux:',1)
    lcd.text(avgLux,2)
    time.sleep(2)
    lcd.clear()
    
    lcd.text('Bounds Errors:',1)
    issues = [pH_flag,temp_flag,level_flag]
    print(issues)
    if sum(issues) == 3:
        lcd.text('pH-temp-wLevel',2)
        
    elif sum(issues) == 0:
        lcd.text('No Errors',2)
        GPIO.output(LED_blue, GPIO.HIGH)
        GPIO.output(LED_red, GPIO.LOW)
    elif issues[0]==1 and issues[1]==1:
        lcd.text('pH-temp',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
    elif issues[0]==1 and issues[2]==1:
        lcd.text('pH-wLevel',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
    elif issues[1]==1 and issues[2]==1:
        lcd.text('temp-wLevel',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
    elif issues[0]==1:
        lcd.text('pH',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
    elif issues[1]==1:
        lcd.text('temp',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
    elif issues[2]==1:
        lcd.text('wLevel',2)
        GPIO.output(LED_blue, GPIO.LOW)
        GPIO.output(LED_red, GPIO.HIGH)
    

    with open("test_data.csv","a") as f:
        writer = csv.writer(f,delimiter=",")
        writer.writerow([time.strftime("%d/%m/%y"),time.strftime("%I:%M %p"),data_split[0],data_split[1],data_split[2],data_split[3]])
    Relay_control(waterLevel,avgLux)
    time.sleep(10)
    lcd.clear()
    ser.flush()
    data_split = ""
    x = 1
