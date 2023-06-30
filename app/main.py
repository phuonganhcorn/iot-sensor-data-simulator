from nicegui import app, ui

from pages.containers_page import ContainersPage
from pages.sensors_page import setup_page as setup_sensors_page
from pages.devices_page import setup_page as setup_devices_page

ContainersPage()


@ui.page('/sensoren')
def sensors_page():
    setup_sensors_page()


@ui.page('/geraete')
def devices_page():
    setup_devices_page()


ui.run(title="IoT Daten Simulator", host="127.0.0.1", port=8081)
