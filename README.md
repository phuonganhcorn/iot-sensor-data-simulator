# Medical IoT Sensor Data Simulator

## Overview
This repository contains the source code for a Medical Internet of Things (IoT) sensor data simulator. The simulator generates realistic medical sensor data for healthcare applications, research, and development purposes. It supports various medical sensors including heart rate monitors, blood pressure sensors, glucose monitors, accelerometers, and more.

The simulator can use real medical data from CSV files or generate synthetic data, making it perfect for testing healthcare IoT systems, medical data pipelines, and blockchain-based healthcare applications.

## Features
- **Real Medical Data Simulation**: Uses actual medical sensor data from CSV files (BVP, HR, ACC, EDA, Temperature, etc.)
- **Synthetic Data Generation**: Generates realistic medical sensor data when CSV files are not available
- **Medical Error States**: Simulates various medical sensor error conditions for realistic testing
- **Multiple Output Formats**: Sends data to Azure IoT Hub, MQTT brokers, or exports to CSV, XLSX, JSON
- **Healthcare-Focused UI**: Graphical user interface designed for medical sensor management
- **Blockchain Pipeline Ready**: Designed to support medical data blockchain pipelines with privacy features

## Medical Sensor Types Supported
- **ACC**: Accelerometer data (X, Y, Z orientation)
- **BVP**: Blood Volume Pulse measurements
- **Dexcom**: Interstitial glucose concentration
- **EDA**: Electrodermal activity
- **TEMP**: Skin temperature
- **IBI**: Interbeat interval
- **HR**: Heart rate
- **Food Log**: Nutritional intake data
- **SpO2**: Oxygen saturation
- **Blood Pressure**: Systolic and diastolic measurements

## Installation

Before you begin, ensure that you have Python 3.7+ installed on your system. You can download it from [here](https://www.python.org/downloads/).

Clone the repository:

```bash
git clone https://github.com/your-username/medical-iot-sensor-simulator
```

Navigate to the project directory:

```bash
cd medical-iot-sensor-simulator
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Setting up Medical Data

1. **Place your CSV files** in the `medical_data/` directory:
   - `bvp_sample.csv` - Blood volume pulse data
   - `hr_sample.csv` - Heart rate data  
   - `acc_sample.csv` - Accelerometer data
   - Add other medical data files as needed

2. **CSV Format Requirements**:
   - **Single-value sensors** (BVP, HR, EDA, etc.): `Timestamp, Value`
   - **Accelerometer**: `Timestamp, X, Y, Z`
   - **Food Log**: `date, time_of_day, logged_food, calorie, total_carb, protein, total_fat`

### Running the Simulator

```bash
python setup_medical_sensors.py  # Setup medical sensors in database
python app/main.py               # Start the simulator
```

Access the simulator at `http://localhost:8080`

### Quick Demo

Run a quick demo to see the medical data simulation in action:

```bash
python demo_medical_simulation.py
```

### Configuration for Data Transmission

#### Sending Data to Azure IoT Hub

To send medical data to Azure IoT Hub, create an `.env` file in the project root:

```bash
IOT_HUB_CONNECTION_STRING=YourConnectionStringHere
IOT_HUB_PRIMARY_KEY=YourPrimaryKeyHere
IOT_HUB_SECONDARY_KEY=YourSecondaryKeyHere
```

#### Sending Data to MQTT Broker

For MQTT broker connectivity, add these variables to your `.env` file:

```bash
MQTT_BROKER_ADDRESS=YourBrokerAddressHere
MQTT_BROKER_PORT=YourBrokerPortHere
```

## Medical Data Pipeline Architecture

This simulator is designed to support a complete medical data pipeline with blockchain integration:

```
📱 Medical Devices/Sensors
         ↓
🔍 Edge Gateway with AI Processing
   ├─ Medical Data Importance Classifier
   ├─ Health Anomaly Detector  
   ├─ Privacy/PII Protection
   └─ Data Quality Scoring
         ↓ (if score > threshold)
📦 Secure Data Batching
   ├─ Time-series aggregation
   ├─ Merkle Tree generation
   └─ Metadata encryption
         ↓
⛓️ Blockchain Smart Contract
   ├─ Merkle root storage
   ├─ Access control policies
   └─ Audit trail
         ↓
🗄️ Off-chain Storage
   ├─ Encrypted medical records
   ├─ Time-series databases
   └─ Key management system
```

## Sample Data Formats

The simulator includes sample medical data files:

- **BVP Data**: Blood volume pulse measurements
- **Heart Rate**: Continuous heart rate monitoring
- **Accelerometer**: 3-axis movement data for activity tracking
- **EDA**: Electrodermal activity for stress monitoring
- **Temperature**: Skin temperature measurements
- **Glucose**: Blood glucose level tracking
- **Food Log**: Nutritional intake tracking

## API Integration

The simulator provides RESTful APIs for:
- Real-time medical data streaming
- Historical data retrieval
- Sensor configuration management
- Alert and anomaly notifications

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/medical-enhancement`)
3. Commit your changes (`git commit -am 'Add new medical sensor support'`)
4. Push to the branch (`git push origin feature/medical-enhancement`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Medical data formats based on common healthcare IoT standards
- Blockchain integration designed for healthcare privacy compliance
- Built for research and development in digital health technologies

For brokers requiring authentication, you can provide a username and password:

```python
MQTT_BROKER_USERNAME=YourUsernameHere
MQTT_BROKER_PASSWORD=YourPasswordHere
```

Again, these details are optional and are not necessary to run the application without MQTT broker connectivity. Remember to restart the application if you made any changes during execution.

## Contribution

If you find any bugs or have a feature request, please open an issue on GitHub. I welcome any contributions, whether it's improving the documentation, fixing bugs, or implementing new features.

## Diagrams

Some parts of the code and design of the project are described in more detail by diagrams, which can be found in the `diagrams` folder in the project directory. These diagrams were created using [draw.io](https://www.drawio.com/).

To open and edit these diagrams you can use their [web application](https://app.diagrams.net/). Another way to view and modify the diagrams is to download and install the unofficial Visual Studio Code extension for draw.io from this [link](https://marketplace.visualstudio.com/items?itemName=hediet.vscode-drawio).

## License

This project is licensed under the terms of the [MIT](https://choosealicense.com/licenses/mit/) - see the [LICENSE](LICENSE.txt) file for details.
