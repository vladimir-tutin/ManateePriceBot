Requirements:
- python3
- python3 modules discord.py, gspread, dateutil, ascyncio, re

Usage:
python3 discordSheet.py

Note:
Update sheet.client.open("sheet").sheet1 with the name of the Google Spreadsheet
Update creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) with a credential file downloaded from Google
Update discordClient.run('token') with oauth2 token provided by Discord

Commands:
!help
!price item
!add item
!nib item price
!nis item price
!inb item price
!ins item price
!updatepin
