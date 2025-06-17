import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import csv
import threading
import signalControl
from enum import Enum
import json
from datetime import datetime


class TransitionState(Enum):
     ENTER = 0
     EXIT = 1
     DWELL = 2
     BUTTON = 3
     ERROR = 4

class serverClient:
     def __init__(self):
          self.config = {}
          
          with open("config.csv.txt", mode='r') as file:
               reader = csv.DictReader(file)
               for row in reader:
                    self.config[row['key']] = row['value']
                    
          self.client = None
          
          
          self.running = False
          self.gpio = signalControl.Control()
          self.gpio.TransitionState = TransitionState.DWELL
          self.pending = False

     def MQTTConnect(self):

          print("Configuring MQTT Client")
          self.client = AWSIoTMQTTClient(self.config["client_id"])
          self.client.configureEndpoint(self.config["endpoint"],8883)
          self.client.configureCredentials(self.config["root_ca"], self.config["private_key"], self.config["certificate"])
          self.client.configureOfflinePublishQueueing(-1)
          self.client.configureDrainingFrequency(2)
          self.client.configureConnectDisconnectTimeout(10)
          self.client.configureMQTTOperationTimeout(5)

     def start_polling(self):
          print("Connecting to client...")
          self.client.connect()
          self.running = True
          self.client.subscribe(topic=self.config["topic"], QoS=1, callback=self.callback)
          print("Subscribed to topic")
     
     def callback(self, client, userdata, message):
          data = json.loads(message.payload.decode('utf-8'))
          print(data)
          
          if self.pending:
               time.sleep(20) # 15 seconds to prevent garage from doing sending consecutive data
               self.pending = False
          
          if data["transition type"] == TransitionState.ENTER:
               self.gpio.enable()
               self.gpio.TransitionState = TransitionState.ENTER
               
          elif data["transition type"] == TransitionState.EXIT:
               self.gpio.enable()
               self.gpio.TransitionState = TransitionState.EXIT
               
          elif data["transition type"] == TransitionState.DWELL:
               self.gpio.TransitionState = TransitionState.DWELL
               
          elif data["transition type"] == TransitionState.ERROR:
               self.gpio.TransitionState = TransitionState.ERROR
               self.client.disconnect
               self.running = False
               print("Transition error")
               
          elif data["transition type"] == TransitionState.BUTTON:
               self.enable()
               self.gpio.TransitionState = TransitionState.BUTTON

          else:
               print(f"ERROR invalid transition type {data['transition type']}")
               
          self.pending = True
          
          # Log the event to a CSV file
          with open("logfile.csv", mode="a", newline="") as file:
             writer = csv.writer(file)
             writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.gpio.TransitionState.name, data["transition type"]])

     
def main():

     client = serverClient()
     client.MQTTConnect() # connect to IoT cloud
     client.start_polling() # start polling for messages

     try:
          print("Client running. Press Ctrl+C to exit.")
          while True:
               if client.running == False:
                    break
               time.sleep(1)  # Main thread can perform other tasks if needed
     except KeyboardInterrupt:
          print("\nStopping services...")

if __name__ == "__main__":
     main()




