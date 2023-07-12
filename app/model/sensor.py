from model.models import SensorModel
from utils.simulator import Simulator
import threading


class Sensor(SensorModel):

    @staticmethod
    def add(name, base_value, unit, variation_range, change_rate, interval, error_definition, device_id):
        new_sensor = Sensor(name=name, base_value=base_value,
                            unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval, error_definition=error_definition, device_id=device_id)

        Sensor.session.add(new_sensor)
        Sensor.session.commit()

        return new_sensor

    @staticmethod
    def get_all():
        return Sensor.session.query(Sensor).all()

    @staticmethod
    def get_all_by_ids(list_of_ids):
        return Sensor.session.query(Sensor).filter(Sensor.id.in_(list_of_ids)).all()
    
    @staticmethod
    def get_by_id(id):
        return Sensor.session.query(Sensor).filter(Sensor.id == id).first()

    # Returns all sensors that are not assigned to a device
    @staticmethod
    def get_all_unassigned():
        return Sensor.session.query(Sensor).filter(Sensor.device_id == None).all()
    
    @staticmethod
    def check_if_name_in_use(name):
        return Sensor.session.query(Sensor).filter(Sensor.name.ilike(name)).first() is not None
    
    def _callback(self, device_callback):
        # Überprüfen, ob die Schleife unterbrochen werden soll
        if self.running:
            data = self.simulator.generate_data()
            device_callback(self, data)

            # Wiederholung des Callbacks nach einer bestimmten Zeit
            timer = threading.Timer(
                interval=self.interval, function=self._callback, args=[device_callback])
            timer.start()

    def start_bulk_simulation(self, amount):
        simulator = Simulator(sensor=self)
        data = simulator.generate_bulk_data(amount)
        return data
    
    def start_simulation(self, callback):
        self.simulator = Simulator(sensor=self)
        self.running = True

        timer = threading.Timer(interval=self.interval, function=self._callback, args=[callback])
        timer.start()

    def stop_simulation(self):
        self.running = False

    def delete(self):
        Sensor.session.delete(self)
        Sensor.session.commit()
