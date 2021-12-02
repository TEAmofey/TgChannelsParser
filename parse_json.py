import json

def parse(filename):
	json_file = open(filename, 'r', encoding="utf-8")
	json_data = json.load(json_file)
	filtered_data = []

	for obj in json_data:
		try: # Сообщения о смене названия канала тоже считаются объектом, но не имеют поля "message" 
			msg = obj["message"]
			time_stamp = obj["date"]
			filtered_data.append({"message": msg, "date": time_stamp})
		except:
			continue
	
	return filtered_data