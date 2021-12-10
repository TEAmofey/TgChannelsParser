from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut

import sys


def create_check_box(condition):
    widget_check_box = QtWidgets.QWidget()
    check_box = QtWidgets.QCheckBox()
    check_box.setChecked(condition)
    check_box.setFixedWidth(27)
    check_box.setFixedHeight(27)
    check_box.setStyleSheet('''
        QCheckBox::indicator {
            width: 25px;
            height: 25px;
            background-color: white;
            border: 1px solid black;
        }

        QCheckBox::indicator:hover {
            border: 1px solid gray;
        }

        QCheckBox::indicator:checked {
            background-color: #66ff66;
        }
        ''')
    layout = QtWidgets.QHBoxLayout(widget_check_box)
    layout.addWidget(check_box)
    layout.setAlignment(QtCore.Qt.AlignCenter)
    layout.setContentsMargins(0, 0, 0, 0)
    return widget_check_box


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        MainWindow.setObjectName(self, "MainWindow")
        MainWindow.setFixedWidth(self, 1280)
        MainWindow.setFixedHeight(self, 720)

        # Если захотим сделать лого
        # self.setWindowIcon(QtGui.QIcon("icon.png"))

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

        # Insert field (insert key words)
        self.insert_key_word = QtWidgets.QPlainTextEdit(self)
        self.create_insert_key_word_field()

        # Button (Show help)
        self.button_show_help = QtWidgets.QPushButton(self)
        self.create_button_help()

        # Texts (Date intervals instruction)
        self.text_date_interval = QtWidgets.QLabel(self)

        # Date fields
        self.date_field_from = QtWidgets.QDateEdit(self)
        self.date_field_to = QtWidgets.QDateEdit(self)
        self.create_date_fields()

        # ----- Shortcuts -----

        # Exit
        self.shortcut_exit = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut_exit.activated.connect(self.close_app)

        # # Enter
        # self.shortcut_enter = QShortcut(QtCore.Qt.Key_Return, self)
        # self.shortcut_enter.activated.connect(self.add_channel)

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

    # Initializing methods

    def retranslate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(self, _translate("MainWindow", "Telegram search"))
        self.button_add_link.setText(_translate("MainWindow", "Добавить"))
        self.menu_file.setTitle(_translate("MainWindow", "File"))
        self.action_edit.setText(_translate("MainWindow", "Settings"))
        self.action_exit.setText(_translate("MainWindow", "Exit"))

    def create_button_add_link(self):
        self.button_add_link.setGeometry(QtCore.QRect(538, 75, 80, 35))
        self.button_add_link.setObjectName("pushButton")
        self.button_add_link.clicked.connect(self.add_channel)

    def create_button_choose_everything(self):
        self.button_choose_everything.setGeometry(QtCore.QRect(50, 660, 100, 30))
        self.button_choose_everything.setText("Выбрать все")
        self.button_choose_everything.setFont(self.main_font_small)
        self.button_choose_everything.clicked.connect(self.choose_everything)

    def create_button_remove_everything(self):
        self.button_remove_everything.setGeometry(QtCore.QRect(160, 660, 100, 30))
        self.button_remove_everything.setText("Убрать все")
        self.button_remove_everything.setFont(self.main_font_small)
        self.button_remove_everything.clicked.connect(self.remove_everything)

    def create_button_delete_chosen(self):
        self.button_delete_chosen.setGeometry(QtCore.QRect(510, 660, 140, 30))
        self.button_delete_chosen.setText("Удалить выбранное")
        self.button_delete_chosen.setFont(self.main_font_small)
        self.button_delete_chosen.clicked.connect(self.delete_chosen)

    def create_insert_link_field(self):
        self.insert_link.setGeometry(QtCore.QRect(78, 75, 450, 35))
        self.insert_link.setObjectName("plainTextEdit")
        self.insert_link.setFont(self.main_font_medium)
        self.insert_link.setMaximumBlockCount(1)
        self.insert_link.setPlaceholderText("Введите ссылку на telegram-канал")

    def create_insert_key_word_field(self):
        self.insert_key_word.setGeometry(QtCore.QRect(741, 75, 450, 35))
        self.insert_key_word.setObjectName("plainTextEditKeyWord")
        self.insert_key_word.setFont(self.main_font_medium)
        self.insert_key_word.setMaximumBlockCount(1)
        self.insert_key_word.setPlaceholderText("Введите ключевые слова")

    def create_button_help(self):
        self.button_show_help.setGeometry(QtCore.QRect(1200, 75, 30, 35))
        self.button_show_help.setObjectName("pushButton")
        self.button_show_help.setText("?")
        self.button_show_help.setFont(self.main_font_big)
        self.button_show_help.clicked.connect(self.show_help)

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

    def create_date_fields(self):
        # From
        self.date_field_from.setGeometry(QtCore.QRect(820, 150, 125, 30))
        self.date_field_from.setFont(self.main_font_big)
        self.date_field_from.setDateTime(QtCore.QDateTime.currentDateTime())

        # To
        self.date_field_to.setGeometry(QtCore.QRect(820, 200, 125, 30))
        self.date_field_to.setFont(self.main_font_big)
        self.date_field_to.setDateTime(QtCore.QDateTime.currentDateTime())

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
        print("Help")

    def close_app(self):
        self.close()


def application():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    application()
