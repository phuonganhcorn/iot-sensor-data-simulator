from nicegui import ui
from components.navigation import Navigation
from model.device import Device
from model.sensor import Sensor
from components.device_item import DeviceItem


class DevicesPage:

    def __init__(self, iot_hub_helper):
        self.iot_hub_helper = iot_hub_helper
        self.iot_hub_devices = self.iot_hub_helper.get_devices()
        self.devices = Device.get_all()
        self.update_stats()
        self.setup_page()

    def setup_page(self):
        Navigation()
        ui.query('.nicegui-content').classes('p-8')
        ui.label("Geräte").classes('text-2xl font-bold')

        self.setup_menu_bar()
        self.setup_list()

    def setup_menu_bar(self):
        with ui.row().classes('px-4 w-full flex items-center justify-between h-20 bg-gray-200 rounded-lg shadow-md'):
            ui.button('Neues Gerät erstellen',
                      on_click=lambda: self.show_create_device_dialog()).classes('')

            with ui.row():
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Gesamt:').classes('text-sm font-medium')
                    ui.label().classes('text-sm').bind_text(self, 'devices_count')

            with ui.row():
                ui.input(placeholder='Filter').classes('w-44')
                ui.select({1: "Alle", 2: "Aktiv", 3: "Inaktiv"},
                          value=1).classes('w-24')

    def setup_list(self):
        self.list_container = ui.column().classes('w-full gap-0 divide-y')

        with self.list_container:
            if len(self.devices) == 0:
                self.print_no_devices()
            else:
                for device in self.devices:
                    DeviceItem(device=device,
                               delete_callback=self.delete_button_handler)

    def print_no_devices(self):
        self.list_container.classes('justify-center')
        with self.list_container:
            with ui.column().classes('self-center mt-48'):
                ui.label('Keine Geräte vorhanden')

    def update_stats(self):
        self.devices_count = len(self.devices)

    def show_create_device_dialog(self):
        with ui.dialog(value=True) as dialog, ui.card().classes('w-full min-h-[500px]'):
            with ui.stepper().props('vertical').classes('w-full h-full') as stepper:
                with ui.step('Allgemein'):
                    with ui.column():
                        ui.label(
                            'Gibt den Namen des Geräts an. Das Gerät kann dann mit diesem Namen im IoT Hub gefunden werden.')
                        name_input = ui.input('Name (Device ID)')
                    with ui.stepper_navigation():
                        ui.button('Abbrechen', on_click=lambda: dialog.close()).props(
                            'flat')
                        ui.button('Weiter', on_click=lambda: self.check_device_name_input(
                            stepper, name_input))
                with ui.step('Sensoren'):
                    sensors = Sensor.get_all_unassigned()

                    if len(sensors) == 0:
                        ui.label(
                            "Es sind keine freien Sensoren verfügbar. Erstelle zuerst einen neuen Sensor.")

                        ui.button('Abbrechen', on_click=lambda: dialog.close()).props(
                            'flat')
                    else:
                        sensors_options = {
                            sensor.id: sensor.name for sensor in sensors}

                        ui.label(
                            "Wähle die Sensoren aus, die dem Gerät zugeordnet werden sollen. Mehrfachauswahl möglich. Später können keine weiteren Sensoren hinzugefügt werden.")
                        sensors_input = ui.select(sensors_options, multiple=True, label='Sensoren auswählen').props(
                            'use-chips').classes('w-64')

                        with ui.stepper_navigation():
                            ui.button('Zurück', on_click=stepper.previous).props(
                                'flat')
                            ui.button('Erstellen', on_click=lambda: self.complete_device_creation(
                                dialog, name_input, sensors_input))

    def check_device_name_input(self, stepper, name_input):
        if name_input.value == '':
            ui.notify('Bitte gib einen Namen für das Gerät an.',
                      type='negative')
            return

        stepper.next()

    def complete_device_creation(self, dialog, name_input, sensors_input):
        if len(sensors_input.value) == 0:
            ui.notify('Bitte wähle mindestens einen Sensor aus.',
                      type='warning')
            return

        self.create_device(name_input.value, sensors_input.value)
        dialog.close()

    def create_device(self, name, sensor_ids):
        if len(self.devices) == 0:
            self.list_container.clear()

        device_id = self.replace_special_characters(name)
        response = self.iot_hub_helper.create_device(device_id=device_id)

        if not response.success:
            ui.notify(response.message, type='negative')
            return

        ui.notify(response.message, type='positive')

        new_device = Device.store(response.object, sensor_ids=sensor_ids)
        self.devices.append(new_device)

        self.add_device_to_list(device=new_device)
        self.update_stats()

    def add_device_to_list(self, device):
        with self.list_container:
            DeviceItem(device=device,
                       delete_callback=self.delete_button_handler)

    def delete_button_handler(self, device):
        with ui.dialog(value=True) as dialog, ui.card().classes('items-center'):
            ui.label('Möchtest du das Gerät wirklich löschen?')
            with ui.row():
                ui.button('Abbrechen', on_click=dialog.close).props('flat')
                ui.button('Löschen', on_click=lambda d=dialog: self.delete_handler(
                    d, device)).classes('text-white bg-red')

    def delete_handler(self, dialog, device):
        dialog.close()

        # TODO: Check if container is running and stop it

        self.iot_hub_helper.delete_device(
            device_id=device.name, etag=device.etag)
        Device.delete(device)

        index = self.devices.index(device)

        del self.devices[index]
        self.list_container.remove(index)

        self.update_stats()

        if len(self.devices) == 0:
            self.print_no_devices()

    def replace_special_characters(self, value):
        replacements = {
            ' ': '_',
            'Ä': 'AE',
            'Ö': 'OE',
            'Ü': 'UE',
            'ä': 'ae',
            'ö': 'oe',
            'ü': 'ue',
            'ß': 'ss'
        }

        for old_char, new_char in replacements.items():
            value = value.replace(old_char, new_char)

        return value