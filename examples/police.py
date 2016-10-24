from machine import Pin
from neopixel import NeoPixel
from time import sleep

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

def police(wait_ms=250, iterations=10):
	side_1 = list(range(0, int(NUM_OF_LEDS/2)))
	side_2 = list(range(int(NUM_OF_LEDS/2), NUM_OF_LEDS))
	for run in range(iterations):
		for side in side_1:
			NEOPIXEL[side] = (255, 0, 0)
		for side in side_2:
			NEOPIXEL[side] = (0, 0, 255)
		side_1, side_2 = side_2, side_1
		NEOPIXEL.write()
		sleep(wait_ms/1000.0)