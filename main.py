import machine
import utime
import network
import secrets
import utime
import urequests
import neopixel
import re, math
import random

def demo(np):
    clockin = 8
    clockout = 17.5
    bedtime = 22.5
    if rtc.datetime()[3] > 4:
        weekend = True
    else:
        weekend = False
    n = np.n
#	This will create a dim background 'ideal' day based on day of week
    for i in range(n):
        if i < math.floor(n*clockin/24) and weekend == False:
            np[i] = (1, 1, 0)
        elif i < math.floor(n*clockout/24) and weekend == False:
            np[i] = (0, 0, 1)
        elif i < math.floor(n*bedtime/24):
            np[i] = (0, 1, 0)
        else:
            np[i] = (1,1,0)
        utime.sleep_ms(20)
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
            utime.sleep_ms(20)
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
    utime.sleep(1)
n = 144
p = 15
np = neopixel.NeoPixel(machine.Pin(p), n)
try:
    rtc = machine.RTC() 
    upto=int(math.floor(n*(float(rtc.datetime()[4])+float(rtc.datetime()[4])/60)/24))
    demo (np)
    init (np, upto)

    while True:
        bar(np, upto)
        utime.sleep(100)
except:
    off(np)
    
    

    
