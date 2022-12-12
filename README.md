# Progress Bar

A physical progress bar that uses a Raspberry Pi Pico W and an addressable led strip. 

The progress bar measures the working day. It runs from your defined start time to hometime. 

There's a slightly elaborate link between google calendar and the bar. A computer running gcalcli checks the agenda every few minutes and then pops the result on a local webserver. The script checks that file and adds event start times as coloured dots, as well as a progress bar for the working day.

If it is the weekend, of outside work hours, no lights show.

# To Do

the RTC automatically sets when connected to thonny, but not otherwise it seems....investigate
