import PyQt5.QtWidgets

from tg_parser import client
from tg_parser import dump_all_messages
import app_ui
from morph import search
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    window = app_ui.MainWindow()
    window.show()
    sys.exit(app.exec_())


async def parse(data, window):
    for link in data["links"]:
        channel = await client.get_entity(link)
        await dump_all_messages(channel)
        results = await search(data["request"], data["date_from"], data["date_to"])
        print("Results for {}".format(link))
        if results:
            print(results)
        else:
            print("Nothing")


def start(data, window):
    with client:
        client.loop.run_until_complete(parse(data, window))


if __name__ == "__main__":
    main()
