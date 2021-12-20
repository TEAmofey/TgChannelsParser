import asyncio
import traceback

from telethon import TelegramClient


from tg_parser import telethon_data, dump_all_messages
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
        telethon_data["client"] = TelegramClient(
            telethon_data["username"],
            int(telethon_data["api_id"]),
            telethon_data["api_hash"])
        await telethon_data["client"].start()
    except:
        print(traceback.format_exc())

    print("Client connected.")
    print("Links loop.")
    for link in data["links"]:
        try:
            print("\tLink: {}".format(link))
            channel = await telethon_data["client"].get_entity(link)
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

    if telethon_data["client"] is not None and telethon_data["client"].is_connected():
        await telethon_data["client"].disconnect()
        print("Client disconnected.")

    print("Completed task.")


def start(data, window):
    asyncio.run(parse(data, window))


if __name__ == "__main__":
    main()
