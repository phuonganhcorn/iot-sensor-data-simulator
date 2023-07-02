from nicegui import ui
from dotenv import load_dotenv

from utils.iot_hub_helper import IoTHubHelper
from pages.containers_page import ContainersPage
from pages.sensors_page import SensorsPage
from pages.devices_page import DevicesPage

load_dotenv()

iot_hub_helper = IoTHubHelper()

ContainersPage()


@ui.page('/sensoren')
def sensors_page():
    SensorsPage()


@ui.page('/geraete')
def devices_page():
    DevicesPage(iot_hub_helper)


ui.run(title="IoT Telemetrie Simulator", host="127.0.0.1", port=8081)
