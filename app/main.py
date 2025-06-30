from nicegui import ui
from dotenv import load_dotenv
from utils.iot_hub_helper import IoTHubHelper
from pages.containers_page import ContainersPage
from pages.sensors_page import SensorsPage
from pages.devices_page import DevicesPage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.models import Base
from model.option import Option
from model.container import Container
from model.device import Device
from model.sensor import Sensor
import os

# Load environment variables
load_dotenv()

# Create database if it does not exist
# Setup database session
engine = create_engine('sqlite:///telemetry_simulator.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Set database session for all models
Option.session = session
Container.session = session
Device.session = session
Sensor.session = session

# Initialize medical data directory
medical_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'medical_data')
print(f"Looking for medical data in: {medical_data_dir}")
Sensor.set_data_directory(medical_data_dir)


# Create IoT Hub helper
iot_hub_helper = IoTHubHelper()

@ui.page('/')
def containers_page():
    '''Renders the containers page at / path.'''
    ContainersPage(iot_hub_helper)


@ui.page('/geraete')
def devices_page():
    '''Renders the devices page at /geraete path.'''
    DevicesPage(iot_hub_helper)


@ui.page('/sensoren')
def sensors_page():
    '''Renders the sensors page at /sensoren path.'''
    SensorsPage()


# Start the UI
ui.run(title="IoT Telemetrie Simulator", host="127.0.0.1", port=8080)
