# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './control_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_KShapeControl(object):
    def setupUi(self, KShapeControl):
        KShapeControl.setObjectName("KShapeControl")
        KShapeControl.resize(400, 643)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_8 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_12.addWidget(self.label_8)
        self.comboBoxDataColumn = QtWidgets.QComboBox(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxDataColumn.sizePolicy().hasHeightForWidth())
        self.comboBoxDataColumn.setSizePolicy(sizePolicy)
        self.comboBoxDataColumn.setObjectName("comboBoxDataColumn")
        self.horizontalLayout_12.addWidget(self.comboBoxDataColumn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_12.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.dockWidgetContents)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.spinBoxN_clusters = QtWidgets.QSpinBox(self.dockWidgetContents)
        self.spinBoxN_clusters.setMinimum(2)
        self.spinBoxN_clusters.setProperty("value", 3)
        self.spinBoxN_clusters.setObjectName("spinBoxN_clusters")
        self.horizontalLayout.addWidget(self.spinBoxN_clusters)
        self.horizontalLayout_6.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.spinBoxMaxIter = QtWidgets.QSpinBox(self.dockWidgetContents)
        self.spinBoxMaxIter.setMaximum(9999)
        self.spinBoxMaxIter.setSingleStep(50)
        self.spinBoxMaxIter.setProperty("value", 300)
        self.spinBoxMaxIter.setObjectName("spinBoxMaxIter")
        self.horizontalLayout_2.addWidget(self.spinBoxMaxIter)
        self.horizontalLayout_6.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_9.addLayout(self.horizontalLayout_6)
        spacerItem1 = QtWidgets.QSpacerItem(37, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.spinBoxRandom = QtWidgets.QSpinBox(self.dockWidgetContents)
        self.spinBoxRandom.setEnabled(False)
        self.spinBoxRandom.setMaximum(999)
        self.spinBoxRandom.setObjectName("spinBoxRandom")
        self.horizontalLayout_5.addWidget(self.spinBoxRandom)
        self.checkBoxRandom = QtWidgets.QCheckBox(self.dockWidgetContents)
        self.checkBoxRandom.setChecked(True)
        self.checkBoxRandom.setObjectName("checkBoxRandom")
        self.horizontalLayout_5.addWidget(self.checkBoxRandom)
        self.horizontalLayout_8.addLayout(self.horizontalLayout_5)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.spinBoxTol = QtWidgets.QSpinBox(self.dockWidgetContents)
        self.spinBoxTol.setMinimum(-20)
        self.spinBoxTol.setMaximum(10)
        self.spinBoxTol.setSingleStep(1)
        self.spinBoxTol.setProperty("value", -6)
        self.spinBoxTol.setObjectName("spinBoxTol")
        self.horizontalLayout_3.addWidget(self.spinBoxTol)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_4.addWidget(self.label_4)
        self.spinBoxN_init = QtWidgets.QSpinBox(self.dockWidgetContents)
        self.spinBoxN_init.setMinimum(1)
        self.spinBoxN_init.setObjectName("spinBoxN_init")
        self.horizontalLayout_4.addWidget(self.spinBoxN_init)
        self.horizontalLayout_7.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_10.addLayout(self.horizontalLayout_7)
        spacerItem3 = QtWidgets.QSpacerItem(37, 17, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_10.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.pushButtonStart = QtWidgets.QPushButton(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonStart.setFont(font)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.horizontalLayout_11.addWidget(self.pushButtonStart)
        self.pushButtonAbort = QtWidgets.QPushButton(self.dockWidgetContents)
        self.pushButtonAbort.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.pushButtonAbort.setFont(font)
        self.pushButtonAbort.setObjectName("pushButtonAbort")
        self.horizontalLayout_11.addWidget(self.pushButtonAbort)
        self.verticalLayout.addLayout(self.horizontalLayout_11)
        self.label_6 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.textBrowser = QtWidgets.QTextBrowser(self.dockWidgetContents)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.label_7 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.verticalLayout.addWidget(self.label_7)
        self.listWidgetClusterNumber = QtWidgets.QListWidget(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidgetClusterNumber.sizePolicy().hasHeightForWidth())
        self.listWidgetClusterNumber.setSizePolicy(sizePolicy)
        self.listWidgetClusterNumber.setMinimumSize(QtCore.QSize(0, 33))
        self.listWidgetClusterNumber.setMaximumSize(QtCore.QSize(16777215, 33))
        self.listWidgetClusterNumber.setProperty("showDropIndicator", False)
        self.listWidgetClusterNumber.setDefaultDropAction(QtCore.Qt.IgnoreAction)
        self.listWidgetClusterNumber.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.listWidgetClusterNumber.setFlow(QtWidgets.QListView.LeftToRight)
        self.listWidgetClusterNumber.setObjectName("listWidgetClusterNumber")
        self.verticalLayout.addWidget(self.listWidgetClusterNumber)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_9 = QtWidgets.QLabel(self.dockWidgetContents)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_13.addWidget(self.label_9)
        self.comboBoxGroups = QtWidgets.QComboBox(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxGroups.sizePolicy().hasHeightForWidth())
        self.comboBoxGroups.setSizePolicy(sizePolicy)
        self.comboBoxGroups.setObjectName("comboBoxGroups")
        self.horizontalLayout_13.addWidget(self.comboBoxGroups)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_13.addItem(spacerItem4)
        self.verticalLayout.addLayout(self.horizontalLayout_13)
        KShapeControl.setWidget(self.dockWidgetContents)

        self.retranslateUi(KShapeControl)
        QtCore.QMetaObject.connectSlotsByName(KShapeControl)

    def retranslateUi(self, KShapeControl):
        _translate = QtCore.QCoreApplication.translate
        KShapeControl.setWindowTitle(_translate("KShapeControl", "Co&ntrols"))
        self.label_8.setText(_translate("KShapeControl", "data_column"))
        self.label.setText(_translate("KShapeControl", "n_clusters:"))
        self.label_2.setText(_translate("KShapeControl", "max_iter:"))
        self.label_5.setText(_translate("KShapeControl", "random_state:"))
        self.checkBoxRandom.setText(_translate("KShapeControl", "random"))
        self.label_3.setText(_translate("KShapeControl", "tol: 10 ^"))
        self.label_4.setText(_translate("KShapeControl", "n_init:"))
        self.pushButtonStart.setText(_translate("KShapeControl", "Start"))
        self.pushButtonAbort.setText(_translate("KShapeControl", "Abort"))
        self.label_6.setText(_translate("KShapeControl", "Status:"))
        self.textBrowser.setHtml(_translate("KShapeControl", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_7.setText(_translate("KShapeControl", "Cluster to plot:"))
        self.label_9.setText(_translate("KShapeControl", "Groups"))

