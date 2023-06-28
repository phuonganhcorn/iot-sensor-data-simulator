from nicegui import ui
from components.navigation import setup as setup_navigation

DUMMY_CONTAINERS = [
    {
        'name': 'Container 1',
        'active': True
    },
    {
        'name': 'Container 2',
        'active': False
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
        ui.query('.nicegui-content').classes('p-8 grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4')

        for container in DUMMY_CONTAINERS:
            with ui.card().tight():
                with ui.card_section().classes('min-h-[260px]'):
                    with ui.row().classes('justify-between items-center'):
                        ui.label(container['name']).classes('text-xl font-semibold')
                        ui.button(icon='more_vert').props('flat').classes('px-2 text-black')
                with ui.card_section().classes('bg-gray-100'):
                    with ui.row().classes('items-center justify-between'):
                        with ui.row().classes('items-center'):
                            ui.row().classes('h-4 w-4 rounded-full' + (' bg-green-500' if container['active'] else ' bg-red-500'))
                            ui.label('Aktiv' if container['active'] else 'Inaktiv')
                        with ui.row().classes('gap-2'):
                            ui.button(icon='play_arrow').props('flat').classes('px-2 text-black')
                            ui.button(icon='pause').props('flat').classes('px-2 text-black')