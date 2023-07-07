from nicegui import ui


class DeviceItem:

    def __init__(self, device, delete_callback):
        self.device = device
        self.visible = True

        with ui.row().bind_visibility(self, 'visible').classes('px-3 py-6 flex justify-between items-center w-full hover:bg-gray-50'):
            with ui.row().classes('gap-6'):
                ui.label(f'{device.id}').classes('w-[30px]')
                ui.label(f'{device.name}').classes('w-[130px]')
                if device.container:
                    ui.label(f'{device.container.name}').classes('w-[130px]')
                ui.label(f'{len(device.sensors)}').classes('w-[60px]')
            with ui.row().classes('gap-2'):
                ui.button(icon='delete', on_click=lambda d=device: delete_callback(d)).props(
                    'flat').classes('px-2 text-red')
