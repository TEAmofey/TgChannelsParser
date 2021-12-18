import os
import traceback

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QSystemTrayIcon, QAction

import main
import sys

import tg_parser
from threads_ui import TelethonHandler


def date_to_string(date):
    year = str(date.year())
    month = str(date.month())
    day = str(date.day())
    return "{}-{}-{}".format(
        '0' * (4 - len(year)) + year,
        '0' * (2 - len(month)) + month,
        '0' * (2 - len(day)) + day
    )


def create_check_box(condition):
    widget_check_box = QtWidgets.QWidget()
    check_box = QtWidgets.QCheckBox()
    check_box.setChecked(condition)
    check_box.setFixedWidth(25)
    check_box.setFixedHeight(27)
    with open("styles/check_box.styl", "r") as style:
        check_box.setStyleSheet(style.read())
    layout = QtWidgets.QHBoxLayout(widget_check_box)
    layout.addWidget(check_box)

    layout.setAlignment(QtCore.Qt.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    return widget_check_box


class ParseHandler(QObject):
    # def __init__(self, data, window):
    #     super(ParseHandler, self).__init__()
    #     self.data = data
    #     self.window = window

    data = None
    window = None

    def insert(self, data, window):
        self.data = data
        self.window = window

    def run(self):
        print("Launching parse from UI")
        print("Links: {}".format(self.data["links"]))
        main.start(self.data, self.window)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        MainWindow.setObjectName(self, "MainWindow")
        MainWindow.setFixedWidth(self, 1280)
        MainWindow.setFixedHeight(self, 720)

        # Если захотим сделать лого
        self.setWindowIcon(QtGui.QIcon("images/icon.png"))

        self.begin_row_quantity = 15
        self.row_counter = 0
        self.main_font_big = QtGui.QFont("Calibri", 12, QtGui.QFont.Bold)
        self.main_font_medium = QtGui.QFont("Calibri", 10, QtGui.QFont.Bold)
        self.main_font_small = QtGui.QFont("Calibri", 9, QtGui.QFont.Bold)

        # ----- Left side -----

        # Links table
        self.table_links = QtWidgets.QTableWidget(self)
        self.create_table_links()

        # Button (Choose everything)
        self.button_choose_everything = QtWidgets.QPushButton(self)
        self.create_button_choose_everything()

        # Button (Remove everything)
        self.button_remove_everything = QtWidgets.QPushButton(self)
        self.create_button_remove_everything()

        # Button (Delete chosen)
        self.button_delete_chosen = QtWidgets.QPushButton(self)
        self.create_button_delete_chosen()

        # Button (Add channel)
        self.button_add_link = QtWidgets.QPushButton(self)
        self.create_button_add_link()

        # Insert field (insert telegram link)
        self.insert_link = QtWidgets.QPlainTextEdit(self)
        self.create_insert_link_field()

        # ----- Right side -----

        # Insert field (insert keywords)
        self.insert_key_word = QtWidgets.QPlainTextEdit(self)
        self.create_insert_key_word_field()

        # Button (Show help)
        self.button_show_help = QtWidgets.QPushButton(self)
        self.create_button_help()

        # Texts (Date intervals instruction)
        self.text_date_interval = QtWidgets.QLabel(self)
        self.text_date_from = QtWidgets.QLabel(self)
        self.text_date_to = QtWidgets.QLabel(self)
        self.create_date_descriptions()

        # Date fields
        self.date_field_from = QtWidgets.QDateEdit(self)
        self.date_field_to = QtWidgets.QDateEdit(self)
        self.create_date_fields()

        # # Calendar
        # self.calendar = QtWidgets.QCalendarWidget(self)
        # self.create_calendar()

        # Button (Start)
        self.button_start = QtWidgets.QPushButton(self)
        self.create_button_start()

        # ----- Shortcuts -----

        # Exit
        self.shortcut_exit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_exit.activated.connect(self.close_app)

        # # Enter
        # self.shortcut_enter = QShortcut(QtCore.Qt.Key_Return, self)
        # self.shortcut_enter.activated.connect(self.add_channel)

        # ----- Windows -----

        # Help Window
        self.help_window = HelpWindow()

        # ----- Menu -----
        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_file = QtWidgets.QMenu(self.menu_bar)
        self.menu_edit = QtWidgets.QMenu(self.menu_bar)
        self.create_menu_bar()

        MainWindow.setMenuBar(self, self.menu_bar)
        self.status_bar = QtWidgets.QStatusBar()
        self.status_bar.setObjectName("statusBar")

        MainWindow.setStatusBar(self, self.status_bar)
        self.action_edit = QtWidgets.QAction()
        self.action_edit.setObjectName("actionEdit")
        self.action_exit = QtWidgets.QAction()
        self.action_exit.setObjectName("actionExit")
        self.action_exit.triggered.connect(self.close_app)

        self.fill_menu_bar()
        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.parse_thread = QtCore.QThread()
        self.parse_handler = ParseHandler()
        self.parse_handler.moveToThread(self.parse_thread)
        self.parse_thread.started.connect(self.parse_handler.run)

        self.first_connect_thread = QtCore.QThread()
        self.connect_handler = TelethonHandler()
        self.connect_handler.moveToThread(self.first_connect_thread)
        self.first_connect_thread.started.connect(self.connect_handler.run)
        self.first_connect_thread.start()

    # Initializing methods

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(self, _translate("MainWindow", "Telegram search"))
        self.menu_file.setTitle(_translate("MainWindow", "Меню"))
        self.action_edit.setText(_translate("MainWindow", "Настройки"))
        self.action_exit.setText(_translate("MainWindow", "Выход"))

    # Text fields

    def create_date_descriptions(self):
        self.text_date_interval.setText("Выберите диапазон поиска:")
        self.text_date_interval.setFont(self.main_font_big)
        self.text_date_interval.setGeometry(QtCore.QRect(820, 225, 100, 100))
        self.text_date_interval.adjustSize()

        self.text_date_from.setText("От:")
        self.text_date_from.setFont(self.main_font_big)
        self.text_date_from.setGeometry(QtCore.QRect(850, 277, 10, 10))
        self.text_date_from.adjustSize()

        self.text_date_to.setText("До:")
        self.text_date_to.setFont(self.main_font_big)
        self.text_date_to.setGeometry(QtCore.QRect(850, 327, 10, 10))
        self.text_date_to.adjustSize()

    # Buttons

    def create_button_add_link(self):
        self.button_add_link.setGeometry(QtCore.QRect(538, 75, 0, 0))
        with open("styles/button_add.styl", "r") as style:
            self.button_add_link.setStyleSheet(style.read())
        self.button_add_link.adjustSize()
        self.button_add_link.clicked.connect(self.add_channel)

    def create_button_choose_everything(self):
        self.button_choose_everything.setGeometry(QtCore.QRect(50, 660, 0, 0))
        with open("styles/button_choose.styl", "r") as style:
            self.button_choose_everything.setStyleSheet(style.read())
        self.button_choose_everything.adjustSize()
        self.button_choose_everything.clicked.connect(self.choose_everything)

    def create_button_remove_everything(self):
        self.button_remove_everything.setGeometry(QtCore.QRect(160, 660, 0, 0))
        with open("styles/button_remove.styl", "r") as style:
            self.button_remove_everything.setStyleSheet(style.read())
        self.button_remove_everything.adjustSize()
        self.button_remove_everything.clicked.connect(self.remove_everything)

    def create_button_delete_chosen(self):
        self.button_delete_chosen.setGeometry(QtCore.QRect(510, 660, 0, 0))
        with open("styles/button_delete.styl", "r") as style:
            self.button_delete_chosen.setStyleSheet(style.read())
        self.button_delete_chosen.adjustSize()
        self.button_delete_chosen.clicked.connect(self.delete_chosen)

    def create_button_start(self):
        self.button_start.setGeometry(QtCore.QRect(850, 400, 0, 0))
        with open("styles/button_start.styl", "r") as style:
            self.button_start.setStyleSheet(style.read())
        self.button_start.adjustSize()
        self.button_start.clicked.connect(self.send_request)

    def create_button_help(self):
        self.button_show_help.setGeometry(QtCore.QRect(1200, 150, 0, 0))
        with open("styles/button_help.styl", "r") as style:
            self.button_show_help.setStyleSheet(style.read())
        self.button_show_help.adjustSize()
        self.button_show_help.clicked.connect(self.show_help)

    # Insert fields

    def create_insert_link_field(self):
        self.insert_link.setGeometry(QtCore.QRect(78, 75, 450, 35))
        self.insert_link.setObjectName("plainTextEdit")
        self.insert_link.setFont(self.main_font_medium)
        self.insert_link.setMaximumBlockCount(1)
        self.insert_link.setPlaceholderText("Введите ссылку на telegram-канал")

    def create_insert_key_word_field(self):
        self.insert_key_word.setGeometry(QtCore.QRect(741, 150, 450, 35))
        self.insert_key_word.setObjectName("plainTextEditKeyWord")
        self.insert_key_word.setFont(self.main_font_medium)
        self.insert_key_word.setMaximumBlockCount(1)
        self.insert_key_word.setPlaceholderText("Введите ключевые слова")

    # Table

    def create_table_links(self):
        self.table_links.setGeometry(QtCore.QRect(50, 150, 601, 500))
        self.table_links.setObjectName("tableWidget")
        self.table_links.setColumnCount(2)
        self.table_links.setRowCount(self.begin_row_quantity)
        self.table_links.setFont(self.main_font_medium)
        self.table_links.setHorizontalHeaderLabels(["Ссылка", "Выбрать"])
        self.table_links.setColumnWidth(0, 450)
        self.table_links.setColumnWidth(1, 100)
        self.table_links.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table_links.setSelectionMode(QtWidgets.QTableWidget.NoSelection)

    # Date fields

    def create_date_fields(self):
        # From
        self.date_field_from.setGeometry(QtCore.QRect(900, 275, 125, 30))
        self.date_field_from.setFont(self.main_font_big)
        self.date_field_from.setDateTime(QtCore.QDateTime.currentDateTime())

        # To
        self.date_field_to.setGeometry(QtCore.QRect(900, 325, 125, 30))
        self.date_field_to.setFont(self.main_font_big)
        self.date_field_to.setDateTime(QtCore.QDateTime.currentDateTime())

    # Menu

    def create_menu_bar(self):
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 978, 26))
        self.menu_bar.setObjectName("menuBar")
        self.menu_file.setObjectName("menuFile")

    def fill_menu_bar(self):
        self.menu_file.addAction(self.action_exit)
        self.menu_bar.addAction(self.menu_file.menuAction())

    #   Action methods

    def add_channel(self):
        channel = self.insert_link.toPlainText()
        if channel == "":
            return
        if self.row_counter >= self.begin_row_quantity:
            self.table_links.insertRow(self.row_counter)
        self.table_links.setItem(self.row_counter, 0, QtWidgets.QTableWidgetItem(channel))

        widget_check_box = create_check_box(True)
        self.table_links.setCellWidget(self.row_counter, 1, widget_check_box)
        self.row_counter = self.row_counter + 1
        self.insert_link.clear()

    def choose_everything(self):
        self.set_checkboxes(True)

    def remove_everything(self):
        self.set_checkboxes(False)

    def set_checkboxes(self, condition):
        for row in range(self.row_counter):
            self.table_links.cellWidget(row, 1).layout().itemAt(0).widget().setChecked(condition)

    def delete_chosen(self):
        chosen = []
        for row in range(self.row_counter):
            if self.table_links.cellWidget(row, 1).layout().itemAt(0).widget().isChecked():
                chosen.append(row)
        self.row_counter = self.row_counter - len(chosen)
        for row in reversed(chosen):
            self.table_links.removeRow(row)
        self.table_links.setRowCount(max(self.begin_row_quantity, self.row_counter))

    def show_help(self):
        self.help_window.show()

    def close_app(self):
        self.help_window.close()
        self.close()

    # Backend connection

    def send_request(self):
        data = {
            "links": self.collect_links(),
            "request": self.insert_key_word.toPlainText(),
            "date_from": date_to_string(self.date_field_from.date()),
            "date_to": date_to_string(self.date_field_to.date())
        }

        self.parse_handler.insert(data, self)
        self.parse_thread.start()

    def collect_links(self):
        channels = []
        for row in range(self.row_counter):
            if self.table_links.cellWidget(row, 1).layout().itemAt(0).widget().isChecked():
                channels.append(self.table_links.item(row, 0).text())
        return channels


class HelpWindow(QMainWindow):
    def __init__(self):
        super(HelpWindow, self).__init__()

        HelpWindow.setWindowTitle(self, "Построение запроса")
        HelpWindow.setFixedWidth(self, 640)
        HelpWindow.setFixedHeight(self, 360)
        HelpWindow.setWindowIcon(self, QtGui.QIcon("images/question.png"))

        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Prosto text")
        self.label.setFont(QtGui.QFont("Calibri", 12, QtGui.QFont.Medium))
        self.label.setContentsMargins(20, 20, 0, 0)
        self.label.adjustSize()
        self.layout.addWidget(self.label)


# def application():
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

# https://my.telegram.org/auth
