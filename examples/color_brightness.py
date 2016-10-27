from . import fire
# from ..tools.hsv_to_rgb import hsv_to_rgb as htr
# from tools.rgb_to_hsv import rgb_to_hsv as rth
# from tools.hsv_to_rgb import hsv_to_rgb as htr
# from tools.rgb_to_hsv import rgb_to_hsv as rth
# from machine import Pin
# from neopixel import NeoPixel
# from time import sleep

# LED_PIN = 5
# NUM_OF_LEDS = 6
# PIN = Pin(LED_PIN, Pin.OUT)
# NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

color = (234,31,69)
r = color[0]
g = color[1]
b = color[2]

def get_hsv_value(colors):
    '''returns value in hsv'''
    r, g, b = [color/255.0 for color in colors]
    h, s, v = rth(r, g, b)
    return h, s, v

def get_rgb_value(color, new_v):
    h, s, _ = get_hsv_value(color)
    r, g, b = [int(round(color*255)) for color in htr(h, s, new_v)]
    return r, g, b

print(get_hsv_value([123,121,123]))