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
    n = np.n
    # cycle
    for i in range(n):
        np[i % n] = (1, 5, 1)
        utime.sleep_ms(20)
        np.write()
    for i in range(n):
        np[n-(i % n)-1]= (0, 0, 0)
        utime.sleep_ms(20)
        np.write()
        
def bar(np, upto):
    for i in range(upto):
        if i<=upto:
            np[i]= (50, 50 ,255)
    np.write()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
print(wlan.isconnected())
n = 144
p = 15
rtc = machine.RTC()
print(rtc.datetime())
np = neopixel.NeoPixel(machine.Pin(p), n)
upto = int(math.floor(n*(float(rtc.datetime()[4])+float(rtc.datetime()[4])/60)/24))
demo(np)
while True:
    bar(np, upto)
    utime.sleep(100)
