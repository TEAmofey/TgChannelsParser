import asyncio
import traceback

import PyQt5.QtWidgets
from telethon import TelegramClient


from tg_parser import username, api_id, api_hash, dictionary, dump_all_messages
import app_ui
from exceptions import RequestException, SearchException
from morph import search
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    window = app_ui.MainWindow()
    window.show()
    sys.exit(app.exec_())


async def parse(data, window):
    try:
        print("Connecting client...")
        dictionary["client"] = TelegramClient(username, int(api_id), api_hash)
        await dictionary["client"].start()
    except:
        print(traceback.format_exc())

    print("Client connected.")
    print("Links loop.")
    for link in data["links"]:
        try:
            print("\tLink: {}".format(link))
            channel = await dictionary["client"].get_entity(link)
            print("\t\tChannel found.")
            await dump_all_messages(channel)
            print("\t\tPosts downloaded.")
            results = await (search(data["request"], data["date_from"], data["date_to"]))
            print("\t\tResults for {}:".format(link))
            if results:
                print("\t\t\t{}\n".format(results))
            else:
                print("\t\t\tNothing.")
        except SearchException:
            print("SearchException caught")
        except RequestException as e:
            print("Wrong request")
        except ValueError:
            print("\t\t\tChannel {} not found.".format(link))
        except:
            print(traceback.format_exc())

    if dictionary["client"] is not None and dictionary["client"].is_connected():
        await dictionary["client"].disconnect()
        print("Client disconnected.")

    print("Completed task.")


def start(data, window):
    asyncio.run(parse(data, window))


if __name__ == "__main__":
    main()
