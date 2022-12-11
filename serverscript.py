import subprocess
import json
import re

# Run the `gcalcli` command to get your agenda
agenda = subprocess.run(["gcalcli", "--nocolor", "--nocache", "agenda"], capture_output=True)
string = agenda.stdout.decode("utf-8")
regex = r".*(\d\d):(\d\d)"
stopatbreak = 2
breaksseen = 0
pattern = re.compile(regex)
timearray = []
# Iterate over the lines in the string
for line in string.split("\n"):
    # Search for the regex in each line
    match = pattern.search(line)
    if match:
        timeofdot=float(match.group(1))+float(match.group(2))/60
        print(timeofdot)
        timearray.append(timeofdot)
    if line == "":
        breaksseen += 1
        if breaksseen == 2:
            break

json_string = json.dumps(timearray)

with open('/data/www/array.json', 'w') as f:

  f.write(json_string)

