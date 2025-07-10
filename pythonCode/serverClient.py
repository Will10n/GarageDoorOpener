import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import csv
import threading
import signalControl
from enum import Enum
import json
from datetime import datetime
from ultrasonicSensor import UltrasonicSensor

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

          self.gpio = signalControl.Control()
          self.curr_state = TransitionState.EXIT # set initial transition state
          self.prev_state = None
     
          # self.allowed_transitions = { # defines all allowable states
          #               TransitionState.EXIT: [TransitionState.ENTER, TransitionState.BUTTON, TransitionState.DWELL],
          #               TransitionState.ENTER: [TransitionState.DWELL, TransitionState.BUTTON],
          #               TransitionState.DWELL: [TransitionState.EXIT, TransitionState.BUTTON],
          #               TransitionState.BUTTON: [TransitionState.EXIT, TransitionState.BUTTON, TransitionState.DWELL],
          #               TransitionState.ERROR: [],
          #           }

          self.last_transition_time = 0
          self.transition_cooldown = 10

          self.sensor = UltrasonicSensor()

          # set running event thread
          self.running = threading.Event()
          self.running.set() # enable event thread

          self.sensor_thread = None # define for thread of sensor
          self.sensor_thread_event = threading.Event() # event to control sensor thread loop

     def MQTTConnect(self):

          print("Configuring MQTT Client")
          self.client = AWSIoTMQTTClient(self.config["client_id"])
          self.client.configureEndpoint(self.config["endpoint"],8883)
          self.client.configureCredentials(self.config["root_ca"], self.config["private_key"], self.config["certificate"])
          self.client.configureOfflinePublishQueueing(-1)
          self.client.configureDrainingFrequency(2)
          self.client.configureConnectDisconnectTimeout(10)
          self.client.configureMQTTOperationTimeout(5)

     def start_connection(self):
          print("Connecting to client...")
          self.client.connect()
          self.client.subscribe(topic=self.config["topic"], QoS=1, callback=self.callback)
          print("Successfully subscribed to topic")
     
     def callback(self, client, userdata, message):
          
          data = json.loads(message.payload.decode('utf-8'))
          print(data)
          
          transition_type = data["transition type"] # get transition type
          self.handle_transition(requested_state_val = transition_type)

     def handle_transition(self, requested_state_val):

          try:
               requested_state = TransitionState(requested_state_val)  # Ensure it's a valid enum
               current_state = self.curr_state # get current state

               if current_state != TransitionState.BUTTON:
                    self.prev_state = current_state # save the previous state

               # if ERROR state, immediately shutdown. 
               if requested_state == TransitionState.ERROR:
                    self.gpio.enable() # ditch and stop
                    self.curr_state = TransitionState.ERROR
                    self.errorShutdown()
                    return

               # Manual override (BUTTON)
               if requested_state == TransitionState.BUTTON:
                    self.gpio.enable()
                    self.curr_state = TransitionState.BUTTON # change state to button
                    self.start_sensor_thread() # enable sensor opeartion

               # Cooldown check
               current_time = time.time()
               if current_time - self.last_transition_time < self.transition_cooldown:
                    print("Transition blocked: cooldown period active.")
                    return
                    
               # # Valid transition check
               # if requested_state in self.allowed_transitions.get(current_state, []):

               if requested_state == TransitionState.ENTER: # entering, we enable sensor
                    self.start_sensor_thread()

               self.curr_state = requested_state # update current state
               print(f"Transitioned from {current_state.name} to {requested_state.name}.")
                    
               # else:
               #      print(f"Invalid transition from {current_state.name} to {requested_state.name}.")
               #      self.errorShutdown()

               # set latest transition time
               self.last_transition_time = current_time

               # Log the event to a CSV file
               with open("logfile.csv", mode="a", newline="") as file:
                  writer = csv.writer(file)
                  writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.prev_state.name, requested_state.name])

          except KeyError: # invalid transition occured
               print(f"Invalid transition type received: {data.get('transition type')}")
               self.errorShutdown()

          except Exception as e: # exception error occured
               print(f"Exception occurred in callback: {e}")
               self.errorShutdown()

                  
     def errorShutdown(self):
     
          print("Disconnecting MQTT broker")
          self.client.disconnect # disconnect from AWS Server
          self.running.clear()

          # log into csv file
          with open("logfile.csv", mode = "a", newline="") as file:
               writer = csv.writer(file)
               writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Terminating, entire system will shutdown..."])

     def run_sensor(self):

          persistence = 0

          # sensor enable timer
          sensor_start_time = time.time()
          sensor_timeout = 45
          
          while self.sensor_thread_event.is_set():

               dist = self.sensor.poll_sense()
               print(dist)
               current_time = time.time()
               
               # Entering, once less than 50, car is in
               if (self.curr_state == TransitionState.ENTER):

                    if dist < 50:
                         persistence +=1

                         if persistence > 8:
                              time.sleep(5) # wait 5 seconds before actuating
                              self.gpio.enable()
                              self.handle_transition(TransitionState.DWELL.value) # transition to dwell from enter
                              self.stop_sensor_thread() # clear sensor thread

               # Button is enabled
               elif self.curr_state == TransitionState.BUTTON:
 
                    if dist > 150:
                         persistence +=1

                         if persistence > 7:
                              time.sleep(5)
                              self.gpio.enable()
                              self.stop_sensor_thread()
                    
               else:
                    persistence = 0 # reset persistence due to maybe noise
                    
               # sensor enabled too long, revert back to previous state
               if current_time - sensor_start_time > sensor_timeout:
                    self.handle_transition(self.prev_state)
                    self.gpio.enable()
                    self.stop_sensor_thread()

               time.sleep(0.5) # sense every 500ms

     def start_sensor_thread(self):
          if self.sensor_thread is None or not self.sensor_thread.is_alive():
               self.sensor_thread_event.set()  # Enable the thread loop
               self.sensor_thread = threading.Thread(target=self.run_sensor, daemon=True)
               self.sensor_thread.start()
               print("Sensor polling thread started.")

     def stop_sensor_thread(self):
          if self.sensor_thread is not None and self.sensor_thread.is_alive():
               self.sensor_thread_event.clear()  # Signal thread to stop
               self.sensor_thread = None # Stop polling thread
               print("Sensor polling thread stopped.")
                    
def main():

     client = serverClient()
     client.MQTTConnect() # connect to IoT cloud
     client.start_connection() # start connection for messages

     try:
          print("Client running. Press Ctrl+C to exit.")
          while True:
               if not client.running.is_set():
                    break
               time.sleep(1)  # Main thread can perform other tasks if needed
     except KeyboardInterrupt:
          print("\nKeyboard Interrupt occured, Stopping services...")
 
if __name__ == "__main__":
     main()