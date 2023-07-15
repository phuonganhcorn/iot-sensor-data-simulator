from nicegui import ui
from model.option import Option
import re
import os


class Navigation():

    def __init__(self):
        self.host_name = None
        self.setup()

    def setup(self):
        with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between z-50 lg:items-center'):
            ui.label("IoT Telemetrie Simulator").classes(
                'text-md font-semibold uppercase')
            with ui.row().classes('mx-auto gap-6 order-2 sm:order-[0] lg:mx-0 lg:gap-12'):
                ui.link('Container', '/').classes('text-white !no-underline')
                ui.link('Geräte', '/geraete').classes('text-white !no-underline')
                ui.link('Sensoren', '/sensoren').classes('text-white !no-underline')
            with ui.row().classes('flex-col gap-0 items-center lg:flex-row lg:gap-4 lg:divide-x lg:divide-white/50'):
                self.host_name_label = ui.label(f'Host: {self._get_host_name()}').classes('text-white')
                demo_switch = ui.switch('Demo-Modus', on_change=self.switch_handler).classes('text-white')
                demo_switch.value = Option.get_boolean('demo_mode')
                ui.query('.q-toggle__inner--falsy').classes('!text-white/50')

    def _query_connection_string(self):
        connection_string = Option.get_value('iot_hub_connection_string')
        
        if connection_string is None:
            with ui.row().classes('fixed inset-0 flex justify-center items-center bg-black/50 z-[100]') as container:
                with ui.column().classes('bg-white rounded-lg shadow-lg p-8'):
                    ui.label('Willkommen zum IoT-Telemetrie-Simulator').classes('text-xl font-bold')
                    ui.label('Gib den Hostnamen deines IoT Hubs ein, um loszulegen.')
                    host_name_input = ui.input('Hostname')
                    ui.label("Gib den Gemeinsamen Zugangsschlüssel für die 'iothubowner'-Gruppe an.")
                    shared_access_key_input = ui.input('Primärer Schlüssel').classes('w-full')
                    ui.button('Loslegen', on_click=lambda: self._save_host_name_string(container, host_name_input, shared_access_key_input))
            return
        
        self.host_name = self._get_host_name()

    def _save_host_name_string(self, container, host_name_input, shared_access_key_input):
        if host_name_input.value is None or host_name_input.value == '':
            ui.notify('Bitte gib einen Hostnamen ein.', type='warning')
            return
        elif shared_access_key_input.value is None or shared_access_key_input.value == '':
            ui.notify('Bitte gib einen Primären Schlüssel ein.', type='warning')
            return
        
        self.host_name = host_name_input.value
        self.host_name_label.set_text(f'Host: {self.host_name}')
        connection_string = f'HostName={self.host_name}.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey={shared_access_key_input.value}'
        Option.set_value('iot_hub_connection_string', connection_string)
        container.set_visibility(False)
        ui.notify('Zugangsdaten erfolgreich gespeichert.', type='positive')

    def switch_handler(self, switch):
        Option.set_value('demo_mode', switch.value)
        
        if switch.value:
            ui.query('.q-toggle__inner--truthy').classes('!text-white')
            ui.query('.q-toggle__inner--falsy').classes(remove='!text-white/50')
        else:
            ui.query('.q-toggle__inner--falsy').classes('!text-white/50')
            ui.query('.q-toggle__inner--truthy').classes(remove='!text-white')
        
    def _get_host_name(self):
        connection_string = os.getenv("IOTHUB_CONNECTION_STRING")
        try:
            host_name = re.search('HostName=(.+?).azure-devices.net', connection_string).group(1)
        except AttributeError:
            host_name = ''
        return host_name
