from nicegui import ui
from constants.units import UNITS
from model.sensor import Sensor


class Chart:

    def __init__(self):
        self.wrapper = None
        self.chart = None
        self.setup()

    def setup(self):
        with ui.row().classes('w-full h-64 justify-center items-center') as wrapper:
            self.wrapper = wrapper
            self.note_label = ui.label(
                "Keine Daten").classes("w-full text-center")

    def show_note(self, text):
        self.note_label.set_text(text)

    def show(self, sensor=None, time_series_data=None, data=None):
        if time_series_data is not None:
            sensor_id = time_series_data[0]["sensorId"]
            sensor = Sensor.get_by_id(sensor_id)
            data = [[time_series_data[i]["timestamp"], time_series_data[i]["value"]]
                    for i in range(len(time_series_data))]

        self.wrapper.clear()
        with self.wrapper:
            self.chart = ui.chart({
                "title": False,
                "series": [
                    {"name": "Motor", "data": data},
                ],
                "yAxis": {
                    "title": {
                        "text": UNITS[sensor.unit]["name"]
                    },
                    "labels": {
                        "format": "{value} " + UNITS[sensor.unit]["unit_abbreviation"]
                    }
                },
                "xAxis": {
                    "title": {
                        "text": "Zeit"
                    },
                    "labels": {
                        "format": "{value}s"
                    }
                },
            }).classes("w-full h-64")

    def update(self, sensor, time_series_data):
        data = [[time_series_data[i]["timestamp"], time_series_data[i]["value"]]
                for i in range(len(time_series_data))]

        # Update data
        self.chart.options["series"][0]["data"] = data
        self.update_legend(sensor)

    def update_legend(self, sensor):
        # Update y axis
        self.chart.options["yAxis"]["title"]["text"] = UNITS[sensor.unit]["name"]
        self.chart.options["yAxis"]["labels"]["format"] = "{value} " + \
            UNITS[sensor.unit]["unit_abbreviation"]

        # Update dataset name
        self.chart.options["series"][0]["name"] = sensor.name
        self.chart.update()

    def append_value(self, sensor, value):
        data = self.chart.options["series"][0]["data"]
        last_item = data[-1] if len(data) > 0 else None
        new_time = last_item[0] + 10 if last_item is not None else 0
        data.append([new_time, value])

        self.chart.options["series"][0]["name"] = sensor.name
        self.chart.options["series"][0]["data"] = data
        self.chart.update()

    def empty(self):
        self.chart.options["series"][0]["name"] = "Leer"
        self.chart.options["series"][0]["data"] = []
        self.chart.update()
