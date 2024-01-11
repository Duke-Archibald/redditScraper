# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pb_test = QtWidgets.QPushButton(self.centralwidget)
        self.pb_test.setObjectName("pb_test")
        self.verticalLayout_4.addWidget(self.pb_test)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.le_url = QtWidgets.QLineEdit(self.centralwidget)
        self.le_url.setObjectName("le_url")
        self.verticalLayout.addWidget(self.le_url)
        self.le_novel_name = QtWidgets.QLineEdit(self.centralwidget)
        self.le_novel_name.setObjectName("le_novel_name")
        self.verticalLayout.addWidget(self.le_novel_name)
        self.le_sub = QtWidgets.QLineEdit(self.centralwidget)
        self.le_sub.setReadOnly(True)
        self.le_sub.setObjectName("le_sub")
        self.verticalLayout.addWidget(self.le_sub)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pb_next = QtWidgets.QPushButton(self.centralwidget)
        self.pb_next.setObjectName("pb_next")
        self.horizontalLayout.addWidget(self.pb_next)
        self.pb_finish = QtWidgets.QPushButton(self.centralwidget)
        self.pb_finish.setEnabled(False)
        self.pb_finish.setObjectName("pb_finish")
        self.horizontalLayout.addWidget(self.pb_finish)
        self.pb_cancel = QtWidgets.QPushButton(self.centralwidget)
        self.pb_cancel.setEnabled(False)
        self.pb_cancel.setAutoDefault(True)
        self.pb_cancel.setObjectName("pb_cancel")
        self.horizontalLayout.addWidget(self.pb_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cb_subreddit = QtWidgets.QComboBox(self.centralwidget)
        self.cb_subreddit.setObjectName("cb_subreddit")
        self.verticalLayout_2.addWidget(self.cb_subreddit)
        self.verticalLayout_4.addLayout(self.verticalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.cb_post_title = QtWidgets.QComboBox(self.centralwidget)
        self.cb_post_title.setObjectName("cb_post_title")
        self.horizontalLayout_5.addWidget(self.cb_post_title)
        self.pb_complete = QtWidgets.QPushButton(self.centralwidget)
        self.pb_complete.setObjectName("pb_complete")
        self.horizontalLayout_5.addWidget(self.pb_complete)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.cb_entry_name = QtWidgets.QComboBox(self.centralwidget)
        self.cb_entry_name.setObjectName("cb_entry_name")
        self.horizontalLayout_4.addWidget(self.cb_entry_name)
        self.pb_tts = QtWidgets.QPushButton(self.centralwidget)
        self.pb_tts.setObjectName("pb_tts")
        self.horizontalLayout_4.addWidget(self.pb_tts)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cb_voice = QtWidgets.QComboBox(self.centralwidget)
        self.cb_voice.setObjectName("cb_voice")
        self.horizontalLayout_2.addWidget(self.cb_voice)
        self.cb_gender = QtWidgets.QComboBox(self.centralwidget)
        self.cb_gender.setObjectName("cb_gender")
        self.cb_gender.addItem("")
        self.cb_gender.addItem("")
        self.cb_gender.addItem("")
        self.horizontalLayout_2.addWidget(self.cb_gender)
        self.pb_sample = QtWidgets.QPushButton(self.centralwidget)
        self.pb_sample.setObjectName("pb_sample")
        self.horizontalLayout_2.addWidget(self.pb_sample)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pb_duplicate_line = QtWidgets.QPushButton(self.centralwidget)
        self.pb_duplicate_line.setObjectName("pb_duplicate_line")
        self.horizontalLayout_3.addWidget(self.pb_duplicate_line)
        self.pb_delete_line = QtWidgets.QPushButton(self.centralwidget)
        self.pb_delete_line.setObjectName("pb_delete_line")
        self.horizontalLayout_3.addWidget(self.pb_delete_line)
        self.pb_clear = QtWidgets.QPushButton(self.centralwidget)
        self.pb_clear.setObjectName("pb_clear")
        self.horizontalLayout_3.addWidget(self.pb_clear)
        self.pb_merge_lines = QtWidgets.QPushButton(self.centralwidget)
        self.pb_merge_lines.setObjectName("pb_merge_lines")
        self.horizontalLayout_3.addWidget(self.pb_merge_lines)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.tv_lines = QtWidgets.QTableView(self.centralwidget)
        self.tv_lines.setObjectName("tv_lines")
        self.tv_lines.verticalHeader().setVisible(False)
        self.verticalLayout_3.addWidget(self.tv_lines)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1920, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pb_test.setText(_translate("MainWindow", "test"))
        self.pb_next.setText(_translate("MainWindow", "next subreddit"))
        self.pb_finish.setText(_translate("MainWindow", "finish"))
        self.pb_cancel.setText(_translate("MainWindow", "cancel"))
        self.pb_complete.setText(_translate("MainWindow", "complete"))
        self.pb_tts.setText(_translate("MainWindow", "Create TTS"))
        self.cb_gender.setItemText(0, _translate("MainWindow", "special"))
        self.cb_gender.setItemText(1, _translate("MainWindow", "male"))
        self.cb_gender.setItemText(2, _translate("MainWindow", "female"))
        self.pb_sample.setText(_translate("MainWindow", "sample"))
        self.pb_duplicate_line.setText(_translate("MainWindow", "Duplicate Line(s)"))
        self.pb_delete_line.setText(_translate("MainWindow", "Delete Line(s)"))
        self.pb_clear.setText(_translate("MainWindow", "Clear Selection"))
        self.pb_merge_lines.setText(_translate("MainWindow", "Merge 2 Lines"))