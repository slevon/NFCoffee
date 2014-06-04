#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
            buttonBox =  QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
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
                "<h2>Fehler</h2>Die ID muss exact <b>fünf</b> Byte lang sein.<br/>Der Name mehr als <b>drei</b> Zeichen haben.")


    def getUUID(self):
        return self.mUuidLineEdit.text();
    def getName(self):
        return self.mNameEdit.text();
    def setUUID(self,text):
        self.mUuidLineEdit.setText(text);
    def setName(self,text):
        self.mNameEdit.setText(text);




class MainWidget(QWidget):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        self.mTable = QTableWidget(1,4,self)
        self.mTable.setSortingEnabled(True)
        self.initTable()

        self.mTextEdit=QTextEdit(self)
        self.mTextEdit.setFont(QFont ("Trebuchet,sans-serif", 9))
        self.mTextEdit.setTabChangesFocus(False)

        self.logText("Starting...");

        self.mSplitter=QSplitter(Qt.Vertical,self)
        self.mSplitter.addWidget(self.mTable)
        self.mSplitter.addWidget(self.mTextEdit)
        self.mSplitter.setStretchFactor (0, 100)
        self.mSplitter.setStretchFactor(1, 1)

        self.mLayout=QGridLayout()
        self.mLayout.addWidget(self.mSplitter,0,0)

        self.setLayout(self.mLayout)
    def logNewSection(self):
            self.mTextEdit.append("<hr/>")

    def logText(self,string,timestamp=True):
            if timestamp:
                #self.mTextEdit.append("<hr/><span style=\"font: Trebuchet,sans-serif\">"+QDateTime().currentDateTimeUtc().toString("yyyy-MM-dd HH:mm:ss:")+"</span><br/>")
                self.mTextEdit.append("<small style=\"color:gray\" >"+QDateTime().currentDateTimeUtc().toString("yyyy-MM-dd HH:mm:ss:")+"</small><br/>")

            self.mTextEdit.append(string.replace("\n","<br/>")+"<br/>")

    def initTable(self):
        header = [ "UUID", "Name", "Anzahl", "Betrag"]
        self.mTable.setHorizontalHeaderLabels(header)
        self.mTable.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.mTable.setContextMenuPolicy(Qt.CustomContextMenu)

        for x in range(0, 3):
            row=self.mTable.rowCount()
            self.mTable.insertRow(row)

            uuid=QTableWidgetItem(str(x)*3)
            uuid.setFlags(uuid.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsDragEnabled & ~Qt.ItemIsDropEnabled)

            self.mTable.setItem(row, 0, uuid )
            self.mTable.setItem(row, 1, QTableWidgetItem(str(x)) )
###########################################################################################################
###########################################################################################################
###########################################################################################################
class MyMainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        #init attributes:
        self.mMainWidget=MainWidget(self)
        self.setCentralWidget(self.mMainWidget)
        self.resize(600,400)
        self.statusBar().showMessage('Ready')

        self.mPopMenu=QMenu()
        self.mMainMenu=self.menuBar()

        self.connect(self.mMainWidget.mTable,SIGNAL('customContextMenuRequested(QPoint)'), self.onContextMenu)
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
        self.aExport.triggered.connect(self.addUser)
        self.toolbarOptions.addAction(self.aExport)




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
        print("mainMenu picked");

    def initMenus(self):
        self.mActions.append(QAction("Klick",self))
        self.mPopMenu.addAction(self.mActions[-1])
        mainFile = QMenu("Datei",self)
        mainFile.addAction(QAction(u"SD-Karte auswählen",mainFile))
        self.mMainMenu.addMenu(mainFile)

    def addUser(self):
        dia = AddUserDialog()
        dia.exec()
    def deleteUser(self):
        # TODO Delete user function
        QMessageBox.critical(None, "Fehler",
                "<h2>:-( TODO</h2>")

app = QApplication([])
mW = MyMainWindow()
mW.show()
sys.exit(app.exec_())
