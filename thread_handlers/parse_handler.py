from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class ParseHandler(QObject):
    debug_append = QtCore.pyqtSignal(str)
    change_posts = QtCore.pyqtSignal(str)
    enable_buttons = QtCore.pyqtSignal()
    save = QtCore.pyqtSignal(dict)

    def save_file(self, results):
        self.save.emit(results)

    def activate_buttons(self):
        self.enable_buttons.emit()

    def change_posts_info(self, posts):
        self.change_posts.emit(posts)

    def add_debug(self, text):
        self.debug_append.emit(text)
