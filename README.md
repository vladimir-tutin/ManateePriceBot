Requirements:
- python3
- python3 modules discord.py, gspread, dateutil, ascyncio, re, oauth2client, dateutil
- install via "pip install -r requirements.txt"

Usage:
- python3 discordSheet.py

Install Notes:
Update configData.py with the needed information, rename to configData.py

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
- Integrate with runescape.wikia.com to display item limits upon !price command
- Create a "dictionary" to match misspellings and abbreviated item names
- Add print()s for commands for verbose output of when functions are running
