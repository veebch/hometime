CALENDAR = "INSERT YOUR CALENDAR NAME"        # "@group.calendar.google.com" also has to be in the string
APIKEY = "INSERT YOUR APIKEY"
TIMEZONE = "Europe/Zurich"
PIXELS = 144
GPIOPIN = 15
BARCOL = (0, 100, 0)                          # Color in RGB from 0 to 255
EVENTCOL = [(255, 255, 255), (255, 255, 0)]   # list of tuples used as meeting colours, if you only use one: [(255, 255, 255)]
FLIP = False                                  # Flip display (set to True if the strip runs from right to left)
TIPANI = "Blink"  # [Blink | Dim | None]      # Animation at the end of the progress (This has to be a string) [NOT IMPLEMENTED YET]
EVENTANI = "None" # [Blink | Breathe | None]  # The animation used when an event is triggert. (This has to be a string)
EVENTANIDURATION = 30                         # Length of the animation in seconds
GOOGLECALBOOL = True                          # Boolean for whether to check google calendar page
GOOGLEREFRESH = 60                            # Seconds between google calendar refresh
IGNORE_HARDCODED = False                      # Set to True if you want Clock in at the start of first meeting and Clockout at end of last meeting
SCHEDULE = {                                  # This doesn't get used if IGNORE_HARDCODED is True. Othewise, it's the working hours for the week. (9.5 = 09:30 AM; 13 = 01:00 PM)
    "monday":     [{"clockin": "9",   "clockout": "17"}],
    "tuesday":    [{"clockin": "9",   "clockout": "17"}],
    "wednesday":  [{"clockin": "9",   "clockout": "17"}],
    "thursday":   [{"clockin": "9",   "clockout": "17"}],
    "friday":     [{"clockin": "9",   "clockout": "17"}],
    "saturday":   [{"clockin": "0",   "clockout": "0"}],
    "sunday":     [{"clockin": "0",   "clockout": "0"}]
}
AP_NAME = "veebprojects"
AP_DOMAIN = "pipico.net"
AP_TEMPLATE_PATH = "ap_templates"
WIFI_FILE = "wifi.json"
