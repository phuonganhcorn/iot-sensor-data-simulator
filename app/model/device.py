from model.models import DeviceModel
from model.sensor import Sensor
from utils.iot_hub_helper import IoTHubHelper


class Device(DeviceModel):

    @staticmethod
    def get_all():
        return Device.session.query(Device).all()

    @staticmethod
    def get_all_by_ids(ids):
        return Device.session.query(Device).filter(Device.id.in_(ids)).all()
    
    def get_by_id(id):
        return Device.session.query(Device).filter_by(id=id).first()
    
    @staticmethod
    def get_all_unassigned():
        return Device.session.query(Device).filter(Device.container_id == None).all()

    @staticmethod
    def add(sensor_ids, **kwargs):
        device_client = kwargs.get("device_client")
        device_name = kwargs.get("device_name")

        device_db = None
        if device_client:
            primary_key = device_client.authentication.symmetric_key.primary_key
            host_name = IoTHubHelper.get_host_name()
            connection_string = f"HostName={host_name}.azure-devices.net;DeviceId={device_client.device_id};SharedAccessKey={primary_key}"

            device_db = Device(name=device_client.device_id, generation_id=device_client.generation_id,
                            etag=device_client.etag, status=device_client.status, connection_string=connection_string)
        elif device_name:
            device_db = Device(name=device_name)

        if device_db is not None:
            Device.session.add(device_db)
            Device.session.commit()

            device_db.create_relationship_to_sensors(sensor_ids)

            return device_db
        
        return None
    
    @staticmethod
    def check_if_name_in_use(name):
        return Device.session.query(Device).filter(Device.name.ilike(name)).first() is not None

    def create_relationship_to_sensors(self, sensor_ids):
        sensors = Sensor.get_all_by_ids(sensor_ids)
        for sensor in sensors:
            sensor.device_id = self.id
        Sensor.session.commit()

    def clear_relationship_to_sensors(self):
        for sensor in self.sensors:
            sensor.device_id = None
        Sensor.session.commit()

    def start_simulation(self, interface, callback, **kwargs):
        self.interface = interface

        if interface == "iothub":
            self.iot_hub_helper = kwargs.get("iot_hub_helper")
        elif interface == "mqtt":
            self.mqtt_helper = kwargs.get("mqtt_helper")

        self.container_callback = callback

        for sensor in self.sensors:
            sensor.start_simulation(callback=self.send_simulator_data)

    def send_simulator_data(self, sensor, data):
        if self.interface == "iothub" and self.iot_hub_helper is not None and self.client is not None:
            self.iot_hub_helper.send_message(self.client, data)
        elif self.interface == "mqtt" and self.mqtt_helper is not None:
            self.mqtt_helper.publish(topic=self.container.name, data=data)
        
        self.container_callback(sensor, data)

    def delete(self):
        Device.session.delete(self)
        Device.session.commit()
