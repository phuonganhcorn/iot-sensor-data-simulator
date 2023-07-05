import random

class Simulator:

    def __init__(self, sensor):
        self.base_value = sensor.base_value
        self.variation_range = sensor.variation_range
        self.change_rate = sensor.change_rate
        self.previous_value = sensor.base_value

    def generate_values(self, num_values=10):
        return [random.randint(20, 30) for _ in range(int(num_values))]
    
    def generate_value(self):
        value_change = random.uniform(-self.change_rate, self.change_rate)
        value = self.previous_value + value_change

        value = max(self.base_value - self.variation_range, min(self.base_value + self.variation_range, value))

        self.previous_value = value

        # TODO: Anomalien einführen

        value = round(value, 2)
        return value
