import re
import dateutil.parser as dparser
import requests
import dropbox
from datetime import date
import credentials

# Set time zone
import os
import time
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

# Access token
TOKEN = credentials.dropbox_token

dbx = dropbox.Dropbox(TOKEN)
md,res = dbx.files_download('/journal/journal.txt')
journaltext = res.content.decode('utf-8')

delimiter = '####'

# Extract the entries
reg = re.compile(delimiter+'.*'+delimiter)
entries = {}
regexresults =  reg.finditer(journaltext)
regexresults = [x for x in regexresults]

for i in range(len(regexresults)):
	found = regexresults[i]
	try:
		end = regexresults[i+1].start()
	except IndexError:
		end = len(journaltext)
	start = found.end()+1
	entries[found.group()] = journaltext[start:end]

# Check entries for validity
def isvalidjournalentry(s):
	return len(s)>30

validity_dict = {}
for entry in entries:
	try:
		date_of_entry = dparser.parse(entry,fuzzy=True).date()
	except:
		date_of_entry = None
	validity_dict[str(date_of_entry)] = isvalidjournalentry(entries[entry])

print(validity_dict)

# Send to beeminder
params = {'auth_token':credentials.beeminder_token}
r = requests.get('https://www.beeminder.com/api/v1/users/tmkadamcz/goals/journal/datapoints.json', params=params)
datapoints = r.json()

# Delete the day's datapoint so we don't have to bother checking if it exists or not
for datapoint in datapoints:
	daystamp = dparser.parse(datapoint['daystamp'],fuzzy=True).date()
	if daystamp == date.today():
		id = datapoint['id']
		r = requests.delete(
			'https://www.beeminder.com/api/v1/users/tmkadamcz/goals/journal/datapoints/' + id + '.json',
			params=params)

# Send today's datapoint. Only check today's entry, so the user can't get credit on beeminder for retroactively
# created journal entries
for entry in validity_dict:
	entrydate = dparser.parse(entry,fuzzy=True).date()
	if entrydate == date.today():
		params['value'] = 1 if validity_dict[entry] else 0
		params['daystamp'] = entry
		requests.post('https://www.beeminder.com/api/v1/users/tmkadamcz/goals/journal/datapoints.json', params=params)
