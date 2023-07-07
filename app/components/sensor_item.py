from nicegui import ui


class SensorItem:

    def __init__(self, sensor, delete_callback):
        self.sensor = sensor
        self.visible = True
        
        with ui.row().bind_visibility(self, 'visible').classes('px-3 py-6 flex justify-between items-center w-full hover:bg-gray-50'):
            with ui.row().classes('gap-12'):
                ui.label(f'{sensor.id}')
                ui.label(f'{sensor.name}')
            with ui.row():
                with ui.row().classes('gap-2'):
                    # ui.button(icon='edit').props(
                    #     'flat').classes('px-2 text-black')
                    ui.button(icon='delete', on_click=lambda s=sensor: delete_callback(s)).props(
                        'flat').classes('px-2 text-red')
