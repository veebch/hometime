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
import math
import socket
import struct

NTP_DELTA = 2208988800 	# NTP delta is 1 Jan 1970 for host
GMT_OFFSET = 3600      	# hack, seconds relative to GMT
host = "pool.ntp.org"	# The ntp server used for grabbing time
n = 144   				# Number of pixels on strip
p = 15    				# GPIO pin that data line of lights is connected to
barcolor = (0, 25, 0)	# RGB for bar color
eventcolor = (0, 0, 255)	# RGB for event color
flip = False				# Flip display (set to True if the strip runs from right to left)
googlecalbool = True		# Boolean for whether to check google calendar page
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()
time.sleep(1)
schedule = {
    "monday": [
      {
        "clockin": "9",
        "clockout": "17"
      }
    ],
    "tuesday": [
      {
        "clockin": "9",
        "clockout": "17"
      }
    ],
    "wednesday": [
      {
        "clockin": "9",
        "clockout": "17"
      }
    ],
    "thursday": [
      {
        "clockin": "9",
        "clockout": "17"
      }
    ],
    "friday": [
      {
        "clockin": "9",
        "clockout": "17"
      }
    ],
    "saturday": [
      {
        "clockin": "0",
        "clockout": "0"
      }
    ],
    "sunday": [
      {
        "clockin": "0",
        "clockout": "0"
      }
    ]
}


def whatday(weekday):
    dayindex = int(weekday)
    nameofday = ['monday', 'tuesday', 'wednesday', 'thursday','friday','saturday','sunday']
    day = nameofday[dayindex]
    return day


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
    barupto = hourtoindex(upto)
    for i in range(n):
        if flip ==  True:
            if i>=barupto:
                np[i] = barcolor
            else:
                np[i] = (0,0,0) 
        else:
            if i<=barupto:
                np[i] = barcolor
            else:
                np[i] = (0,0,0)



def addevents(np,response):
    for x in response:
        index = hourtoindex(x)
        if valid(index):
            np[index] = eventcolor


def valid(index):
    valid=False
    if index <= n and index > 0:
        valid = True
    return valid


def off(np):
    for i in range(n):
        np[i]= (0, 0 , 0)
        np.write()


def hourtoindex(hoursin):
    index=int(math.floor(n*(float (hoursin) - clockin)/(clockout-clockin)))
    if flip ==  True:
        index = n - 1 - index
    if index <= 1 or index >= n:
        index = -1
    return index


def eventnow(hoursin,response):
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



def atwork(clockin,clockout,time):
    index = -1
    if clockin != clockout:
        index=hourtoindex(time)
    work = False
    if index > -1:
        work = True
    return work


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while wlan.isconnected() is not True:
    time.sleep(1)
    print("Not connecting to WiFi\nWaiting\n")
np = neopixel.NeoPixel(machine.Pin(p), n)
todayseventsurl = secrets.LANURL
count = 1
firstrun = True 
# When you plug in, update rather than wait until the stroke of the next minute
print("connected to WiFi: Start loop")
off(np)
shonetoday = True
led.off()
set_time()
while True:
    try:
        now = time.gmtime()
        dayname = whatday(int(now[6]))
        clockin = float(schedule[dayname][0]['clockin'])
        clockout = float(schedule[dayname][0]['clockout'])
        hoursin = float(now[3])+float(now[4])/60							# hours into the day
        print('working?')
        working = atwork(clockin, clockout, hoursin)
        print(working, hoursin)
        if working is True:
            shonetoday = False
            # If not working, no lights will show
            # update lights at the stroke of every minute, or on first run
            bar(np, hoursin)
            if googlecalbool is True:
                response = urequests.get(todayseventsurl).json()
                eventbool = eventnow(hoursin, response)
                addevents(np, response)
            else:
                # This is where you would add hardcoded events if you were not using google
                eventbool =  False
            if firstrun:
                # If this was the initial update, mark it as complete
                firstrun = False
            count = (count + 1) % 2	
            # The value used to toggle lights
            if  eventbool == True:  									# If an event is starting, flash all LEDS otherwise just the end of the bar
                for i in range(n):
                    np[i]=tuple(z*count for z in eventcolor) 			# All lights
            else:
                ledindex = min(hourtoindex(hoursin), n)
                np[ledindex] = tuple(z*count for z in barcolor) 			# Just the tip of the bar
            np.write()
        else:
            if shonetoday is False:
                led.on()
                rainbow_cycle(np)
                shonetoday = True
                off(np)
                time.sleep(600)
        if wlan.isconnected() is not True:
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(secrets.SSID, secrets.PASSWORD)
            while wlan.isconnected() is not True:
                time.sleep(1)
                print("Not connecting to WiFi\nWaiting\n")
        if now[5] == 0 and now[4] == 44 and now[3] == 4:
            machine.reset()						# Reset at 4:44 because Jay Z, and to start afresh
        time.sleep(1)
        #led.toggle()														# LED HEARTBEAT	
    except Exception as e:
        print(e)
        machine.reset()
        off(np)
    except KeyboardInterrupt:
        off(np)
