from nicegui import ui
from constants.units import *
from components.sensor_selection import SensorSelection
from components.chart import Chart


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

                self.chart = Chart()

    def show(self, container):
        self.title_label.set_text(f"Live View: {container.name}")
        self.selects_row.clear()

        text = "Warten auf Sensordaten..." if container.is_active else "Container ist nicht aktiv"
        self.chart.show_note(text)

        with self.selects_row:
            self.sensor_selection = SensorSelection(
                container=container, sensor_select_callback=self.sensor_select_change_handler)

        self.dialog.open()

    def sensor_select_change_handler(self, sensor):
        self.chart.update_legend(sensor=sensor)

    def append_data_point(self, sensor, timestamp, value):
        # Return if the dialog is not open
        if not self.dialog.value:
            return

        # Only append value if the correct device and the sensor is selected
        if self.sensor_selection.device_select.value != sensor.device_id or self.sensor_selection.sensor_select.value != sensor.id:
            return

        if self.chart.chart is None:
            self.chart.show(sensor=sensor, data=[[timestamp, value]])
            return

        self.chart.append_data_point(
            sensor=sensor, timestamp=timestamp, value=value)
