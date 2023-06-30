from nicegui import ui


class ContainerCard():
    def __init__(self, container, start_callback=None, stop_callback=None, logs_callback=None, delete_callback=None):
        self.card = None
        self.active_dot = None
        self.setup(container, start_callback=start_callback, stop_callback=stop_callback,
                   logs_callback=logs_callback, delete_callback=delete_callback)

    def setup(self, container, start_callback=None, stop_callback=None, logs_callback=None, delete_callback=None):
        with ui.card().tight() as card:
            self.card = card
            with ui.card_section().classes('min-h-[260px]'):
                with ui.row().classes('pb-2 w-full justify-between items-center border-b border-gray-200'):
                    ui.label(container.name).classes('text-xl font-semibold')
                    with ui.button(icon='more_vert').props('flat').classes('px-2 text-black'):
                        with ui.menu().props(remove='no-parent-event') as menu:
                            ui.menu_item('Log anzeigen', lambda c=container: logs_callback(
                                c)).classes('flex items-center')
                            ui.menu_item('Löschen', lambda c=container: delete_callback(
                                c)).classes('text-red-500').classes('flex items-center')
                with ui.column().classes('py-4 gap-2'):
                    with ui.row().classes('gap-1'):
                        ui.label('Geräte:').classes('text-sm font-medium')
                        ui.label().classes('text-sm').bind_text_from(container,
                                                                     'devices', backward=lambda d: len(d))
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
