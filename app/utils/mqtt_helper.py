from model.option import Option
from utils.response import Response
import paho.mqtt.client as mqtt
import json
import os


class MQTTHelper():

    def __init__(self, container_id=None):
        '''Initializes the MQTT helper'''
        client_id = f"container-{container_id}" if container_id else None
        self.client = mqtt.Client(client_id=client_id)
        
        try:
            self.broker_address = os.getenv("MQTT_BROKER_ADDRESS")
            self.broker_port = int(os.getenv("MQTT_BROKER_PORT"))
        except ValueError:
            print("MQTT_BROKER_PORT ist kein gültiger Port")

    def connect(self):
        '''Connects to the MQTT broker'''

        # Check if broker address and port are set
        if self.broker_address is None:
            print("MQTT_BROKER_ADDRESS nicht gesetzt")
            return False
        elif self.broker_port is None:
            print("MQTT_BROKER_PORT nicht gesetzt")
            return False

        # Connect to broker
        self.client.connect(self.broker_address, self.broker_port)

    def publish(self, topic, data):
        '''Publish data to a MQTT topic'''

        if self.client is None:
            print("MQTT-Client nicht verbunden")
            return False
        
        # Prevent sending messages in demo mode
        is_demo_mode = Option.get_boolean('demo_mode')
        if is_demo_mode:
            return Response(False, "Demo-Modus aktiviert. Nachrichten werden nicht gesendet.")
        
        # Prevent manipulation of original data used in other places
        data_copy = data.copy()
        
        # Convert datetime to ISO format
        data_copy["timestamp"] = data_copy["timestamp"].isoformat()

        # Remove sendDuplicate flag
        send_duplicate = data_copy.get("sendDuplicate", False)
        data_copy.pop("sendDuplicate", None)

        # Convert the dictionary to JSON string
        message = json.dumps(data_copy)

        # Publish message
        for _ in range(1 if not send_duplicate else 2):
            print(f"Sending message '{message}' to topic '{topic}'")
            self.client.publish(topic, message)

        return Response(True, "Nachricht erfolgreich gesendet")

    def disconnect(self):
        '''Disconnects from the MQTT broker'''
        if self.client is None:
            print("MQTT-Client nicht verbunden")
            return False

        self.client.disconnect()

