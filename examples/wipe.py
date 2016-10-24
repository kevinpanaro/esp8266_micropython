from machine import Pin
from neopixel import NeoPixel
from time import sleep

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

def wipe(wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for x in range(NUM_OF_LEDS):
		for i in range(NUM_OF_LEDS):
			if x == i:
				NEOPIXEL[x] = (100, 0, 15)
			else:
				NEOPIXEL[i] = (0,0,0)
		NEOPIXEL.write()
		sleep(wait_ms/1000.0)
