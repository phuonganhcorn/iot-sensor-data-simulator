import paho.mqtt.client as mqtt
import json
import os


class MQTTHelper():

    def __init__(self):
        self.client = None
        
        try:
            self.broker_address = os.getenv("MQTT_BROKER_ADDRESS")
            self.broker_port = int(os.getenv("MQTT_BROKER_PORT"))
        except ValueError:
            print("MQTT_BROKER_PORT ist kein gültiger Port")

    def connect(self, container_id=None):
        if self.broker_address is None:
            print("MQTT_BROKER_ADDRESS nicht gesetzt")
            return False
        elif self.broker_port is None:
            print("MQTT_BROKER_PORT nicht gesetzt")
            return False

        # MQTT-Client erstellen
        client_id = f"container-{container_id}" if container_id else None
        self.client = mqtt.Client(client_id=client_id)

        # Mit dem MQTT-Broker verbinden
        self.client.connect(self.broker_address, self.broker_port)

    def publish(self, topic, data):
        if self.client is None:
            print("MQTT-Client nicht verbunden")
            return False

        # MQTT-Nachricht senden
        message = json.dumps(data)
        print(f"Sending message '{message}' to topic '{topic}'")
        self.client.publish(topic, message)

    def disconnect(self):
        if self.client is None:
            print("MQTT-Client nicht verbunden")
            return False

        # Verbindung zum Broker trennen
        self.client.disconnect()

