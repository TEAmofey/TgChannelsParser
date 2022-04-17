from PyQt5.QtCore import QObject

import main


class ParseRunner(QObject):
    data = None
    thread = None
    window = None
    handler = None

    def insert(self, window, data, thread, handler):
        self.window = window
        self.data = data
        self.thread = thread
        self.handler = handler

    def run(self):
        print("Launching parse from UI")
        print("Links: {}".format(self.data["links"]))
        main.start(self.data, self.window, self.thread, self.handler)
