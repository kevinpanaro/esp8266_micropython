from machine import Pin
from neopixel import NeoPixel
from time import sleep
from hsv_to_rgb import hsv_to_rgb

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)
SEPERATION = 36

def rainbow(wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(101*iterations):
		print(j)
		for i in range(NUM_OF_LEDS):
			r,g,b = hsv_to_rgb(float(j)/float(100)+i/SEPERATION, 1, .1)
			NEOPIXEL[i] = (int(r*255), int(g*255), int(b*255))
		NEOPIXEL.write()
		sleep(wait_ms/1000)
