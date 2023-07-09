from nicegui import ui
from model.device import Device
from components.live_view_dialog import LiveViewDialog
from components.logs_dialog import LogsDialog
from components.sensor_selection import SensorSelection
from components.chart import Chart
from tkinter import filedialog
import json


class ContainerCard():
    def __init__(self, wrapper, container, start_callback=None, stop_callback=None, delete_callback=None, live_view_callback=None):
        self.wrapper = wrapper
        self.container = container
        self.card = None
        self.visible = True
        self.sensor_count = 0
        self.generated_container_data = None
        self.logs_dialog = LogsDialog(wrapper)
        container.log = self.logs_dialog.log
        self.active_dot = None
        self.setup(wrapper, container, start_callback=start_callback,
                   stop_callback=stop_callback, delete_callback=delete_callback, live_view_callback=live_view_callback)

    def setup(self, wrapper, container, start_callback=None, stop_callback=None, delete_callback=None, live_view_callback=None):
        self.update_sensor_count()

        with ui.card().tight().bind_visibility(self, 'visible') as card:
            self.card = card
            with ui.card_section().classes('min-h-[260px]'):
                with ui.row().classes('pb-2 w-full justify-between items-center border-b border-gray-200'):
                    ui.label(container.name).classes('text-xl font-semibold')
                    with ui.row().classes('gap-0.5'):
                        ui.button(icon='insert_chart_outlined', on_click=lambda: live_view_callback(
                            container)).props('flat').classes('px-2 text-black')
                        with ui.button(icon='more_vert').props('flat').classes('px-2 text-black'):
                            with ui.menu().props(remove='no-parent-event'):
                                ui.menu_item('Details anzeigen', lambda: self.show_details_dialog()).classes(
                                    'flex items-center')
                                ui.menu_item('Logs anzeigen', lambda: self.show_logs_dialog(container)).classes(
                                    'flex items-center')
                                ui.menu_item('Löschen', lambda w=wrapper, c=container, callback=delete_callback: self.show_delete_dialog(
                                    w, c, callback)).classes('text-red-500').classes('flex items-center')
                with ui.column().classes('py-4 gap-2'):
                    with ui.row().classes('gap-1'):
                        ui.label('Geräte:').classes('text-sm font-medium')
                        ui.label().classes('text-sm').bind_text_from(container,
                                                                     'devices', backward=lambda d: len(d))
                    with ui.row().classes('gap-1'):
                        ui.label('Sensoren:').classes('text-sm font-medium')
                        ui.label().bind_text(self, 'sensor_count').classes('text-sm')
                    with ui.row().classes('gap-1'):
                        ui.label('Gesendete Nachrichten:').classes(
                            'text-sm font-medium')
                        ui.label().classes('text-sm').bind_text(container, 'message_count')
                    with ui.row().classes('gap-1'):
                        ui.label('Startzeit:').classes('text-sm font-medium')
                        ui.label().classes('text-sm').bind_text_from(container, 'start_time',
                                                                     backward=lambda t: f'{t.strftime("%d.%m.%Y, %H:%M:%S")} Uhr' if t else '')
            with ui.card_section().classes('bg-gray-100'):
                with ui.row().classes('items-center justify-between'):
                    with ui.row().classes('gap-3 items-center'):
                        self.active_dot = ui.row().classes('h-4 w-4 rounded-full' +
                                                           (' bg-green-500' if container.is_active else ' bg-red-500'))
                        ui.label().bind_text_from(container, 'is_active',
                                                  backward=lambda is_active: f'{"Aktiv" if is_active else "Inaktiv"}')
                    with ui.row().classes('h-9 gap-0.5'):
                        with ui.row().classes('gap-0.5'):
                            ui.button(icon='play_arrow', on_click=lambda c=container: start_callback(
                                c)).props('flat').classes('px-2 text-black')
                            ui.button(icon='pause', on_click=lambda c=container: stop_callback(
                                c)).props('flat').classes('px-2 text-black')
                        ui.row().classes('w-px h-full bg-gray-300')
                        ui.button(icon='exit_to_app', on_click=lambda: self.show_export_dialog()).props('flat').classes('px-2 text-black')

    def set_active(self):
        self.active_dot.classes('bg-green-500', remove='bg-red-500')

    def set_inactive(self):
        self.active_dot.classes('bg-red-500', remove='bg-green-500')

    def update_sensor_count(self):
        self.sensor_count = 0
        for device in self.container.devices:
            self.sensor_count += len(device.sensors)

    def show_live_view_dialog(self, wrapper, container):
        LiveViewDialog(wrapper, container)

    def show_details_dialog(self):
        with self.wrapper:
            with ui.dialog(value=True) as dialog, ui.card().classes("px-6 pb-6 w-[696px] !max-w-none overflow-auto"):
                self.dialog = dialog
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(
                        f"Details - '{self.container.name}'").classes("text-xl font-semibold")
                    ui.button(icon="close", on_click=self.dialog.close).props(
                        "flat").classes("px-2 text-black")

                with ui.row().classes("w-full flex justify-between"):
                    with ui.column().classes("gap-4"):
                        ui.label("Allgemein").classes(
                            "text-lg font-semibold mt-2")
                        with ui.row().classes("gap-10"):
                            with ui.column().classes("gap-0"):
                                ui.label("ID").classes("text-sm text-gray-500")
                                ui.label(f"{self.container.id}").classes(
                                    "text-md font-medium")
                            with ui.column().classes("gap-0"):
                                ui.label("Name").classes(
                                    "text-sm text-gray-500")
                                ui.label(f"{self.container.name}").classes(
                                    "text-md font-medium")
                            with ui.column().classes("gap-0"):
                                ui.label("Standort").classes(
                                    "text-sm text-gray-500")
                                location = self.container.location
                                ui.label(f"{location if location else 'k.A.'}").classes(
                                    "text-md font-medium")
                        with ui.row().classes("gap-10"):
                            with ui.column().classes("gap-0"):
                                ui.label("Beschreibung").classes(
                                    "text-sm text-gray-500")
                                description = self.container.description
                                ui.label(f"{description if description else 'k.A.'}").classes(
                                    "text-md font-medium")
                    with ui.column().classes('pr-3 gap-1 items-end'):
                        ui.label("Status").classes("text-sm text-gray-500")
                        with ui.row().classes('gap-3 items-center'):
                            ui.row().classes(
                                f'h-4 w-4 rounded-full {"bg-green-500" if self.container.is_active else "bg-red-500"}')
                            ui.label().bind_text_from(self.container, 'is_active',
                                                      backward=lambda is_active: f'{"Aktiv" if is_active else "Inaktiv"}')

                with ui.column().classes("w-full gap-4"):
                    ui.label("Geräte und Sensoren").classes(
                        "text-lg font-semibold mt-2")

                    with ui.row().classes("gap-x-28"):
                        with ui.column().classes('gap-0'):
                            ui.label("Ansicht").classes(
                                "text-sm text-gray-500")
                            data = self.create_tree_data(
                                self.container.devices)
                            with ui.row() as row:
                                self.tree_container = row
                                ui.tree(
                                    data, label_key="id")

                        unassigned_devices = Device.get_all_unassigned()
                        with ui.column().classes('gap-0'):
                            device_options = {
                                device.id: device.name for device in unassigned_devices}

                            ui.label("Bearbeiten").classes(
                                "text-sm text-gray-500")
                            if len(unassigned_devices) > 0:
                                with ui.row().classes("items-center"):
                                    self.new_device_select = ui.select(
                                        value=unassigned_devices[0].id, options=device_options).classes("min-w-[120px]")
                                    ui.button("Hinzufügen", on_click=self.add_device_handler).props(
                                        "flat")
                            else:
                                ui.label(
                                    "Keine weiteren Geräte frei.").classes()

    def create_tree_data(self, devices):
        tree = []
        for device in devices:
            device_node = {'id': device.name, 'children': []}
            for sensor in device.sensors:
                sensor_node = {'id': sensor.name}
                device_node['children'].append(sensor_node)
            tree.append(device_node)
        return tree
    
    def show_export_dialog(self):
        if self.container.is_active:
            ui.notify("Bitte deaktiviere den Container, um einen Massenexport ausführen zu können.", type="warning")
            return

        with self.wrapper:
            with ui.dialog(value=True) as dialog, ui.card().classes("px-6 pb-6 w-[696px] !max-w-none overflow-auto"):
                self.dialog = dialog
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(
                        f"Massenexport - '{self.container.name}'").classes("text-xl font-semibold")
                    ui.button(icon="close", on_click=dialog.close).props(
                        "flat").classes("px-2 text-black")
                
                ui.label("Führe einen Massenexport aus und wähle aus, wie die Daten exportiert werden sollen.")

                with ui.row().classes("gap-6 items-center"):
                    self.bulk_amount_input = ui.number(label="Werte pro Sensor", min=1, max=1000, step=1, value=10).classes('w-24')
                    ui.button("Daten generieren", on_click=self.generate_bulk_data).props("flat")

                ui.label("Vorschau").classes("text-lg font-semibold mt-2")

                self.sensor_selection = SensorSelection(container=self.container, sensor_select_callback=self.update_export_preview)
                self.chart = Chart()

                self.export_button = ui.button("Exportieren", on_click=self.save_bulk_to_file).classes("mt-8 self-end")
                self.export_button.set_enabled(False)

    def generate_bulk_data(self):
        container_data = {}
        bulk_amount = int(self.bulk_amount_input.value)

        for device in self.container.devices:
            device_data = {}
            for sensor in device.sensors:
                data = sensor.start_bulk_simulation(bulk_amount)
                device_data[sensor.name] = data
            container_data[device.name] = device_data
        
        self.generated_container_data = container_data

        self.show_export_preview(container_data)
        self.export_button.set_enabled(True)

    def show_export_preview(self, container_data):
        selected_sensor = self.sensor_selection.get_sensor()
        time_series_data = container_data[selected_sensor.device.name][selected_sensor.name]
        self.chart.show(time_series_data=time_series_data)
        
    def update_export_preview(self, sensor):
        if self.generated_container_data is None:
            return
        elif sensor is None:
            self.chart.empty()
            return
        
        time_series_data = self.generated_container_data[sensor.device.name][sensor.name]
        self.chart.update(sensor, time_series_data)

    def save_bulk_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])

        if file_path.endswith(".json"):
            with open(file_path, "w") as json_file:
                json.dump(self.container_data, json_file, indent=4)
            ui.notify(f"Daten erfolgreich exportiert", type="positive")

        self.dialog.close()

    def add_device_handler(self):
        if self.container.is_active:
            ui.notify(
                f"Hinzufügen nicht möglich während dieser Container aktiv ist.", type="negative")
            return

        device_id = self.new_device_select.value
        device = Device.get_by_id(device_id)
        device.container_id = self.container.id
        Device.session.commit()

        ui.notify(f"Gerät erfolgreich hinzugefügt.", type="positive")
        self.update_sensor_count()

        # Remove device from select
        del self.new_device_select.options[device_id]
        self.new_device_select.update()
        self.new_device_select.value = None

        # Show device in tree
        new_data = self.create_tree_data(self.container.devices)
        self.tree_container.clear()
        with self.tree_container:
            ui.tree(new_data, label_key="id")

    def show_logs_dialog(self, container):
        if not container.is_active:
            ui.notify('Container ist nicht aktiv', type='warning')
            return

        self.logs_dialog.show()

    def show_delete_dialog(self, wrapper, container, delete_callback):
        with wrapper:
            with ui.dialog(value=True) as dialog, ui.card().classes('items-center'):
                ui.label('Soll der Container wirklich gelöscht werden?')
                with ui.row():
                    ui.button('Abbrechen', on_click=dialog.close).props('flat')
                    ui.button('Löschen', on_click=lambda: delete_callback(
                        container, dialog)).classes('text-white bg-red')
