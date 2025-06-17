from enum import Enum
import RPi.GPIO as gpio
import time

gpio.setwarnings(False)

class Control():
     def __init__(self, pin1 = 16):
          
          # direction pins
          self.operation = pin1
          self.initialise_pins()
          
     def initialise_pins(self):
          gpio.setmode(gpio.BCM)
          gpio.setup(self.operation, gpio.OUT)
          gpio.output(self.operation, gpio.HIGH)
          
     def enable(self):
          gpio.output(self.operation, gpio.LOW)
          time.sleep(0.1) # setup to low for a sec
          gpio.output(self.operation, gpio.HIGH)


     

