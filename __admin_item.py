# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '_admin_item.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(620, 400)
        MainWindow.setMinimumSize(QtCore.QSize(620, 400))
        MainWindow.setMaximumSize(QtCore.QSize(620, 400))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.m_tw = QtWidgets.QTableWidget(self.centralwidget)
        self.m_tw.setGeometry(QtCore.QRect(10, 10, 600, 300))
        self.m_tw.setObjectName("m_tw")
        self.m_tw.setColumnCount(0)
        self.m_tw.setRowCount(0)
        self.m_paste = QtWidgets.QPushButton(self.centralwidget)
        self.m_paste.setGeometry(QtCore.QRect(100, 320, 80, 40))
        self.m_paste.setObjectName("m_paste")
        self.m_add = QtWidgets.QPushButton(self.centralwidget)
        self.m_add.setGeometry(QtCore.QRect(10, 320, 80, 41))
        self.m_add.setObjectName("m_add")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.m_paste.setText(_translate("MainWindow", "paste picture"))
        self.m_add.setText(_translate("MainWindow", "add new var"))
