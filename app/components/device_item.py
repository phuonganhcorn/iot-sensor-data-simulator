from nicegui import ui


class DeviceItem:

    def __init__(self, device, delete_callback):
        with ui.row().classes('px-3 py-6 flex justify-between items-center w-full hover:bg-gray-50'):
            with ui.row().classes('gap-12'):
                ui.label(f'{device.device_id}')
            with ui.row().classes('gap-2'):
                ui.button(icon='delete', on_click=lambda d=device: delete_callback(d)).props(
                    'flat').classes('px-2 text-red')
