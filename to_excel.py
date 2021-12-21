import json

import pandas as pd

input_name = "messages.json"  # Имя json файла
output_name = "messages.xlsx"  # Имя json файла


def file_to_json(file_name):
    json_file = open(file_name, 'r', encoding="utf-8")
    json_data = json.load(json_file)
    return json_data


def save_all_channels(dictionary, exel_file_name):
    print(dictionary.items())
    writer = pd.ExcelWriter(exel_file_name)
    for channel in dictionary.items():
        save_one_channel_messages_to_exel(channel[0], channel[1], writer)
        save_one_channel_messages_to_exel("Общий список", channel[1], writer)
    # writer.save()
    writer.close()


def save_one_channel_messages_to_exel(sheet_name, json_data, exel_writer):
    pd.json_normalize(json_data).to_excel(exel_writer, sheet_name=sheet_name)


# save_all_channels(file_to_json(input_name), output_name)