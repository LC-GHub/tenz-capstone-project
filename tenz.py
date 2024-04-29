import time
import RPi.GPIO as GPIO

# GPIO pin number of LED
LED = 22
# Setup GPIO as output
def set_up_GPIO():
    print("Set up GPIO start")
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.output(LED, GPIO.LOW)
    print("Set up GPIO end")
def set_GPIO_High():
    set_up_GPIO()
    GPIO.output(LED, GPIO.HIGH)
    GPIO.cleanup()
    print("low set")

def set_GPIO_low():
    set_up_GPIO()
    GPIO.output(LED, GPIO.LOW)
    GPIO.cleanup()
    print("low set")

def GPIO_cleanup():
    GPIO.cleanup()

def shock():
    set_up_GPIO()
    print("shock start")
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED, GPIO.LOW)
    print("shock ended")
    GPIO_cleanup()

set_up_GPIO()
GPIO.output(LED, GPIO.LOW)
GPIO.cleanup()
