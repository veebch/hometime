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
from random import choice
import machine
import _thread
import utime
import time
import network
import config
import urequests
import neopixel
import math
import os
import json
import re
import gc

# Time with daylight savings time and time zone factored in, edit this to fit where you are
worldtimeurl = "https://timeapi.io/api/TimeZone/zone?timezone=" + config.TIMEZONE
# The ID of the public Google Calendar to be used
calendar = config.CALENDAR
# The API key for google... Not sure why it is needed, but it seems to be
api_key = config.APIKEY
n = config.PIXELS           # Number of pixels on strip
p = config.GPIOPIN          # GPIO pin that data line of lights is connected to
barcolourlist = config.BARCOL	# RGB for bar color
eventcolourlist = config.EVENTCOL	# RGB for event color
schedule = config.SCHEDULE  # Working hours in config file (only used if google calendar not used)
flip = config.FLIP
googlecalbool = config.GOOGLECALBOOL
ignorehardcoded = config.IGNORE_HARDCODED
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()
time.sleep(1)
eventbool = False # Initialising, no need to edit
checkevery = config.REFRESH   # Number of seconds for interval refreshing neopixel
AP_NAME = "veebprojects"
AP_DOMAIN = "pipico.net"
AP_TEMPLATE_PATH = "ap_templates"
WIFI_FILE = "wifi.json"
if (ignorehardcoded is True) and (googlecalbool is False):
    print('incompatible options, setting ignorehardcoded to False')
    ignorehardcoded = False

def machine_reset():
    time.sleep(1)
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
         start = item["end"].get("dateTime", item["end"].get("date"))
         appointment_times.append(start)
    array = appointment_times
    for x in range(len(array)):
        array[x]=re.sub('.*T','',array[x])
    array=sorted(array)
    for x in array:
        print(x)
    return array


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
    print('Grab time:',worldtimeurl)
    try:
        response = urequests.get(worldtimeurl)
    except:
        print('Problem with',worldtimeurl)
    # parse JSON
    print('got response')
    parsed = response.json()
    print('parsed')
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


def bar(np, upto, clockin, clockout, event):
    barupto = hourtoindex(upto, clockin, clockout)
    if event is False:
        colourbar = barcolourlist[0]
    else:
        colourbar = barcolourlist[1]
    for i in range(barupto):
        np[i] = colourbar
        

def eventnow(hoursin, googletimes):
    # This returns whether you're currently in a meeting and will be used to change the colour of the bar
    event = False
    print('EventNow')
    try:
        for i in range(0,len(googletimes)-1,2):
            hourstart = timetohour(googletimes[i])
            hourend = timetohour(googletimes[i+1])
            if ((hourstart <= hoursin) & (hourend >= hoursin)):
                event = True
                print('In an event, bar will change colour')
    except:
        pass
    return event
   

def flipit(np,n):
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
            start= indexes.pop()
            for i in range(start,end):
                if valid(i):
                    np[i] = eventcolourlist[index % len(eventcolourlist)]
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

def hourtoindex(hoursin, clockin, clockout):
    index = int(math.floor(n*(hoursin - clockin)/(clockout-clockin)))
    if index < 0 or index > n:
        index = -1
    return index


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
    print ('Rainbow!')
    for j in range(255):
        for i in range(n):
            pixel_index = (i * 256 // n) + j
            np[i] = wheel(pixel_index & 255)
        np.write()


def atwork(clockin, clockout, time):
    work = False
    if (time >= clockin) & (time <clockout):
        work = True
    return work


def wifi_setup_mode():
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
    
    
def progress_bar(np):
    print("Entering Progress Bar Display Mode")
    # When you plug in, update rather than wait until the stroke of the next minute
    print("Connected to WiFi")
    # Set time and initialise variables
    dow, offset = set_time(worldtimeurl)
    clockin = 0
    clockout = 0
    eventbool = False
    lastloopwork = False
    appointment_times = []
    while True:
        try:
            # wipe led clean before adding the pixels that represent the bar
            for i in range(n):
                np[i] = (0, 0, 0)
            now = time.gmtime()
            hoursin = float(now[3])+float(now[4])/60 + float(now[5])/3600  # hours into the day
            dayname = whatday(int(now[6]))
            if ignorehardcoded is False:
                clockin = float(schedule[dayname][0]['clockin'])
                clockout = float(schedule[dayname][0]['clockout'])
            if googlecalbool:
                print('Updating from Google Calendar')
                try:
                    appointment_times = get_today_appointment_times(calendar, api_key, config.TIMEZONE)
                    eventbool = eventnow(hoursin, appointment_times)
                    if ignorehardcoded is True:
                        clockin = timetohour(appointment_times[0])
                        clockout = timetohour(appointment_times[len(appointment_times)-1]) 
                except:
                    print('Scheduling issues when looking at Google Calendar')
            working = atwork(clockin, clockout, hoursin)
            print(f"Working={working}, clock-in={clockin}, clock-out={clockout}, hours in={hoursin}")
            if working is True: # These only need to be added to the bar if you're working
                # Add the events and bar to np and flip if needed
                if googlecalbool: addevents(np, appointment_times, clockin, clockout)
                bar(np, hoursin, clockin, clockout,eventbool)
                if flip: np = flipit(np,n)
            np.write()
            gc.collect()  # clean up garbage in memory
            if (lastloopwork is True) & (working is False):
                # For event animations, use interrupts so that the time is exactly right
                rainbow_cycle(np)
                time.sleep(1)
                off(np)
                led.off()
                machine_reset() # You were working last cycle, now you aren't - it's hometime        
            lastloopwork = working
            time.sleep(checkevery) 
        except Exception as e:
            print('Exception:',e)
            off(np)
            time.sleep(1)
            machine.reset()
        except KeyboardInterrupt:
            off(np)


# Figure out which mode to start up in...
def main():
    np = neopixel.NeoPixel(machine.Pin(p), n)
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
                os.remove(WIFI_FILE)
                machine_reset()
            print(f"Connected to wifi, IP address {ip_address}")
            progress_bar(np)  # Contains all the progress bar code
    except Exception:
        # Either no wifi configuration file found, or something went wrong,
        # so go into setup mode
        for i in range(0, n):
            np[i] = (choice((0,255)), 0, 0)
        np.write()    
        wifi_setup_mode()
    
if __name__ == "__main__":
    main()
