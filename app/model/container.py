from model.models import ContainerModel
from model.device import Device
from utils.threads import ContainerThread
from constants.units import *
import datetime


class Container(ContainerModel):

    message_count = None

    @staticmethod
    def get_all():
        return Container.session.query(Container).all()

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
        container_db.create_relationship_to_devices(container_db, device_ids)
        return container_db

    def create_relationship_to_devices(self, container, device_ids):
        devices = Device.get_all_by_ids(device_ids)
        for device in devices:
            device.container_id = container.id

        Container.session.commit()

    def start(self, iot_hub_helper):
        self.thread = ContainerThread(target=self._thread_function, kwargs={
                                      "iot_hub_helper": iot_hub_helper})
        self.thread.start()

    def _thread_function(self, **kwargs):

        iot_hub_helper = kwargs.get("iot_hub_helper")

        # Start Container

        # Connect all device clients
        for device in self.devices:
            print(f"Connecting device {device.name}")
            device_client = iot_hub_helper.init_device_client(
                device.connection_string)
            device.client = device_client
            print(f"Connected device {device.name}")

        # Update container status
        self.is_active = True
        self.start_time = datetime.datetime.now()
        Container.session.commit()

        # Init simulation for all devices

        self.message_count = 0

        for device in self.devices:
            device.start_simulation(iot_hub_helper, self.message_callback)

        # Run simulation for all sensors

        while not self.thread.stopped():
            pass

        # Stop Container

        # Disconnect all device clients
        for device in self.devices:
            print(device.client)
            device.client.disconnect()
            device.client = None

        # Reset container status
        self.is_active = False
        self.start_time = None
        Container.session.commit()

    def message_callback(self, sensor, data):
        self.message_count += 1
        
        timestamp = data["timestamp"].strftime("%H:%M:%S")
        unit = UNITS[int(data['unit'])]
        unit_abbrev = unit["unit_abbreviation"]
        self.log.push(f"{timestamp}: {data['deviceId']} - {data['sensorName']} - {data['value']} {unit_abbrev}")
        self.live_view_dialog.append_value(sensor, data['value'])

    def stop(self):
        print("Stopping simulation")
        for sensor in self.get_all_sensors():
            sensor.stop()

        self.thread.stop()
        self.thread.join()
        print("Simulation stopped")

        self.message_count = None

    def get_all_sensors(self):
        sensors = []
        for device in self.devices:
            sensors.extend(device.sensors)
        return sensors

    def delete(self):
        Container.session.delete(self)
        Container.session.commit()
