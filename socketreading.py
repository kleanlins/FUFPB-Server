# sensors
import Adafruit_CharLCD as LCD
import Adafruit_MCP3008
from mpu6050 import mpu6050
import MAX6675.MAX6675 as MAX6675

# STD LIBS
from _thread import *
import time
import socket
from datetime import datetime

# CONNECTION DATA
host = ''
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((host, port))

except:
    print(str(e))

s.listen(5)
print("Socket created.")

# FILENAME DATA
date, timer = str(datetime.now()).split(" ")
hour, milli = timer.split(".")

# SCREEN PINS
lcd_rs = 16
lcd_en = 21
lcd_d4 = 20
lcd_d5 = 19
lcd_d6 = 13
lcd_d7 = 26
lcd_bl = 4

# LCD ROWS AND COLUMNS
lcd_c = 16
lcd_r = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_c, lcd_r, lcd_bl)
lcd.message("Hello\neveryone.")
time.sleep(2.0)

csvfile = "{0} {1}.csv".format(date,hour)
# MCP PINS
CLK = 14
MOSI = 18
MISO = 15
CS = 23
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# TERMOCOUPLE PINS
CLK_T = 24
MISO_T = 12
CS0 = 7
CS1 = 8
CS2 = 25
t1 = MAX6675.MAX6675(CLK_T, CS0, MISO_T)
print("Termocouple 1 created")
t2 = MAX6675.MAX6675(CLK_T, CS1, MISO_T)
print("Termocouple 2 created")
t3 = MAX6675.MAX6675(CLK_T, CS2, MISO_T)
print("Termocouple 3 created")

mpu = mpu6050(0x68)

data = ""
complete_data = ""

def main_reading(status):
    #main reading for global variables

    count = 0
    date, timer = str(datetime.now()).split(" ")
    hour, milli = timer.split(".")
  
    csvfile = "local_{0} {1}.csv".format(date,hour)

    while True:
        with open(csvfile, 'a') as file:
            #while count < 100:

            #count += 1
            temp1 = t1.readTempC()
            temp2 = t2.readTempC()
            temp3 = t3.readTempC()

            global data
            data = "{},{},{},".format(temp1, temp2, temp3)

            acc = mpu.get_accel_data()
            acx = acc['x']
            acy = acc['y']
            acz = acc['z']
            temp = mpu.get_temp()
                
            data += "{},{},{},{},".format(acx, acy, acz, temp)

            mcp_values = [0] * 8
            for i in range(5, 8):
                mcp_values[i] = mcp.read_adc(i)
                        
            data += "{},{},{}".format(mcp_values[5], mcp_values[6], mcp_values[7])	
       
            print(data)
            file.write(data + "\n")

            global complete_data
            complete_data = data

            time.sleep(0.100)

        #count = 0


def thread_reading(conn):
        
    date, timer = str(datetime.now()).split(" ")
    hour, milli = timer.split(".")
  
    csvfile = "remote_{0} {1}.csv".format(date,hour)

    with open(csvfile, 'w') as file:

        while True:
        
            client_data = conn.recv(1024)

            print("Sending: " + complete_data)
            file.write(str(complete_data) + "\n")

            if not client_data:
                break

            conn.send(complete_data)
            data = " "
            time.sleep(.100)	

    conn.close()


start_new_thread(main_reading, ("start",))
print("Main thread started.")
time.sleep(1)

while True:
    print("Waiting for a new connection.")
    conn, addr = s.accept()
    print("Connected to {}:{}.".format(addr[0], addr[1]))

    start_new_thread(thread_reading, (conn,))

