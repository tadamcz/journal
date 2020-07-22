import dropbox
from datetime import date
import credentials

# Set time zone
import os
import time
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()


delimiter = '####'

TOKEN = credentials.dropbox_token

dbx = dropbox.Dropbox(TOKEN)
md,res = dbx.files_download('/journal/journal.txt')
journaltext = res.content.decode('utf-8')

addition = delimiter+' '+date.today().strftime("%A")+' '+str(date.today())+' '+delimiter+'\n'
upload = addition+journaltext

print(upload)
dbx.files_upload(upload.encode('utf-8'),'/journal/journal.txt',mode=dropbox.files.WriteMode.overwrite)