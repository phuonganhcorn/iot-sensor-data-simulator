from model.models import ContainerModel
from model.device import Device
from utils.mqtt_helper import MQTTHelper
from utils.threads import ContainerThread
from constants.units import *
from nicegui import ui
import datetime


class Container(ContainerModel):

    message_count = None
    device_clients = {}

    @staticmethod
    def get_all():
        return Container.session.query(Container).all()
    
    @staticmethod
    def get_by_id(id):
        return Container.session.query(Container).filter(Container.id == id).first()

    def get_device_count(self):
        return len(self.devices)

    def get_devices(self):
        return self.devices

    @staticmethod
    def add(name, description, location, device_ids):
        container_db = Container(name=name, description=description,
                                 location=location, is_active=False, start_time=None)
        Container.session.add(container_db)
        Container.session.commit()
        container_db.create_relationship_to_devices(device_ids)
        return container_db
    
    @staticmethod
    def check_if_name_in_use(name):
        return Container.session.query(Container).filter(Container.name.ilike(name)).first() is not None

    def create_relationship_to_devices(self, device_ids):
        devices = Device.get_all_by_ids(device_ids)
        for device in devices:
            device.container_id = self.id

        Container.session.commit()

    def start(self, interface, **kwargs):
        iot_hub_helper = kwargs.get("iot_hub_helper")

        if interface == "iothub" and iot_hub_helper is None:
            ui.notify("IoT Hub Helper ist nicht initialisiert!", type="negative")
            return

        # Update container status
        self.is_active = True
        self.start_time = datetime.datetime.now()
        Container.session.commit()

        self.thread = ContainerThread(target=self._thread_function, kwargs={"interface": interface, "iot_hub_helper": iot_hub_helper})
        self.thread.start()

    def _thread_function(self, *args, **kwargs):
        interface = kwargs.get("interface")
        iot_hub_helper = kwargs.get("iot_hub_helper")

        if interface == "iothub":
            device_clients = self._connect_device_clients(iot_hub_helper)
        elif interface == "mqtt":
            mqtt_helper = MQTTHelper()
            mqtt_helper.connect()

        # Init simulation for all devices
        self.message_count = 0

        for device in self.devices:
            if interface == "iothub":
                device.start_simulation(interface, self._message_callback, iot_hub_helper=iot_hub_helper)
            elif interface == "mqtt":
                device.start_simulation(interface, self._message_callback, mqtt_helper=mqtt_helper)

        # Run simulation
        while not self.thread.stopped():
            pass

        # Stop Container
        if interface == "iothub":
            self._disconnect_device_clients(device_clients)

        # Reset container status
        self.is_active = False
        self.start_time = None
        Container.session.commit()
    
    def _connect_device_clients(self, iot_hub_helper):
        clients = []

        for device in self.devices:
            device_client = iot_hub_helper.init_device_client(
                device.connection_string)
            device.client = device_client
            clients.append(device_client)

        return clients

    def _disconnect_device_clients(self, clients):
        for client in device_clients:
            client.disconnect()
        device_clients = None
        for device in self.devices:
            device.client = None


    def _message_callback(self, sensor, data):
        self.message_count += 1

        value = data["value"]
        timestamp = data["timestamp"]
        timestamp_formatted = timestamp.strftime("%H:%M:%S")

        unit = UNITS[int(data['unit'])]
        unit_abbrev = unit["unit_abbreviation"]

        send_duplicate = data.get("sendDuplicate", False)

        for _ in range(2 if send_duplicate else 1):
            self.log.push(f"{timestamp_formatted}: {data['deviceId']} - {data['sensorName']} - {data['value']} {unit_abbrev}")
            self.live_view_dialog.append_data_point(sensor, timestamp, value)

    def stop(self):
        for sensor in self.get_sensors():
            sensor.stop_simulation()

        self.thread.stop()
        self.thread.join()

        self.message_count = None

    def get_sensors(self):
        sensors = []
        for device in self.devices:
            sensors.extend(device.sensors)
        return sensors

    def delete(self):
        Container.session.delete(self)
        Container.session.commit()
