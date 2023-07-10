from model.models import DeviceModel
from model.options import Options
from model.sensor import Sensor


class Device(DeviceModel):

    @staticmethod
    def get_all():
        return Device.session.query(Device).all()

    @staticmethod
    def get_all_unassigned():
        return Device.session.query(Device).filter_by(container_id=None).all()

    @staticmethod
    def get_all_by_ids(ids):
        return Device.session.query(Device).filter(Device.id.in_(ids)).all()
    
    def get_by_id(id):
        return Device.session.query(Device).filter_by(id=id).first()
    
    @staticmethod
    def get_all_unassigned():
        return Device.session.query(Device).filter(Device.container_id == None).all()

    @staticmethod
    def store(device, sensor_ids):
        primary_key = device.authentication.symmetric_key.primary_key
        host_name = Options.get_option('host_name').value
        connection_string = f"HostName={host_name}.azure-devices.net;DeviceId={device.device_id};SharedAccessKey={primary_key}"

        device_db = Device(name=device.device_id, generation_id=device.generation_id,
                           etag=device.etag, status=device.status, connection_string=connection_string)

        Device.session.add(device_db)
        Device.session.commit()

        device_db.create_relationship_to_sensors(sensor_ids)

        return device_db
    
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

    def start_simulation(self, iot_hub_helper, callback):
        self.iot_hub_helper = iot_hub_helper
        self.container_callback = callback

        for sensor in self.sensors:
            sensor.start_simulation(callback=self.send_simulator_data)

    def send_simulator_data(self, sensor, data):
        self.iot_hub_helper.send_message(self.client, data)
        self.container_callback(sensor, data)

    def delete(self):
        Device.session.delete(self)
        Device.session.commit()
