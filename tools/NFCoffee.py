#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'Roman'
'''
################################################
#@NFCoffee
# This Class provides all the functions that are needed to
# manage the RFID Coffee data.
# Most of the function will be accessed through a GUI but this
# class could be used by any other python tool aswell.
# A basic usage is
#   myCoffee = NFCoffee()
#   myCoffee.setPirce(0.2)
#   myCoffee.setMinimumCoffees(4)
#   myCoffee.readData()
#   allCoffees = myCoffee.getData()
#   #... do what ever you want with allCoffees
#   #create a xlsx report
#   myCoffee.export()
#
#
# Requirements:
#   The Class will by default search for two Files in the workingdir
#   USER.TXT and COUNT.TXT where the last one will be created by
#   the Arduino Box.
#   USER.TXT
#       Is a TAB separated file with Linux Lineendings (\n).
#       It contains the UUID of the NFC-Chip in HEX in the first
#       column and the readable name of the user in the second column.
#       This file is only needed to create a human readable report.
#       Example:
#           88EEDDCCBB	Max Mustermann
#           88EEDDCC34	Foo Bar
#   COUNT.TXT
#       This file is accessed by this class and the arduino.
#       The arduino logs all NFC cards and increments a counter for
#       each ID.
#       WARNING: As the arduino is not very flexible it ist very important
#               not to change this file manually.
#       The file format is very strict.
#       It accepts a 5 Bytes-ID in HEX format than a TAB (\t) and then
#       4 digits integer in decimal format. As lineend it accepts
#       a single newline character(\n)
#       Example:
#           88EEDDCC34	0012
#           99EEDDCCBB	0009
#       The NFCoffee class will modify the COUNT.TXT aswell.
#       In the NFCoffee.export() Function it will do three thing with the
#       File:
#           1) But a Backup of the file into count.zip (automaticly created)
#           2) Rename the current COUNT.TXT into ~COUNT.TXT by overwriting the old one
#           3) Recreate a COUNT.TXT with all the coffess that have a count smaller than
#               minimumCoffees so the count could be increase in the next month.
################################################
'''

import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from xlsxwriter.utility import xl_range
import sys
import os
import time
import zipfile

