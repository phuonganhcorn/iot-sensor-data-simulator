from nicegui import ui
from components.navigation import setup as setup_navigation

def setup_page():
    setup_navigation()
    ui.label('Sensoren')