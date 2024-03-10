# RPI_SendBLEdataToMQTTBroker
Send/Receive data from BLE GAT server and relay it over to MQTT broker.

# Raspberry Pi GATT-to-MQTT Bridge

## Overview
This project implements a bridge between Bluetooth Low Energy (BLE) devices acting as GATT servers and an MQTT broker, running on a Raspberry Pi. It facilitates bidirectional communication between neighboring sensors (GATT servers) and a central MQTT broker, enabling seamless data exchange.

## Features
* GATT client functionality to receive data from neighboring sensors.
* MQTT client functionality to send data received from sensors to an MQTT broker.
* MQTT subscriber functionality to receive updates from the MQTT broker.
* GATT server functionality to send received MQTT updates back to neighboring sensors.

## Prerequisites
* Raspberry Pi running Raspbian or a compatible operating system.
* Python 3.x installed on the Raspberry Pi.
* Bluez library installed for Bluetooth Low Energy support (sudo apt-get install bluez).
* Paho MQTT library installed for MQTT communication (pip install paho-mqtt).

## Installation

* Clone the repository to your Raspberry Pi:
```
git clone https://github.com/yourusername/raspberry-pi-gatt-mqtt-bridge.git
```
* Navigate to the project directory:
```
cd src
```
* Install the required Python libraries:
```
Install_Dependencies.sh
```
## Configuration
Modify the config.py file to specify the MQTT broker's address and credentials, as well as any other configuration parameters specific to your setup.

## Usage
Run the gatt_to_mqtt_bridge.py script to start the GATT-to-MQTT bridge:
```
python scan.py
```
* Ensure that neighboring sensors (GATT servers) are powered on and advertising their GATT services.
* The bridge will automatically connect to neighboring sensors as GATT clients and begin receiving data.
* Data received from sensors will be published to the specified MQTT topics on the broker.
* Subscribe to MQTT topics to receive updates from the MQTT broker.
* Send data to the subscribed MQTT topics to have it forwarded to neighboring sensors as GATT server updates.

## Contributing
* Contributions are welcome! Please feel free to open an issue or submit a pull request for any improvements or fixes.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
* Special thanks to Paho MQTT for the MQTT client library.
* Thanks to the Raspberry Pi community for their valuable contributions and support.
Feel free to customize and expand upon this template to better suit your project's specifics and provide more detailed instructions as needed. Good luck with your project!
