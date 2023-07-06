from constants.sensor_errors import *
import random
import datetime
import json


class Simulator:

    def __init__(self, sensor):
        self.iteration = 0
        self.sensor = sensor
        self.base_value = sensor.base_value
        self.variation_range = sensor.variation_range
        self.change_rate = sensor.change_rate
        self.previous_value = sensor.base_value
        self.error_definition = json.loads(sensor.error_definition) if sensor.error_definition else None

    def generate_data(self):
        value_change = random.uniform(-self.change_rate, self.change_rate)
        value = self.previous_value + value_change

        value = max(self.base_value - self.variation_range,
                    min(self.base_value + self.variation_range, value))
        self.previous_value = value

        if self.error_definition:
            value = self._handle_error_definition(value)
        self.iteration += 1

        value = round(value, 2)
        return {"value": value, "timestamp": datetime.datetime.now(), "sensorName": self.sensor.name, "unit": self.sensor.unit}

    def _handle_error_definition(self, value):        
        if self.error_definition["type"] == "anomaly":
            return self._handle_anomaly_error(value)

    def _handle_anomaly_error(self, value):
        if self.iteration == 0:
            return value
        
        if random.random() > 1 - self.error_definition[PROBABILITY_POS_ANOMALY]:
            value += random.uniform(self.error_definition[POS_ANOMALY_LOWER_RANGE], self.error_definition[POS_ANOMALY_UPPER_RANGE])
        
        if random.random() < self.error_definition[PROBABILITY_NEG_ANOMALY]:
            value -= random.uniform(self.error_definition[NEG_ANOMALY_LOWER_RANGE], self.error_definition[NEG_ANOMALY_UPPER_RANGE])

        return value
