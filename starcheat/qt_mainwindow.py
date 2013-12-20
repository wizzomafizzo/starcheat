# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './MainWindow.ui'
#
# Created: Fri Dec 20 23:40:52 2013
#      by: PyQt5 UI code generator 5.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(637, 490)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.max_health = QtWidgets.QSpinBox(self.centralwidget)
        self.max_health.setGeometry(QtCore.QRect(210, 190, 61, 23))
        self.max_health.setMinimum(1)
        self.max_health.setMaximum(1000000)
        self.max_health.setSingleStep(10)
        self.max_health.setObjectName("max_health")
        self.hunger = QtWidgets.QSlider(self.centralwidget)
        self.hunger.setGeometry(QtCore.QRect(70, 300, 201, 16))
        self.hunger.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: rgb(255, 0, 0);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #000;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}")
        self.hunger.setMinimum(1)
        self.hunger.setOrientation(QtCore.Qt.Horizontal)
        self.hunger.setObjectName("hunger")
        self.health_val = QtWidgets.QLabel(self.centralwidget)
        self.health_val.setGeometry(QtCore.QRect(160, 190, 41, 20))
        self.health_val.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.health_val.setObjectName("health_val")
        self.breath = QtWidgets.QSlider(self.centralwidget)
        self.breath.setGeometry(QtCore.QRect(70, 400, 201, 16))
        self.breath.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: rgb(85, 255, 255);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #000;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}")
        self.breath.setMinimum(1)
        self.breath.setOrientation(QtCore.Qt.Horizontal)
        self.breath.setObjectName("breath")
        self.health_label = QtWidgets.QLabel(self.centralwidget)
        self.health_label.setGeometry(QtCore.QRect(10, 170, 41, 16))
        self.health_label.setObjectName("health_label")
        self.energy = QtWidgets.QSlider(self.centralwidget)
        self.energy.setGeometry(QtCore.QRect(70, 220, 201, 16))
        self.energy.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: rgb(0, 255, 0);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #000;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}")
        self.energy.setMinimum(1)
        self.energy.setOrientation(QtCore.Qt.Horizontal)
        self.energy.setInvertedControls(False)
        self.energy.setObjectName("energy")
        self.energy_regen = QtWidgets.QSpinBox(self.centralwidget)
        self.energy_regen.setGeometry(QtCore.QRect(210, 270, 61, 23))
        self.energy_regen.setMinimum(1)
        self.energy_regen.setMaximum(1000000)
        self.energy_regen.setSingleStep(10)
        self.energy_regen.setObjectName("energy_regen")
        self.energy_label = QtWidgets.QLabel(self.centralwidget)
        self.energy_label.setGeometry(QtCore.QRect(10, 220, 44, 16))
        self.energy_label.setObjectName("energy_label")
        self.max_energy = QtWidgets.QSpinBox(self.centralwidget)
        self.max_energy.setGeometry(QtCore.QRect(210, 240, 61, 23))
        self.max_energy.setMinimum(1)
        self.max_energy.setMaximum(1000000)
        self.max_energy.setSingleStep(10)
        self.max_energy.setObjectName("max_energy")
        self.health = QtWidgets.QSlider(self.centralwidget)
        self.health.setGeometry(QtCore.QRect(70, 170, 201, 16))
        self.health.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: rgb(255, 0, 0);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #000;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}")
        self.health.setMinimum(1)
        self.health.setOrientation(QtCore.Qt.Horizontal)
        self.health.setObjectName("health")
        self.warmth_label = QtWidgets.QLabel(self.centralwidget)
        self.warmth_label.setGeometry(QtCore.QRect(10, 350, 47, 16))
        self.warmth_label.setObjectName("warmth_label")
        self.breath_label = QtWidgets.QLabel(self.centralwidget)
        self.breath_label.setGeometry(QtCore.QRect(10, 400, 42, 16))
        self.breath_label.setObjectName("breath_label")
        self.hunger_label = QtWidgets.QLabel(self.centralwidget)
        self.hunger_label.setGeometry(QtCore.QRect(10, 300, 46, 16))
        self.hunger_label.setObjectName("hunger_label")
        self.warmth = QtWidgets.QSlider(self.centralwidget)
        self.warmth.setGeometry(QtCore.QRect(70, 350, 201, 16))
        self.warmth.setStyleSheet("QSlider::groove:horizontal {\n"
"border: 1px solid #bbb;\n"
"background: white;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::sub-page:horizontal {\n"
"background: rgb(255, 0, 0);\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::add-page:horizontal {\n"
"background: #000;\n"
"border: 1px solid #777;\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"background: qlineargradient(x1:0, y1:0, x2:1, y2:1,\n"
"    stop:0 #eee, stop:1 #ccc);\n"
"border: 1px solid #777;\n"
"width: 13px;\n"
"margin-top: -2px;\n"
"margin-bottom: -2px;\n"
"border-radius: 4px;\n"
"}")
        self.warmth.setMinimum(1)
        self.warmth.setOrientation(QtCore.Qt.Horizontal)
        self.warmth.setObjectName("warmth")
        self.energy_regen_label = QtWidgets.QLabel(self.centralwidget)
        self.energy_regen_label.setGeometry(QtCore.QRect(130, 270, 72, 14))
        self.energy_regen_label.setObjectName("energy_regen_label")
        self.backpack_label = QtWidgets.QLabel(self.centralwidget)
        self.backpack_label.setGeometry(QtCore.QRect(480, 40, 30, 16))
        self.backpack_label.setObjectName("backpack_label")
        self.legs_label = QtWidgets.QLabel(self.centralwidget)
        self.legs_label.setGeometry(QtCore.QRect(560, 130, 29, 16))
        self.legs_label.setObjectName("legs_label")
        self.left_hand_label = QtWidgets.QLabel(self.centralwidget)
        self.left_hand_label.setGeometry(QtCore.QRect(310, 140, 6, 14))
        self.left_hand_label.setObjectName("left_hand_label")
        self.chest_label = QtWidgets.QLabel(self.centralwidget)
        self.chest_label.setGeometry(QtCore.QRect(560, 70, 36, 16))
        self.chest_label.setObjectName("chest_label")
        self.head_label = QtWidgets.QLabel(self.centralwidget)
        self.head_label.setGeometry(QtCore.QRect(560, 10, 33, 16))
        self.head_label.setObjectName("head_label")
        self.right_hand_label = QtWidgets.QLabel(self.centralwidget)
        self.right_hand_label.setGeometry(QtCore.QRect(340, 140, 8, 14))
        self.right_hand_label.setObjectName("right_hand_label")
        self.inv_tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.inv_tabs.setGeometry(QtCore.QRect(300, 280, 326, 159))
        self.inv_tabs.setObjectName("inv_tabs")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.main_bag = QtWidgets.QTableWidget(self.tab_2)
        self.main_bag.setGeometry(QtCore.QRect(0, 0, 322, 130))
        self.main_bag.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.main_bag.setDragEnabled(True)
        self.main_bag.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.main_bag.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.main_bag.setAlternatingRowColors(False)
        self.main_bag.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.main_bag.setCornerButtonEnabled(False)
        self.main_bag.setColumnCount(10)
        self.main_bag.setObjectName("main_bag")
        self.main_bag.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.main_bag.setHorizontalHeaderItem(9, item)
        self.main_bag.horizontalHeader().setVisible(False)
        self.main_bag.horizontalHeader().setDefaultSectionSize(32)
        self.main_bag.horizontalHeader().setMinimumSectionSize(32)
        self.main_bag.verticalHeader().setVisible(False)
        self.main_bag.verticalHeader().setDefaultSectionSize(32)
        self.main_bag.verticalHeader().setMinimumSectionSize(32)
        self.inv_tabs.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tile_bag = QtWidgets.QTableWidget(self.tab_3)
        self.tile_bag.setGeometry(QtCore.QRect(0, 0, 322, 130))
        self.tile_bag.setDragEnabled(True)
        self.tile_bag.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tile_bag.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.tile_bag.setAlternatingRowColors(False)
        self.tile_bag.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.tile_bag.setCornerButtonEnabled(False)
        self.tile_bag.setColumnCount(10)
        self.tile_bag.setObjectName("tile_bag")
        self.tile_bag.setRowCount(4)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tile_bag.setHorizontalHeaderItem(9, item)
        self.tile_bag.horizontalHeader().setVisible(False)
        self.tile_bag.horizontalHeader().setDefaultSectionSize(32)
        self.tile_bag.horizontalHeader().setMinimumSectionSize(32)
        self.tile_bag.verticalHeader().setVisible(False)
        self.tile_bag.verticalHeader().setDefaultSectionSize(32)
        self.tile_bag.verticalHeader().setMinimumSectionSize(32)
        self.inv_tabs.addTab(self.tab_3, "")
        self.action_bar = QtWidgets.QTableWidget(self.centralwidget)
        self.action_bar.setGeometry(QtCore.QRect(300, 230, 322, 34))
        self.action_bar.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.action_bar.setDragEnabled(True)
        self.action_bar.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.action_bar.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.action_bar.setAlternatingRowColors(False)
        self.action_bar.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.action_bar.setCornerButtonEnabled(False)
        self.action_bar.setObjectName("action_bar")
        self.action_bar.setColumnCount(10)
        self.action_bar.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.action_bar.setHorizontalHeaderItem(9, item)
        self.action_bar.horizontalHeader().setVisible(False)
        self.action_bar.horizontalHeader().setDefaultSectionSize(32)
        self.action_bar.horizontalHeader().setMinimumSectionSize(32)
        self.action_bar.verticalHeader().setVisible(False)
        self.action_bar.verticalHeader().setDefaultSectionSize(32)
        self.action_bar.verticalHeader().setMinimumSectionSize(32)
        self.wielded = QtWidgets.QTableWidget(self.centralwidget)
        self.wielded.setGeometry(QtCore.QRect(300, 160, 66, 34))
        self.wielded.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.wielded.setDragEnabled(True)
        self.wielded.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.wielded.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.wielded.setAlternatingRowColors(False)
        self.wielded.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.wielded.setCornerButtonEnabled(False)
        self.wielded.setObjectName("wielded")
        self.wielded.setColumnCount(2)
        self.wielded.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.wielded.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.wielded.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.wielded.setHorizontalHeaderItem(1, item)
        self.wielded.horizontalHeader().setVisible(False)
        self.wielded.horizontalHeader().setDefaultSectionSize(32)
        self.wielded.horizontalHeader().setMinimumSectionSize(32)
        self.wielded.horizontalHeader().setStretchLastSection(True)
        self.wielded.verticalHeader().setVisible(False)
        self.wielded.verticalHeader().setDefaultSectionSize(32)
        self.wielded.verticalHeader().setMinimumSectionSize(32)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(310, 210, 64, 14))
        self.label.setObjectName("label")
        self.legs = QtWidgets.QTableWidget(self.centralwidget)
        self.legs.setGeometry(QtCore.QRect(555, 150, 66, 34))
        self.legs.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.legs.setDragEnabled(True)
        self.legs.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.legs.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.legs.setAlternatingRowColors(False)
        self.legs.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.legs.setCornerButtonEnabled(False)
        self.legs.setObjectName("legs")
        self.legs.setColumnCount(2)
        self.legs.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.legs.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.legs.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.legs.setHorizontalHeaderItem(1, item)
        self.legs.horizontalHeader().setVisible(False)
        self.legs.horizontalHeader().setDefaultSectionSize(32)
        self.legs.horizontalHeader().setMinimumSectionSize(32)
        self.legs.horizontalHeader().setStretchLastSection(True)
        self.legs.verticalHeader().setVisible(False)
        self.legs.verticalHeader().setDefaultSectionSize(32)
        self.legs.verticalHeader().setMinimumSectionSize(32)
        self.chest = QtWidgets.QTableWidget(self.centralwidget)
        self.chest.setGeometry(QtCore.QRect(555, 90, 66, 34))
        self.chest.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.chest.setDragEnabled(True)
        self.chest.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.chest.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.chest.setAlternatingRowColors(False)
        self.chest.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.chest.setCornerButtonEnabled(False)
        self.chest.setObjectName("chest")
        self.chest.setColumnCount(2)
        self.chest.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.chest.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.chest.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.chest.setHorizontalHeaderItem(1, item)
        self.chest.horizontalHeader().setVisible(False)
        self.chest.horizontalHeader().setDefaultSectionSize(32)
        self.chest.horizontalHeader().setMinimumSectionSize(32)
        self.chest.horizontalHeader().setStretchLastSection(True)
        self.chest.verticalHeader().setVisible(False)
        self.chest.verticalHeader().setDefaultSectionSize(32)
        self.chest.verticalHeader().setMinimumSectionSize(32)
        self.back = QtWidgets.QTableWidget(self.centralwidget)
        self.back.setGeometry(QtCore.QRect(470, 60, 66, 34))
        self.back.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.back.setDragEnabled(True)
        self.back.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.back.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.back.setAlternatingRowColors(False)
        self.back.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.back.setCornerButtonEnabled(False)
        self.back.setObjectName("back")
        self.back.setColumnCount(2)
        self.back.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.back.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.back.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.back.setHorizontalHeaderItem(1, item)
        self.back.horizontalHeader().setVisible(False)
        self.back.horizontalHeader().setDefaultSectionSize(32)
        self.back.horizontalHeader().setMinimumSectionSize(32)
        self.back.horizontalHeader().setStretchLastSection(True)
        self.back.verticalHeader().setVisible(False)
        self.back.verticalHeader().setDefaultSectionSize(32)
        self.back.verticalHeader().setMinimumSectionSize(32)
        self.head = QtWidgets.QTableWidget(self.centralwidget)
        self.head.setGeometry(QtCore.QRect(555, 30, 66, 34))
        self.head.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked)
        self.head.setDragEnabled(True)
        self.head.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.head.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.head.setAlternatingRowColors(False)
        self.head.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.head.setCornerButtonEnabled(False)
        self.head.setObjectName("head")
        self.head.setColumnCount(2)
        self.head.setRowCount(1)
        item = QtWidgets.QTableWidgetItem()
        self.head.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.head.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.head.setHorizontalHeaderItem(1, item)
        self.head.horizontalHeader().setVisible(False)
        self.head.horizontalHeader().setDefaultSectionSize(32)
        self.head.horizontalHeader().setMinimumSectionSize(32)
        self.head.horizontalHeader().setStretchLastSection(True)
        self.head.verticalHeader().setVisible(False)
        self.head.verticalHeader().setDefaultSectionSize(32)
        self.head.verticalHeader().setMinimumSectionSize(32)
        self.energy_val = QtWidgets.QLabel(self.centralwidget)
        self.energy_val.setGeometry(QtCore.QRect(160, 240, 41, 20))
        self.energy_val.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.energy_val.setObjectName("energy_val")
        self.cold_immune = QtWidgets.QCheckBox(self.centralwidget)
        self.cold_immune.setGeometry(QtCore.QRect(150, 370, 105, 20))
        self.cold_immune.setObjectName("cold_immune")
        self.hungerless = QtWidgets.QCheckBox(self.centralwidget)
        self.hungerless.setGeometry(QtCore.QRect(150, 320, 96, 20))
        self.hungerless.setObjectName("hungerless")
        self.amazing_lungs = QtWidgets.QCheckBox(self.centralwidget)
        self.amazing_lungs.setGeometry(QtCore.QRect(150, 420, 124, 20))
        self.amazing_lungs.setObjectName("amazing_lungs")
        self.pixels_label = QtWidgets.QLabel(self.centralwidget)
        self.pixels_label.setGeometry(QtCore.QRect(310, 10, 35, 14))
        self.pixels_label.setObjectName("pixels_label")
        self.pixels = QtWidgets.QSpinBox(self.centralwidget)
        self.pixels.setGeometry(QtCore.QRect(300, 30, 91, 23))
        self.pixels.setMaximum(9999999)
        self.pixels.setSingleStep(100)
        self.pixels.setObjectName("pixels")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(11, 11, 261, 141))
        self.widget.setObjectName("widget")
        self.formLayout = QtWidgets.QFormLayout(self.widget)
        self.formLayout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.name_label = QtWidgets.QLabel(self.widget)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)
        self.name = QtWidgets.QLineEdit(self.widget)
        self.name.setObjectName("name")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.name)
        self.race_label = QtWidgets.QLabel(self.widget)
        self.race_label.setObjectName("race_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.race_label)
        self.race = QtWidgets.QComboBox(self.widget)
        self.race.setObjectName("race")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.race)
        self.gender_label = QtWidgets.QLabel(self.widget)
        self.gender_label.setObjectName("gender_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.gender_label)
        self.widget1 = QtWidgets.QWidget(self.widget)
        self.widget1.setMinimumSize(QtCore.QSize(0, 20))
        self.widget1.setObjectName("widget1")
        self.male = QtWidgets.QRadioButton(self.widget1)
        self.male.setGeometry(QtCore.QRect(0, 0, 57, 19))
        self.male.setObjectName("male")
        self.female = QtWidgets.QRadioButton(self.widget1)
        self.female.setGeometry(QtCore.QRect(60, 0, 72, 19))
        self.female.setObjectName("female")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.widget1)
        self.desc_label = QtWidgets.QLabel(self.widget)
        self.desc_label.setObjectName("desc_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.desc_label)
        self.description = QtWidgets.QPlainTextEdit(self.widget)
        self.description.setObjectName("description")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.description)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 637, 19))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuTools = QtWidgets.QMenu(self.menubar)
        self.menuTools.setObjectName("menuTools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtWidgets.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionQuit = QtWidgets.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionManage_Blueprints = QtWidgets.QAction(MainWindow)
        self.actionManage_Blueprints.setObjectName("actionManage_Blueprints")
        self.actionManage_Techs = QtWidgets.QAction(MainWindow)
        self.actionManage_Techs.setObjectName("actionManage_Techs")
        self.actionMake_Backups = QtWidgets.QAction(MainWindow)
        self.actionMake_Backups.setCheckable(True)
        self.actionMake_Backups.setChecked(True)
        self.actionMake_Backups.setObjectName("actionMake_Backups")
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionMake_Backups)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuTools.addAction(self.actionManage_Blueprints)
        self.menuTools.addAction(self.actionManage_Techs)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuTools.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.inv_tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "starcheat"))
        self.health_val.setText(_translate("MainWindow", "1 /"))
        self.health_label.setText(_translate("MainWindow", "Health"))
        self.energy_label.setText(_translate("MainWindow", "Energy"))
        self.warmth_label.setText(_translate("MainWindow", "Warmth"))
        self.breath_label.setText(_translate("MainWindow", "Breath"))
        self.hunger_label.setText(_translate("MainWindow", "Hunger"))
        self.energy_regen_label.setText(_translate("MainWindow", "Regen Rate"))
        self.backpack_label.setText(_translate("MainWindow", "Back"))
        self.legs_label.setText(_translate("MainWindow", "Legs"))
        self.left_hand_label.setText(_translate("MainWindow", "L"))
        self.chest_label.setText(_translate("MainWindow", "Chest"))
        self.head_label.setText(_translate("MainWindow", "Head"))
        self.right_hand_label.setText(_translate("MainWindow", "R"))
        item = self.main_bag.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.main_bag.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.main_bag.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.main_bag.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.main_bag.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.main_bag.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.main_bag.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.main_bag.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.main_bag.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.main_bag.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.main_bag.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.main_bag.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.main_bag.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.main_bag.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        self.inv_tabs.setTabText(self.inv_tabs.indexOf(self.tab_2), _translate("MainWindow", "Main Bag"))
        item = self.tile_bag.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.tile_bag.verticalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.tile_bag.verticalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.tile_bag.verticalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.tile_bag.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.tile_bag.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.tile_bag.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.tile_bag.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.tile_bag.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.tile_bag.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.tile_bag.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.tile_bag.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.tile_bag.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.tile_bag.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        self.inv_tabs.setTabText(self.inv_tabs.indexOf(self.tab_3), _translate("MainWindow", "Tile Bag"))
        item = self.action_bar.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.action_bar.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.action_bar.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.action_bar.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "3"))
        item = self.action_bar.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "4"))
        item = self.action_bar.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "5"))
        item = self.action_bar.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "6"))
        item = self.action_bar.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "7"))
        item = self.action_bar.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "8"))
        item = self.action_bar.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "9"))
        item = self.action_bar.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "10"))
        item = self.wielded.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.wielded.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.wielded.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        self.label.setText(_translate("MainWindow", "Action Bar"))
        item = self.legs.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.legs.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.legs.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.chest.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.chest.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.chest.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.back.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.back.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.back.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        item = self.head.verticalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.head.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "1"))
        item = self.head.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "2"))
        self.energy_val.setText(_translate("MainWindow", "1 /"))
        self.cold_immune.setText(_translate("MainWindow", "Cold Immune"))
        self.hungerless.setText(_translate("MainWindow", "Hungerless"))
        self.amazing_lungs.setText(_translate("MainWindow", "Amazing Lungs"))
        self.pixels_label.setText(_translate("MainWindow", "Pixels"))
        self.name_label.setText(_translate("MainWindow", "Name"))
        self.race_label.setText(_translate("MainWindow", "Race"))
        self.gender_label.setText(_translate("MainWindow", "Gender"))
        self.male.setText(_translate("MainWindow", "Male"))
        self.female.setText(_translate("MainWindow", "Female"))
        self.desc_label.setText(_translate("MainWindow", "Description"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.actionOpen.setText(_translate("MainWindow", "Open..."))
        self.actionOpen.setStatusTip(_translate("MainWindow", "Open a player save file"))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setStatusTip(_translate("MainWindow", "Save player changes"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As..."))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionQuit.setText(_translate("MainWindow", "Quit"))
        self.actionQuit.setStatusTip(_translate("MainWindow", "Quit program"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.actionManage_Blueprints.setText(_translate("MainWindow", "Manage Blueprints"))
        self.actionManage_Techs.setText(_translate("MainWindow", "Manage Techs"))
        self.actionMake_Backups.setText(_translate("MainWindow", "Make Backups"))

