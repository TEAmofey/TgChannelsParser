import asyncio
import traceback

from PyQt5.QtCore import QThread, QObject
from telethon import TelegramClient

import main
from tg_parser import dictionary, username, api_id, api_hash


class TelethonHandler(QObject):

    def run(self):
        print("First-time connection")
        try:
            async def do_it():
                dictionary["client"] = TelegramClient(username, int(api_id), api_hash)
                await dictionary["client"].start()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(do_it())

            dictionary["client"].disconnect()
        except:
            print(traceback.format_exc())


