from nicegui import ui
from model.device import Device
from model.sensor import Sensor
from constants.units import *
from components.sensor_selection import SensorSelection


class LiveViewDialog():

    def __init__(self, parent):
        self.parent = parent
        self.dialog = None
        self.chart = None
        self.setup()

    def setup(self):
        with self.parent:
            with ui.dialog() as dialog, ui.card().classes("w-[696px] !max-w-none"):
                self.dialog = dialog
                with ui.row().classes("w-full justify-between items-center"):
                    self.title_label = ui.label().classes("text-lg font-semibold")
                    ui.button(icon="close", on_click=self.dialog.close).props(
                        "flat").classes("px-2 text-black")
                with ui.row().classes():
                    self.selects_row = ui.row().classes("mb-5")

                self.chart_wrapper = ui.row().classes('w-full h-64 justify-center items-center')

    def setup_chart(self, sensor, init_data=[]):
        with self.chart_wrapper:
            self.chart = ui.chart({
                "title": False,
                "series": [
                    {"name": sensor.name, "data": init_data},
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

    def show(self, container):
        self.title_label.set_text(f"Live View: {container.name}")
        self.selects_row.clear()

        self.chart = None
        self.chart_wrapper.clear()
        with self.chart_wrapper:
            text = "Warten auf Sensordaten..." if container.is_active else "Container ist nicht aktiv"
            self.note_label = ui.label(text).classes("-translate-y-full")

        with self.selects_row:
            self.sensor_selection = SensorSelection(
                container=container, sensor_select_callback=self.sensor_select_change_handler_test)

        self.dialog.open()

    def sensor_select_change_handler_test(self, sensor):
        self.clear_chart()
        self.update_series_name(sensor.name)
        self.update_y_axis(sensor)

    def clear_chart(self):
        self.chart.options["series"][0]["data"] = []
        self.chart.update()

    def update_series_name(self, name):
        self.chart.options["series"][0]["name"] = name
        self.chart.update()

    def update_y_axis(self, sensor):
        self.chart.options["yAxis"]["title"]["text"] = UNITS[sensor.unit]["name"]
        self.chart.options["yAxis"]["labels"]["format"] = "{value} " + \
            UNITS[sensor.unit]["unit_abbreviation"]
        self.chart.update()

    def append_value(self, sensor, value):
        # Return if the dialog is not open
        if not self.dialog.value:
            return

        # Only append value if the correct device and the sensor is selected
        if self.sensor_selection.device_select.value != sensor.device_id or self.sensor_selection.sensor_select.value != sensor.id:
            return

        if self.chart is None:
            self.chart_wrapper.clear()
            self.setup_chart(sensor=sensor, init_data=[[0, value]])
            return

        data = self.chart.options["series"][0]["data"]
        last_item = data[-1] if len(data) > 0 else None
        new_time = last_item[0] + 10 if last_item is not None else 0
        data.append([new_time, value])

        self.chart.options["series"][0]["name"] = sensor.name
        self.chart.options["series"][0]["data"] = data
        self.chart.update()
