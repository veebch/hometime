"""
    Progress Bar. Takes a pico W and a light strip to make a physical progress bar.
    PoC, fok and make it better
    
     Copyright (C) 2023 Veeb Projects https://veeb.ch

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

from phew import access_point, connect_to_wifi, is_connected_to_wifi, dns, server
from phew.template import render_template
import machine
import _thread
import utime
import time
import network
import config # type: ignore
import urequests
import neopixel
import math
import os
import json
import re

worldtimeurl = "https://timeapi.io/api/TimeZone/zone?timezone=" + config.TIMEZONE
calendar = config.CALENDAR
api_key = config.APIKEY
n = config.PIXELS
p = config.GPIOPIN
barcolor = config.BARCOL
eventcollist = config.EVENTCOL
tipanimation = config.TIPANI
eventanimation = config.EVENTANI
eventanidur = config.EVENTANIDURATION
schedule = config.SCHEDULE
flip = config.FLIP
googlecalbool = config.GOOGLECALBOOL
checkevery = config.GOOGLEREFRESH
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()
time.sleep(1)
eventbool = False # Initialising, no need to edit
KeyboardExceptionCount = 0 # Initialising, no need to edit
dimcol = (barcolor[0]//4, barcolor[1]//4, barcolor[2]//4)
AP_NAME = config.AP_NAME
AP_DOMAIN = config.AP_DOMAIN
AP_TEMPLATE_PATH = config.AP_TEMPLATE_PATH 
WIFI_FILE = config.WIFI_FILE
IGNORE_HARDCODED = config.IGNORE_HARDCODED
rDURpPXL = config.RESTOREANIDURATIONPERPIXEL

def machine_reset():
    utime.sleep(1)
    print("Resetting...")
    machine.reset()

def get_today_appointment_times(calendar_id, api_key, tz):
    # Get the date from the RTC
    rtc = machine.RTC()
    year, month, day, _, hour, minute, _, _ = rtc.datetime()

    # Format the date
    date = "{:04d}-{:02d}-{:02d}".format(year, month, day)

    # Format the request URL
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    url += f"?timeMin={date}T00:00:00Z&timeMax={date}T23:59:59Z&timeZone={tz}&key={api_key}"

    # Send the request
    response = urequests.get(url)
    data = response.json()
    # Extract the appointment times
    appointment_times = []
    for item in data.get("items", []):
         if item["status"] == "cancelled":
             continue
         start = item["start"].get("dateTime", item["start"].get("date"))
         appointment_times.append(start)
         end = item["end"].get("dateTime", item["end"].get("date"))
         appointment_times.append(end)
    return appointment_times


def whatday(weekday):
    dayindex = int(weekday)
    nameofday = [
                    'monday',
                    'tuesday',
                    'wednesday',
                    'thursday',
                    'friday',
                    'saturday',
                    'sunday']
    day = nameofday[dayindex]
    return day


def set_time(worldtimeurl):
        print('Grab time: ', worldtimeurl)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} # type: ignore
        try:
            response = urequests.get(worldtimeurl, headers=headers)
        except:
            print('Problem Getting Time')
        # parse JSON
        parsed = response.json() # type: ignore
        datetime_str = str(parsed["currentLocalTime"])
        year = int(datetime_str[0:4])
        month = int(datetime_str[5:7])
        day = int(datetime_str[8:10])
        hour = int(datetime_str[11:13])
        minute = int(datetime_str[14:16])
        second = int(datetime_str[17:19])
        offset = int(parsed["currentUtcOffset"]["seconds"])/3600
        # update internal RTC
        machine.RTC().datetime((year,
                      month,
                      day,
                      0,
                      hour,
                      minute,
                      second,
                      0))
        dow = time.localtime()[6]
        return dow,offset
    

def bar(np, upto, clockin, clockout):
    barupto = hourtoindex(upto, clockin, clockout)
    for i in range(barupto):
        np[i] = barcolor
        

def flipit(np, n):
    temp=[0]*n
    for i in range(n):
        temp[i]=np[i]
    for i in range(n):
        np[i]=temp[n-1-i]
    return np


def timetohour(time_string):

    # Extract the time portion from the string
    if time_string.count('-') == 0:
        time_part = time_string.split("+")[0]
    else:
        time_part = time_string.split("-")[0]
    # Split the time into hours, minutes, and seconds
    hours, minutes, seconds = time_part.split(":")

    parsed_time = int(hours)+int(minutes)/60+int(seconds)/3600

    return parsed_time


def addevents(np, response, clockin, clockout):
    indexes = []
    for x in response:
        hour = timetohour(x)
        index = hourtoindex(hour, clockin, clockout)
        if valid(index):
            indexes.append(index)
    #pop out pairs of values and paint in meetings
    try:
        index = 0
        while True:
            end = indexes.pop()
            start = indexes.pop()
            for i in range(start,end):
                if valid(i):
                    np[i] = eventcollist[index % len(eventcollist)]
            index = (index + 1) 
    except:
        pass
        
    

def valid(index):
    valid = False
    if index <= n and index >= 0:
        valid = True
    return valid


def off(np):
    print('Turn off all LEDs')
    for i in range(n):
        np[i] = (0, 0, 0)
        np.write()
        time.sleep(rDURpPXL)

def hourtoindex(hoursin, clockin, clockout):
    index = int(math.floor(n*(hoursin-clockin)/(clockout-clockin)))
    if index < 0 or index > n:
        index = -1
    return index


def eventnow(hoursin, response):
    event = False
    for x in response:
        hour = timetohour(x)
        if abs(hour - hoursin) < eventanidur/3600:
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


def rainbow_cycle(np, cycle=1):
    print ('Rainbow!')
    for x in range(cycle):
        for j in range(255):
            for i in range(n):
                pixel_index = (i * 256 // n) + j
                np[i] = wheel(pixel_index & 255)
            np.write()


def atwork(clockin, clockout, time):
    work = False
    if (time >= clockin) & (time < clockout):
        work = True
    return work


def eventaniend(np):
    ledindex = min(hourtoindex(hoursin, clockin, clockout), n)
    for i in range(n):
        np[i] = (0, 0, 0)
    for i in range(ledindex+1):
        np[i] = barcolor
        np.write()
        time.sleep(rDURpPXL)
    
def blink(np, seconds):
    for j in range(seconds//2):
        for i in range(n):
            np[i] = eventcollist[0]
        np.write()
        time.sleep(1)
        for i in range(n):
            np[i] = (0, 0, 0)
        np.write()
        time.sleep(1)
    eventaniend(np)
                    
def breathe(np, seconds):
    nval = 0
    n = np.n
    index = 0
    sleeptime = .05
    breathespeed = .1
    cycles = seconds/sleeptime
    while index < cycles:
        val = int((255/2)*(1+math.sin(nval)))
        for j in range(n):
            np[j]=(val, val , val)      # Set LED to a converted HSV value
        np.write()
        nval = (nval + breathespeed ) % 360
        time.sleep(sleeptime)
        index = index + 1
    eventaniend(np)


def sorted_appointments(array):
    # This is just a placeholder for when/if the google api sends garbled times
    print('Appointment times:')
    for x in range(len(array)):
        array[x]=re.sub('.*T', '', array[x])
    array=sorted(array)
    for x in array:
        print(x)
    return array
    

def application_mode(np):
    global clockin, clockout, hoursin, KeyboardExceptionCount
    print("Entering application mode.")
    count = 1
    # When you plug in, update rather than wait until the stroke of the next minute
    print("Connected to WiFi")
    time.sleep(1)
    dow, offset = set_time(worldtimeurl)
    firstrun = True
    checkindex = 0
    appointment_times = []
    led.off()
    print('Begin endless loop')
    while True:
        try:
            # wipe led clean before adding stuff
            for i in range(n):
                np[i] = (0, 0, 0)
            eventbool = False
            checkindex = checkindex + 1
            now = time.gmtime()
            hoursin = float(now[3])+float(now[4])/60 + float(now[5])/3600  # hours into the day
            dayname = whatday(int(now[6]))
            if checkindex == 1:
                clockin = float(schedule[dayname][0]['clockin'])
                clockout = float(schedule[dayname][0]['clockout'])
                if googlecalbool is True: # overwrite clockin/clockout times if Google Calendar is to be used
                    appointment_times = []
                    clockin = 0
                    clockout = 0
                    eventbool = False
                    print('Updating from Google Calendar')
                    try:
                        appointment_times = get_today_appointment_times(calendar, api_key, config.TIMEZONE)
                        appointment_times = sorted_appointments(appointment_times)
                        eventbool = eventnow(hoursin, appointment_times[::2]) # only the even elements (starttimes)
                        if IGNORE_HARDCODED is True:
                            clockin = timetohour(appointment_times[0])
                            clockout = timetohour(appointment_times[len(appointment_times)-1]) 
                    except:
                        print('Scheduling issues')
            working = atwork(clockin, clockout, hoursin)
            print(f"Working={working}, clock-in={clockin}, clock-out={clockout}, hours in={hoursin}")
            if abs(hoursin - clockout) < 40/3600: # If we're within 40 seconds of clockout reset
                machine.reset()
            if working is True:
                # Draw the bar
                bar(np, hoursin, clockin, clockout)
                # Draw the events
                addevents(np, appointment_times, clockin, clockout)
                if eventbool is False:
                    ledindex = min(hourtoindex(hoursin, clockin, clockout), n)
                    # Toggle the end led of the bar
                    if "Blink" in tipanimation:
                        count = (count + 1) % 2
                    elif "Dim" in tipanimation:
                        np[ledindex+1] = dimcol
                    # The value used to toggle lights
                    np[ledindex] = tuple(z*count for z in barcolor)
                    # Just the tip of the bar
                elif "Breathe" in eventanimation: breathe(np, eventanidur)
                elif "Blink" in eventanimation: blink(np, eventanidur)    
                if flip == True:
                    np = flipit(np,n)
            # reset the google check index if needed
            if (checkindex > checkevery):
                checkindex = 0
            if firstrun:
                firstrun = False
                if working:
                    eventaniend(np)
            np.write()
            time.sleep(1)
        except Exception as e:
            print('Exception: ', e)
            off(np)
            time.sleep(1)
            machine.reset()
        except KeyboardInterrupt:
            off(np)
            KeyboardExceptionCount += 1
            if KeyboardExceptionCount == 1: eventaniend(np)
            else: break


def setup_mode():
    print("Entering setup mode...")

    def ap_index(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN)

        return render_template(f"{AP_TEMPLATE_PATH}/index.html")

    def ap_configure(request):
        print("Saving wifi credentials...")

        with open(WIFI_FILE, "w") as f:
            json.dump(request.form, f)
            f.close()

        # Reboot from new thread after we have responded to the user.
        _thread.start_new_thread(machine_reset, ())
        return render_template(f"{AP_TEMPLATE_PATH}/configured.html", ssid=request.form["ssid"])

    def ap_catch_all(request):
        if request.headers.get("host") != AP_DOMAIN:
            return render_template(f"{AP_TEMPLATE_PATH}/redirect.html", domain=AP_DOMAIN)

        return "Not found.", 404

    server.add_route("/", handler=ap_index, methods=["GET"])
    server.add_route("/configure", handler=ap_configure, methods=["POST"])
    server.set_callback(ap_catch_all)

    ap = access_point(AP_NAME)
    ip = ap.ifconfig()[0]
    dns.run_catchall(ip)
    server.run()


np = neopixel.NeoPixel(machine.Pin(p), n)
rainbow_cycle(np, 3)
off(np)

# Main Logic
# Figure out which mode to start up in...
try:
    os.stat(WIFI_FILE)

    # File was found, attempt to connect to wifi...
    with open(WIFI_FILE) as f:
        wifi_credentials = json.load(f)
        ip_address = connect_to_wifi(wifi_credentials["ssid"], wifi_credentials["password"])

        if not is_connected_to_wifi():
            # Bad configuration, delete the credentials file, reboot
            # into setup mode to get new credentials from the user.
            print("Bad wifi connection!")
            print(wifi_credentials)
            for i in range(0, n, 2):
                np[i] = (100, 0, 0)
                np.write()
                time.sleep(15*2/n)
            for i in reversed(range(n)):
                np[i] = (100, 0, 0)
                np.write()
                time.sleep(15/n)
            os.remove(WIFI_FILE)
            machine_reset()

        print(f"Connected to wifi, IP address {ip_address}")
        application_mode(np)  # Contains all the progress bar code

except Exception:
    # Either no wifi configuration file found, or something went wrong,
    # so go into setup mode.
    off(np)
    led.on()
    for i in range(0, n, 2):
        np[i] = (100, 100, 0)
        np.write()
    setup_mode()
