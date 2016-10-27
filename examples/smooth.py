from machine import Pin
from neopixel import NeoPixel
from time import sleep

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

def smooth(old, new, wait_ms=10):
	colors = transition(old, new)
	for color in colors:
		for led in range(NUM_OF_LEDS):
			NEOPIXEL[led] = color
		NEOPIXEL.write()
		sleep(wait_ms/1000)

def transition(old, new):
	change = tuple(old-new for old, new in zip(old,new))
	largest_change = max((abs(delta) for delta in change))
	red = list(linspace(old[0], new[0], largest_change))
	green = list(linspace(old[1], new[1], largest_change))
	blue = list(linspace(old[2], new[2], largest_change))
	for color in zip(red,green,blue):
		yield color

def linspace(a,b, n=100):
	if n < 2:
		yield b
	diff = (float(b) - a)/(n - 1)
	for i in range(n):
		yield int(round(diff * i + a))

