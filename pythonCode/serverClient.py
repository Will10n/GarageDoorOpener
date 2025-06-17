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
          
          with open("config.csv", mode='r') as file:
               reader = csv.DictReader(file)
               for row in reader:
                    self.config[row['key']] = row['value']
                    
          self.client = None
     
          
          self.running = False
          self.gpio = signalControl.Control()
          self.gpio.TransitionState = TransitionState.EXIT
          self.pending = False
          
          self.allowed_transitions = { # defines all allowable states
                        TransitionState.EXIT: [TransitionState.ENTER],
                        TransitionState.ENTER: [TransitionState.DWELL],
                        TransitionState.DWELL: [TransitionState.EXIT, TransitionState.BUTTON],
                        TransitionState.BUTTON: [TransitionState.EXIT, TransitionState.BUTTON],
                        TransitionState.ERROR: [],
                    }
                    
          self.last_transition_time = 0
          self.transition_cooldown = 20

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
          
          try:
               data = json.loads(message.payload.decode('utf-8'))
               print(data)

               
               requested_state = TransitionState(data["transition type"])  # Ensure it's a valid enum
               current_state = self.gpio.TransitionState # get current state

               # Cooldown check
               current_time = time.time()
               if current_time - self.last_transition_time < self.transition_cooldown:
                    print("Transition blocked: cooldown period active.")
                    return
                     
               if requested_state == TransitionState.ERROR:
                    self.errorShutdown()
                    return
               
                # Manual override (BUTTON)
               if requested_state == TransitionState.BUTTON:
                    self.gpio.enable()
                    self.gpio.TransitionState = TransitionState.BUTTON
                    print("Manual BUTTON press: transition applied.")
                    
                # Valid transition check
               elif requested_state in self.allowed_transitions.get(current_state, []):
                    self.gpio.enable()
                    self.gpio.TransitionState = requested_state
                    print(f"Transitioned from {current_state.name} to {requested_state.name}.")
               else:
                    print(f"Invalid transition from {current_state.name} to {requested_state.name}.")
                    self.errorShutdown()
                    return

               # set latest transition time
               self.last_transition_time = current_time

               
               # Log the event to a CSV file
               with open("logfile.csv", mode="a", newline="") as file:
                  writer = csv.writer(file)
                  writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.gpio.TransitionState.name, data["transition type"]])

          except KeyError:
           print(f"Invalid transition type received: {data.get('transition type')}")
           self.errorShutdown()

          except Exception as e:
           print(f"Exception occurred in callback: {e}")
           self.errorShutdown()
                  
     def errorShutdown(self):
          self.gpio.TransitionState = TransitionState.ERROR
          self.client.disconnect
          self.running = False
          print("Transition error")
          
          return

     
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




