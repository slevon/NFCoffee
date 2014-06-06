#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
This is the GUI Managment Tool for NFCoffee




icons taken from http://dryicons.com

'''

from NFCoffee import NFCoffee

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import configparser

import sys
import json

class AddUserDialog(QDialog):
    def __init__(self, parent=None):

            super(AddUserDialog, self).__init__(parent)
            #Items
            self.mNameEdit = None
            self.mUuidLineEdit = None

            self.setWindowTitle("User hinzufügen")
            self.mLayout=QGridLayout()
            self.mLayout.addWidget(QLabel('''
                <h2><img src="icons/user.png" /> Nutzerdaten </h2>Geben sie hier die ID des Ausweises und den Nutzernamen an.<br/>
                <small>Tipp: Die Id kann mit der <em>Info</em>-Taste an dem Gerät ausgelesen werden'''), 0, 0, 1, 2)
            self.mLayout.addWidget(QLabel('NFC/RFID (hex):'), 1, 0)
            self.mUuidLineEdit=QLineEdit()
            self.mUuidLineEdit.setInputMask("HHHHHHHHHH")
            self.mLayout.addWidget(self.mUuidLineEdit, 1, 1)
            self.mLayout.addWidget(QLabel('Name:'), 2, 0)
            self.mNameEdit=QLineEdit()
            self.mLayout.addWidget(self.mNameEdit, 2, 1)
            buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttonBox.accepted.connect(self.checkData)
            buttonBox.rejected.connect(self.reject)
            #connect(buttonBox, SIGNAL(rejected()), this, SLOT(reject()));

            self.mLayout.addWidget(buttonBox,3,1)
            self.setLayout(self.mLayout)


    def checkData(self):
        if self.mUuidLineEdit.text().__len__() == 10 and self.mNameEdit.text().__len__() > 3:
            self.accept()
        else:
            QMessageBox.critical(None, "Fehler",
                "<h2>Fehler</h2>"
                "Die ID muss exact <b>fünf</b> Byte lang sein.<br/>Der Name mehr als <b>drei</b> Zeichen haben.")


    def getUUID(self):
        return self.mUuidLineEdit.text()

    def getName(self):
        return self.mNameEdit.text()

    def setUUID(self, text):
        self.mUuidLineEdit.setText(text)

    def setName(self, text):
        self.mNameEdit.setText(text)

##########################################################################################
##########################################################################################
##########################################################################################

class MainWidget(QWidget):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)

        self.mTable = QTableWidget(0,4,self)
        header = [ "UUID", "Name", "Anzahl", "Betrag"]
        self.mTable.setHorizontalHeaderLabels(header)
        self.mTable.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.mTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mTable.setSortingEnabled(True)
        self.mTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mTable.setColumnWidth(1,250)

        self.mTextEdit=QTextEdit(self)
        self.mTextEdit.setFont(QFont ("Trebuchet,sans-serif", 9))
        self.mTextEdit.setTabChangesFocus(False)

        self.logText("Starting...")

        self.mSplitter=QSplitter(Qt.Vertical,self)
        self.mSplitter.addWidget(self.mTable)
        self.mSplitter.addWidget(self.mTextEdit)
        self.mSplitter.setStretchFactor(0, 100)
        self.mSplitter.setStretchFactor(1, 1)

        self.mLayout=QGridLayout()
        self.mLayout.addWidget(self.mSplitter, 0, 0)

        self.setLayout(self.mLayout)

    def logNewSection(self):
            self.mTextEdit.append("<hr/>")

    def logText(self, string, timestamp=True):
            if timestamp:
                self.mTextEdit.append("<small style=\"color:gray\" >"
                                      + QDateTime().currentDateTimeUtc().toString("yyyy-MM-dd HH:mm:ss:")
                                      + "</small><br/>")

            self.mTextEdit.append(string.replace("\n","<br/>")+"<br/>")

    def initTable(self, data):
        """

        :param data: A List of dics with uuid,name and count as keys
        """

        self.mTable.clear()
        self.mTable.setRowCount(0)

        for item in data:
            row = self.mTable.rowCount()
            self.mTable.insertRow(row)
            #Name
            self.mTable.setItem(row, 1, self.__createItem(str(item['name'])))
            #count
            self.mTable.setItem(row, 2, self.__createItem(str(item['count'])))
            #Price
            price = self.__createItem('')
            price.setTextAlignment(Qt.AlignRight)
            self.mTable.setItem(row, 3, price)
            #UUID
            #For some verrrrry strange reason this line has to be the last in this loop
            self.mTable.setItem(row, 0, self.__createItem(str(item['uuid'])))



    def __createItem(self, text):
        twItem = QTableWidgetItem(text)
        twItem.setFlags(twItem.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)
        return twItem

    def recalcAmount(self, price):
        """

        :param price: The price in EUR for one coffee
        """
        rows = self.mTable.rowCount()
        for row in range(0, rows):
            try:
                count = int(self.mTable.item(row,2).text())
                self.mTable.item(row, 3).setText("{0:.2f} €".format((count*price)))
            except Exception as e:
                print(e)

    def markMinimumCoffees(self, minimum):
        rows = self.mTable.rowCount()
        cols = self.mTable.columnCount()
        for row in range(0, rows):
            #try:
                count = int(self.mTable.item(row,2).text())
                if count < minimum:
                    for col in range(0, cols):
                        self.mTable.item(row,col).setBackground(QColor(250, 220, 220))
                else:
                    for col in range(0, cols):
                        self.mTable.item(row, col).setBackground(QColor(255, 255, 255))
            #except Exception as e:
            #    pass

###########################################################################################################
###########################################################################################################
###########################################################################################################
class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        #init attributes:

        #We have our working Class, that will do all the work on the files:
        #TODO NFC Class usage
        self.mNFCoffee = NFCoffee()
        self.mNFCoffee.readData()

        self.mMainWidget = MainWidget(self)

        self.setCentralWidget(self.mMainWidget)
        self.resize(600,400)
        self.statusBar().showMessage('Ready')

        self.mPopMenu = QMenu()
        self.mMainMenu = self.menuBar()

        self.connect(self.mMainWidget.mTable, SIGNAL('customContextMenuRequested(QPoint)'), self.onContextMenu)
        #self.connect(self.mMainMenu,SIGNAL('triggered(QAction)'), self.onMainMenu)
        self.mMainMenu.triggered.connect(self.onMainMenu)

        #will hold all the actions in order do find which one was triggerd by the contex menu
        self.mActions = []
        self.initMenus()

        #init Toolbar
        self.toolbarUser = self.addToolBar('User')
        self.toolbarUser.setFloatable(False)

        self.aAddUser = QAction(QIcon('icons/add_user.png'), 'User hinzufügen', self)
        self.aAddUser.setShortcut('Ctrl++')
        self.aAddUser.triggered.connect(self.addUser)
        self.toolbarUser.addAction(self.aAddUser)
        self.aDeleteUser = QAction(QIcon('icons/delete_user.png'), 'User entfernen', self)
        self.aDeleteUser.setShortcut('Ctrl+-')
        self.aDeleteUser.triggered.connect(self.deleteUser)
        self.toolbarUser.addAction(self.aDeleteUser)
        #options
        self.toolbarOptions = self.addToolBar('Options')
        self.toolbarOptions.setFloatable(False)

        self.aExport = QAction(QIcon('icons/download_page.png'), 'Report erstellen', self)
        self.aExport.setShortcut('Ctrl+E')
        self.aExport.triggered.connect(self.createReport)
        self.toolbarOptions.addAction(self.aExport)

        # PriceBox
        self.toolbarOptions.addSeparator()
        self.toolbarOptions.addWidget(QLabel("Preis/Kaffee:"))
        self.aPriceBox = QDoubleSpinBox()
        self.aPriceBox.setSingleStep(0.05)
        self.aPriceBox.setSuffix("€")
        # TODO Save and restore settings
        self.aPriceBox.setValue(self.mNFCoffee.price())
        self.aPriceBox.valueChanged.connect(self.updatePrice)
        self.toolbarOptions.addWidget(self.aPriceBox)
        self.toolbarOptions.addSeparator()
        # Minimum Coffees
        self.toolbarOptions.addWidget(QLabel("Mindesanzahl an Kaffees:"))
        self.aMinimumBox = QSpinBox()
        self.aMinimumBox.setToolTip("Geben sie hier die Mindestanzahl der Kaffees an, die erreicht werden muss damit die"
                                    " Kaffees abgerechnet werden.\nAlle anderen bleiben erhalten.")
        # TODO Save and restore settings
        self.aMinimumBox.setValue(self.mNFCoffee.minimumCoffees())
        self.aMinimumBox.valueChanged.connect(self.updateMinimumCoffees)
        self.toolbarOptions.addWidget(self.aMinimumBox)
        self.toolbarOptions.addSeparator()

        #Save the settings
        self.restoreSettings()

        #init the Table
        self.mMainWidget.initTable(self.mNFCoffee.getData)
        self.mMainWidget.recalcAmount(self.mNFCoffee.price())
        self.mMainWidget.markMinimumCoffees(self.mNFCoffee.minimumCoffees())

        #Show all errors
        self.mMainWidget.logText("\n".join(self.mNFCoffee.getErrors()))


    def closeEvent(self, evnt):
        self.saveSettings()
        super(MyMainWindow, self).closeEvent(evnt)

    def onContextMenu(self,point):


        treeItem=self.mMainWidget.mTable.itemAt(point)
        #find the toplevel item
        while treeItem.parent():
            treeItem=treeItem.parent()
        name=treeItem.child(0).text(1)
        print("ok "+name)

        result = self.mPopMenu.exec_( self.mMainWidget.mTable.mapToGlobal(point) )
        for menuItem in self.mActions:
            if menuItem == result:
                print("Popup found: "+result.text())

    def onMainMenu(self, action):
        QMessageBox.critical(None, "Fehler Hauptmenü",
                "<h2>:-( TODO</h2>")

    def initMenus(self):
        self.mActions.append(QAction("Klick",self))
        self.mPopMenu.addAction(self.mActions[-1])
        mainFile = QMenu("Datei",self)
        mainFile.addAction(QAction(u"SD-Karte auswählen",mainFile))
        self.mMainMenu.addMenu(mainFile)

    def addUser(self):
        dia = AddUserDialog()
        dia.exec_()
    def deleteUser(self):
        # TODO Delete user function
        QMessageBox.critical(None, "Fehler Delete",
                "<h2>:-( TODO</h2>")


    def createReport(self):
        # TODO REport/Export Function
        QMessageBox.critical(None, "Fehler Report",
                "<h2>:-( TODO</h2>")

    def updatePrice(self, price):
        self.mNFCoffee.setPrice(price)
        self.mMainWidget.recalcAmount(price)


    def updateMinimumCoffees(self, minimumCoffees):
        self.mNFCoffee.setMinimumCoffees(minimumCoffees)
        self.mMainWidget.markMinimumCoffees(minimumCoffees)

    def saveSettings(self):
        config = configparser.ConfigParser()
        config.read('NFCoffee.INI')
        #TODO all Config
        config['COFFEE']['price'] = str(self.mNFCoffee.price())
        config['COFFEE']['minimumCoffees'] = str(self.mNFCoffee.minimumCoffees())

        with open('NFCoffee.INI', 'w') as configfile:    # save
            config.write(configfile)

        self.mMainWidget.logText("Ini File updated...")

    def restoreSettings(self):
        config = configparser.ConfigParser()
        config.read('NFCoffee.INI')
        self.mMainWidget.logText("Reading Ini File...")
        #TODO all Config
        self.aPriceBox.setValue(float(config['COFFEE']['price']))
        self.aMinimumBox.setValue(int(config['COFFEE']['minimumCoffees']))

app = QApplication([])
mW = MyMainWindow()
mW.show()
sys.exit(app.exec_())
