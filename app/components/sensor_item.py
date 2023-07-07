from nicegui import ui
from constants.units import *
import json


class SensorItem:

    def __init__(self, sensor, delete_callback):
        self.sensor = sensor
        self.visible = True

        error_type = None
        if sensor.error_definition:
            error_definition = json.loads(sensor.error_definition) if sensor.error_definition else None
            error_type = error_definition['type']

        with ui.row().bind_visibility(self, 'visible').classes('px-3 py-4 flex justify-between items-center w-full hover:bg-gray-50'):
            with ui.row().classes('gap-6'):
                ui.label(f'{sensor.id}').classes('w-[30px]')
                ui.label(f'{sensor.name}').classes('w-[130px]')
                ui.label(f'{UNITS[sensor.unit]["name"]}').classes('w-[130px]')
                if error_type:
                    ui.label(f'{error_type.title()}').classes('w-[130px]')
            with ui.row():
                with ui.row().classes('gap-2'):
                    # ui.button(icon='edit').props(
                    #     'flat').classes('px-2 text-black')
                    ui.button(icon='delete', on_click=lambda s=sensor: delete_callback(s)).props(
                        'flat').classes('px-2 text-red')
