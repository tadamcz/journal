import dropbox
from datetime import date
import credentials

# Set time zone
import os
import time
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

# Dropbox login
TOKEN = credentials.dropbox_token
dbx = dropbox.Dropbox(TOKEN)

# Download journal
md,response = dbx.files_download('/journal/journal.md')
journaltext = response.content.decode('utf-8')

# The main part, where we prepend the '#### YYYY-MM-DD ####' header to the journal
delimiter = '####'
addition = delimiter+' '+date.today().strftime("%A")+' '+str(date.today())+' '+delimiter+'\n'
upload = addition+journaltext #we prepend today's header to the journal

# Upload to dropbox
dbx.files_upload(upload.encode('utf-8'),'/journal/journal.md',mode=dropbox.files.WriteMode.overwrite)