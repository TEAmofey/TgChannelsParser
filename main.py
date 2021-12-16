from tg_parser import client
from tg_parser import dump_all_messages
import app_ui
from morph import search
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app_ui.application()


async def parse(data):
    for link in data["links"]:
        channel = await client.get_entity(link)
        await dump_all_messages(channel)
        results = await search(data["request"], data["date_from"], data["date_to"])
        print("Results for {}".format(link))
        if results:
            print(results)
        else:
            print("Nothing")


def start(data):
    print("вхожу в старт")
    with client:
        client.loop.run_until_complete(parse(data))


if __name__ == "__main__":
    main()
