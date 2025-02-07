# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QButtonGroup, QComboBox,
    QFrame, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QLineEdit, QMainWindow,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QSpacerItem, QStatusBar, QTabWidget, QTreeView,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1026, 696)
        MainWindow.setMinimumSize(QSize(800, 600))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(10)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QSize(0, 0))
        self.tabWidget.setToolTipDuration(-4)
        self.tabWidget.setStyleSheet(u"")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setTabBarAutoHide(False)
        self.airtableUploadTab = QWidget()
        self.airtableUploadTab.setObjectName(u"airtableUploadTab")
        self.verticalLayout_3 = QVBoxLayout(self.airtableUploadTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_3 = QHBoxLayout()
#ifndef Q_OS_MAC
        self.horizontalLayout_3.setSpacing(-1)
#endif
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.label_7 = QLabel(self.airtableUploadTab)
        self.label_7.setObjectName(u"label_7")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)
        self.label_7.setFrameShape(QFrame.Shape.NoFrame)
        self.label_7.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_7.setWordWrap(True)

        self.horizontalLayout_3.addWidget(self.label_7)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.apiKeyTextEntry = QLineEdit(self.airtableUploadTab)
        self.apiKeyTextEntry.setObjectName(u"apiKeyTextEntry")
        self.apiKeyTextEntry.setEnabled(True)
        self.apiKeyTextEntry.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.apiKeyTextEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.apiKeyTextEntry.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.apiKeyTextEntry, 1, 1, 1, 1)

        self.aPIKeyLabel = QLabel(self.airtableUploadTab)
        self.aPIKeyLabel.setObjectName(u"aPIKeyLabel")
        self.aPIKeyLabel.setStyleSheet(u"font-weight: bold")

        self.gridLayout.addWidget(self.aPIKeyLabel, 1, 0, 1, 1)

        self.transcriptsFolderLabel = QLabel(self.airtableUploadTab)
        self.transcriptsFolderLabel.setObjectName(u"transcriptsFolderLabel")
        self.transcriptsFolderLabel.setStyleSheet(u"font-weight: bold")

        self.gridLayout.addWidget(self.transcriptsFolderLabel, 0, 0, 1, 1)

        self.folderDisplayText = QLabel(self.airtableUploadTab)
        self.folderDisplayText.setObjectName(u"folderDisplayText")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.folderDisplayText.sizePolicy().hasHeightForWidth())
        self.folderDisplayText.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.folderDisplayText, 0, 1, 1, 1)

        self.folderSelectButton = QPushButton(self.airtableUploadTab)
        self.folderSelectButton.setObjectName(u"folderSelectButton")
        self.folderSelectButton.setEnabled(True)
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.folderSelectButton.sizePolicy().hasHeightForWidth())
        self.folderSelectButton.setSizePolicy(sizePolicy3)

        self.gridLayout.addWidget(self.folderSelectButton, 0, 2, 1, 1)

        self.apiKeySubmit = QPushButton(self.airtableUploadTab)
        self.apiKeySubmit.setObjectName(u"apiKeySubmit")
        self.apiKeySubmit.setEnabled(True)
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.apiKeySubmit.sizePolicy().hasHeightForWidth())
        self.apiKeySubmit.setSizePolicy(sizePolicy4)
        self.apiKeySubmit.setCheckable(False)

        self.gridLayout.addWidget(self.apiKeySubmit, 1, 2, 1, 1)


        self.horizontalLayout_3.addLayout(self.gridLayout)


        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(self.airtableUploadTab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setTextFormat(Qt.TextFormat.MarkdownText)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.recordSelectBox = QComboBox(self.airtableUploadTab)
        self.recordSelectBox.setObjectName(u"recordSelectBox")
        self.recordSelectBox.setEnabled(False)
        self.recordSelectBox.setEditable(False)

        self.horizontalLayout_2.addWidget(self.recordSelectBox)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.label_11 = QLabel(self.airtableUploadTab)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_11)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_4 = QLabel(self.airtableUploadTab)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.existingTranscript = QScrollArea(self.airtableUploadTab)
        self.existingTranscript.setObjectName(u"existingTranscript")
        self.existingTranscript.setEnabled(True)
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.existingTranscript.sizePolicy().hasHeightForWidth())
        self.existingTranscript.setSizePolicy(sizePolicy5)
        self.existingTranscript.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.existingTranscript.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.existingTranscript.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setEnabled(True)
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 98, 40))
        self.gridLayout_5 = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.existingTranscriptFrameText = QLabel(self.scrollAreaWidgetContents)
        self.existingTranscriptFrameText.setObjectName(u"existingTranscriptFrameText")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.existingTranscriptFrameText.sizePolicy().hasHeightForWidth())
        self.existingTranscriptFrameText.setSizePolicy(sizePolicy6)
        self.existingTranscriptFrameText.setWordWrap(True)

        self.gridLayout_5.addWidget(self.existingTranscriptFrameText, 0, 0, 1, 1)

        self.existingTranscript.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_3.addWidget(self.existingTranscript, 1, 0, 1, 1)

        self.label_5 = QLabel(self.airtableUploadTab)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 0, 1, 1, 1)

        self.scrollArea = QScrollArea(self.airtableUploadTab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setEnabled(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 98, 40))
        self.scrollAreaWidgetContents_2.setAutoFillBackground(True)
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.fromFileTranscriptFrameText = QLabel(self.scrollAreaWidgetContents_2)
        self.fromFileTranscriptFrameText.setObjectName(u"fromFileTranscriptFrameText")
        self.fromFileTranscriptFrameText.setWordWrap(True)

        self.verticalLayout_4.addWidget(self.fromFileTranscriptFrameText)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_3.addWidget(self.scrollArea, 1, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_3)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.appendRadioButton = QRadioButton(self.airtableUploadTab)
        self.radioButtonGroup = QButtonGroup(MainWindow)
        self.radioButtonGroup.setObjectName(u"radioButtonGroup")
        self.radioButtonGroup.addButton(self.appendRadioButton)
        self.appendRadioButton.setObjectName(u"appendRadioButton")
        self.appendRadioButton.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.appendRadioButton)

        self.prependRadioButton = QRadioButton(self.airtableUploadTab)
        self.radioButtonGroup.addButton(self.prependRadioButton)
        self.prependRadioButton.setObjectName(u"prependRadioButton")
        self.prependRadioButton.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.prependRadioButton)

        self.overwriteRadioButton = QRadioButton(self.airtableUploadTab)
        self.radioButtonGroup.addButton(self.overwriteRadioButton)
        self.overwriteRadioButton.setObjectName(u"overwriteRadioButton")
        self.overwriteRadioButton.setEnabled(False)

        self.horizontalLayout_6.addWidget(self.overwriteRadioButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_6)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.approveButton = QPushButton(self.airtableUploadTab)
        self.approveButton.setObjectName(u"approveButton")
        self.approveButton.setEnabled(False)
        sizePolicy4.setHeightForWidth(self.approveButton.sizePolicy().hasHeightForWidth())
        self.approveButton.setSizePolicy(sizePolicy4)

        self.horizontalLayout.addWidget(self.approveButton)

        self.flagButton = QPushButton(self.airtableUploadTab)
        self.flagButton.setObjectName(u"flagButton")
        self.flagButton.setEnabled(False)
        sizePolicy4.setHeightForWidth(self.flagButton.sizePolicy().hasHeightForWidth())
        self.flagButton.setSizePolicy(sizePolicy4)

        self.horizontalLayout.addWidget(self.flagButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout_4.addLayout(self.verticalLayout, 2, 2, 1, 1)

        self.label_6 = QLabel(self.airtableUploadTab)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(131, 31))

        self.gridLayout_4.addWidget(self.label_6, 0, 2, 1, 1)

        self.label_2 = QLabel(self.airtableUploadTab)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setMinimumSize(QSize(0, 30))

        self.gridLayout_4.addWidget(self.label_2, 0, 1, 1, 1)

        self.label_9 = QLabel(self.airtableUploadTab)
        self.label_9.setObjectName(u"label_9")
        sizePolicy2.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy2)
        self.label_9.setWordWrap(True)

        self.gridLayout_4.addWidget(self.label_9, 1, 1, 1, 1)

        self.label_10 = QLabel(self.airtableUploadTab)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setWordWrap(True)

        self.gridLayout_4.addWidget(self.label_10, 1, 2, 1, 1)

        self.transcriptsTreeView = QTreeView(self.airtableUploadTab)
        self.transcriptsTreeView.setObjectName(u"transcriptsTreeView")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.transcriptsTreeView.sizePolicy().hasHeightForWidth())
        self.transcriptsTreeView.setSizePolicy(sizePolicy7)

        self.gridLayout_4.addWidget(self.transcriptsTreeView, 2, 1, 1, 1)

        self.gridLayout_4.setRowStretch(0, 1)
        self.gridLayout_4.setRowStretch(1, 3)

        self.verticalLayout_3.addLayout(self.gridLayout_4)

        self.tabWidget.addTab(self.airtableUploadTab, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.tabWidget.addTab(self.tab_3, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PPL Tools", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"This tool allows you to **bulk** upload text files of interview transcripts into Airtable. It expects all transcripts to be stored as *.txt files, in one folder.\n"
"\n"
"It expects filenames of the format: [some explainer text about filename convention].", None))
        self.apiKeyTextEntry.setText("")
        self.aPIKeyLabel.setText(QCoreApplication.translate("MainWindow", u"Airtable Access Token", None))
        self.transcriptsFolderLabel.setText(QCoreApplication.translate("MainWindow", u"Transcripts Folder", None))
        self.folderDisplayText.setText("")
        self.folderSelectButton.setText(QCoreApplication.translate("MainWindow", u"Select", None))
        self.apiKeySubmit.setText(QCoreApplication.translate("MainWindow", u"Submit", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"**Select a matching record.**", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>If the selected record already has a transcript uploaded, please <span style=\" font-weight:700;\">select an option</span> from the three radio buttons below, <span style=\" font-weight:700;\">or press flag</span> to upload manually.</p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Existing transcript (1)", None))
        self.existingTranscriptFrameText.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Transcript from File (2)", None))
        self.fromFileTranscriptFrameText.setText("")
        self.appendRadioButton.setText(QCoreApplication.translate("MainWindow", u"Append (1 then 2)", None))
        self.prependRadioButton.setText(QCoreApplication.translate("MainWindow", u"Prepend (2 then 1)", None))
        self.overwriteRadioButton.setText(QCoreApplication.translate("MainWindow", u"Overwrite (just 2)", None))
        self.approveButton.setText(QCoreApplication.translate("MainWindow", u"Approve and Upload", None))
        self.flagButton.setText(QCoreApplication.translate("MainWindow", u"Flag for Manual Review", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:18pt; font-weight:700;\">Process File</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:18pt; font-weight:700;\">Transcript File Queue</span></p></body></html>", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Select files from the drawers below to process in the right-hand pane.", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Select a file from the left-hand queue to process. If no record with interview code matching the exact filename was found, please select from the fuzzy matches found below.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.airtableUploadTab), QCoreApplication.translate("MainWindow", u"Upload Transcripts", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Pull Key Quotes", None))
    # retranslateUi

