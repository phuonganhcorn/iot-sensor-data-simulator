#!/usr/bin/env python3
"""
Medical IoT Sensor Data Simulator Demo

This script demonstrates the medical sensor data simulation capabilities.
It shows how the simulator can work with real medical data for healthcare IoT applications
and blockchain-based medical data pipelines.
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model.models import Base
from model.sensor import Sensor
from model.device import Device
from model.container import Container
from model.option import Option
from utils.csv_data_loader import CSVDataLoader
from utils.medical_simulator import MedicalDataSimulator

def demo_medical_simulation():
    """Demonstrate medical sensor data simulation."""
    
    print("🏥 Medical IoT Sensor Data Simulator Demo")
    print("=" * 50)
    
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
    print(f"📂 Loading medical data from: {medical_data_dir}")
    Sensor.set_data_directory(medical_data_dir)
    
    csv_loader = Sensor.get_csv_data_loader()
    if csv_loader:
        available_types = csv_loader.get_available_sensor_types()
        print(f"✅ Available medical data types: {available_types}")
        for sensor_type in available_types:
            count = csv_loader.get_data_count(sensor_type)
            print(f"   📊 {sensor_type}: {count} data points")
    else:
        print("❌ No medical data found")
        return
    
    print("\n" + "=" * 50)
    print("🔬 Creating Medical Sensors")
    
    # Get or create medical sensors
    sensors = Sensor.get_all()
    if not sensors:
        print("📝 No sensors found. Please run 'python setup_medical_sensors.py' first")
        return
    
    medical_sensors = [s for s in sensors if s._is_medical_sensor()]
    print(f"✅ Found {len(medical_sensors)} medical sensors")
    
    for sensor in medical_sensors[:5]:  # Demo with first 5 sensors
        print(f"   🩺 {sensor.name} (Unit: {sensor.unit})")
    
    print("\n" + "=" * 50)
    print("⚡ Simulating Medical Data")
    
    # Demonstrate data generation
    for i, sensor in enumerate(medical_sensors[:3]):  # Demo with 3 sensors
        print(f"\n📈 Sensor: {sensor.name}")
        
        # Create medical simulator
        if csv_loader:
            simulator = MedicalDataSimulator(sensor=sensor, csv_data_loader=csv_loader)
        else:
            print("   ⚠️ Using synthetic data (no CSV data available)")
            continue
        
        # Generate some sample data
        print("   Generating 5 data points...")
        for j in range(5):
            data = simulator.generate_data()
            if data:
                timestamp = data['timestamp']
                value = data['value']
                unit_id = data['unit']
                from constants.units import UNITS
                unit_info = UNITS[unit_id] if unit_id < len(UNITS) else {"unit_abbreviation": "?"}
                unit_abbrev = unit_info['unit_abbreviation']
                
                if isinstance(timestamp, str):
                    time_str = timestamp[:19]  # Remove microseconds for display
                else:
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                
                print(f"   📊 [{time_str}] {value} {unit_abbrev}")
            else:
                print("   ⚠️ No data generated")
            
            time.sleep(0.5)  # Small delay for demo effect
    
    print("\n" + "=" * 50)
    print("🔗 Blockchain Pipeline Integration")
    print("""
    This medical sensor data can be integrated into a blockchain-based
    healthcare data pipeline:
    
    📱 Smart Device (Sensors)
         ↓
    🔍 Edge Gateway with AI Filter
         ├─ Importance Classifier
         ├─ Anomaly Detector  
         └─ Privacy/PII Detector
         ↓ Score Aggregator → final_score
         ↓ If final_score > threshold:
    📦 Batching
         ├─ Group records by time/count
         ├─ Create Merkle Tree → Merkle root
         └─ Encrypt metadata + store keys off-chain
         ↓
    ⛓️ Blockchain Smart Contract
         ├─ Store Merkle root on-chain
         └─ Store hash(encrypted metadata) + access policy
         ↓
    🗄️ Off-chain DB + Key Store
         ├─ Store time-series data (human_id, record_id, timestamp, O₂, HR...)
         └─ Store keys to decrypt metadata or destroy when needed
    """)
    
    print("\n" + "=" * 50)
    print("✅ Demo Complete!")
    print("\nTo start the full simulator with GUI:")
    print("python app/main.py")
    
    session.close()

if __name__ == "__main__":
    demo_medical_simulation()
