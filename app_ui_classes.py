import asyncio
import time
import traceback

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QThread, QObject
from PyQt5.QtWidgets import QMainWindow
from telethon import TelegramClient
from telethon.errors import FloodWaitError

import main
from tg_parser import dictionary

''' Thread handlers section '''


class TelethonHandler(QObject):

    def __init__(self, main_window, phone_window):
        super().__init__()
        self.main_window = main_window
        self.phone_window = phone_window

    def run(self):
        print("Authorization")
        print("Inserted code will be {}".format(dictionary["code"]))
        try:
            async def do_it():
                dictionary["client"] = TelegramClient(
                    dictionary["username"],
                    int(dictionary["api_id"]),
                    dictionary["api_hash"]
                )
                await dictionary["client"].start(
                    lambda: dictionary["phone"],
                    code_callback=lambda: dictionary["code"]
                )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(do_it())

            dictionary["client"].disconnect()
            self.main_window.correct_code = True
            print("Connected.")
        except RuntimeError:
            self.main_window.correct_code = False
            print("Didn't connect: entered phone, next time will require code.")
        except FloodWaitError as e:
            print(traceback.format_exc())
            print("Cooldown. Try again later: {}".format(e.message))
        except:
            print(traceback.format_exc())


class ParseHandler(QObject):
    data = None
    window = None

    def insert(self, data, window):
        self.data = data
        self.window = window

    def run(self):
        print("Launching parse from UI")
        print("Links: {}".format(self.data["links"]))
        main.start(self.data, self.window)


''' Pop-up windows section'''


class HelpWindow(QMainWindow):
    def __init__(self):
        super(HelpWindow, self).__init__()

        HelpWindow.setWindowTitle(self, "Построение запроса")
        HelpWindow.setFixedWidth(self, 640)
        HelpWindow.setFixedHeight(self, 360)
        HelpWindow.setWindowIcon(self, QtGui.QIcon("images/question.png"))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Prosto text")
        self.label.setFont(QtGui.QFont("Calibri", 12, QtGui.QFont.Medium))
        self.label.setContentsMargins(20, 20, 0, 0)
        self.label.adjustSize()
        self.layout.addWidget(self.label)


class PhoneWindow(QMainWindow):
    def __init__(self, main_window):
        super(PhoneWindow, self).__init__()

        self.main_window = main_window
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        HelpWindow.setWindowTitle(self, "Конфигурация")
        HelpWindow.setFixedWidth(self, 360)
        HelpWindow.setFixedHeight(self, 360)
        HelpWindow.setWindowIcon(self, QtGui.QIcon("images/icon-settings.svg"))

        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)

        self.insert_phone = QtWidgets.QTextEdit()
        self.insert_phone.setPlaceholderText("Номер телефона")
        self.insert_api_id = QtWidgets.QTextEdit()
        self.insert_api_id.setPlaceholderText("API ID")
        self.insert_api_hash = QtWidgets.QTextEdit()
        self.insert_api_hash.setPlaceholderText("API Hash")
        self.insert_username = QtWidgets.QTextEdit()
        self.insert_username.setPlaceholderText("Username")
        self.button_get_code = QtWidgets.QPushButton("Получить код")
        self.button_get_code.clicked.connect(self.get_code)

        self.insert_code = QtWidgets.QTextEdit()
        self.insert_code.setPlaceholderText("Введите код")
        self.insert_code.setFixedSize(150, 33)
        self.button_save = QtWidgets.QPushButton("Сохранить")
        self.button_save.clicked.connect(self.check_code)
        self.button_pressed = False
        self.insert_code.setEnabled(False)
        self.button_save.setEnabled(False)

        self.layout = QtWidgets.QVBoxLayout(self.widget)
        self.layout.addWidget(self.insert_phone)
        self.layout.addWidget(self.insert_api_id)
        self.layout.addWidget(self.insert_api_hash)
        self.layout.addWidget(self.insert_username)
        self.layout.addWidget(self.button_get_code)
        self.layout.addWidget(self.insert_code)
        self.layout.addWidget(self.button_save)

        for pos in range(self.layout.count()):
            if pos < 4:
                self.layout.itemAt(pos).widget().setFixedSize(300, 33)
            self.layout.itemAt(pos).widget().setFont(QtGui.QFont("Calibri", 10, QtGui.QFont.Bold))
            self.layout.itemAt(pos).setAlignment(QtCore.Qt.AlignCenter)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(self.layout)

    def get_code(self):
        with open('config.ini', 'w') as cf:
            cf.write("[Telegram]\n"
                     "phone = {}\n"
                     "api_id = {}\n"
                     "api_hash = {}\n"
                     "username = {}\n"
                .format(
                    self.insert_phone.toPlainText(),
                    self.insert_api_id.toPlainText(),
                    self.insert_api_hash.toPlainText(),
                    self.insert_username.toPlainText()
                )
            )
            dictionary["phone"] = self.insert_phone.toPlainText()
            dictionary["api_id"] = self.insert_api_id.toPlainText()
            dictionary["api_hash"] = self.insert_api_hash.toPlainText()
            dictionary["username"] = self.insert_username.toPlainText()

        try:
            dictionary["client"] = TelegramClient(
                dictionary["username"],
                int(dictionary["api_id"]),
                dictionary["api_hash"]
            )
            dictionary["client"].connect()
            dictionary["client"].send_code_request(self.insert_phone.toPlainText())
            dictionary["client"].disconnect()
        except:
            print(traceback.format_exc())
        self.insert_code.setEnabled(True)
        self.button_save.setEnabled(True)

    def check_code(self):
        dictionary["code"] = self.insert_code.toPlainText()
        self.main_window.authorize()
        self.close()

