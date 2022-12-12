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

NTP_DELTA = 2208988800 	# NTP delta is 1 Jan 1970 for host
GMT_OFFSET = 3600      	# hack because timezone support seems to be lacking, seconds relative to GMT
host = "pool.ntp.org"	# The ntp server used for grabbing time
n = 144   				# Number of pixels on strip
p = 15    				# GPIO pin that data line of lights is connected to
clockin = 8				# The time work starts (hours into day)
clockout = 17.5			# The time work ends (hours into day)
barcolor = (255, 50 ,25)# RGB for bar color
eventcolor = (0,0,255)	# RGB for event color

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
    clock = machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 'Europe/Zurich'  ))

def bar(np, upto):
    for i in range(hourtoindex(upto)):
        np[i]= barcolor
  
def addmeet(np,response):
    n = np.n
    for x in response:
        np[hourtoindex(x)] = eventcolor
                
def off(np):
    n=np.n
    for i in range(n):
        np[i]= (0, 0 , 0)
        np.write()
        
def hourtoindex(hoursin):
    index=int(math.floor(n*(float (hoursin) - clockin)/(clockout-clockin)))
    return index

def eventnow(hoursin):
    meetingnow = False
    for x in response:
        if hourtoindex(x) == hourtoindex(hoursin):
            meetingnow = True
    return meetingnow

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while wlan.isconnected()!= True:
    time.sleep(1)

np = neopixel.NeoPixel(machine.Pin(p), n)
todayseventsurl=secrets.LANURL
response=urequests.get(todayseventsurl).json()
now = set_time()
count = 1
firstrun = True   			# When you plug in, update rather than wait until the stroke of the next minute
try:
    while True:
        if time.gmtime()[5] == 0 or firstrun:
            hoursin = float(time.gmtime()[3])+float(time.gmtime()[4])/60	# hours into day
            if hoursin >= clockin and hoursin <= clockout:
                bar(np, hoursin)
                addmeet(np,response)
            else:
                off(np)
        if firstrun:		# If this was the initial update, mark it as complete
            firstrun = False
        count = (count + 1) % 2
        if eventnow(hoursin):
            np[hourtoindex(hoursin)]=tuple(z*count for z in eventcolor)
        else:
            np[hourtoindex(hoursin)]=tuple(z*count for z in barcolor)
        np.write()
        time.sleep(1)
except Exception as e:
    print(e)
    off(np)
except KeyboardInterrupt:
    off(np)
