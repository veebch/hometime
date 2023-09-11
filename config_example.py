# Calendar

CALENDAR = "INSERT YOUR CALENDAR NAME"          # "@group.calendar.google.com" also has to be on the end of the string (see 'get shareable link' on calendar on google 
APIKEY = "INSERT YOUR APIKEY"
TIMEZONE = "Europe/Zurich"
GOOGLECALBOOL = True                            # Boolean for whether to check google calendar page
GOOGLEREFRESH = 30                              # Seconds between google calendar refresh
IGNORE_HARDCODED = False                        # Set to True if you want Clock in at the start of first meeting and Clockout at end of last meeting
SCHEDULE = {                                    # This doesn't get used if IGNORE_HARDCODED is True. Othewise, it's the working hours for the week. (9.5 = 09:30 AM; 13 = 01:00 PM)
    "monday":     [{"clockin": "9",   "clockout": "17"}],
    "tuesday":    [{"clockin": "9",   "clockout": "17"}],
    "wednesday":  [{"clockin": "9",   "clockout": "17"}],
    "thursday":   [{"clockin": "9",   "clockout": "17"}],
    "friday":     [{"clockin": "9",   "clockout": "17"}],
    "saturday":   [{"clockin": "0",   "clockout": "0"}],
    "sunday":     [{"clockin": "0",   "clockout": "0"}]
}

# Neopixel

PIXELS = 144                                    # The number of pixels on the neopixel strip
GPIOPIN = 15                                    # The pin that the signal wire of the LED strip is connected to
BARCOL = [(0, 100, 0),(0,0,100)]                # Color in RGB from 0 to 255 of the bar when in and not in meeting respectively
EVENTCOL = [(255, 255, 255), (255, 255, 0)]     # list of tuples used as meeting colors, if you only use one: [(255, 255, 255)]
FLIP = False                                    # Flip display (set to True if the strip runs from right to left)
