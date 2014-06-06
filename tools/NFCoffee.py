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

    def readData(self, path=""):

        #read the user file
        try:
            with open(path + 'USER.TXT') as file:  # Use file to refer to the file object
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
            with open(path + 'COUNT.TXT') as file:  # Use file to refer to the file object
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

    '''
        OLD ort the DICT by Name by creating a List with UUIDs in the correct order
        #sortedCounts=sorted(counts.items(), key=lambda x: x[1]['name'])
        #now we have a list like so
        #[('AABBEE9F',{'uuid':'AABBEE9F','name':'Adam','count':3},
        #  ...]

        # Clear the old container to free memory
        counts=None
    '''

    def setPrice(self, price):
        self.mPrice = price


    def price(self):
        return self.mPrice

    def setMinimumCoffees(self,minimumCoffeeAmount):
        self.mMinimumCoffees = minimumCoffeeAmount

    def minimumCoffees(self):
        return self.mMinimumCoffees

    def export(self, filename=None):

        # ################################
        # Create the excel sheet
        #################################
        # Create a workbook and add a worksheet.
        if filename == None:
            filename = 'Abrechnung_'+time.strftime("%Y-%m-%d_%H-%M-%S")

        workbook = xlsxwriter.Workbook(filename + '.xlsx')
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
        worksheet.write(0, 4, pPrice, moneyFormat)
        # Iterate over the data and write it out row by row.
        # OLD Version without sorting for key, item in counts.items():
        for item in self.mCounts:
            worksheet.write(row, col, item[1]['name'])
            worksheet.write(row, col + 1, item[1]['count'])
            worksheet.write(row, col + 2, '=PRODUCT(E1,' + xl_rowcol_to_cell(row, col + 1) + ')')
            row += 1

        # Write a total using a formula.
        worksheet.write(row, 0, 'Total', resultFormat)
        worksheet.write(row, 1, '=SUM(' + xl_range(1, 1, row - 1, 1) + ')', resultFormat)
        worksheet.write(row, 2, '=SUM(' + xl_range(1, 2, row - 1, 2) + ')', resultFormat)

        workbook.close()

        print('File: ' + filename + '.xlsx created')

        #########################################
        ## Remove the old Count File and back it up
        #########################################
        zip = zipfile.ZipFile("count.zip", "a")
        zip.write("COUNT.TXT", filename + ".TXT")
        zip.close()

        # Everthing is fine now, so delete the old Backup and write back the Counts of the users with
        # few coffes this month
        try:
            os.remove('~COUNT.TXT')
        except (OSError, IOError) as e:
            pass

        os.rename('COUNT.TXT', '~COUNT.TXT')

    @property
    def getData(self):
        return list(self.data.values())

    def getErrors(self):
        erros=self.errors
        self.errors=[]
        return erros



