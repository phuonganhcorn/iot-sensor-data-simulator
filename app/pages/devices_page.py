from nicegui import ui
from components.navigation import Navigation
from model.database import Device, Sensor
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
        # with ui.row().classes('fixed inset-0 bg-black/50 z-10') as container:
        with ui.dialog(value=True) as dialog, ui.card().classes('w-full h-[70vh]'):
            with ui.stepper().props('vertical').classes('w-full h-full') as stepper:
                with ui.step('Allgemein'):
                    with ui.column():
                        ui.label(
                            'Gibt den Namen des Geräts an. Das Gerät kann dann mit diesem Namen im IoT Hub gefunden werden.')
                        name_input = ui.input('Name (Device ID)')
                    with ui.stepper_navigation():
                        ui.button('Abbrechen', on_click=lambda: dialog.close()).props(
                            'flat')
                        ui.button('Weiter', on_click=stepper.next)
                with ui.step('Simulationswerte'):
                    sensors = Sensor.get_all()
                    print(sensors)
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

    def create_device(self):
        if len(self.devices) == 0:
            self.list_container.clear()

        name = "dev001234567"

        response = self.iot_hub_helper.create_device(device_id=name)

        if not response.success:
            ui.notify(response.message, type='negative')
            return

        ui.notify(response.message, type='positive')

        new_device = Device.add(response.object)
        self.devices.append(new_device)

        with self.list_container:
            DeviceItem(device=new_device,
                       delete_callback=self.delete_button_handler)

        self.update_stats()

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

        Device.delete(device)

        index = self.devices.index(device)

        del self.devices[index]
        self.list_container.remove(index)

        self.update_stats()

        if len(self.devices) == 0:
            self.print_no_devices()
