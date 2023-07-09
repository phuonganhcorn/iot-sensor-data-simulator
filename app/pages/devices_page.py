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
        self.list_items = []
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
                self.filter_input = ui.input(
                    placeholder='Filter', on_change=self.filter_handler).classes('w-44')

    def setup_list(self):
        self.list_container = ui.column().classes('relative w-full gap-0 divide-y')

        with self.list_container:
            headings = [{'name': 'ID', 'classes': 'w-[30px]'},
                        {'name': 'Name', 'classes': 'w-[130px]'},
                        {'name': 'Container', 'classes': 'w-[130px]'},
                        {'name': 'Sensoren', 'classes': 'w-[60px]'}]

            with ui.row().classes('px-3 py-6 flex gap-6 items-center w-full'):
                for heading in headings:
                    ui.label(heading['name']).classes(
                        f'font-medium {heading["classes"]}')

            if len(self.devices) == 0:
                self.show_note('Keine Geräte vorhanden')
            else:
                for device in self.devices:
                    new_item = DeviceItem(device=device,
                                          delete_callback=self.delete_button_handler)
                    self.list_items.append(new_item)

            self.setup_note_label()

    def setup_note_label(self):
        with self.list_container:
            self.note_label = ui.label().classes(
                'absolute left-1/2 top-48 self-center -translate-x-1/2 !border-t-0')
            self.note_label.set_visibility(False)

    def filter_handler(self):
        search_text = self.filter_input.value
        results = list(filter(lambda item: search_text.lower()
                       in item.device.name.lower(), self.list_items))

        for item in self.list_items:
            item.visible = item in results

        if len(results) == 0:
            self.show_note('Keine Treffer')
        else:
            self.hide_note()

        if len(results) == 1:
            self.list_container.classes(add='divide-y-0', remove='divide-y')
        else:
            self.list_container.classes(add='divide-y', remove='divide-y-0')

    def show_note(self, message):
        self.note_label.text = message
        self.note_label.set_visibility(True)

    def hide_note(self):
        self.note_label.set_visibility(False)

    def update_stats(self):
        self.devices_count = len(self.devices)

    def show_create_device_dialog(self):
        with ui.dialog(value=True) as dialog, ui.card().classes('relative w-[696px] min-h-[500px]'):
            ui.button(icon="close", on_click=dialog.close).props(
                    "flat").classes("absolute top-6 right-6 px-2 text-black z-10")

            with ui.stepper().props('vertical') as stepper:
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
            new_item = DeviceItem(device=device,
                                  delete_callback=self.delete_button_handler)
            self.list_items.append(new_item)

    def delete_button_handler(self, device):
        with ui.dialog(value=True) as dialog, ui.card().classes('items-center'):
            ui.label(
                f"Möchtest du das Gerät '{device.name}' wirklich löschen?")
            with ui.row():
                ui.button('Abbrechen', on_click=dialog.close).props('flat')
                ui.button('Löschen', on_click=lambda d=dialog: self.delete_handler(
                    d, device)).classes('text-white bg-red')

    def delete_handler(self, dialog, device):
        dialog.close()

        # Check if container is active
        if device.container_id is not None and device.container.is_active:
            ui.notify(f"Löschen nicht möglich während Container '{device.container.name}' aktiv ist", type="warning")
            return

        self.iot_hub_helper.delete_device(
            device_id=device.name, etag=device.etag)
        device.delete()

        index = self.devices.index(device)
        # Increment due to headings row
        self.list_container.remove(self.list_items[index].item)
        del self.devices[index]
        del self.list_items[index]

        ui.notify(
            f"Gerät '{device.name}' erfolgreich gelöscht", type="positive")
        self.update_stats()

        if len(self.devices) == 0:
            self.show_note('Keine Geräte vorhanden')

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
