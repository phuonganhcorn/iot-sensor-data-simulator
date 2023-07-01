from nicegui import app, ui

from pages.containers_page import ContainersPage
from pages.sensors_page import SensorsPage
from pages.machines_page import MachinesPage

ContainersPage()


@ui.page('/sensoren')
def sensors_page():
    SensorsPage()


@ui.page('/maschinen')
def devices_page():
    MachinesPage()


ui.run(title="IoT Telemetrie Simulator", host="127.0.0.1", port=8081)
