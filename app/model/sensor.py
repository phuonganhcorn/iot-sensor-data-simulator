from model.models import SensorModel
from utils.simulator import Simulator
from utils.medical_simulator import MedicalDataSimulator
from utils.csv_data_loader import CSVDataLoader
import threading
import os


class Sensor(SensorModel):
    '''This class represents a sensor.'''
    
    # Class-level CSV data loader - shared across all sensors
    _csv_data_loader = None
    _data_directory = None

    @classmethod
    def set_data_directory(cls, data_directory: str):
        '''Set the directory containing CSV medical data files.'''
        cls._data_directory = data_directory
        if data_directory and os.path.exists(data_directory):
            cls._csv_data_loader = CSVDataLoader(data_directory)
            # Auto-load all CSV files in the directory
            load_results = cls._csv_data_loader.auto_load_directory()
            print(f"Loaded medical data: {load_results}")
        else:
            print(f"Warning: Data directory not found: {data_directory}")
            cls._csv_data_loader = None

    @classmethod
    def get_csv_data_loader(cls):
        '''Get the CSV data loader instance.'''
        return cls._csv_data_loader

    @staticmethod
    def add(name, base_value, unit, variation_range, change_rate, interval, error_definition, device_id):
        '''Adds a new sensor to the database'''
        new_sensor = Sensor(name=name, base_value=base_value,
                            unit=unit, variation_range=variation_range, change_rate=change_rate, interval=interval, error_definition=error_definition, device_id=device_id)

        Sensor.session.add(new_sensor)
        Sensor.session.commit()

        return new_sensor

    @staticmethod
    def get_all():
        '''Returns all sensors'''
        return Sensor.session.query(Sensor).all()

    @staticmethod
    def get_all_by_ids(list_of_ids):
        '''Returns all sensors with the given ids'''
        return Sensor.session.query(Sensor).filter(Sensor.id.in_(list_of_ids)).all()
    
    @staticmethod
    def get_by_id(id):
        '''Returns a sensor by its id'''
        return Sensor.session.query(Sensor).filter(Sensor.id == id).first()

    @staticmethod
    def get_all_unassigned():
        '''Returns all sensors that are not assigned to a device'''
        return Sensor.session.query(Sensor).filter(Sensor.device_id == None).all()
    
    @staticmethod
    def check_if_name_in_use(name):
        return Sensor.session.query(Sensor).filter(Sensor.name.ilike(name)).first() is not None
    
    def start_simulation(self, callback):
        '''Starts the simulation using medical data if available, otherwise fallback to synthetic data.'''
        
        # Choose simulator based on data availability
        if self._csv_data_loader and self._is_medical_sensor():
            self.simulator = MedicalDataSimulator(sensor=self, csv_data_loader=self._csv_data_loader)
            print(f"Using medical data simulator for sensor: {self.name}")
        else:
            self.simulator = Simulator(sensor=self)
            print(f"Using synthetic data simulator for sensor: {self.name}")
        
        self.running = True
        timer = threading.Timer(interval=self.interval, function=self._callback, args=[callback])
        timer.start()

    def _is_medical_sensor(self) -> bool:
        '''Check if this is a medical sensor based on name or unit.'''
        name_lower = self.name.lower()
        medical_keywords = ['acc', 'bvp', 'dexcom', 'glucose', 'eda', 'temp', 'temperature', 
                          'ibi', 'heart', 'hr', 'food', 'medical', 'accelerometer', 
                          'electrodermal', 'interbeat', 'blood', 'oxygen', 'pressure']
        
        # Check if sensor name contains medical keywords
        for keyword in medical_keywords:
            if keyword in name_lower:
                return True
        
        # All units 0-19 are now medical units
        if 0 <= self.unit <= 19:
            return True
            
        return False

    def _callback(self, device_callback):
        '''Callback function for the simulation'''

        # Check if simulation is still running
        if self.running:
            data = self.simulator.generate_data()
            device_callback(self, data)

            # Repeat callback after interval
            timer = threading.Timer(
                interval=self.interval, function=self._callback, args=[device_callback])
            timer.start()

    def stop_simulation(self):
        '''Stops the simulation'''
        self.running = False

    def start_bulk_simulation(self, amount):
        '''Starts a bulk simulation and returns the generated data'''
        # Choose simulator based on data availability
        if self._csv_data_loader and self._is_medical_sensor():
            simulator = MedicalDataSimulator(sensor=self, csv_data_loader=self._csv_data_loader)
        else:
            simulator = Simulator(sensor=self)
            
        data = simulator.generate_bulk_data(amount)
        return data

    def delete(self):
        '''Deletes the sensor'''
        Sensor.session.delete(self)
        Sensor.session.commit()
