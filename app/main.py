from nicegui import ui
from dotenv import load_dotenv
from utils.iot_hub_helper import IoTHubHelper
from pages.containers_page import ContainersPage
from pages.sensors_page import SensorsPage
from pages.devices_page import DevicesPage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.database import Options, Container, Device, Sensor, Base

load_dotenv()

engine = create_engine('sqlite:///telemetry_simulator.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

Options.session = session
Container.session = session
Device.session = session
Sensor.session = session


iot_hub_helper = IoTHubHelper()

ContainersPage(iot_hub_helper)


@ui.page('/sensoren')
def sensors_page():
    SensorsPage()


@ui.page('/geraete')
def devices_page():
    DevicesPage(iot_hub_helper)


ui.run(title="IoT Telemetrie Simulator", host="127.0.0.1", port=8081)
