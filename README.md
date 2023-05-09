[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)


# Hometime: A work/school day progress bar that talks to Google Calendar

A physical LED progress bar for the working day that includes information from a public Google Calendar. The bar uses an addressable led strip and a Raspberry Pi Pico W. It:

- keeps you posted on how much of the workday has already passed, 
- flashes when it's time for an event on the Calendar, 
- rewards you with a pretty rainbow at hometime.

## Video

Tap on the picture for a video of it being assembled and working as part of a home made whiteboard.

[![Video](https://img.youtube.com/vi/MDij1lKcI70/maxresdefault.jpg)](https://www.youtube.com/watch?v=MDij1lKcI70)

## How it works

The progress bar displays your progress through the working day. It connects to wifi, grabs the time from a [time api](https://timeapi.io), then shows you how far through the day you are.

The events are maintained in a public Google calendar, and connection parameters are stored in the config file.


If it is outside work hours, no lights show.

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

## Installing

Download a `uf2` image and install it on the Pico W according to the [instructions](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython) on the Raspberry Pi website.

Clone this repository to your computer using the commands (from a terminal):

```
cd ~
git clone https://github.com/veebch/hometime.git
cd hometime
mv config_example.py config.py
```
Edit config.py to contain your WiFi credentials and other parameters. If you are going to use the Google Calendar functionality, you'll need an API key and a public Google Calendar address.

Check the port of the pico with the port listing command:
```
python -m serial.tools.list_ports
```
Now, using the port path (in our case `/dev/ttyACM0`) copy the contents to the repository by installing [ampy](https://pypi.org/project/adafruit-ampy/) and using  and the commands:

```
ampy -p /dev/ttyACM0 put main.py 
ampy -p /dev/ttyACM0 put config.py
```
(*nb. make sure you are using the right port name, as shown in the port listing command above*)

Done! All the required files should now be on the Pico. Whenever you sconnect to USB power the script will autorun.

## Configuration

You can edit the code to give your start/end time for each day. That, and a number of other parameters are in `config.py`
