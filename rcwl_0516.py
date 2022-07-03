import RPi.GPIO as GPIO
import config as cfg
#from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(cfg.SENSOR_PIN, GPIO.IN)


#  _____________ 3V3 -> /
#  |        |___ GND -> GROUND (PIN 6)
#  |  RCWL  |___ OUT -> GPIO 4 (PIN 7)
#  |  0516  |___ VIN -> 5V     (PIN 2)
#  |________|___ CDS -> /
#

class RCWL_0516():
    
    def __init__(self, callback, sensor_pin=cfg.SENSOR_PIN):
        self.sensor_pin = sensor_pin
        self.callback = callback

    def detect(self):
        GPIO.add_event_detect(self.sensor_pin, GPIO.BOTH, callback=self.forwarder)

    def forwarder(self, channel):
        print(GPIO.input(self.sensor_pin))
        self.callback(GPIO.input(self.sensor_pin))
        
if __name__ == '__main__':
    
    def callback(b):
        print(b)
    
    radar = RCWL_0516(callback)
    
    while True:
        sleep(5)
        