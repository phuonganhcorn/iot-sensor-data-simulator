from nicegui import ui
from components.navigation import Navigation
from components.container_card import ContainerCard
from model.container import Container


class ContainersPage:

    containers = [
        # Container(id=1),
        # Container(id=2)
    ]

    def __init__(self):
        self.cards_container = None
        self.cards_grid = None
        self.cards = []
        self.update_stats()
        self.setup_page()

    def setup_page(self):
        Navigation()

        ui.query('main').classes('h-px')
        ui.query('.nicegui-content').classes('p-8')

        ui.label("Container").classes('text-2xl font-bold')

        self.setup_menu_bar()
        self.setup_cards_container()

    def setup_menu_bar(self):
        with ui.row().classes('px-4 w-full flex items-center justify-between h-20 bg-gray-200 rounded-lg shadow-md'):
            ui.button('Neuen Container erstellen',
                      on_click=lambda: self.create_container()).classes('')

            with ui.row():
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Gesamt:').classes('text-sm font-medium')
                    ui.label().classes('text-sm').bind_text(self, 'containers_count')
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Aktiv:').classes('text-sm font-medium')
                    ui.label().classes('text-sm').bind_text(self, 'active_containers_count')
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Inaktiv:').classes('text-sm font-medium')
                    ui.label().classes('text-sm').bind_text(self, 'inactive_containers_count')

            with ui.row():
                ui.input(placeholder='Filter').classes('w-44')
                ui.select({1: "Alle", 2: "Aktiv", 3: "Inaktiv"},
                          value=1).classes('w-24')

    def setup_cards_container(self):
        self.cards_container = ui.row().classes('w-full')
        self.cards_grid = ui.grid().classes(
            'mt-6 w-full grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4')

        with self.cards_container:
            if len(self.containers) == 0:
                self.print_no_containers()
            else:
                with self.cards_grid:
                    for container in self.containers:
                        new_container_card = ContainerCard(
                            container=container, start_callback=self.start_container, stop_callback=self.stop_container, delete_callback=self.delete_container)
                        self.cards.append(new_container_card)

    def update_stats(self):
        self.containers_count = len(self.containers)
        self.active_containers_count = len(
            list(filter(lambda c: c.is_active, self.containers)))
        self.inactive_containers_count = self.containers_count - self.active_containers_count

    def print_no_containers(self):
        self.cards_container.classes('justify-center')
        with self.cards_container:
            with ui.column().classes('self-center mt-48'):
                ui.label('Keine Container vorhanden')

    def create_container(self):
        if len(self.containers) == 0:
            self.cards_container.clear()

        new_container = Container(id=len(self.containers) + 1)
        self.containers.append(new_container)
        with self.cards_grid:
            new_container_card = ContainerCard(container=new_container, start_callback=self.start_container,
                                               stop_callback=self.stop_container, logs_callback=self.show_logs, delete_callback=self.delete_container)
            self.cards.append(new_container_card)
        self.update_stats()

    def start_container(self, container):
        if container.start():
            index = self.containers.index(container)
            self.cards[index].set_active()
            self.update_stats()

    def stop_container(self, container):
        if container.stop():
            index = self.containers.index(container)
            self.cards[index].set_inactive()
            self.update_stats()

    def show_logs(self, container):
        ui.notify('Logs anzeigen', type='info')

    def delete_container(self, container):
        if container.is_active:
            ui.notify(
                'Container ist aktiv und kann nicht gelöscht werden.', type='warning')
            return

        if not container.delete():
            return

        index = self.containers.index(container)

        del self.containers[index]
        del self.cards[index]
        self.cards_grid.remove(index)

        self.update_stats()

        if len(self.containers) == 0:
            self.print_no_containers()
