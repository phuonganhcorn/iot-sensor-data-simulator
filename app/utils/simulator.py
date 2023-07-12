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
        self.last_duplicate = -1  # Used to prevent more than one duplicate in a row
        self.drifting = False
        self.error_definition = json.loads(
            sensor.error_definition) if sensor.error_definition else None

    def generate_bulk_data(self, amount):
        records = []
        start_time = datetime.datetime.now()
        interval = self.sensor.interval

        for i in range(amount):
            timestamp = (start_time + datetime.timedelta(seconds=i * interval))
            record = self.generate_data(timestamp=timestamp)
            send_duplicate = record["sendDuplicate"]
            del record["sendDuplicate"]
            records.append(record)

            if send_duplicate:
                records.append(record)

        return records

    def generate_data(self, **kwargs):
        iso_format = kwargs.get("iso_format", False)
        timestamp = kwargs.get("timestamp", None)

        value_change = random.uniform(-self.change_rate, self.change_rate)
        value = self.previous_value + value_change

        value = max(self.base_value - self.variation_range,
                    min(self.base_value + self.variation_range, value))
        self.previous_value = value

        send_duplicate = False
        if self.error_definition:
            result = self._handle_error_definition(value)
            value = result["value"]
            send_duplicate = result.get("duplicate", False)

        # Errors might change the value to None
        if value is not None:
            value = round(value, 2)
        self.iteration += 1
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat(
            ) if iso_format else datetime.datetime.now()

        return {"timestamp": timestamp, "sensorId": self.sensor.id, "sensorName": self.sensor.name, "value": value, "unit": self.sensor.unit, "deviceId": self.sensor.device_id, "deviceName": self.sensor.device.name, "sendDuplicate": send_duplicate}

    def _handle_error_definition(self, value):
        error_type = self.error_definition["type"]

        if error_type == ANOMALY:
            return self._handle_anomaly_error(value)
        elif error_type == MCAR:
            return self._handle_mcar_error(value)
        elif error_type == DUPLICATE_DATA:
            return self.handle_duplicate_data_error(value)
        elif error_type == DRIFT:
            return self.handle_drift_error(value)

        return {"value": value}

    def _handle_anomaly_error(self, value):
        if random.random() > 1 - self.error_definition[PROBABILITY_POS_ANOMALY]:
            value += random.uniform(self.error_definition[POS_ANOMALY_LOWER_RANGE],
                                    self.error_definition[POS_ANOMALY_UPPER_RANGE])

        if random.random() < self.error_definition[PROBABILITY_NEG_ANOMALY]:
            value -= random.uniform(self.error_definition[NEG_ANOMALY_LOWER_RANGE],
                                    self.error_definition[NEG_ANOMALY_UPPER_RANGE])

        return {"value": value}

    def _handle_mcar_error(self, value):
        if random.random() < self.error_definition[PROBABILITY]:
            return {"value": None}
        return {"value": value}

    def handle_duplicate_data_error(self, value):
        if self.iteration - self.last_duplicate > 2 and random.random() < self.error_definition[PROBABILITY]:
            self.last_duplicate = self.iteration
            return {"value": value, "duplicate": True}
        return {"value": value}

    def handle_drift_error(self, value):
        after_n_iterations = self.error_definition[AFTER_N_ITERATIONS]
        if self.drifting or after_n_iterations > self.iteration:
            self.drifting = True
            if self.iteration % 10 != 0:
                return {"value": value}

            average_drift_rate = self.error_definition[AVERAGE_DRIFT_RATE]
            variation_range = self.error_definition[VARIATION_RANGE]
            deviation = random.uniform(-variation_range, variation_range)
            drift_change = average_drift_rate + deviation

            self.base_value += drift_change
        return {"value": value}
