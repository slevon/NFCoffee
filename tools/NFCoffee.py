#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'Roman'


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
        self.data = {}
        self.mMinimumCoffees = 8    # 3EUR at the beginning
        self.mPrice = 0.4             # 0,4 EU
        self.errors=[]
        self.mPath=""

    def readData(self, path=""):

        #read the user file
        self.mPath = path
        try:
            with open(self.mPath + 'USER.TXT') as file:  # Use file to refer to the file object
                for line in file:
                    uuid, name = line.replace("\n", '').split("\t", maxsplit=1)
                    #Check is we hav two keys in the file -> Something went terribly wrong
                    if uuid in self.data:
                        raise Exception("Error 1: duplicate ID in USER.TXT")
                        return
                        #if not: we add it to our dict
                    self.data[uuid] = {'uuid': uuid, 'name': name, 'count': 0}
        except Exception as e:
            raise Exception("File USER.TXT not found, or it contains errors")

        #read the coffe-file.
        try:
            with open(self.mPath + 'COUNT.TXT') as file:  # Use file to refer to the file object
                for line in file:
                    uuid, count = line.replace("\n", '').split("\t", maxsplit=1)
                    try:
                        self.data[uuid]['count'] = int(count)
                    except Exception as e:
                        print(e)
                        print("Unknown UUID", uuid, "found in COUNTS.txt")
                        self.errors.append("Unknown UUID "+ uuid+ " found in COUNTS.txt")
                        self.data[uuid]={'uuid': uuid, 'name': '???'}
                        self.data[uuid]['count'] = int(count)
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
        for key, item in self.data.items():
            worksheet.write(row, col, item['name'])
            worksheet.write(row, col + 1, item['count'])
            worksheet.write(row, col + 2, '=PRODUCT(E1,' + xl_rowcol_to_cell(row, col + 1) + ')')
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total', resultFormat)
        worksheet.write(row, 1, '=SUM(' + xl_range(1, 1, row - 1, 1) + ')', resultFormat)
        worksheet.write(row, 2, '=SUM(' + xl_range(1, 2, row - 1, 2) + ')', resultFormat)

        workbook.close()

        print('File: ' + filename + ' created')

        #########################################
        ## Remove the old Count File and back it up
        #########################################
        backupFilename = 'COUNT_'+os.path.basename(filename).replace('.xlsx', '') + ".TXT"
        zip = zipfile.ZipFile(self.mPath+"count.zip", "a")
        i=0
        while backupFilename in zip.namelist():
            i += 1
            backupFilename = 'COUNT_'+str(i)+"_"+os.path.basename(filename).replace('.xlsx', '') + ".TXT"
        zip.write(self.mPath+"COUNT.TXT", backupFilename)
        zip.close()

        # Everthing is fine now, so delete the old Backup and write back the Counts of the users with
        # few coffes this month
        try:
            os.remove(self.mPath+'~COUNT.TXT')
        except (OSError, IOError) as e:
            pass

        os.rename(self.mPath+'COUNT.TXT', self.mPath+'~COUNT.TXT')

        #Now create a new File that contains all people with less than the min Amount
        with open(self.mPath+'COUNT.TXT', 'w') as f:
            for key, item in self.data.items():
                if item['count'] < self.mMinimumCoffees:
                    f.write(key+"\t"+str(item['count']).zfill(4)+"\n")



    @property
    def getData(self):
        return list(self.data.values())

    def getErrors(self):
        erros=self.errors
        self.errors=[]
        return erros

    def deleteUser(self,UUID):
        del self.data[UUID]

    def addUser(self, uuid, name):
        UUID = uuid.upper()
        if UUID in self.data:
            return False, "UUID wird schon verwendet."

        self.data[UUID] = {'name': name, 'count': 0, 'uuid': UUID}

        return True, "User "+name+" und UUID "+UUID+" hinzugefügt"
        print(self.data)


