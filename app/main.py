from nicegui import app, ui

from pages.containers_page import ContainersPage
from pages.sensors_page import SensorsPage
from pages.devices_page import setup_page as setup_devices_page

ContainersPage()


@ui.page('/sensoren')
def sensors_page():
    SensorsPage()


@ui.page('/geraete')
def devices_page():
    setup_devices_page()


ui.run(title="IoT Telemetrie Simulator", host="127.0.0.1", port=8081)
