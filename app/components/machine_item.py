from nicegui import ui


class MachineItem:

    def __init__(self, machine, delete_callback):
        with ui.row().classes('px-3 py-6 flex justify-between items-center w-full hover:bg-gray-50'):
            with ui.row().classes('gap-12'):
                ui.label(f'{machine.name}')
            with ui.row():
                with ui.row().classes('gap-2'):
                    ui.button(icon='edit').props(
                        'flat').classes('px-2 text-black')
                    ui.button(icon='delete', on_click=lambda m=machine: delete_callback(m)).props(
                        'flat').classes('px-2 text-red')
