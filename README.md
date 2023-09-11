[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)


# Hometime: A work/school day progress bar linked to a Google Calendar

A physical LED progress bar for the working day based on information from a public Google Calendar. The bar uses an addressable led strip and a Raspberry Pi Pico W. It:

- keeps you posted on how much of the workday (start of first meeting to end of last meeting) has already passed, 
- flashes when it's time for an event on the calendar, 
- rewards you with a pretty rainbow at hometime.

## Videos

Tap on the picture for a video of it being assembled and working as part of a home made whiteboard. Since the video was made, there have been some improvements to how meetings are displayed, that is shown in the second short video.

[![Video](images/video.png)](https://www.youtube.com/watch?v=MDij1lKcI70)

[![Mod demo](http://img.youtube.com/vi/boY1xJGBQk4/0.jpg)](http://www.youtube.com/watch?v=boY1xJGBQk4)

## Tutorial

There's a pretty comprehensive start-to-finish walkthrough by Dan Ionescu [here](https://medium.com/@ionescu.dan84/workday-progressbar-with-google-calendar-integration-b266aabd32a8)

## How it works

The progress bar displays your progress through the working day. It connects to wifi, grabs the time from a [time api](https://timeapi.io), then shows you how far through the day you are.

The events are maintained in a public Google calendar, and connection parameters are stored in the config file. For getting an API key, visit https://console.cloud.google.com/apis/credentials. For getting the calendar link just select 'share calendar' on google calendar and copy the link (it ends in `@group.calendar.google.com`)

If it is outside the working hours, no lights show.

## Hardware

- Raspberry Pi Pico W
- 5V Addressable LED strip (we used a 1 m, 144 LED, WS2812B Eco).

## Assembly

Attach the Light Strip to the Pico as described below:

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | Light Strip|
|-----------|------|
|   VBUS     | VCC  |
|   GND      | GND  |
|   15      | DATA  |

### Schematic:

![Schematic](https://github.com/veebch/hometime/blob/main/images/schematic_fritzing.png)


## Installing

Download a `uf2` image and install it on the Pico W according to the [instructions](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython) on the Raspberry Pi website.

Clone this repository to your computer using the commands (from a terminal):

```
cd ~
git clone https://github.com/veebch/hometime.git
cd hometime
mv config_example.py config.py
```

Check the port of the pico with the port listing command:
```
python -m serial.tools.list_ports
```
Now, using the port path (in our case `/dev/ttyACM0`) copy the contents to the repository by installing [ampy](https://pypi.org/project/adafruit-ampy/) and using  and the commands:

```
ampy -p /dev/ttyACM0 put main.py 
ampy -p /dev/ttyACM0 put config.py
ampy -p /dev/ttyACM0 put phew
ampy -p /dev/ttyACM0 put ap_templates
```
(*NB. make sure you are using the right port name, as shown in the port listing command above*)

Done! All the required files should now be on the Pico. Whenever you connect to USB power the script will autorun.

## Setup

On the first run, the pico will realise that it has no valid WiFi credentials and start up as an access point. To add them, on another WiFi enabled device (eg smartphone) connect to the network '**pi pico**'. You'll then be prompted to provide login credentials for your WiFi network. Once you've added these, the pico will restart and connect to WiFi.

## Configuration

Parameters are in `config.py`.

* If you do not want to use Google Calendar, you can set the calendar useage to **False** and rely on hardcoded clock in/out times.
* If you are going to use the Google Calendar functionality, you'll need an [API key](https://support.google.com/googleapi/answer/6158862?hl=en) and a public Google Calendar address.
* Set your timezone "**TIMEZONE**". The default is "Europe/Zurich"; choose one from [this list](https://logic.edchen.org/linux-all-available-time-zones/).
* Choose the number of LED pixels "**PIXELS**". Note: if you have the one-meter WS2812BLED strip mentioned above, leave the default as **144**.
* Set the "**GPIOPIN**" for controlling the LED strip (only change this if you're using different pins than the default). 
* You can also set RGB values for the progress bar "**BARCOL**", and events "**EVENTCOL**".
* If you need the strip to display from right to left, set "**FLIP**" to **True**.
* In the "SCHEDULE" config dictionary, change the 'clocking' and 'clockout' values for each day (or set **IGNORE_HARDCODED** to **True** if you'd like values derived from your calendar entries for the day)

That's it. Now whenever you plug it in to power, the code will autorun.

