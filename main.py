from tg_parser import client
from tg_parser import dump_all_messages


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)
    await dump_all_messages(channel)


with client:
    client.loop.run_until_complete(main())
