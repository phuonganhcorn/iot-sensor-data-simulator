from nicegui import ui
from model.device import Device
import random


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
                    ui.button(icon="close", on_click=self.dialog.close).props("flat").classes("px-2 text-black")
                with ui.row().classes():
                    self.selects_row = ui.row().classes("mb-5")

                self.chart_wrapper = ui.row().classes('w-full h-64 justify-center items-center')

    def setup_chart(self, init_data=[]):
        with self.chart_wrapper:
            self.chart = ui.chart({
                "title": False,
                "series": [
                    {"name": "-", "data": init_data},
                ],
                "yAxis": {
                    "title": {
                        "text": "Temperatur"
                    },
                    "labels": {
                        "format": "{value} °C"
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

        self.chart_wrapper.clear()
        if self.chart is None:
            with self.chart_wrapper:
                text = "Warten auf Sensordaten..." if container.is_active else "Container ist nicht aktiv"
                self.note_label = ui.label(text).classes("-translate-y-full")
        
        self.chart = None

        device_options = {
            device.id: device.name for device in container.devices}
        first_device = container.devices[0]
        first_sensor = first_device.sensors[0] if len(
            first_device.sensors) > 0 else None
        sensor_options = {
            sensor.id: sensor.name for sensor in container.devices[0].sensors}

        with self.selects_row:
            self.device_select = ui.select(device_options, value=first_device.id,
                                           label="Gerät", on_change=self.device_select_change_handler).classes("w-32")
            first_sensor_value = first_sensor.id if first_sensor is not None else -1
            self.sensor_select = ui.select(sensor_options, value=first_sensor_value,
                                           label="Sensor", on_change=self.sensor_select_change_handler).classes("w-32")
            
        self.dialog.open()

    def device_select_change_handler(self):
        sensor_name = self.update_sensor_select()
        self.clear_chart()
        self.update_series_name(sensor_name)

    def sensor_select_change_handler(self):
        self.clear_chart()
        self.update_series_name(
            self.sensor_select.options[self.sensor_select.value])

    def clear_chart(self):
        self.chart.options["series"][0]["data"] = []
        self.chart.update()

    def update_series_name(self, name):
        self.chart.options["series"][0]["name"] = name
        self.chart.update()

    def update_sensor_select(self):
        device_id = self.device_select.value
        device = Device.get_by_id(device_id)

        if len(device.sensors) > 0:
            sensor_options = {
                sensor.id: sensor.name for sensor in device.sensors}
            self.sensor_select.options = sensor_options
            first_value = list(sensor_options.keys())[0]
            self.sensor_select.update()
            self.sensor_select.value = first_value

            return sensor_options[first_value]

    def append_value(self, sensor, value):
        # Return if the dialog is not open
        if not self.dialog.value:
            return

        # Only append value if the correct device and the sensor is selected
        if self.device_select.value != sensor.device_id or self.sensor_select.value != sensor.id:
            return
        
        if self.chart is None:
            self.chart_wrapper.clear()
            self.setup_chart([[0, value]])
            return
        
        data = self.chart.options["series"][0]["data"]
        last_item = data[-1] if len(data) > 0 else None
        new_time = last_item[0] + 10 if last_item is not None else 0
        data.append([new_time, value])

        self.chart.options["series"][0]["name"] = sensor.name
        self.chart.options["series"][0]["data"] = data
        self.chart.update()
