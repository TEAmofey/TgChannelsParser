import json


def parse(filename, date_from, date_to):
    json_file = open(filename, 'r', encoding="utf-8")
    json_data = json.load(json_file)
    filtered_data = []

    for obj in json_data:
        time_stamp = obj["date"][:10]
        if time_stamp < date_from:
            continue
        if time_stamp > date_to:
            break

        try:  # Сообщения о смене названия канала тоже считаются объектом, но не имеют поля "message"
            msg = obj["message"]
            filtered_data.append({"message": msg, "date": time_stamp})
        except:
            continue

    return filtered_data