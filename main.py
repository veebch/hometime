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
barcolor = (5, 50 ,0)	# RGB for bar color
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
    clock = machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0  ))
    return tm[6]+1

def bar(np, upto):
    for i in range(hourtoindex(upto)):
        np[i]= barcolor
  
def addmeet(np,response):
    n = np.n
    for x in response:
        np[hourtoindex(x)] = eventcolor
        if hourtoindex(x)+1 < n:
            np[hourtoindex(x)+1] = eventcolor
                
def off(np):
    n=np.n
    for i in range(n):
        np[i]= (0, 0 , 0)
        np.write()
        
def hourtoindex(hoursin):
    index=int(math.floor(n*(float (hoursin) - clockin)/(clockout-clockin)))
    return index

def eventnow(hoursin):
    event = False
    for x in response:
        if hourtoindex(x) == hourtoindex(hoursin):
            event = True
    return event

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) 


def rainbow_cycle(np):
    for j in range(255):
        for i in range(n):
            pixel_index = (i * 256 // n) + j
            np[i] = wheel(pixel_index & 255)
        np.write()
        
def atwork(dow,time):
    work = False
    if dow > 5:
        pass
    else:
        if time >= clockin and time <= clockout:
            work = True
    return work
        
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while wlan.isconnected()!= True:
    time.sleep(1)
np = neopixel.NeoPixel(machine.Pin(p), n)
todayseventsurl=secrets.LANURL
response=urequests.get(todayseventsurl).json()
dayofweek = set_time()
count = 1
firstrun = True   																# When you plug in, update rather than wait until the stroke of the next minute
while True:
    try:
        now = time.gmtime()
        hoursin = float(now[3])+float(now[4])/60								# hours into the day
        working = atwork(dayofweek,hoursin)
        if working:
            if time.gmtime()[5] == 0 or firstrun: 								# update lights at the stroke of every minute, or on first run
                bar(np, hoursin)
                addmeet(np,response)
                if firstrun:													# If this was the initial update, mark it as complete
                    firstrun = False
            count = (count + 1) % 2												# The value used to toggle lights
            if eventnow(hoursin):  												# If an event is starting, flash all LEDS otherwise just the end of the bar
                for i in range(n):
                    np[i]=tuple(z*count for z in eventcolor) 					# All lights
            else:
                np[hourtoindex(hoursin)]=tuple(z*count for z in barcolor) 		# Just the tip of the bar
            np.write()
        if hoursin - clockout > 0 and hoursin - clockout < (1/60):
            rainbow_cycle(np)
            off(np)
            time.sleep(600)														# Sleep for 10 min
        if now[5] == 0 and now[4] == 44 and now[3] == 4:
            machine.reset()														# Reset at 4:44 because Jay Z
        time.sleep(1)
    except Exception as e:
        print(e)
        off(np)
    except KeyboardInterrupt:
        off(np)

