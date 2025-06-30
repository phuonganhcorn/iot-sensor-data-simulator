"""
Medical Sensor Setup Helper

This script helps create medical sensors for the IoT simulator.
Run this script to automatically create medical sensors based on available CSV data.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.models import Base
from model.sensor import Sensor
from model.device import Device
from model.container import Container
from model.option import Option

def setup_medical_sensors():
    """Setup medical sensors in the database."""
    
    # Setup database
    engine = create_engine('sqlite:///app/telemetry_simulator.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Set database session for all models
    Option.session = session
    Container.session = session
    Device.session = session
    Sensor.session = session
    
    # Initialize medical data
    medical_data_dir = os.path.join(os.path.dirname(__file__), 'medical_data')
    Sensor.set_data_directory(medical_data_dir)
    
    # Create medical sensors based on available data
    medical_sensors = [
        {
            'name': 'Blood Volume Pulse Sensor',
            'base_value': 0.0,
            'unit': 0,  # BVP unit
            'variation_range': 0.1,
            'change_rate': 0.01,
            'interval': 1.0,
            'error_definition': None
        },
        {
            'name': 'Heart Rate Monitor',
            'base_value': 75.0,
            'unit': 5,  # HR unit
            'variation_range': 15.0,
            'change_rate': 2.0,
            'interval': 1.0,
            'error_definition': None
        },
        {
            'name': 'Accelerometer X-Axis',
            'base_value': 0.0,
            'unit': 6,  # ACC X unit
            'variation_range': 1.0,
            'change_rate': 0.1,
            'interval': 0.05,
            'error_definition': None
        },
        {
            'name': 'Accelerometer Y-Axis',
            'base_value': 0.0,
            'unit': 7,  # ACC Y unit
            'variation_range': 1.0,
            'change_rate': 0.1,
            'interval': 0.05,
            'error_definition': None
        },
        {
            'name': 'Accelerometer Z-Axis',
            'base_value': 0.0,
            'unit': 8,  # ACC Z unit
            'variation_range': 1.0,
            'change_rate': 0.1,
            'interval': 0.05,
            'error_definition': None
        },
        {
            'name': 'Glucose Monitor',
            'base_value': 100.0,
            'unit': 1,  # Glucose unit
            'variation_range': 50.0,
            'change_rate': 5.0,
            'interval': 300.0,  # 5 minutes
            'error_definition': None
        },
        {
            'name': 'Skin Temperature Sensor',
            'base_value': 36.5,
            'unit': 3,  # Skin temp unit
            'variation_range': 2.0,
            'change_rate': 0.2,
            'interval': 5.0,
            'error_definition': None
        },
        {
            'name': 'EDA Sensor',
            'base_value': 5.0,
            'unit': 2,  # EDA unit
            'variation_range': 3.0,
            'change_rate': 0.5,
            'interval': 1.0,
            'error_definition': None
        },
        {
            'name': 'Oxygen Saturation Monitor',
            'base_value': 98.0,
            'unit': 15,  # SpO2 unit
            'variation_range': 5.0,
            'change_rate': 1.0,
            'interval': 2.0,
            'error_definition': None
        },
        {
            'name': 'Blood Pressure Monitor (Systolic)',
            'base_value': 120.0,
            'unit': 13,  # BP Systolic unit
            'variation_range': 20.0,
            'change_rate': 3.0,
            'interval': 30.0,
            'error_definition': None
        }
    ]
    
    # Create a medical device if it doesn't exist
    medical_device = Device.session.query(Device).filter(Device.name == 'Medical Wearable Device').first()
    if not medical_device:
        medical_device = Device(
            name='Medical Wearable Device',
            generation_id=1,
            etag='medical_device_etag',
            status='enabled',
            connection_string='',
            container_id=None
        )
        Device.session.add(medical_device)
        Device.session.commit()
        print(f"Created medical device: {medical_device.name}")
    
    # Create sensors
    created_sensors = []
    for sensor_data in medical_sensors:
        # Check if sensor already exists
        existing_sensor = Sensor.session.query(Sensor).filter(
            Sensor.name == sensor_data['name']
        ).first()
        
        if not existing_sensor:
            new_sensor = Sensor(
                name=sensor_data['name'],
                base_value=sensor_data['base_value'],
                unit=sensor_data['unit'],
                variation_range=sensor_data['variation_range'],
                change_rate=sensor_data['change_rate'],
                interval=sensor_data['interval'],
                error_definition=sensor_data['error_definition'],
                device_id=medical_device.id
            )
            Sensor.session.add(new_sensor)
            created_sensors.append(new_sensor)
            print(f"Created sensor: {sensor_data['name']}")
        else:
            print(f"Sensor already exists: {sensor_data['name']}")
    
    Sensor.session.commit()
    
    # Create a medical container if it doesn't exist
    medical_container = Container.session.query(Container).filter(
        Container.name == 'Medical Data Pipeline Demo'
    ).first()
    
    if not medical_container:
        medical_container = Container(
            name='Medical Data Pipeline Demo',
            description='Container for demonstrating medical data pipeline with blockchain integration',
            location='Edge Gateway',
            is_active=False,
            start_time=None
        )
        Container.session.add(medical_container)
        Container.session.commit()
        
        # Assign the medical device to the container
        medical_device.container_id = medical_container.id
        Container.session.commit()
        
        print(f"Created medical container: {medical_container.name}")
        print(f"Assigned medical device to container")
    else:
        print(f"Medical container already exists: {medical_container.name}")
    
    print(f"\nSetup complete!")
    print(f"- Created {len(created_sensors)} new sensors")
    print(f"- Medical device ID: {medical_device.id}")
    print(f"- Medical container ID: {medical_container.id}")
    
    # Get CSV data loader info
    csv_loader = Sensor.get_csv_data_loader()
    if csv_loader:
        available_types = csv_loader.get_available_sensor_types()
        print(f"- Available CSV data types: {available_types}")
        for sensor_type in available_types:
            count = csv_loader.get_data_count(sensor_type)
            print(f"  - {sensor_type}: {count} data points")
    else:
        print("- No CSV data loader available")
    
    session.close()

if __name__ == "__main__":
    setup_medical_sensors()
