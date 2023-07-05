from model.models import SensorModel
from utils.simulator import Simulator
import threading


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
    
    def callback(self, device_callback):
        # Überprüfen, ob die Schleife unterbrochen werden soll
        if self.running:
            value = self.simulator.generate_value()
            print("Callback aufgerufen von: " + self.name + " mit Wert: " + str(value))
            device_callback(value)

            # Wiederholung des Callbacks nach einer bestimmten Zeit
            timer = threading.Timer(
                interval=self.interval, function=self.callback, args=[device_callback])
            timer.start()

    def start_simulation(self, callback):
        self.simulator = Simulator(sensor=self)
        self.running = True

        timer = threading.Timer(interval=self.interval, function=self.callback, args=[callback])
        timer.start()

    def stop(self):
        self.running = False

    @staticmethod
    def delete(sensor):
        Sensor.session.delete(sensor)
        Sensor.session.commit()
