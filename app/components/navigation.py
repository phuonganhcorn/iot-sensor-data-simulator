from nicegui import ui


class Navigation():

    def __init__(self):
        self.setup()

    def setup(self):
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
            ui.label("IoT Telemetrie Simulator").classes(
                'text-md font-semibold uppercase')
            with ui.row().classes('gap-12'):
                ui.link('Container', '/').classes('text-white !no-underline')
                ui.link('Sensoren', '/sensoren').classes('text-white !no-underline')
                ui.link('Maschinen', '/maschinen').classes('text-white !no-underline')
            ui.row()