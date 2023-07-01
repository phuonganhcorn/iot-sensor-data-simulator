from nicegui import ui
from components.navigation import setup as setup_navigation
from model.sensor import Sensor
from components.sensor_item import SensorItem


class SensorsPage():

    def __init__(self):
        self.sensors = []
        self.update_stats()
        self.setup_page()

    def setup_page(self):
        setup_navigation()
        ui.query('.nicegui-content').classes('p-8')
        ui.label("Sensoren").classes('text-2xl font-bold')

        self.setup_menu_bar()
        self.setup_list()

    def setup_menu_bar(self):
        with ui.row().classes('px-4 w-full flex items-center justify-between h-20 bg-gray-200 rounded-lg shadow-md'):
            ui.button('Neuen Sensor erstellen',
                      on_click=lambda: self.create_sensor()).classes('')

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

    def create_sensor(self):
        if len(self.sensors) == 0:
            self.list_container.clear()

        new_sensor = Sensor(id=len(self.sensors) + 1)
        self.sensors.append(new_sensor)

        with self.list_container:
            SensorItem(sensor=new_sensor,
                       delete_callback=self.delete_button_handler)

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

        if not sensor.delete():
            return

        index = self.sensors.index(sensor)

        del self.sensors[index]
        self.list_container.remove(index)

        self.update_stats()

        if len(self.sensors) == 0:
            self.print_no_sensors()
