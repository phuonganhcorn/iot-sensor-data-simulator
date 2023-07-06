from nicegui import ui
from components.live_view_dialog import LiveViewDialog
from components.logs_dialog import LogsDialog


class ContainerCard():
    def __init__(self, wrapper, container, start_callback=None, stop_callback=None, delete_callback=None, live_view_callback=None):
        self.card = None
        self.logs_dialog = LogsDialog(wrapper)
        container.log = self.logs_dialog.log
        self.active_dot = None
        self.setup(wrapper, container, start_callback=start_callback,
                   stop_callback=stop_callback, delete_callback=delete_callback, live_view_callback=live_view_callback)

    def setup(self, wrapper, container, start_callback=None, stop_callback=None, delete_callback=None, live_view_callback=None):
        sensor_count = 0
        for device in container.devices:
            sensor_count += len(device.sensors)

        with ui.card().tight() as card:
            self.card = card
            with ui.card_section().classes('min-h-[260px]'):
                with ui.row().classes('pb-2 w-full justify-between items-center border-b border-gray-200'):
                    ui.label(container.name).classes('text-xl font-semibold')
                    with ui.row().classes('gap-0.5'):
                        ui.button(icon='insert_chart_outlined', on_click=lambda: live_view_callback(container)).props('flat').classes('px-2 text-black')
                        with ui.button(icon='more_vert').props('flat').classes('px-2 text-black'):
                            with ui.menu().props(remove='no-parent-event'):
                                ui.menu_item('Log anzeigen', lambda: self.show_logs_dialog(container)).classes(
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
                        ui.label(f"{sensor_count}").classes('text-sm')
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
                    with ui.row().classes('gap-2'):
                        ui.button(icon='play_arrow', on_click=lambda c=container: start_callback(
                            c)).props('flat').classes('px-2 text-black')
                        ui.button(icon='pause', on_click=lambda c=container: stop_callback(
                            c)).props('flat').classes('px-2 text-black')

    def set_active(self):
        self.active_dot.classes('bg-green-500', remove='bg-red-500')

    def set_inactive(self):
        self.active_dot.classes('bg-red-500', remove='bg-green-500')

    def show_live_view_dialog(self, wrapper, container):
        LiveViewDialog(wrapper, container)

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
