from machine import Pin
from neopixel import NeoPixel
from time import sleep
from urandom import getrandbits

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

def strobe(wait_ms=75, iterations=50):
	"""Wipe color across display a pixel at a time."""
	for run in range(iterations):
		if run % 2 == 0:
			for led in range(NUM_OF_LEDS):
				NEOPIXEL[led] = (255, 255, 255)
		else:
			for led in range(NUM_OF_LEDS):
				NEOPIXEL[led] = (0, 0, 0)
		NEOPIXEL.write()
		sleep(wait_ms/1000.0)
