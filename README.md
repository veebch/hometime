[![YouTube Channel Views](https://img.shields.io/youtube/channel/views/UCz5BOU9J9pB_O0B8-rDjCWQ?label=YouTube&style=social)](https://www.youtube.com/channel/UCz5BOU9J9pB_O0B8-rDjCWQ)

[![Instagram](https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/v_e_e_b/)


# Progress Bar

A physical progress bar for the working day, that uses a Raspberry Pi Pico W and an addressable led strip.

## How it works

The progress bar measures the working day. It connects to wifi, grabs the time from an ntp server, then shows you how far through the day you are. It runs from your defined start time to hometime. 

There's also an optional and slightly elaborate link between Google Calendar and the bar. A computer running [gcalcli](https://github.com/insanum/gcalcli) on the LAN checks the agenda every few minutes and then pops the result on a local webserver. The script on the Pico checks that file and adds event start times as coloured dots.


If it is the weekend, of outside work hours, no lights show.

# Assembly

### Light Sensor

| [Pico GPIO](https://www.elektronik-kompendium.de/sites/raspberry-pi/bilder/raspberry-pi-pico-gpio.png) | BH1745 |
|-----------|------|
|   VBUS     | VCC  |
|   GND      | GND  |
|   15      | DATA  |

