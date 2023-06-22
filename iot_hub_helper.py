import time
import json
from azure.iot.device import IoTHubDeviceClient, Message

class IoTHubHelper:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.device_client = None
        self.init_device_client()

    def init_device_client(self):
        self.device_client = IoTHubDeviceClient.create_from_connection_string(self.connection_string)

    def send_telemetry_messages(self, telemetry_messages):
        try:
            if not self.device_client:
                self.init_device_client()

            print("Start sending telemetry messages")
            for msg in telemetry_messages:
                # Convert the dictionary to JSON string
                json_data = json.dumps(msg)

                # Build the message with JSON telemetry data
                message = Message(json_data)

                # Send the message.
                print("Sending message: {}".format(message))
                self.device_client.send_message(message)
            print("All messages successfully sent")
            return Response(True, "All messages successfully sent")
            
        except Exception as e:
            print(e)
            return Response(False, "Error sending telemetry messages: {}".format(e))

class Response:
    def __init__(self, success, message):
        self.success = success
        self.message = message