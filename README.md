[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)


# Hoooometime? A work-day progress bar

A physical LED progress bar for the working day that includes information from Google Calendar. The bar uses an addressable led strip and a Raspberry Pi Pico W. It currently:

- keeps you posted on how much of the workday has already passed, 
- flashes when it's time for an event, 
- rewards you with a pretty rainbow at hometime.

## How it works

The progress bar measures the working day. It connects to wifi, grabs the time from an ntp server, then shows you how far through the day you are. It runs from your defined start time to hometime. 

There's also an optional and slightly elaborate link between Google Calendar and the bar. A computer running [gcalcli](https://github.com/insanum/gcalcli) on the LAN checks the agenda every few minutes and then pops the result on a local webserver. The script on the Pico checks that file and adds event start times as coloured dots.


If it is the weekend, of outside work hours, no lights show.

## Video

Here's a video of it working as part of a home made whiteboard.


[![Video](https://img.youtube.com/vi/MDij1lKcI70/maxresdefault.jpg)](https://www.youtube.com/watch?v=MDij1lKcI70)

## Hardware

- Raspberry Pi Pico W
- 1 m, 144 LED, 5V Addressable LED strip (we used a WS2812B Eco)

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
mv secrets_example.py secrets.py
```
Edit secrets.py to contain your WiFi credentials and (optionally) the url of your Google Calendar schedule. The schedule is created by running serverscript.py on a machine with gcalcli on, and a web server. For automation **systemd** or **cron** will automate running `serverscript.py` nicely. 

Check the port of the pico with the port listing command:
```
python -m serial.tools.list_ports
```
Now, using the port path (in our case `/dev/ttyACM0`) copy the contents to the repository by installing [ampy](https://pypi.org/project/adafruit-ampy/) and using  and the commands:

```
ampy -p /dev/ttyACM0 put main.py 
ampy -p /dev/ttyACM0 put secrets.py
```
(*nb. make sure you are using the right port name, as shown in the port listing command above*)

Done! All the required files should now be on the Pico. Whenever you sconnect to USB power the script will autorun.
