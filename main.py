import traceback

import PyQt5.QtWidgets

from tg_parser import client
from tg_parser import dump_all_messages
from exceptions import RequestException, SearchException
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
        try:
            channel = await client.get_entity(link)
            await dump_all_messages(channel)
            results = await search(data["request"], data["date_from"], data["date_to"])
            print("Results for {}".format(link))
            if results:
                print(results)
            else:
                print("Nothing")
        except SearchException:
            print("SearchException caught")
        except RequestException as e:
            print("Wrong request")
        except ValueError:
            print("Channel {} not found.".format(link))
        except:
            print(traceback.format_exc())


def start(data, window):
    with client:
        client.loop.run_until_complete(parse(data, window))


if __name__ == "__main__":
    main()
