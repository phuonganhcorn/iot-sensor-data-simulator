from utils.csv_data_loader import CSVDataLoader
from constants.sensor_errors import *
import random
import datetime
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MedicalDataSimulator:
    '''Simulates medical sensor data using real CSV data.'''

    def __init__(self, sensor, csv_data_loader: CSVDataLoader):
        '''Initializes the medical simulator.'''
        self.sensor = sensor
        self.csv_data_loader = csv_data_loader
        self.iteration = 0
        self.last_duplicate = -1
        self.sensor_type = self._detect_sensor_type()
        self.error_definition = json.loads(
            sensor.error_definition) if sensor.error_definition else None
        
        logger.info(f"Initialized MedicalDataSimulator for sensor {sensor.name} with type {self.sensor_type}")

    def _detect_sensor_type(self) -> str:
        '''Detect the medical sensor type based on sensor name or unit.'''
        name_lower = self.sensor.name.lower()
        
        # Map sensor names to types
        if 'acc' in name_lower or 'accelerometer' in name_lower:
            if 'x' in name_lower:
                return 'ACC_X'
            elif 'y' in name_lower:
                return 'ACC_Y'
            elif 'z' in name_lower:
                return 'ACC_Z'
            else:
                return 'ACC'
        elif 'bvp' in name_lower or 'blood volume pulse' in name_lower:
            return 'BVP'
        elif 'dexcom' in name_lower or 'glucose' in name_lower:
            return 'Dexcom'
        elif 'eda' in name_lower or 'electrodermal' in name_lower:
            return 'EDA'
        elif 'temp' in name_lower or 'temperature' in name_lower:
            return 'TEMP'
        elif 'ibi' in name_lower or 'interbeat' in name_lower:
            return 'IBI'
        elif 'hr' in name_lower or 'heart rate' in name_lower:
            return 'HR'
        elif 'food' in name_lower:
            return 'Food Log'
        
        # Map by unit ID to sensor type
        unit_to_type = {
            0: 'BVP',           # Blood Volume Pulse
            1: 'Dexcom',        # Glucose Concentration 
            2: 'EDA',           # Electrodermal Activity
            3: 'TEMP',          # Skin Temperature
            4: 'IBI',           # Interbeat Interval
            5: 'HR',            # Heart Rate
            6: 'ACC_X',         # Accelerometer X
            7: 'ACC_Y',         # Accelerometer Y
            8: 'ACC_Z',         # Accelerometer Z
            9: 'Food Log',      # Calories (from food)
        }
        
        if self.sensor.unit in unit_to_type:
            return unit_to_type[self.sensor.unit]
        
        # Default fallback - try to match with available data
        available_types = self.csv_data_loader.get_available_sensor_types()
        if available_types:
            return available_types[0]  # Use first available type
        
        return 'BVP'  # Default fallback

    def generate_bulk_data(self, amount: int) -> list:
        '''Generates a list of medical data records from CSV data.'''
        records = []
        
        # Get base sensor type (remove directional suffixes)
        base_sensor_type = self.sensor_type.replace('_X', '').replace('_Y', '').replace('_Z', '')
        
        for i in range(amount):
            record = self.generate_data()
            
            if record:
                # Handle duplicate data error
                send_duplicate = record.get("sendDuplicate", False)
                if "sendDuplicate" in record:
                    del record["sendDuplicate"]
                records.append(record)

                # Append duplicate data if necessary
                if send_duplicate:
                    records.append(record.copy())
        
        return records

    def generate_data(self, **kwargs) -> Optional[Dict[str, Any]]:
        '''Generates a single medical data record from CSV data.'''
        iso_format = kwargs.get("iso_format", False)
        timestamp = kwargs.get("timestamp", None)
        
        # Get base sensor type (remove directional suffixes)
        base_sensor_type = self.sensor_type.replace('_X', '').replace('_Y', '').replace('_Z', '')
        
        # Get next data point from CSV
        csv_data = self.csv_data_loader.get_next_data_point(base_sensor_type)
        
        if not csv_data:
            logger.warning(f"No CSV data available for sensor type: {base_sensor_type}")
            return None
        
        # Extract value based on sensor type
        value = self._extract_value_from_csv_data(csv_data)
        original_timestamp = csv_data.get('timestamp', datetime.datetime.now())
        
        # Use provided timestamp or CSV timestamp
        if timestamp is None:
            timestamp = original_timestamp.isoformat() if iso_format else original_timestamp
        
        send_duplicate = False
        if self.error_definition:
            result = self._handle_error_definition(value)
            value = result["value"]
            send_duplicate = result.get("duplicate", False)

        # Check if None. Errors might change the value to None
        if value is not None:
            value = round(value, 6)  # More precision for medical data
            
        self.iteration += 1

        # Return the data record with medical sensor characteristics
        return {
            "timestamp": timestamp,
            "sensorId": self.sensor.id,
            "sensorName": self.sensor.name,
            "value": value,
            "unit": self.sensor.unit,
            "deviceId": self.sensor.device_id,
            "deviceName": self.sensor.device.name,
            "sendDuplicate": send_duplicate,
            "medicalData": csv_data  # Include original medical data for context
        }

    def _extract_value_from_csv_data(self, csv_data: Dict[str, Any]) -> float:
        '''Extract the appropriate value from CSV data based on sensor type.'''
        try:
            if self.sensor_type == 'ACC_X':
                return float(csv_data.get('x', 0))
            elif self.sensor_type == 'ACC_Y':
                return float(csv_data.get('y', 0))
            elif self.sensor_type == 'ACC_Z':
                return float(csv_data.get('z', 0))
            elif self.sensor_type == 'ACC':
                # For general ACC, return magnitude
                x = float(csv_data.get('x', 0))
                y = float(csv_data.get('y', 0))
                z = float(csv_data.get('z', 0))
                return (x**2 + y**2 + z**2) ** 0.5
            elif self.sensor_type == 'Food Log':
                # For food log, return calories as default value
                return float(csv_data.get('calorie', 0))
            else:
                # For other sensors (BVP, Dexcom, EDA, TEMP, IBI, HR)
                return float(csv_data.get('value', 0))
        except (ValueError, TypeError) as e:
            logger.warning(f"Error extracting value from CSV data: {e}")
            return 0.0

    def _handle_error_definition(self, value: float) -> Dict[str, Any]:
        '''Handles the error definition of a medical sensor.'''
        if not self.error_definition:
            return {"value": value}
            
        error_type = self.error_definition["type"]

        if error_type == ANOMALY:
            return self._handle_anomaly_error(value)
        elif error_type == MCAR:
            return self._handle_mcar_error(value)
        elif error_type == DUPLICATE_DATA:
            return self._handle_duplicate_data_error(value)
        elif error_type == DRIFT:
            return self._handle_drift_error(value)

        return {"value": value}

    def _handle_anomaly_error(self, value: float) -> Dict[str, Any]:
        '''Handles the anomaly error type for medical data.'''
        if random.random() > 1 - self.error_definition[PROBABILITY_POS_ANOMALY]:
            # Add a random positive anomaly
            anomaly_value = random.uniform(
                self.error_definition[POS_ANOMALY_LOWER_RANGE],
                self.error_definition[POS_ANOMALY_UPPER_RANGE]
            )
            value += anomaly_value
            logger.debug(f"Applied positive anomaly: +{anomaly_value}")

        if random.random() < self.error_definition[PROBABILITY_NEG_ANOMALY]:
            # Add a random negative anomaly
            anomaly_value = random.uniform(
                self.error_definition[NEG_ANOMALY_LOWER_RANGE],
                self.error_definition[NEG_ANOMALY_UPPER_RANGE]
            )
            value -= anomaly_value
            logger.debug(f"Applied negative anomaly: -{anomaly_value}")

        return {"value": value}

    def _handle_mcar_error(self, value: float) -> Dict[str, Any]:
        '''Handles the MCAR (Missing Completely At Random) error type.'''
        if random.random() < self.error_definition[PROBABILITY]:
            logger.debug("Applied MCAR error - value set to None")
            return {"value": None}
        return {"value": value}

    def _handle_duplicate_data_error(self, value: float) -> Dict[str, Any]:
        '''Handles the duplicate data error type.'''
        if (self.iteration - self.last_duplicate > 2 and 
            random.random() < self.error_definition[PROBABILITY]):
            self.last_duplicate = self.iteration
            logger.debug("Applied duplicate data error")
            return {"value": value, "duplicate": True}
        return {"value": value}

    def _handle_drift_error(self, value: float) -> Dict[str, Any]:
        '''Handles the drift error type for medical sensors.'''
        # Note: Drift is typically applied to the base value in the original simulator
        # For medical data from CSV, we apply drift as an additive factor
        
        after_n_iterations = self.error_definition.get(AFTER_N_ITERATIONS, 100)
        
        if self.iteration > after_n_iterations:
            if self.iteration % 10 == 0:  # Apply drift every 10 iterations
                drift_rate = self.error_definition.get(AVERAGE_DRIFT_RATE, 0.01)
                variation = self.error_definition.get(VARIATION_RANGE, 0.005)
                deviation = random.uniform(-variation, variation)
                drift_change = drift_rate + deviation
                
                value += drift_change
                logger.debug(f"Applied drift: +{drift_change}")

        return {"value": value}

    def reset_simulation(self):
        '''Reset the simulation state.'''
        self.iteration = 0
        self.last_duplicate = -1
        # Reset CSV data loader index for this sensor type
        base_sensor_type = self.sensor_type.replace('_X', '').replace('_Y', '').replace('_Z', '')
        self.csv_data_loader.reset_index(base_sensor_type)
