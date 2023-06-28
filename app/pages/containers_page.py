from nicegui import ui
from components.navigation import setup as setup_navigation

DUMMY_CONTAINERS = [
    {
        'name': 'Container 1',
        'active': True,
        'start_time': '10:35',
        'devices': 3,
        'messages': 545
    },
    {
        'name': 'Container 2',
        'active': False,
        'start_time': '08:11',
        'devices': 2,
        'messages': 1237
    }
]

def setup_page():
    setup_navigation('Container')

    ui.query('main').classes('h-px')
    
    if len(DUMMY_CONTAINERS) == 0:
        ui.query('.nicegui-content').classes('h-full items-center justify-center')
        with ui.column() as container:
            container.classes('shadow-lg rounded-lg bg-white p-4')
            ui.label('Keine Container vorhanden.')
            ui.button('Neuen Container erstellen')
    else:
        ui.query('.nicegui-content').classes('p-8')

        with ui.row().classes('px-4 w-full flex items-center justify-between h-20 bg-gray-200 rounded-lg shadow-md'):
            ui.button('Neuen Container erstellen').classes('')

            with ui.row():
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Gesamt:').classes('text-sm font-medium')
                    ui.label(len(DUMMY_CONTAINERS)).classes('text-sm')
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Aktiv:').classes('text-sm font-medium')
                    ui.label("1").classes('text-sm')
                with ui.row().classes('ml-4 gap-1'):
                    ui.label('Inaktiv:').classes('text-sm font-medium')
                    ui.label("1").classes('text-sm')

            with ui.row():
                ui.input(placeholder='Filter').classes('w-44')
                ui.select({ 1: "Alle", 2: "Aktiv", 3: "Inaktiv"}, value=1).classes('w-24')

        with ui.grid().classes('mt-6 w-full grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4'):
            for container in DUMMY_CONTAINERS:
                with ui.card().tight():
                    with ui.card_section().classes('min-h-[260px]'):
                        with ui.row().classes('pb-2 w-full justify-between items-center border-b border-gray-200'):
                            ui.label(container['name']).classes('text-xl font-semibold')
                            with ui.button(icon='more_vert').props('flat').classes('px-2 text-black'):
                                with ui.menu().props(remove='no-parent-event') as menu:
                                    ui.menu_item('Log anzeigen').classes('flex items-center')
                                    ui.menu_item('Löschen').classes('text-red-500').classes('flex items-center')
                        with ui.column().classes('py-4 gap-2'):
                            with ui.row().classes('gap-1'):
                                ui.label('Startzeit:').classes('text-sm font-medium')
                                ui.label(container['start_time']).classes('text-sm')
                            with ui.row().classes('gap-1'):
                                ui.label('Geräte:').classes('text-sm font-medium')
                                ui.label(container['devices']).classes('text-sm')
                            with ui.row().classes('gap-1'):
                                ui.label('Gesendete Nachrichten:').classes('text-sm font-medium')
                                ui.label(container['messages']).classes('text-sm')
                    with ui.card_section().classes('bg-gray-100'):
                        with ui.row().classes('items-center justify-between'):
                            with ui.row().classes('gap-3 items-center'):
                                ui.row().classes('h-4 w-4 rounded-full' + (' bg-green-500' if container['active'] else ' bg-red-500'))
                                ui.label('Aktiv' if container['active'] else 'Inaktiv')
                            with ui.row().classes('gap-2'):
                                ui.button(icon='play_arrow').props('flat').classes('px-2 text-black')
                                ui.button(icon='pause').props('flat').classes('px-2 text-black')