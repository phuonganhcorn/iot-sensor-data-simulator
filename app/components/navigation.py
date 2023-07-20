from nicegui import ui
from model.option import Option
from utils.iot_hub_helper import IoTHubHelper


class Navigation():
    '''Navigation component for displaying the navigation bar'''

    def __init__(self):
        '''Initializes the navigation bar'''
        self.host_name = IoTHubHelper.get_host_name()
        self.setup()

    def setup(self):
        '''Sets up the UI elements of the navigation bar'''
        with ui.header(elevated=True).style('background-color: #3874c8').classes('justify-between z-50 lg:items-center'):
            # Title
            ui.label("IoT Telemetrie Simulator").classes(
                'text-md font-semibold uppercase')
            # Navigation list
            with ui.row().classes('mx-auto gap-6 order-2 sm:order-[0] lg:mx-0 lg:gap-12'):
                ui.link('Container', '/').classes('text-white !no-underline')
                ui.link('Geräte', '/geraete').classes('text-white !no-underline')
                ui.link('Sensoren', '/sensoren').classes('text-white !no-underline')
            # Settings
            with ui.row().classes('flex-col gap-0 items-center lg:flex-row lg:gap-4 lg:divide-x lg:divide-white/50'):
                # Display IoT Hub host name
                host_name = self.host_name if self.host_name else 'Nicht Konfiguriert'
                self.host_name_label = ui.label(f'IoT Hub: {host_name}').classes('text-white')
                
                # Demo mode switch
                demo_switch = ui.switch('Demo-Modus', on_change=self.demo_switch_handler).classes('text-white')
                with demo_switch:
                    ui.tooltip('Wenn aktiviert, werden keine Nachrichten an IoT Hub oder MQTT-Broker gesendet.')
                demo_switch.value = Option.get_boolean('demo_mode')
                ui.query('.q-toggle__inner--falsy').classes('!text-white/50')

    def demo_switch_handler(self, switch):
        '''Handles the switch change event of the demo mode switch'''
        Option.set_value('demo_mode', switch.value)
        
        if switch.value:
            ui.query('.q-toggle__inner--truthy').classes('!text-white')
            ui.query('.q-toggle__inner--falsy').classes(remove='!text-white/50')
        else:
            ui.query('.q-toggle__inner--falsy').classes('!text-white/50')
            ui.query('.q-toggle__inner--truthy').classes(remove='!text-white')
