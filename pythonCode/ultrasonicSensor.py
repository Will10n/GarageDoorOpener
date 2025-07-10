import RPi.GPIO as gpio
import time

class UltrasonicSensor:
     def __init__(self, echo = 5, trig = 6):

          self.echo = echo
          self.trig = trig
          self.initialise_pins()

     def initialise_pins(self):
          gpio.setmode(gpio.BCM)
          gpio.setup(self.trig, gpio.OUT)
          gpio.setup(self.echo, gpio.IN)

     def poll_sense(self):

          # Ensure trigger is low
          gpio.output(self.trig, False)
          time.sleep(0.000002)  # 2 microseconds delay (corrected from 0.0002)

          gpio.output(self.trig, True)
          time.sleep(0.00001) # enable trigger for 1ms
          gpio.output(self.trig, False)

          # Measure echo pulse duration
          start_time = time.time()
          stop_time = time.time()

          # Wait for echo to start (with timeout to prevent hanging)
          while gpio.input(self.echo) == 0:
               start_time = time.time()

          # Wait for echo to end (with timeout)
          while gpio.input(self.echo) == 1:
               stop_time = time.time()


          # Calculate distance
          pulse_duration = stop_time - start_time
          distance = pulse_duration * 17150  # Speed of sound ÷ 2
          distance = round(distance, 2)  # Round to 2 decimal places

          return distance
          
if __name__ == "__main__":

     gpio.setwarnings(False)

     sensor = UltrasonicSensor()

     sensor.initialise_pins()

     while True:
          dist = sensor.poll_sense()

          print(dist)

          
