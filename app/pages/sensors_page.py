from nicegui import ui
from components.navigation import Navigation
from components.sensor_item import SensorItem
from model.device import Device
from model.sensor import Sensor
from constants.units import *
from components.sensor_error_cards import AnomalyCard


class SensorsPage():

    def __init__(self):
        self.sensors = Sensor.get_all()
        self.list_items = []
        self.sensor_error_card = None
        self.update_stats()
        self.setup_page()

    def setup_page(self):
        Navigation()
        ui.query('.nicegui-content').classes('p-8')
        ui.label("Sensoren").classes('text-2xl font-bold')

        self.setup_menu_bar()
        self.setup_list()

    def setup_menu_bar(self):
        with ui.row().classes('px-4 w-full flex items-center justify-between h-20 bg-gray-200 rounded-lg shadow-md'):
            ui.button('Neuen Sensor erstellen',
                      on_click=lambda: self.show_create_sensor_dialog()).classes('')

            with ui.row():
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Gesamt:').classes('text-sm font-medium')
                    ui.label().classes('text-sm').bind_text(self, 'sensors_count')

            with ui.row():
                self.filter_input = ui.input(
                    placeholder='Filter', on_change=self.filter_handler).classes('w-44')

    def setup_list(self):
        self.list_container = ui.column().classes(
            'relative grid w-full gap-0 divide-y')

        with self.list_container:
            headings = [{'name': 'ID', 'classes': 'w-[30px]'},
                        {'name': 'Name', 'classes': 'w-[130px]'},
                        {'name': 'Typ', 'classes': 'w-[130px]'},
                        {'name': 'Gerät', 'classes': 'w-[130px]'},
                        {'name': 'Fehlertyp', 'classes': 'w-[130px]'}]

            with ui.row().classes('px-3 py-6 flex gap-6 items-center w-full'):
                for heading in headings:
                    ui.label(heading['name']).classes(
                        f'font-medium {heading["classes"]}')

            if len(self.sensors) == 0:
                self.show_note('Keine Sensoren vorhanden')
            else:
                for sensor in self.sensors:
                    new_item = SensorItem(sensor=sensor,
                                          delete_callback=self.delete_button_handler)
                    self.list_items.append(new_item)

            self.setup_note_label()

    def setup_note_label(self):
        with self.list_container:
            self.note_label = ui.label().classes(
                'absolute left-1/2 top-48 self-center -translate-x-1/2')
            self.note_label.set_visibility(False)

    def filter_handler(self):
        search_text = self.filter_input.value
        results = list(filter(lambda item: search_text.lower()
                       in item.sensor.name.lower(), self.list_items))

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
        self.list_container.classes(add='divide-y-0', remove='divide-y')
        self.note_label.text = message
        self.note_label.set_visibility(True)

    def hide_note(self):
        self.list_container.classes(add='divide-y', remove='divide-y-0')
        self.note_label.set_visibility(False)

    def update_stats(self):
        self.sensors_count = len(self.sensors)

    def show_create_sensor_dialog(self):
        self.sensor_error_card = None
        device_select = None

        with ui.row().classes('fixed inset-0 bg-black/50 z-10') as container:

            with ui.stepper().props('vertical').classes('absolute left-1/2 top-[15vh] w-[70%] h-[70vh] bg-white -translate-x-1/2 overflow-auto z-50') as stepper:
                with ui.step('Allgemein'):
                    with ui.grid(columns=3):
                        name_input = ui.input('Name*')

                        units = {}
                        for index, unit in enumerate(UNITS):
                            units[index] = f"{unit['name']} [{unit['unit_abbreviation']}]"

                        unit_input = ui.select(units, value=0, label='Einheit')
                    with ui.stepper_navigation():
                        ui.button('Abbrechen', on_click=lambda: container.set_visibility(False)).props(
                            'flat')
                        ui.button('Weiter', on_click=lambda: self.check_general_step_input(
                            stepper, name_input))
                with ui.step('Simulationswerte'):
                    with ui.grid(columns=3).classes('w-full'):
                        base_value_input = ui.number(
                            label='Basiswert', value=25.00, format='%.2f')
                        variation_range_input = ui.number(label='Variationsbereich',
                                                          value=5.00, min=0, format='%.2f')
                        with ui.number(label='Änderungsrate +/-', value=0.5, min=0, max=10) as input:
                            change_rate_input = input
                            ui.tooltip(
                                'Die Änderungsrate gibt an, wie stark sich ein Wert pro Interval bezogen auf den vorherigen Wert maximal ändern kann.').classes('mx-4')
                        interval_input = ui.number(
                            label='Interval [s]', value=10, min=0, max=3600)
                    with ui.stepper_navigation():
                        ui.button('Zurück', on_click=stepper.previous).props(
                            'flat')
                        ui.button('Weiter', on_click=stepper.next)
                with ui.step('Fehlersimulation'):
                    ui.label(
                        'Simuliere Fehler, die bei einer Messung auftreten können.')

                    error_types = {0: 'Kein Fehler',
                                   1: 'Einmalige Anomalien', }

                    error_type_input = ui.select(error_types, value=0, label='Fehlertyp',
                                                 on_change=lambda e: self.error_type_input_handler(error_container, e.value))
                    error_container = ui.row()

                    with ui.stepper_navigation():
                        ui.button('Zurück', on_click=stepper.previous).props(
                            'flat')
                        ui.button('Weiter', on_click=stepper.next)
                with ui.step('Gerätezuordnung'):
                    devices = Device.get_all()
                    devices_options = {
                        device.id: device.name for device in devices}
                    if len(devices) > 0:
                        with ui.column():
                            ui.label(
                                'Wähle das Gerät aus zu dem der Sensor hinzugefügt werden soll (Optional).')
                            device_select = ui.select(
                                options=devices_options, with_input=True).classes('w-40')
                    else:
                        ui.label(
                            'Es sind aktuell noch keine Geräte vorhanden. Du kannst danach zur Geräte-Seite wechseln, ein Gerät erstellen und diesen Sensor dann hinzufügen.')
                    with ui.stepper_navigation():
                        ui.button('Zurück', on_click=stepper.previous).props(
                            'flat')
                        ui.button('Weiter', on_click=stepper.next)
                with ui.step('Abschließen'):
                    ui.label(
                        'Erstelle einen neuen Sensor mit den angegebenen Werten.')
                    with ui.stepper_navigation():
                        ui.button('Zurück', on_click=stepper.previous).props(
                            'flat')
                        ui.button('Sensor erstellen', on_click=lambda: self.create_sensor(
                            container, name_input, unit_input, base_value_input, variation_range_input, change_rate_input, interval_input, device_select))

    def error_type_input_handler(self, container, value):
        container.clear()

        if value == 0:
            self.sensor_error_card = None
        elif value == 1:
            with container:
                self.sensor_error_card = AnomalyCard()

    def check_general_step_input(self, stepper, name_input):
        if name_input.value == '':
            ui.notify('Bitte gib einen Namen für den Sensor an.',
                      type='warning')
            return

        stepper.next()

    def create_sensor(self, dialog, name_input, unit_input, base_value_input, variation_range_input, change_rate_input, interval_input, device_select):
        if len(self.sensors) == 0:
            self.list_container.clear()

        name = name_input.value
        unit = unit_input.value
        base_value = base_value_input.value
        variation_range = variation_range_input.value
        change_rate = change_rate_input.value
        interval = interval_input.value
        error_definition = None if self.sensor_error_card is None else self.sensor_error_card.get_values(
            json_dump=True)
        device_id = None if device_select is None else device_select.value

        new_sensor = Sensor.add(name=name, base_value=base_value, unit=unit, variation_range=variation_range,
                                change_rate=change_rate, interval=interval, error_definition=error_definition, device_id=device_id)
        self.sensors.append(new_sensor)

        with self.list_container:
            SensorItem(sensor=new_sensor,
                       delete_callback=self.delete_button_handler)

        dialog.set_visibility(False)
        ui.notify('Sensor wurde erstellt', type='positive')

        self.update_stats()

    def delete_button_handler(self, sensor):
        with ui.dialog(value=True) as dialog, ui.card().classes('items-center'):
            ui.label('Möchtest du den Sensor wirklich löschen?')
            with ui.row():
                ui.button('Abbrechen', on_click=dialog.close).props('flat')
                ui.button('Löschen', on_click=lambda d=dialog: self.delete_handler(
                    d, sensor)).classes('text-white bg-red')

    def delete_handler(self, dialog, sensor):
        dialog.close()

        # TODO: Check if container is running and stop it

        sensor.delete()

        index = self.sensors.index(sensor)

        del self.sensors[index]
        self.list_container.remove(index)

        self.update_stats()

        if len(self.sensors) == 0:
            self.show_note('Keine Sensoren vorhanden')
