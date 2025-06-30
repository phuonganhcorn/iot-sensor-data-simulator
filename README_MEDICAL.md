# Medical IoT Sensor Data Simulator

## Overview

This is a modified version of the IoT sensor data simulator specifically designed for medical/healthcare applications. It can simulate various medical sensors using real CSV data files, making it perfect for demonstrating medical data pipelines with blockchain integration.

## Supported Medical Sensors

The simulator supports the following medical sensor types:

- **ACC (Accelerometer)**: 3-axis accelerometer data (X, Y, Z)
- **BVP (Blood Volume Pulse)**: Blood volume pulse measurements
- **Dexcom**: Interstitial glucose concentration
- **EDA**: Electrodermal activity measurements
- **TEMP**: Skin temperature readings
- **IBI**: Interbeat interval data
- **HR**: Heart rate measurements
- **Food Log**: Food consumption tracking data

## CSV Data Format

### Single-Value Sensors (BVP, Dexcom, EDA, TEMP, IBI, HR)
```csv
Timestamp,Value
2020-02-21 09:19:06.000000,72.5
2020-02-21 09:19:07.000000,73.1
```

### Accelerometer Data (ACC)
```csv
Timestamp,X,Y,Z
2020-02-21 09:19:06.000000,0.123,0.456,0.789
2020-02-21 09:19:06.050000,0.124,0.457,0.790
```

### Food Log Data
```csv
date,time_of_day,logged_food,calorie,total_carb,protein,total_fat
2020-02-21,12:30:00,Apple,95,25,0.5,0.3
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Medical Data
1. Create a `medical_data` folder in the project root
2. Place your CSV files in this folder
3. Name files with sensor type prefix (e.g., `bvp_data.csv`, `hr_data.csv`, `acc_data.csv`)

### 3. Setup Medical Sensors
Run the setup script to create medical sensors:
```bash
python setup_medical_sensors.py
```

### 4. Run the Application
```bash
cd app
python main.py
```

## Architecture for Medical Data Pipeline

The simulator is designed to work with the following pipeline:

```
[Smart Medical Device]
     ↓
[Edge Gateway with AI Filter]
     ├─ Importance Classifier
     ├─ Anomaly Detector  
     └─ Privacy/PII Detector
     ↓ Score Aggregator → final_score
     ↓ If final_score > threshold:
[Batching]
     ├─ Batch records by time/count
     ├─ Create Merkle Tree → Merkle root
     └─ Encrypt metadata + off-chain key storage
     ↓
[Blockchain Smart Contract]
     ├─ Store Merkle root on-chain
     └─ Store hash(encrypted metadata) + access policy
     ↓
[Off-chain DB + Key Store]
     ├─ Store time-series data (human_id, record_id, timestamp, O₂, HR...)
     └─ Store decryption keys (with destroy capability)
```

## Medical Data Units

The simulator includes medical-specific units:

- **BVP**: Blood Volume Pulse
- **Glucose**: mg/dL
- **EDA**: microsiemens (μS)
- **Skin Temperature**: Celsius (°C)
- **IBI**: milliseconds (ms)
- **Heart Rate**: beats per minute (BPM)
- **Accelerometer**: g-force (g)
- **Nutrition**: calories (cal), grams (g)

## Features

### Real Data Simulation
- Uses actual CSV data instead of synthetic generation
- Maintains temporal relationships in medical data
- Supports continuous data streaming

### Medical-Specific Error Simulation
- Anomaly detection scenarios
- Missing data patterns (MCAR)
- Sensor drift simulation
- Duplicate data handling

### Integration Capabilities
- MQTT broker support
- Azure IoT Hub integration
- CSV/JSON/XLSX data export
- Real-time data visualization

### Demo Scenarios
Perfect for demonstrating:
- Medical data collection and transmission
- Edge computing with AI filtering
- Blockchain-based data integrity
- Privacy-preserving medical data sharing

## Usage Examples

### Basic Medical Data Streaming
1. Load your medical CSV files into the `medical_data` folder
2. Run the setup script to create sensors
3. Create a medical container in the web interface
4. Start simulation to stream data to MQTT/IoT Hub

### Blockchain Demo Pipeline
1. Configure edge gateway settings
2. Set up importance/anomaly thresholds
3. Enable batching and Merkle tree generation
4. Connect to blockchain smart contract
5. Monitor off-chain storage

## File Structure
```
medical_data/           # Your CSV files go here
├── bvp_sample.csv
├── hr_sample.csv  
├── acc_sample.csv
└── ...

app/
├── model/
│   ├── sensor.py       # Modified for medical data
│   └── ...
├── utils/
│   ├── csv_data_loader.py     # CSV data handling
│   ├── medical_simulator.py   # Medical data simulation
│   └── ...
└── constants/
    └── units.py        # Medical units definitions
```

## Contributing

When adding new medical sensor types:
1. Add appropriate units to `constants/units.py`
2. Update CSV data loader validation
3. Add sensor type detection logic
4. Update documentation

## License

Same as original project - see LICENSE.txt
