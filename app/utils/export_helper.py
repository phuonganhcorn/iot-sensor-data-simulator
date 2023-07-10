from tkinter import filedialog
from datetime import datetime
import json
import csv

class ExportHelper:

    def save_to_file(self, data):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("CSV", "*.csv")])

        if file_path.endswith(".json"):
            self._save_as_json(file_path, data)
        elif file_path.endswith(".csv"):
            self._save_as_csv(file_path, data)
    
    def _save_as_json(self, file_path, data):
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4, default=self._datetime_to_string)

    def _save_as_csv(self, file_path, data):
        all_records = self._convert_data_dict_to_list(data)
        fieldnames = all_records[0].keys()

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_records)

    def _datetime_to_string(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type '{type(obj)}' is not JSON serializable")

    def _convert_data_dict_to_list(self, data):
        all_records = []
        device_keys = data.keys()
        for device_key in device_keys:
            sensor_keys = data[device_key].keys()
            for sensor_key in sensor_keys:
                records = data[device_key][sensor_key]
                all_records.extend(records)

        # sort all_records by timestamp
        all_records.sort(key=lambda record: record["timestamp"])
        return all_records


