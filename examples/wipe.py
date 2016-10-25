from machine import Pin
from neopixel import NeoPixel
from time import sleep

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

def wipe(wait_ms=50, color=(255, 0, 0)):
	"""Wipe color across display a pixel at a time."""
	for x in range(NUM_OF_LEDS):
		for i in range(NUM_OF_LEDS):
			if x == i:
				NEOPIXEL[x] = color
			else:
				NEOPIXEL[i] = (0,0,0)
		NEOPIXEL.write()
		sleep(wait_ms/1000.0)
