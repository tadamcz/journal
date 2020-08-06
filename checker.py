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
# time.tzset()

# Dropbox login
TOKEN = credentials.dropbox_token
dbx = dropbox.Dropbox(TOKEN)

# Download journal
md,response = dbx.files_download('/journal/journal.md')
journaltext = response.content.decode('utf-8')


# Extract the entries
## Find '#### YYYY-MM-DD ####' entry headers using regular expressions
delimiter = '####'
reg = re.compile(delimiter+'.*'+delimiter)
header_regexresults_iterator =  reg.finditer(journaltext)
header_regexresults = [x for x in header_regexresults_iterator]

## Create dictionary of entries, where each value is the text of an entry
entries = {}
for i in range(len(header_regexresults)-1):
	header_regexresult = header_regexresults[i]
	entry_start_index = header_regexresult.end()+1 # Entry starts after its header

	if i != len(header_regexresults):
		entry_end_index = header_regexresults[i+1].start() #beginning of the next entry's header
	else: #catch the case where we are at the last entry
		entry_end_index = len(journaltext)
	entry_date_str = header_regexresult.group() #for the dictionary key, we use the header. This isn't actually used anywhere below
	entries[entry_date_str] = journaltext[entry_start_index:entry_end_index] #put the entry string in dictionary

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
req = requests.get('https://www.beeminder.com/api/v1/users/tmkadamcz/goals/journal/datapoints.json', params=params)
datapoints = req.json()

## Delete the day's datapoint so we don't have to bother checking if it exists or not
for datapoint in datapoints:
	daystamp = dparser.parse(datapoint['daystamp'],fuzzy=True).date()
	if daystamp == date.today():
		id = datapoint['id']
		requests.delete(
			'https://www.beeminder.com/api/v1/users/tmkadamcz/goals/journal/datapoints/' + id + '.json',
			params=params)

## Send today's datapoint. Only check today's entry, so the user can't get credit on beeminder for retroactively
## created journal entries
for entry in validity_dict:
	entrydate = dparser.parse(entry,fuzzy=True).date()
	if entrydate == date.today():
		params['value'] = 1 if validity_dict[entry] else 0
		params['daystamp'] = entry
		requests.post('https://www.beeminder.com/api/v1/users/tmkadamcz/goals/journal/datapoints.json', params=params)
