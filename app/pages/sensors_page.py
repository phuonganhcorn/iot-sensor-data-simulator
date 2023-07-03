from nicegui import ui
from components.navigation import Navigation
from components.sensor_item import SensorItem
from model.database import Sensor
from constants.units import *


class SensorsPage():

    def __init__(self):
        self.sensors = Sensor.get_all()
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
                ui.input(placeholder='Filter').classes('w-44')
                ui.select({1: "Alle", 2: "Aktiv", 3: "Inaktiv"},
                          value=1).classes('w-24')

    def setup_list(self):
        self.list_container = ui.column().classes('w-full gap-0 divide-y')

        with self.list_container:
            if len(self.sensors) == 0:
                self.print_no_sensors()
            else:
                for sensor in self.sensors:
                    SensorItem(sensor=sensor,
                               delete_callback=self.delete_button_handler)

    def print_no_sensors(self):
        self.list_container.classes('justify-center')
        with self.list_container:
            with ui.column().classes('self-center mt-48'):
                ui.label('Keine Sensoren vorhanden')

    def update_stats(self):
        self.sensors_count = len(self.sensors)

    def show_create_sensor_dialog(self):
        with ui.row().classes('fixed inset-0 bg-black/50 z-10') as container:

            with ui.stepper().props('vertical').classes('absolute left-1/2 top-[15vh] w-[70%] h-[70vh] bg-white -translate-x-1/2 z-50') as stepper:
                with ui.step('Allgemein'):
                    with ui.grid(columns=3):
                        name_input = ui.input('Name')

                        units = {}
                        for index, unit in enumerate(UNITS):
                            units[index] = f"{unit['name']} [{unit['unit_abbreviation']}]"

                        unit_input = ui.select(units, value=0, label='Einheit')
                    with ui.stepper_navigation():
                        ui.button('Abbrechen', on_click=lambda: container.set_visibility(False)).props(
                            'flat')
                        ui.button('Weiter', on_click=stepper.next)
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
                with ui.step('Abschließen'):
                    ui.label(
                        'Erstelle einen neuen Sensor mit den angegebenen Werten.')
                    with ui.stepper_navigation():
                        ui.button('Zurück', on_click=stepper.previous).props(
                            'flat')
                        ui.button('Sensor erstellen', on_click=lambda: self.create_sensor(
                            container, name_input, unit_input, base_value_input, variation_range_input, change_rate_input, interval_input))

    def create_sensor(self, dialog, name_input, unit_input, base_value_input, variation_range_input, change_rate_input, interval_input):
        if len(self.sensors) == 0:
            self.list_container.clear()

        name = name_input.value
        unit = unit_input.value
        base_value = base_value_input.value
        variation_range = variation_range_input.value
        change_rate = change_rate_input.value
        interval = interval_input.value

        new_sensor = Sensor.add(name=name, base_value=base_value,
                                unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval)
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

        Sensor.delete(sensor)

        index = self.sensors.index(sensor)

        del self.sensors[index]
        self.list_container.remove(index)

        self.update_stats()

        if len(self.sensors) == 0:
            self.print_no_sensors()
