from nicegui import ui
from components.navigation import Navigation
from model.device import Device
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
                      on_click=lambda: self.create_device()).classes('')

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

    def create_device(self):
        if len(self.devices) == 0:
            self.list_container.clear()

        new_device = Device.add(name="Mein Gerät", connection_string="hier.mein.string")
        self.devices.append(new_device)

        with self.list_container:
            DeviceItem(device=new_device,
                       delete_callback=self.delete_button_handler)

        self.update_stats()

    def delete_button_handler(self, device):
        with ui.dialog(value=True) as dialog, ui.card().classes('items-center'):
            ui.label('Möchtest du die Maschine wirklich löschen?')
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
