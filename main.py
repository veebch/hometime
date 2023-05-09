#
#  Progress Bar. Takes a pico W and a light strip to make a physical progress bar.
#  PoC, fork and make it better
#  GPL 3
#
import machine
import time
import network
import config
import urequests
import neopixel
import math

# Time with daylight savings time and time zone factored in, edit this to fit where you are
worldtimeurl = config.CLOCK
# The ID of the public Google Calendar to be used
calendar = config.CALENDAR
# The API key for google... Not sure why it is needed, but it seems to be
api_key = config.APIKEY
n = config.PIXELS           # Number of pixels on strip
p = config.GPIOPIN          # GPIO pin that data line of lights is connected to
barcolor = config.BARCOL    # RGB for bar color
eventcolor = config.EVENTCOL# RGB for event color
flip = False                # Flip display (set to True if the strip runs from right to left)
googlecalbool = True        # Boolean for whether to check google calendar page
led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()
time.sleep(1)
eventbool = False # Initialising, no need to edit
checkgoogleevery = 10
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


def get_today_appointment_times(calendar_id, api_key):
    # Get the date from the RTC
    rtc = machine.RTC()
    year, month, day, _, hour, minute, _, _ = rtc.datetime()

    # Format the date
    date = "{:04d}-{:02d}-{:02d}".format(year, month, day)

    # Format the request URL
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    url += f"?timeMin={date}T00:00:00Z&timeMax={date}T23:59:59Z&key={api_key}"


    # Send the request
    print(url)
    response = urequests.get(url)
    data = response.json()
    print(data)

    # Extract the appointment times
    appointment_times = []
    for item in data.get("items", []):
         start = item["start"].get("dateTime", item["start"].get("date"))
         appointment_times.append(start)
    print(appointment_times)
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
        print(worldtimeurl)
        response = urequests.get(worldtimeurl)
        print(response) 
        # parse JSON
        parsed = response.json()
        print(parsed)
        datetime_str = str(parsed["currentLocalTime"])
        print(datetime_str)
        year = int(datetime_str[0:4])
        month = int(datetime_str[5:7])
        day = int(datetime_str[8:10])
        hour = int(datetime_str[11:13])
        minute = int(datetime_str[14:16])
        second = int(datetime_str[17:19])
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
        print('SET')
        return dow


def bar(np, upto):
    barupto = hourtoindex(upto)
    for i in range(n):
        if flip is True:
            if i >= barupto:
                np[i] = barcolor
            else:
                np[i] = (0, 0, 0) 
        else:
            if i <= barupto:
                np[i] = barcolor
            else:
                np[i] = (0, 0, 0)


def timetohour(time_string):

    # Extract the time portion from the string
    time_part = time_string.split("T")[1].split("+")[0]

    # Split the time into hours, minutes, and seconds
    hours, minutes, seconds = time_part.split(":")

    parsed_time = int(hours)+int(minutes)/60+int(seconds)/3600

    return parsed_time


def addevents(np,response):
    for x in response:
        print(x)
        hour = timetohour(x)
        index = hourtoindex(hour)
        print("INDEX: ",index)
        if valid(index):
            np[index] = eventcolor


def valid(index):
    valid = False
    if index <= n and index > 0:
        valid = True
    return valid


def off(np):
    print('turnoff')
    for i in range(n):
        np[i] = (0, 0, 0)
        np.write()


def hourtoindex(hoursin):
    index = int(math.floor(n*(hoursin - clockin)/(clockout-clockin)))
    if flip is True:
        index = n - 1 - index
    if index <= 1 or index >= n:
        index = -1
    return index


def eventnow(hoursin, response):
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


def atwork(clockin, clockout, time):
    index = -1
    if clockin != clockout:
        index = hourtoindex(time)
    work = False
    if index > -1:
        work = True
    return work


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.SSID, config.PASSWORD)
while wlan.isconnected() is not True:
    time.sleep(1)
    print("Not connecting to WiFi\nWaiting\n")
np = neopixel.NeoPixel(machine.Pin(p), n)
count = 1
firstrun = True
# When you plug in, update rather than wait until the stroke of the next minute
print("connected to WiFi: Start loop")
time.sleep(1)
off(np)
shonetoday = True
led.off()
set_time(worldtimeurl)
print(time.localtime())
# appointment_times = get_today_appointment_times(calendar, api_key)
# print(appointment_times)
googleindex = 0
while True:
    try:
        googleindex = googleindex + 1
        now = time.gmtime()
        dayname = whatday(int(now[6]))
        clockin = float(schedule[dayname][0]['clockin'])
        clockout = float(schedule[dayname][0]['clockout'])
        hoursin = float(now[3])+float(now[4])/60  # hours into the day
        print('working?')
        working = atwork(clockin, clockout, hoursin)
        print(working, hoursin)
        if working is True:
            shonetoday = False
            # If not working, no lights will show
            # update lights at the stroke of every minute, or on first run
            bar(np, hoursin)
            if (googlecalbool is True) & (googleindex == 1):
                appointment_times = get_today_appointment_times(calendar, api_key)
                time.sleep(1)
                #eventbool = eventnow(hoursin, appointment_times)
                print('getgoogle')
            if (googleindex > checkgoogleevery):
                googleindex = 0
            if googlecalbool is True:
                addevents(np, appointment_times)
            if firstrun:
                # If this was the initial update, mark it as complete
                firstrun = False
            count = (count + 1) % 2
            # The value used to toggle lights
            if  eventbool is True:
                # If an event is starting, flash all LEDS otherwise just the end of the bar
                for i in range(n):
                    np[i] = tuple(z*count for z in eventcolor)
                    # All lights
            else:
                ledindex = min(hourtoindex(hoursin), n)
                np[ledindex] = tuple(z*count for z in barcolor)
                # Just the tip of the bar
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
            wlan.connect(config.SSID, config.PASSWORD)
            while wlan.isconnected() is not True:
                time.sleep(1)
                print("Not connecting to WiFi\nWaiting\n")
        if now[5] == 0 and now[4] == 44 and now[3] == 4:
            machine.reset()  # Reset at 4:44 because Jay Z, and to start afresh
        time.sleep(1)
    except Exception as e:
        print(e)
        off(np)
        time.sleep(1)
        machine.reset()
    except KeyboardInterrupt:
        off(np)
