#
#  Progress Bar. Takes a pico W and a light strip to make a physical progress bar.
#  PoC, make it better and fork
#  GPL 3
#
import machine
import time
import network
import secrets
import urequests
import neopixel
import re, math
import socket
import struct

NTP_DELTA = 2208988800 	# NTP is  1 Jan 1970
GMT_OFFSET = 3600      	# hack because timezone support seems to be lacking, seconds relative to GMT
host = "pool.ntp.org"	# The ntp server used for grabbing time
n = 144   				# Number of pixels on strip
p = 15    				# GPIO pin that data line of lights is connected to
clockin = 8				# The time work starts (hours into day)
clockout = 17.5			# The time work ends (hours into day)

def set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA  + GMT_OFFSET  
    tm = time.gmtime(t)
    print("time:",tm)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 'Europe/Zurich'  ))
    print("systime:",time.localtime())
        
def bar(np, upto):
    for i in range(upto):
        if i<=upto:
            np[i]= (255, 50 ,25)
    np.write()
    
def addmeet(np,response):
    n = np.n
    for x in response:
        index=int(math.floor(((float (x) - clockin)/(clockout-clockin))*n))
        print(index)
        np[index] = (0,0,255)
    np.write()

            
def off(np):
    n=np.n
    for i in range(n):
        np[i]= (0, 0 , 0)
        np.write()          


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while wlan.isconnected()!= True:
    time.sleep(1)
set_time()
np = neopixel.NeoPixel(machine.Pin(p), n)
pingzapierurl="http://throb.local/array.json"
response=urequests.get(pingzapierurl).json()
print(response)
try:
    rtc = machine.RTC()
    while True:
        hoursin = float(rtc.datetime()[4])+float(rtc.datetime()[4])/60	# hours into day
        upto=int(math.floor(n*(hoursin-clockin)/(clockout-clockin))) 	# number of the LEDs into working day
        if upto >=1 and upto <= n:
            bar(np, upto)
            addmeet(np,response)
        else:
            off(np)
        time.sleep(60)
except Exception as e:
    print(e)
    off(np)
except KeyboardInterrupt:
    off(np)
    
