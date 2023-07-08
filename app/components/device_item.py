from nicegui import ui
from model.container import Container
from model.sensor import Sensor


class DeviceItem:

    def __init__(self, device, delete_callback):
        self.device = device
        self.visible = True

        with ui.row().bind_visibility(self, 'visible').classes('px-3 py-6 flex justify-between items-center w-full hover:bg-gray-50'):
            with ui.row().classes('gap-6'):
                ui.label(f'{device.id}').classes('w-[30px]')
                ui.label(f'{device.name}').classes('w-[130px]')
                if device.container:
                    self.container_label = ui.label(device.container.name).classes('w-[130px]')
                self.sensor_count_label = ui.label(f'{len(device.sensors)}').classes('w-[60px]')
            with ui.row().classes('gap-2'):
                ui.button(icon="info_outline", on_click=self.show_details_dialog).props(
                    "flat").classes("px-2")
                ui.button(icon='delete', on_click=lambda d=device: delete_callback(d)).props(
                    'flat').classes('px-2 text-red')

    def show_details_dialog(self):
        with ui.dialog(value=True) as dialog, ui.card().classes("w-[696px] !max-w-none px-6 pb-6"):
            self.dialog = dialog
            with ui.row().classes("w-full justify-between items-center"):
                ui.label(
                    f"Details - '{self.device.name}'").classes("text-xl font-semibold")
                ui.button(icon="close", on_click=self.dialog.close).props(
                    "flat").classes("px-2 text-black")

            with ui.row().classes("grid grid-cols-2 gap-4 mt-4"):
                with ui.column().classes("gap-4"):
                    ui.label("Allgemein").classes("text-lg font-semibold mt-2")
                    with ui.row().classes("gap-10"):
                        with ui.column().classes("gap-0"):
                            ui.label("ID").classes("text-sm text-gray-500")
                            ui.label(f"{self.device.id}").classes(
                                "text-md font-medium")
                        with ui.column().classes("gap-0"):
                            ui.label("Name").classes("text-sm text-gray-500")
                            ui.label(f"{self.device.name}").classes(
                                "text-md font-medium")

                with ui.column().classes("gap-4"):
                    ui.label("Container").classes("text-lg font-semibold mt-2")
                    with ui.column().classes("gap-2"):
                        ui.label(
                            "Wähle aus zu welchem Container dieses Gerät gehören soll.")
                        containers = Container.get_all()
                        container_options = {
                            container.id: container.name for container in containers}

                        with ui.row().classes("items-center"):
                            self.container_select = ui.select(
                                value=self.device.container.id, options=container_options, with_input=True).classes("min-w-[120px]")
                            ui.button("Speichern", on_click=self.change_container).props(
                                "flat")

            ui.row().classes("mt-4 mb-2 h-px w-full bg-gray-200 border-0")

            with ui.column().classes("pl-4 gap-4"):
                ui.label("Sensoren").classes("text-lg font-semibold mt-2")
                with ui.column().classes("gap-2"):
                    ui.label(
                        "Wähle aus welche Sensoren zu diesem Gerät gehören sollen. Nur Sensoren erlaubt, die noch keinem Gerät zugewiesen wurden.")
                    sensors = Sensor.get_all_unassigned()
                    sensors.extend(self.device.sensors)
                    sensors.sort(key=lambda x: x.id)

                    sensor_options = {
                        sensor.id: sensor.name for sensor in sensors}
                    preselected = [sensor.id for sensor in self.device.sensors]

                    with ui.row().classes("items-center"):
                        self.sensor_select = ui.select(
                            options=sensor_options, multiple=True, value=preselected).props('use-chips').classes("w-[130px] max-w-[350px]")
                        ui.button("Speichern", on_click=self.change_sensors).props(
                            "flat")

    def change_container(self):
        # Check if container is active
        if self._check_if_container_is_active(self.device.container):
            return

        # Check if new container is active
        new_container_id = self.container_select.value
        new_container = Container.get_by_id(new_container_id)
        if self._check_if_container_is_active(new_container):
            return
        
        self.device.container_id = new_container_id
        Container.session.commit()

        self.container_label.text = new_container.name
        ui.notify(f"Änderung erfolgreich gespeichert.", type="positive")

    def change_sensors(self):
        # Check if container is active
        if self._check_if_container_is_active(self.device.container):
            return
        
        self.device.clear_relationship_to_sensors()
        self.device.create_relationship_to_sensors(self.sensor_select.value)

        self.sensor_count_label.text = f'{len(self.device.sensors)}'
        ui.notify(f"Änderung erfolgreich gespeichert.", type="positive")

    def _check_if_container_is_active(self, container):
        if container is not None and container.is_active:
            ui.notify(
                f"Änderung kann nicht übernommen werden während Container '{container.name}' aktiv ist.", type="negative")
            return True
        return False
