# Progress Bar

A physical progress bar that uses a raspberry pi pico W and an addressable led strip. The progress bar runs from midnight to midnight.
There's a slightly elaborate link between google calendar and the bar. A computer running gcalcli checks the agenda every few minutes and then pops the result on a local webserver. The script checks that file and adds appointments as blue dots.
