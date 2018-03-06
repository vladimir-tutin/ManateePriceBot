Requirements:
- python3
- python3 modules discord.py, gspread, dateutil, ascyncio, re, oauth2client, dateutil

Usage:
- python3 discordSheet.py

Note:
- Update sheet.client.open("sheet").sheet1 with the name of the Google Spreadsheet
- Update creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope) with a credential file downloaded from Google
- Update discordClient.run('token') with oauth2 token provided by Discord
- Update  pin = await discordClient.send_message(discord.Object(id="channel pin") with the ID of the channel you want the bot to pin the message in

Commands:
- !help
- !price item
- !add item
- !add item nib=price nis=price
- !nib item price
- !nis item price
- !inb item price
- !ins item price
- !updatepin

TODO:
- Modify !add command to be able accept prices for initial add
- Integrate with runescape.wikia.com to display item limits upon !price command
- Create a "dictionary" to match misspellings and abbreviated item names
