import asyncio
import ctypes
import sys
import time
import traceback

from PyQt5.QtWidgets import QApplication
from telethon import TelegramClient
from telethon.errors import FloodWaitError

import app_ui
import app_ui_classes
from morph import search
from tg_parser import telethon_data, dump_all_messages
from thread_handlers import parse_handler


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main():
    app = QApplication(sys.argv)
    window = app_ui.MainWindow()
    window.show()
    sys.exit(app.exec_())

    # if is_admin():
    #     app = QApplication(sys.argv)
    #     window = app_ui.MainWindow()
    #     window.show()
    #     sys.exit(app.exec_())
    # else:
    #     # Re-run the program with admin rights
    #     ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)


async def parse(data, window, thread, handler: parse_handler.ParseHandler):
    handler.add_debug("Запуск")
    try:
        print("Connecting...")
        handler.add_debug("Установка соединения...")
        telethon_data["client"] = TelegramClient(
            telethon_data["username"],
            int(telethon_data["api_id"]),
            telethon_data["api_hash"]
        )
        await telethon_data["client"].start(telethon_data["phone"])
    except FloodWaitError as e:
        app_ui_classes.alert_popup_flood_exception(e)
        window.main_widget.setEnadled(False)
    except:
        handler.add_debug(traceback.format_exc())

    print("Connected. Starting search.")
    handler.add_debug("Соединение установлено.\nНачало поиска.")
    channels_with_messages = {}
    try:
        for link in data["links"]:
            try:
                handler.add_debug(4 * ' ' + "Текущий канал: {}".format(link))

                channel = await telethon_data["client"].get_entity(link)

                # Секунда между запросом на канал и началом запросов на посты
                time.sleep(1)

                handler.add_debug(8 * ' ' + "Канал найден. Скачиваем все посты...")

                await dump_all_messages(channel, data["date_from"], handler)

                handler.add_debug(8 * ' ' + "Посты скачаны. Начинаем поиск по ключевым словам.")

                list_of_posts = await (search(data["request"], data["date_from"], data["date_to"]))

                handler.add_debug(12 * ' ' + "Найдено подходящих постов: {}.".format(len(list_of_posts)))

                channels_with_messages[channel.title] = list_of_posts

            except ValueError:
                handler.add_debug(4 * ' ' + "Канал {} не найден.".format(link))
    except:
        handler.add_debug(traceback.format_exc())
    finally:
        if telethon_data["client"] is not None and telethon_data["client"].is_connected():
            await telethon_data["client"].disconnect()
            print("Disconnected.")

    try:
        handler.save_file(channels_with_messages)
    except:
        handler.add_debug(traceback.format_exc())

    handler.add_debug("Поиск завершен.\n")

    handler.activate_buttons()

    thread.terminate()


def start(data, window, thread, handler):
    asyncio.run(parse(data, window, thread, handler))


if __name__ == "__main__":
    main()
