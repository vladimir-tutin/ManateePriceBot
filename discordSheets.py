import os
import sys
import discord
import asyncio
import gspread
import re
import datetime
from dateutil.relativedelta import relativedelta
from oauth2client.service_account import ServiceAccountCredentials

scriptpath = "./configData.py"
sys.path.append(os.path.abspath(scriptpath))
import configData as cfg

#STATIC VARIABLES
ITEM = 1
LOW = 2
HIGH = 3
LAST_UPDATED = 4

#Global Variable
pinID = None

discordClient = discord.Client()

# Credentials for connecting to Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name(cfg.credFile, scope)
client = gspread.authorize(creds)
 
# Connection to Google Sheet
sheet = client.open(cfg.sheetName).sheet1

#Get all items and margins from sheet
def getAllItems():
    index = indexItems()
    w, h = 4, len(index);
    allItemList = [[0 for x in range(w)] for y in range(h)] 
    for item, elem in enumerate(index):
        allItemList[item][0] = elem
        allItemList[item][1] = sheet.cell((item + 1),LOW).value
        allItemList[item][2] = sheet.cell((item + 1),HIGH).value
        allItemList[item][3] = sheet.cell((item + 1),LAST_UPDATED).value
    return allItemList

#index the Items in the sheet
def indexItems():
    item_list = list(filter(None, sheet.col_values(ITEM)))
    return item_list
  
#Get row of searched item  
def getItemRow(itemList, itemSearch):
    i = 0
    print('Searching for', str(itemSearch))
    for index, elem in enumerate(itemList):
        if str(elem) == str(itemSearch):
            i = index + 1
    print('Found', str(itemSearch), 'at row', i)
    return i
    
def getPrices(item):
    index = indexItems()
    try:
        itemRow = getItemRow(index, item)
        lowPrice = sheet.cell(itemRow, 2).value
        highPrice = sheet.cell(itemRow, 3).value
        lastUpdated = sheet.cell(itemRow, 4).value
        currentTime = str(datetime.datetime.today().strftime('%m/%d/%y %H:%M:%S'))
        cTime = datetime.datetime.strptime(currentTime, '%m/%d/%y %H:%M:%S')
        rTime = datetime.datetime.strptime(lastUpdated, '%m/%d/%y %H:%M:%S')
        diff = relativedelta(rTime, cTime)
        itemMargins = item + " Price: " + lowPrice + " - " + highPrice + "\nUpdate Age: Hours: " + str(diff.hours) + " Minutes: " + str(diff.minutes)
    except:
        itemMargins = "Not found in the database, run _!add " + item + "_ to add it"
    return itemMargins
    
def addItem(item, lowPrice = None, highPrice = None):
    print("Attempting to add", item)
    index = indexItems()
    #check if item already exists
    try:
        sheet.find(item)
        print(item, "already exists in database")
        return "already exists"
    except:
        sheet.update_cell((len(index) + 1), 1, item)
        if lowPrice != None:
            sheet.update_cell((len(index) + 1), 2, lowPrice)
            sheet.update_cell((len(index) + 1), 3, highPrice)
            sheet.update_cell((len(index) + 1), 4, str(datetime.datetime.today().strftime('%m/%d/%y %H:%M:%S')))
        print(item, "added to database")
    return "success"
       
def setPrice(item, option, price):
    if option == "nib" or option == "ins":
        #check to make sure item exists first
        try:
            if sheet.find(item):
                itemExists = True
        except:
            print(item, "doesnt exist in database")
            return "no item"
        
        if itemExists == True:
            itemList = indexItems()
            itemRow = getItemRow(itemList, item)
            sheet.update_cell(itemRow, LOW, price)
            time = str(datetime.datetime.today().strftime('%m/%d/%y %H:%M:%S'))
            sheet.update_cell(itemRow, LAST_UPDATED, time)
            return "updated"
    elif option == "nis" or option == "inb":
        #check to make sure item exists first
        try:
            if sheet.find(item):
                itemExists = True
        except:
            print(item, "doesnt exist in database")
            return "no item"
        
        if itemExists == True:
            itemList = indexItems()
            itemRow = getItemRow(itemList, item)
            sheet.update_cell(itemRow, HIGH, price)
            time = str(datetime.datetime.today().strftime('%m/%d/%y %H:%M:%S'))
            sheet.update_cell(itemRow, LAST_UPDATED, time)
            return "updated"

