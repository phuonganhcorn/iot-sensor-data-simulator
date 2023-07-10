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
                "Keine Daten").classes("w-full text-center -translate-y-full")

    def show_note(self, text):
        self.note_label.set_text(text)

    def show(self, sensor=None, time_series_data=None, data=None):
        if time_series_data is not None:
            sensor_id = time_series_data[0]["sensorId"]
            sensor = Sensor.get_by_id(sensor_id)
            data = [
                [  
                    time_series_data[i]["timestamp"].strftime("%d.%m.%Y, %H:%M:%S"), time_series_data[i]["value"]
                ]
                for i in range(len(time_series_data))
            ]

        x_values = [i * sensor.interval for i in range(len(data))]

        self.wrapper.clear()
        with self.wrapper:
            self.chart = ui.chart({
                "title": False,
                "series": [
                    {"name": sensor.name, "data": data},
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
                    },
                    "categories": x_values,
                },
            }).classes("w-full h-64")

    def update(self, sensor, time_series_data):
        data = [[time_series_data[i]["timestamp"].strftime("%d.%m.%Y, %H:%M:%S"), time_series_data[i]["value"]]
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

    def append_data_point(self, sensor, timestamp, value):
        # Append data point
        data = self.chart.options["series"][0]["data"]
        data.append([timestamp, value])
        self.chart.options["series"][0]["data"] = data

        # Update x axis
        x_values = self.chart.options["xAxis"]["categories"]
        x_values.append(x_values[-1] + sensor.interval)
        self.chart.options["xAxis"]["categories"] = x_values

        # Update dataset name
        self.chart.options["series"][0]["name"] = sensor.name
        self.chart.update()

    def empty(self):
        self.chart.options["series"][0]["name"] = "Leer"
        self.chart.options["series"][0]["data"] = []
        self.chart.update()
