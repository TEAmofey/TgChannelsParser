import json

import pandas as pd


def file_to_json(file_name):
    json_file = open(file_name, 'r', encoding="utf-8")
    json_data = json.load(json_file)
    return json_data


def save_all_channels(dictionary, excel_file_name):
    writer = pd.ExcelWriter(excel_file_name)
    append_data_to_excel("Общий список", "Название", [{"message": "Сообщение", "date": "Дата"}], writer, start_row=0)
    row_number = 1
    for channel in dictionary.items():
        append_data_to_excel("Общий список", channel[0], channel[1], writer, start_row=row_number)
        row_number += len(channel[1])
        save_one_channel_messages_to_excel(channel[0], channel[1], writer)
    # writer.save()
    writer.close()


def save_one_channel_messages_to_excel(sheet_name, json_data, excel_writer):
    pd.json_normalize(json_data).to_excel(excel_writer, sheet_name=sheet_name)


def append_data_to_excel(sheet_name, channel_name, json_data, excel_writer, start_row):
    df = pd.json_normalize(json_data)
    df.insert(0, 'Название канала', channel_name)
    df.to_excel(excel_writer,
                sheet_name=sheet_name,
                startrow=start_row,
                index=False,
                header=False,
                index_label=channel_name)