# Update the Pin with new prices            
def updatePin():
    allItemList = getAllItems()
    pinMsg = ""
    pos = 0
    for index, elem in enumerate(allItemList):
        if pos != 0:
            rowTime = str(allItemList[pos][3])
            currentTime = str(datetime.datetime.today().strftime('%m/%d/%y %H:%M:%S'))
            cTime = datetime.datetime.strptime(currentTime, '%m/%d/%y %H:%M:%S')
            rTime = datetime.datetime.strptime(rowTime, '%m/%d/%y %H:%M:%S')
            diff = relativedelta(cTime, rTime)
            if diff.hours >= 4:
                flag = "- "
            else:
                flag = "+ "
            pinMsg = pinMsg + flag + allItemList[pos][0] + ": " + allItemList[pos][1] + " - " + allItemList[pos][2] + "\n"
        pos += 1
    return pinMsg

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    print('------')
    
    #PIN SETUP
    pinMsg = updatePin()
    pin = await discordClient.send_message(discord.Object(id=cfg.channelID), "```diff\n- Red refers to over an hour old \n" + pinMsg + "```")
    await discordClient.pin_message(pin)
    global pinID
    pinID = pin

@discordClient.event
async def on_message(message):
    #Commands start with "!"
    if message.content.startswith("!"):
        #Determine if command has args, command goes in cmd, args in args. Separate the args later 
        try:
             cmdMsg = re.search("^!(\w*)\s(.*)$", message.content)
             cmd = cmdMsg.group(1).lower()
             args = cmdMsg.group(2)
        except:
             cmdMsg = re.search("^!(.*)$", message.content)
             cmd = cmdMsg.group(1)
                
         #!add command
        if cmd == "add":
            try:
                item = re.search("^(.*)\s(?:nib=|ins=)\s*(\w*)\s(?:nis=|inb=)(\w*)$", args).group(1)
                lowPrice = re.search("^(.*)\s(?:nib=|ins=)\s*(\w*)\s(?:nis=|inb=)(\w*)$", args).group(2)
                highPrice = re.search("^(.*)\s(?:nib=|ins=)\s*(\w*)\s(?:nis=|inb=)(\w*)$", args).group(3)
                if addItem(item, lowPrice, highPrice) == "already exists":
                    msg = args + " already exists in the database.\nYou can update it's prices with !NIB " + args + " PRICE or !NIS " + args + " PRICE"
                    await discordClient.send_message(message.channel, msg)
                else:
                    msg = item + " added to the database, you can now add prices with !NIB and !NIS"
                    await discordClient.send_message(message.channel, msg)
                    pinMsg = updatePin()
                    await discordClient.edit_message(pinID, "```diff\n- Red refers to over an hour old \n" + pinMsg + "```")
                    await discordClient.send_message(message.channel, "Pin Updated!")
             
            except:
                item = args
                if addItem(args) == "already exists":
                    msg = args + " already exists in the database.\nYou can update it's prices with !NIB " + args + " PRICE or !NIS " + args + " PRICE"
                    await discordClient.send_message(message.channel, msg)

        if cmd == "price":
            print("!price command invoked")
            price = getPrices(args)
            msg = price
            await discordClient.send_message(message.channel, msg)
            print("\n------------------------------")
            
        if cmd == "nib" or cmd == "ins" or cmd == "nis" or cmd == "inb": 
            print("!nib/nis/ins/inb command invoked")
            item = re.search("^(.*)\s(\w*)$", args).group(1)
            price = re.search("^(.*)\s(\w*)$", args).group(2)
            status = setPrice(item, cmd, price)
            if status == "no item":
                msg = item + " doesn't exist in database.\n Add it with !add " + item
                tmp = await discordClient.send_message(message.channel, msg)
            elif status == "updated":
                msg = item + " " + cmd + " price updated to " + price
                tmp = await discordClient.send_message(message.channel, msg)
                editPinMsg = updatePin()
                await discordClient.edit_message(pinID, "```diff\n- Red refers to over 4 hours old \n" + editPinMsg + "```")
                
        if cmd == "updatepin":
            print("!updatepin command invoked")
            print("Updating Pins")
            pinMsg = updatePin()
            await discordClient.edit_message(pinID, "```diff\n- Red refers to over an hour old \n" + pinMsg + "```")
            await discordClient.send_message(message.channel, "Pin Updated!")
                
#Bot oauth2 authentication       
discordClient.run(cfg.discordAuth)
