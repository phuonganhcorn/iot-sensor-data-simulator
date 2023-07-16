from nicegui import ui
from model.option import Option
from utils.iot_hub_helper import IoTHubHelper


class Navigation():

    def __init__(self):
        self.host_name = IoTHubHelper.get_host_name()
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
                self.host_name_label = ui.label(f'Host: {self.host_name}').classes('text-white')
                demo_switch = ui.switch('Demo-Modus', on_change=self.switch_handler).classes('text-white')
                demo_switch.value = Option.get_boolean('demo_mode')
                ui.query('.q-toggle__inner--falsy').classes('!text-white/50')

    def switch_handler(self, switch):
        Option.set_value('demo_mode', switch.value)
        
        if switch.value:
            ui.query('.q-toggle__inner--truthy').classes('!text-white')
            ui.query('.q-toggle__inner--falsy').classes(remove='!text-white/50')
        else:
            ui.query('.q-toggle__inner--falsy').classes('!text-white/50')
            ui.query('.q-toggle__inner--truthy').classes(remove='!text-white')
