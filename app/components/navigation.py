from nicegui import ui

def setup():
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.label("IoT Daten Simulator").classes('text-md font-semibold uppercase')
        with ui.row():
            ui.link('Container', '/').classes('text-white !no-underline')
            ui.link('Sensoren', '/sensoren').classes('text-white !no-underline')
            ui.link('Geräte', '/geraete').classes('text-white !no-underline')
        ui.button(icon='menu').props('flat color=white')