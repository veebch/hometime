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

NTP_DELTA = 2208988800 # NTP is  1 Jan 1970
GMT_OFFSET = 3600      # hack because timezone support seems to be lacking, seconds relative to GMT
host = "pool.ntp.org"
n = 144   # Number of pixels on strip
p = 15    # GPIO pin that data line of lights is connected to

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

def demo(np):
    clockin = 8
    clockout = 17.5
    bedtime = 22.5
    if rtc.datetime()[3] >= 5:  # If it's after Friday (day of week is 5 or 6)
        weekend = True
    else:
        weekend = False
    n = np.n
#	This will create a dim background 'ideal' day based on day of week
    for i in range(n):
        if i < math.floor(n*clockin/24):
            np[i] = (1, 1, 0)
        elif i < math.floor(n*clockout/24) and weekend == False:
            np[i] = (0, 0, 1)
        elif i < math.floor(n*bedtime/24):
            np[i] = (0, 0, 0)
        else:
            np[i] = (1,1,0)
        time.sleep_ms(20)
        np.write()
        
def bar(np, upto):
    for i in range(upto):
        if i<=upto:
            np[i]= (255, 50 ,25)
    np.write()
    
def init(np, upto):
    for i in range(upto):
        if i<=upto:
            np[i]= (255, 50 ,25)
            time.sleep_ms(20)
            np.write()

def addmeet(np,response):
    n = np.n
    for x in response:
        index=int(math.floor((float (x) /24)*n))
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
    upto=int(math.floor(n*(float(rtc.datetime()[4])+float(rtc.datetime()[4])/60)/24))
    demo (np)
    init (np, upto)

    while True:
        bar(np, upto)
        addmeet(np,response)
        time.sleep(100)
except Exception as e:
    print(e)
    off(np)
except KeyboardInterrupt:
    off(np)
    
    
