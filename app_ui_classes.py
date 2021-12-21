import asyncio
import re
import time
import traceback

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QThread, QObject
from PyQt5.QtWidgets import QMainWindow, QFrame
from telethon import TelegramClient
from telethon.errors import FloodWaitError

import main
from tg_parser import telethon_data

''' Thread handlers section '''


class TelethonHandler(QObject):

    def __init__(self, main_window, phone_window):
        super().__init__()
        self.main_window = main_window
        self.phone_window = phone_window

    def run(self):
        print("Authorization")
        print("Inserted code will be {}".format(telethon_data["code"]))
        try:
            async def do_it():
                telethon_data["client"] = TelegramClient(
                    telethon_data["username"],
                    int(telethon_data["api_id"]),
                    telethon_data["api_hash"]
                )
                await telethon_data["client"].start(
                    lambda: telethon_data["phone"],
                    code_callback=lambda: telethon_data["code"]
                )

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(do_it())

            telethon_data["client"].disconnect()
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

    debug_append = QtCore.pyqtSignal(str)

    def insert(self, data):
        self.data = data

    def add_debug(self, text):
        self.debug_append.emit(text)

    def run(self):
        print("Launching parse from UI")
        print("Links: {}".format(self.data["links"]))
        main.start(self.data, self)


''' Pop-up windows section'''


class HelpWindow(QMainWindow):
    def __init__(self):
        super(HelpWindow, self).__init__()

        HelpWindow.setWindowTitle(self, "Построение запроса")
        HelpWindow.setFixedWidth(self, 750)
        HelpWindow.setFixedHeight(self, 360)
        HelpWindow.setWindowIcon(self, QtGui.QIcon("images/question.png"))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.scroll = QtWidgets.QScrollArea(self)
        self.label = QtWidgets.QLabel(self)
        self.label.setText(help_text)
        self.label.setFont(QtGui.QFont("Calibri", 12, QtGui.QFont.Medium))
        self.label.setContentsMargins(20, 20, 0, 0)
        self.label.adjustSize()
        self.scroll.setWidget(self.label)
        self.scroll.setFixedSize(750, 360)
        self.scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.layout.addWidget(self.scroll)


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

        self.insert_phone = QtWidgets.QLineEdit()
        self.insert_phone.setPlaceholderText("Номер телефона")
        self.insert_api_id = QtWidgets.QLineEdit()
        self.insert_api_id.setPlaceholderText("API ID")
        self.insert_api_hash = QtWidgets.QLineEdit()
        self.insert_api_hash.setPlaceholderText("API Hash")
        self.insert_username = QtWidgets.QLineEdit()
        self.insert_username.setPlaceholderText("Username")
        self.button_get_code = QtWidgets.QPushButton("Получить код")
        self.button_get_code.clicked.connect(self.get_code)

        self.insert_code = QtWidgets.QLineEdit()
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
                     "username = {}\n".format(
                self.insert_phone.text(),
                self.insert_api_id.text(),
                self.insert_api_hash.text(),
                self.insert_username.text()
            )
            )

            self.insert_phone.setText(re.sub(r'[^0-9A-Za-z]+', '', self.insert_phone.text()))
            self.insert_api_id.setText(re.sub(r'[^0-9A-Za-z]+', '', self.insert_api_id.text()))
            self.insert_api_hash.setText(re.sub(r'[^0-9A-Za-z]+', '', self.insert_api_hash.text()))
            self.insert_username.setText(re.sub(r'[^0-9A-Za-z]+', '', self.insert_username.text()))

            telethon_data["phone"] = self.insert_phone.text()
            telethon_data["api_id"] = self.insert_api_id.text()
            telethon_data["api_hash"] = self.insert_api_hash.text()
            telethon_data["username"] = self.insert_username.text()

        try:
            telethon_data["client"] = TelegramClient(
                telethon_data["username"],
                int(telethon_data["api_id"]),
                telethon_data["api_hash"]
            )
            telethon_data["client"].connect()
            telethon_data["client"].send_code_request(self.insert_phone.text())
            telethon_data["client"].disconnect()
        except:
            print(traceback.format_exc())
        self.insert_code.setEnabled(True)
        self.button_save.setEnabled(True)

    def check_code(self):
        telethon_data["code"] = re.sub(r'[^0-9]+', '', self.insert_code.text())
        self.main_window.authorize()
        self.close()


help_text = ("\t\tКак работает поиск по ключевым словам?\n"
             "\n"
             "Вы можете вводить ключевые слова в любой форме.\n"
             "\n"
             "Операция & (логическое И)\n"
             "Если вы хотите, чтобы в сообщении одновременно встречалось\n"
             "2 ключевых слова или словосочетание, то нужно написать\n"
             "команду 'слово1 & слово2' (без кавычек).\n"
             "Пример:\n"
             "Если вы хотите найти сообщения, в которых упоминаются синие столы,\n"
             "введите запрос 'синие & столы'\n"
             "\n"
             "Операция | (логическое ИЛИ)\n"
             "Если вы хотите, чтобы в сообщении встречалось одно из двух ключевых\n"
             "слов, то нужно написать команду 'слово1 | слово2'.\n"
             "Пример:\n"
             "Если вы хотите найти сообщения, в которых упоминаются табуретки или столы,\n"
             "введите запрос 'табуретки | столы'.\n"
             "\n"
             "Комбинации операций\n"
             "Чтобы выполнять более сложные запросы, нужно комбинировать первые\n"
             "две операции с помощью скобок (по порядку выполнения действий).\n"
             "Примеры:\n"
             "Если вы хотите найти сообщения, в которых есть или синие,\n"
             "или красные столы, введите запрос '(синие | красные) & столы'.\n"
             "Если вы хотите найти сообщения, в которых есть или синие столы,\n"
             "или табуретки, пишите запрос '(синие & столы) | табуретки'.\n"
             "\n"
             "Важно:\n"
             "Программа не распознаёт запросы, в которых написаны словосочетания\n"
             "без операций & или | (запрос 'синие столы' является некорректным).\n"
             "Запрос из одного слова без операций является корректным.\n\n")