class NFCoffee():
    def __init__(self):
        # init attibutes:
        #The Dict with the User ID, Name and count of Coffees, where the ID is the Key
        self.mData = {}
        self.mMinimumCoffees = 8    # 3EUR at the beginning
        self.mPrice = 0.4           # 0,4 EUR
        self.mMessages = []
        self.mSdPath = ""

    def readData(self, path=None):
        """
        Reads the data from COUNT.TXT and USER.TXT and assoziates it with each other. One can retrieve the data using
        getData() as a list of dicts with the fields uuid, name and count.
        :param path: Path to the SD Card (Default is . )
        :return: void
        :raise Exception: Multiple Exceptions regarding file-io and file-format.
        """
        if not path:
            path = self.mSdPath
        else:
            self.setSdPath(path)
        ###
        #Clear the old data:
        ###
        self.mData = {}
        try:
            with open(path + 'USER.TXT') as file:  # Use file to refer to the file object
                for line in file:
                    uuid, name = line.replace("\n", '').split("\t", maxsplit=1)
                    #Check is we hav two keys in the file -> Something went terribly wrong
                    if uuid in self.mData:
                        raise Exception("Error 1: duplicate ID in USER.TXT")
                        return
                        #if not: we add it to our dict
                    self.mData[uuid] = {'uuid': uuid, 'name': name, 'count': 0}
        except Exception as e:
            print(e)
            raise Exception("File USER.TXT not found, or it contains errors, are you in the right directory? {path}"
                            .format(path=path))

        #read the coffe-file.
        try:
            with open(path + 'COUNT.TXT') as file:  # Use file to refer to the file object
                for line in file:
                    uuid, count = line.replace("\n", '').split("\t", maxsplit=1)
                    try:
                        self.mData[uuid]['count'] = int(count)
                    except Exception as e:
                        print(e)
                        print("Unknown UUID", uuid, "found in COUNTS.txt")
                        self.mMessages.append("Unbekannte UUID " + uuid + " in COUNTS.txt gefunden")
                        self.mData[uuid]={'uuid': uuid, 'name': ''}
                        self.mData[uuid]['count'] = int(count)
        except Exception as e:
            raise Exception("File COUNT.TXT not found, or it contains errors")


    def setPrice(self, price):
        try:
            self.mPrice = price
        except Exception as e:
            raise Exception("Could not set PRICE")

    def price(self):
        return self.mPrice

    def setMinimumCoffees(self, minimumCoffeeAmount):
        try:
            self.mMinimumCoffees = minimumCoffeeAmount
        except Exception as e:
            raise Exception("Could not set Minimum Coffees")

    def minimumCoffees(self):
        return self.mMinimumCoffees

    def export(self, filename=None):
        """
        Does three things:ä
            - Exports the data into a xlsx file
            - backups the count.txt
            - clear all entries from the counts.txt That are larger than minimumCoffees
        :param filename: The filename of the xlsx file. DEFAULT: Abrechnung_<timestamp>.xlsx
        :return: void
        :raise Exception: Multiple exceptions for file-io and consistensy errors
        """
        # ################################
        # Create the excel sheet
        #################################
        # Create a workbook and add a worksheet.

        if filename is None:
            filename = 'Abrechnung_'+time.strftime("%Y-%m-%d_%H-%M-%S")

        if not filename.endswith(".xlsx"):
            filename += '.xlsx'
            
        workbook = xlsxwriter.Workbook(filename )
        worksheet = workbook.add_worksheet('Kaffee-Abrechnung')

        # Add a number format for cells with money.
        moneyFormat = workbook.add_format({'num_format': u'0.00€'})
        resultFormat = workbook.add_format({'bold': True, 'top': 1})

        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        col = 0
        worksheet.write(0, 0, 'Name')
        worksheet.set_column(0, 0, 50)
        worksheet.write(0, 1, 'Anzahl')
        worksheet.write(0, 2, 'Betrag')
        worksheet.set_column(2, 2, 10, moneyFormat)
        worksheet.write(0, 3, '€/Kaffe:')
        worksheet.write(0, 4, self.mPrice, moneyFormat)
        # Iterate over the data and write it out row by row.
        # OLD Version without sorting for key, item in counts.items():
        for key, item in self.mData.items():
            worksheet.write(row, col, item['name'])
            worksheet.write(row, col + 1, item['count'])
            worksheet.write(row, col + 2, '=PRODUCT(E1,' + xl_rowcol_to_cell(row, col + 1) + ')')
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total', resultFormat)
        worksheet.write(row, 1, '=SUM(' + xl_range(1, 1, row - 1, 1) + ')', resultFormat)
        worksheet.write(row, 2, '=SUM(' + xl_range(1, 2, row - 1, 2) + ')', resultFormat)

        try:
            workbook.close()
        except Exception as e:
            self.mMessages.append(str(e))
            raise Exception("EXCEL workbook could not be created")

        #########################################
        ## Remove the old Count File and back it up
        #########################################
        backupFilename = 'COUNT_'+os.path.basename(filename).replace('.xlsx', '') + ".TXT"
        try:
            zip = zipfile.ZipFile(self.mSdPath+"count.zip", "a")
            i=0
            while backupFilename in zip.namelist():
                i += 1
                backupFilename = 'COUNT_'+str(i)+"_"+os.path.basename(filename).replace('.xlsx', '') + ".TXT"
            zip.write(self.mSdPath+"COUNT.TXT", backupFilename)
            zip.close()
        except Exception as e:
            self.mMessages.append(str(e))
            raise Exception("FATAL ERROR:  Backup of CUNT.TXT could not be saved int count.zip"
                            "\nSTOPPING EXECUTION: CONTACT ROMAN")
            return
        # Everthing is fine now, so delete the old Backup and write back the Counts of the users with
        # few coffes this month
        try:
            os.remove(self.mSdPath+'~COUNT.TXT')
        except (OSError, IOError) as e:
            pass

        os.rename(self.mSdPath+'COUNT.TXT', self.mSdPath+'~COUNT.TXT')

        #Now create a new File that contains all people with less than the min Amount
        try:
            with open(self.mSdPath+'COUNT.TXT', 'w') as f:
                for key, item in self.mData.items():
                    if item['count'] < self.mMinimumCoffees:
                        f.write(str(key).upper()+"\t"+str(item['count']).zfill(4)+"\n")
        except Exception as e:
            self.mMessages.append(str(e))
            raise Exception("FATAL ERROR: Remaining counts could not be written back onto SD-CARD"
                            "\nSTOPPING EXECUTION: CONTACT ROMAN")
            return

    def getData(self):
        """
        Returns the data, that was read from the files using readData()
        :return: A List of dicts that contain the data
        """
        return list(self.mData.values())

    def getMessages(self):
        """
        Returns all the cached messages and empties the cache
        :return: STRING message
        """
        msg=self.mMessages
        self.mMessages=[]
        return msg

    def deleteUser(self,UUID):
        """
        This function removes one user and writes it to the file
        :param UUID: The ID that should be removed
        """
        del self.mData[UUID]
        #storeSettings
        self.writeUsersFile()

    def addUser(self, uuid, name):
        """
        :param uuid: The ID of the RFID Card in HEX representation
        :param name: The Name of the user
        :return: BOOLEAN success, STRING message
        """
        UUID = uuid.upper()
        if UUID in self.mData:
            return False, "UUID wird schon verwendet."

        self.mData[UUID] = {'name': name, 'count': 0, 'uuid': UUID}
        #Store Settings
        self.writeUsersFile()

        return True, "User "+name+" und UUID "+UUID+" hinzugefügt"

    def writeUsersFile(self):
        """
        Writes the USER.TXT accordung to the current data
        :raise Exception: File Errors
        """
        try:
            with open(self.mSdPath + 'USER.TXT', 'w') as f:  # Use file to refer to the file object
                for key, item in self.mData.items():
                    if item['name']:   # ignore unknown users
                        f.write(str(key).upper()+"\t"+item['name']+"\n")
        except Exception as e:
            print(e)
            raise Exception("FATAL ERROR: File USER.TXT Could not be updated! {path}"
                            .format(path=self.mSdPath))


    def setSdPath(self,sdPath):
        """
        Set the path to the SD-Card, that contains the COUNT.TXT and USER.TXT
        :param sdPath: Path to the SD root
        """
        if not sdPath.endswith("/"):
            sdPath += "/"

        self.mSdPath = sdPath

