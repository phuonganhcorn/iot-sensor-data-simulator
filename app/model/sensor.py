from model.models import SensorModel
from utils.simulator import Simulator


class Sensor(SensorModel):

    @staticmethod
    def add(name, base_value, unit, variation_range, change_rate, interval, device_id):
        new_sensor = Sensor(name=name, base_value=base_value,
                            unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval, device_id=device_id)

        Sensor.session.add(new_sensor)
        Sensor.session.commit()

        return new_sensor

    @staticmethod
    def get_all():
        return Sensor.session.query(Sensor).all()

    @staticmethod
    def get_all_by_ids(list_of_ids):
        return Sensor.session.query(Sensor).filter(Sensor.id.in_(list_of_ids)).all()

    # Returns all sensors that are not assigned to a device
    @staticmethod
    def get_all_unassigned():
        return Sensor.session.query(Sensor).filter(Sensor.device_id == None).all()

    def run_simulation(self, iot_hub_helper, device_client):
        simulator = Simulator()
        values = simulator.generate_values(self.interval)

        data = [{
            'time': "2023-06-01T12:00:00Z",
            'deviceId': self.device_id,
            'temperature': value,
        } for value in values]

        response = iot_hub_helper.send_telemetry_messages(device_client, data)

    @staticmethod
    def delete(sensor):
        Sensor.session.delete(sensor)
        Sensor.session.commit()
