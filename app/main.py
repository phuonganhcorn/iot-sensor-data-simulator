from nicegui import app, ui

from pages.containers_page import setup_page as setup_container_page
from pages.sensors_page import setup_page as setup_sensors_page
from pages.devices_page import setup_page as setup_devices_page

setup_container_page()

# @ui.page('/sensoren')
# def sensors_page():
#     init_sensors_page()

# @ui.page('/geraete')
# def devices_page():
#     init_devices_page()

ui.run()