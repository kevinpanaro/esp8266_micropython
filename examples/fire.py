from machine import Pin
from neopixel import NeoPixel
from time import sleep
from urandom import getrandbits
from hsv_to_rgb import hsv_to_rgb

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)
ORANGE_FLAME = .04 # hsv value, works better imho

def fire(color=ORANGE_FLAME, flicker_intensity=5):
	"""Wipe color across display a pixel at a time.
	color is the base color you want to flicked"""
	while True:
		for led in range(NUM_OF_LEDS):
			flicker = getrandbits(flicker_intensity)
			r, g, b = hsv_to_rgb(color, 1, (100-flicker)/100)
			NEOPIXEL[led] = tuple(int(x*255) for x in hsv_to_rgb(color, 1, (100-flicker)/100))
		NEOPIXEL.write()
		sleep((100-getrandbits(5))/1000.0)
