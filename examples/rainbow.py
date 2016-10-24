from machine import Pin
from neopixel import NeoPixel
from time import sleep
LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)
SEPERATION = 36

def rainbow(wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(101*iterations):
		for i in range(NUM_OF_LEDS):
			r,g,b = hsv_to_rgb(float(j)/float(100)+i/SEPERATION, 1, .1)
			NEOPIXEL[i] = (int(r*255), int(g*255), int(b*255))
		NEOPIXEL.write()
		sleep(wait_ms/1000)

def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q

