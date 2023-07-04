from model.models import ContainerModel
from model.device import Device
import datetime


class Container(ContainerModel):

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
        # Connect all device clients
        for device in self.devices:
            device_client = iot_hub_helper.init_device_client(
                device.connection_string)
            self.device_clients.append(device_client)

        # Update container status
        self.is_active = True
        self.start_time = datetime.datetime.now()
        Container.session.commit()

    def stop(self):
        # Disconnect all device clients
        for device_client in self.device_clients:
            device_client.disconnect()
        self.device_clients = []

        # Reset container status
        self.is_active = False
        self.start_time = None
        Container.session.commit()

    @staticmethod
    def delete(container):
        Container.session.delete(container)
        Container.session.commit()
