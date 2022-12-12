# Progress Bar

A physical progress bar for the working day, that uses a Raspberry Pi Pico W and an addressable led strip. 

The progress bar measures the working day. It connects to wifi, grabs the time from an ntp server, then shows you how far through the day you are. It runs from your defined start time to hometime. 

There's also an optional and slightly elaborate link between Google Calendar and the bar. A computer running gcalcli on the LAN checks the agenda every few minutes and then pops the result on a local webserver. The script on the Pico checks that file and adds event start times as coloured dots.

If it is the weekend, of outside work hours, no lights show.

# To Do

the RTC automatically sets when connected to thonny, but not otherwise it seems....investigate
