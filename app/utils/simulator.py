import random
import datetime


class Simulator:

    def __init__(self, sensor):
        self.sensor = sensor
        self.base_value = sensor.base_value
        self.variation_range = sensor.variation_range
        self.change_rate = sensor.change_rate
        self.previous_value = sensor.base_value

    def generate_data(self):
        value_change = random.uniform(-self.change_rate, self.change_rate)
        value = self.previous_value + value_change

        value = max(self.base_value - self.variation_range,
                    min(self.base_value + self.variation_range, value))

        self.previous_value = value

        # TODO: Anomalien einführen

        value = round(value, 2)

        return {"value": value, "timestamp": datetime.datetime.now(), "sensorName": self.sensor.name, "unit": self.sensor.unit}
