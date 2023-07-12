from nicegui import ui
from model.option import Option


class Navigation():

    def __init__(self):
        self.host_name = None
        self.query_connection_string()
        self.setup()

    def setup(self):
        with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between z-50'):
            ui.label("IoT Telemetrie Simulator").classes(
                'text-md font-semibold uppercase')
            with ui.row().classes('gap-12'):
                ui.link('Container', '/').classes('text-white !no-underline')
                ui.link('Geräte', '/geraete').classes('text-white !no-underline')
                ui.link('Sensoren', '/sensoren').classes('text-white !no-underline')
            with ui.row().classes('items-center divide-x divide-white/50'):
                self.host_name_label = ui.label(f'Host: {self.host_name}').classes('text-white')
                demo_switch = ui.switch('Demo-Modus', on_change=self.switch_handler).classes('text-white')
                demo_switch.value = Option.get_boolean('demo_mode')
                ui.query('.q-toggle__inner--falsy').classes('!text-white/50')

    def query_connection_string(self):
        host_name = Option.get_value('host_name')
        
        if host_name is None:
            with ui.row().classes('fixed inset-0 flex justify-center items-center bg-black/50 z-[100]') as container:
                with ui.column().classes('bg-white rounded-lg shadow-lg p-8'):
                    ui.label('Willkommen zum IoT-Telemetrie-Simulator').classes('text-xl font-bold')
                    ui.label('Bitte gib den Hostnamen deines IoT Hubs ein, um loszulegen.')
                    host_name_input = ui.input('Hostname')
                    ui.button('Loslegen', on_click=lambda: self.save_host_name_string(container, host_name_input))
            return
        
        self.host_name = host_name

    def save_host_name_string(self, container, host_name_input):
        if host_name_input.value is None or host_name_input.value == '':
            ui.notify('Bitte gib einen Hostnamen ein.', type='warning')
            return
        
        self.host_name = host_name_input.value
        self.host_name_label.set_text(f'Host: {self.host_name}')
        Option.set_option('host_name', host_name_input.value)
        container.set_visibility(False)
        ui.notify('Hostname erfolgreich gespeichert.', type='positive')

    def switch_handler(self, switch):
        Option.set_option('demo_mode', switch.value)
        
        if switch.value:
            ui.query('.q-toggle__inner--truthy').classes('!text-white')
            ui.query('.q-toggle__inner--falsy').classes(remove='!text-white/50')
        else:
            ui.query('.q-toggle__inner--falsy').classes('!text-white/50')
            ui.query('.q-toggle__inner--truthy').classes(remove='!text-white')