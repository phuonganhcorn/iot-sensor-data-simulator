from nicegui import ui
from components.navigation import Navigation
from model.machine import Machine
from components.machine_item import MachineItem


class MachinesPage():

    def __init__(self):
        self.machines = []
        self.update_stats()
        self.setup_page()

    def setup_page(self):
        Navigation()
        ui.query('.nicegui-content').classes('p-8')
        ui.label("Maschinen").classes('text-2xl font-bold')

        self.setup_menu_bar()
        self.setup_list()

    def setup_menu_bar(self):
        with ui.row().classes('px-4 w-full flex items-center justify-between h-20 bg-gray-200 rounded-lg shadow-md'):
            ui.button('Neue Maschine erstellen',
                      on_click=lambda: self.create_machine()).classes('')

            with ui.row():
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Gesamt:').classes('text-sm font-medium')
                    ui.label().classes('text-sm').bind_text(self, 'machines_count')

            with ui.row():
                ui.input(placeholder='Filter').classes('w-44')
                ui.select({1: "Alle", 2: "Aktiv", 3: "Inaktiv"},
                          value=1).classes('w-24')

    def setup_list(self):
        self.list_container = ui.column().classes('w-full gap-0 divide-y')

        with self.list_container:
            if len(self.machines) == 0:
                self.print_no_machines()
            else:
                for machine in self.machines:
                    MachineItem(machine=machine,
                               delete_callback=self.delete_button_handler)

    def print_no_machines(self):
        self.list_container.classes('justify-center')
        with self.list_container:
            with ui.column().classes('self-center mt-48'):
                ui.label('Keine Maschinen vorhanden')

    def update_stats(self):
        self.machines_count = len(self.machines)

    def create_machine(self):
        if len(self.machines) == 0:
            self.list_container.clear()

        new_machine = Machine(id=len(self.machines) + 1)
        self.machines.append(new_machine)

        with self.list_container:
            MachineItem(machine=new_machine,
                       delete_callback=self.delete_button_handler)

        self.update_stats()

    def delete_button_handler(self, machine):
        with ui.dialog(value=True) as dialog, ui.card().classes('items-center'):
            ui.label('Möchtest du die Maschine wirklich löschen?')
            with ui.row():
                ui.button('Abbrechen', on_click=dialog.close).props('flat')
                ui.button('Löschen', on_click=lambda d=dialog: self.delete_handler(
                    d, machine)).classes('text-white bg-red')

    def delete_handler(self, dialog, machine):
        dialog.close()

        # TODO: Check if container is running and stop it

        if not machine.delete():
            return

        index = self.machines.index(machine)

        del self.machines[index]
        self.list_container.remove(index)

        self.update_stats()

        if len(self.machines) == 0:
            self.print_no_machines()
