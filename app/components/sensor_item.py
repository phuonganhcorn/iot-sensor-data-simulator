from nicegui import ui
from model.sensor import Sensor
from model.device import Device
from constants.units import *
import json


class SensorItem:

    def __init__(self, sensor, delete_callback):
        self.sensor = sensor
        self.visible = True

        error_type = None
        if sensor.error_definition:
            error_definition = json.loads(sensor.error_definition) if sensor.error_definition else None
            error_type = error_definition["type"]
        
        with ui.row().bind_visibility(self, "visible").classes("px-3 py-4 flex justify-between items-center w-full hover:bg-gray-50"):
            with ui.row().classes("gap-6"):
                ui.label(f"{sensor.id}").classes("w-[30px]")
                ui.label(f"{sensor.name}").classes("w-[130px]")
                ui.label(f"{UNITS[sensor.unit]['name']}").classes("w-[130px]")
                if sensor.device:
                    ui.label(f"{sensor.device.name}").classes("w-[130px]")
                if error_type:
                    ui.label(f"{error_type.title()}").classes("w-[130px]")
            with ui.row():
                with ui.row().classes("gap-2"):
                    ui.button(icon="info_outline", on_click=self.show_details_dialog).props(
                        "flat").classes("px-2")
                    ui.button(icon="delete", on_click=lambda s=sensor: delete_callback(s)).props(
                        "flat").classes("px-2 text-red")

    def show_details_dialog(self):
        with ui.dialog(value=True) as dialog, ui.card().classes("w-[696px] !max-w-none px-6 pb-6"):
            self.dialog = dialog
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(f"Details - '{self.sensor.name}'").classes("text-xl font-semibold")
                ui.button(icon="close", on_click=self.dialog.close).props("flat").classes("px-2 text-black")

            with ui.column().classes("gap-4"):
                ui.label("Allgemein").classes("text-lg font-semibold mt-2")
                with ui.row().classes("gap-10"):
                    with ui.column().classes("gap-0"):
                        ui.label("ID").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{self.sensor.id}").classes("text-md")
                    with ui.column().classes("gap-0"):
                        ui.label("Name").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{self.sensor.name}").classes("text-md")
                    with ui.column().classes("gap-0"):
                        ui.label("Typ").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{UNITS[self.sensor.unit]['name']}").classes("text-md")
                    with ui.column().classes("gap-0"):
                        ui.label("Einheit").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{UNITS[self.sensor.unit]['unit_abbreviation']}").classes("text-md")

            ui.row().classes("mt-4 mb-2 h-px w-full bg-gray-200 border-0")

            with ui.column().classes("gap-1"):
                ui.label("Gerät").classes("text-lg font-semibold mt-2")

                with ui.column().classes("gap-2"):
                    ui.label("Wähle aus zu welchem Gerät dieser Sensor gehören soll.")
                    devices = Device.get_all()
                    device_options = {device.id: device.name for device in devices}

                    with ui.row().classes("items-center"):
                        self.device_select = ui.select(value=self.sensor.device.id, options=device_options, with_input=True).classes("min-w-[120px]")
                        ui.button("Speichern", on_click=self.change_device).props("flat")

            ui.row().classes("mt-4 mb-2 h-px w-full bg-gray-200 border-0")

            with ui.column().classes("gap-4"):
                ui.label("Simulation").classes("text-lg font-semibold mt-2")

                with ui.row().classes("gap-10"):
                    with ui.column().classes("gap-0"):
                        ui.label("Basiswert").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{self.sensor.base_value}").classes("text-md")
                    with ui.column().classes("gap-0"):
                        ui.label("Variationsbereich").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{self.sensor.variation_range}").classes("text-md")
                    with ui.column().classes("gap-0"):
                        ui.label("Änderungsrate +/-").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{self.sensor.change_rate}").classes("text-md")
                    with ui.column().classes("gap-0"):
                        ui.label("Interval [s]").classes("text-sm font-semibold text-gray-500")
                        ui.label(f"{self.sensor.change_rate}").classes("text-md")

    
    def change_device(self):
        # Check if container is active
        if self._check_if_container_is_active(self.sensor.device):
            return
        
        # Check if container of new device is active
        new_device = Device.get_by_id(self.device_select.value)
        if self._check_if_container_is_active(new_device):
            return

        self.sensor.device_id = self.device_select.value
        Sensor.session.commit()
        
        ui.notify(f"Änderung erfolgreich gespeichert.", type="positive")

    def _check_if_container_is_active(self, device):
        container = device.container
        if container is not None and container.is_active:
            ui.notify(f"Änderung kann nicht gespeichert werden während Container '{container.name}' aktiv ist.", type="negative")
            return True
        return False
        