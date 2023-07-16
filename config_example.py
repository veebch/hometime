CALENDAR = "INSERT YOUR CALENDAR NAME"
APIKEY = "INSERT YOUR APIKEY"
TIMEZONE = "Europe/Zurich"
# Lighting
PIXELS = 144
GPIOPIN = 15
BARCOL = (0,100,0)
EVENTCOL =[(255, 255, 255),(255,255,0)] # list of tuples used as meeting colours
FLIP = False                # Flip display (set to True if the strip runs from right to left)
GOOGLECALBOOL = True        # Boolean for whether to check google calendar page
IGNORE_HARDCODED = True
SCHEDULE = {                # This only gets used if you're NOT using google calendar
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

