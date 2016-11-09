from hsv_to_rgb import hsv_to_rgb as htr
from rgb_to_hsv import rgb_to_hsv as rth
from simple import MQTTClient
from neopixel import NeoPixel
from machine import Pin
from time import sleep
from sys import exit
import ubinascii
import machine
import network
# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
'''
light:
  - platform: mqtt
    name: test
    state_topic: 'led/status'
    command_topic: 'led/switch'
    brightness_state_topic: 'led/brightness/status'
    brightness_command_topic: 'led/brightness/set'
    rgb_state_topic: 'led/rgb/status'
    rgb_command_topic: 'led/rgb/set'

switch:
  - platform: mqtt
    name: test mqtt kill switch
    command_topic: 'led/kill'
    state_topic: 'led/alive'
    payload_on: "alive"
    payload_off: "dead"
'''
# Wifi 
SSID = ""
PASS = ""

# MQTT server to connect to 
SERVER = "192.168.0.102" 
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
STATE_TOPIC= b"led/status"
COMMAND_TOPIC = b"led/switch"
BRIGHTNESS_STATE_TOPIC = b'led/brightness/status'
BRIGHTNESS_COMMAND_TOPIC = b'led/brightness/set'
RGB_STATE_TOPIC = b'led/rgb/status'
RGB_COMMAND_TOPIC = b'led/rgb/set'

# extra topics
KILL_COMMAND_TOPIC = b'led/kill'
KILL_STATE_TOPIC = b'led/alive'
SCENES_COMMAND_TOPIC = b'led/scene/set'
SCENES_STATE_STOPIC = b'leb/scene/status'

# Pin for NODEMCU and Neopixel
LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)
BRIGHTNESS_STATE = 0    # last known brightness state (DO NOT NEED)
STATE = "OFF"           # last known state (ON, OFF)
RGB_STATE = (0, 0, 0)   # last known set RGB state 
LIGHT_STATE = (0, 0, 0) # last known light state

def publish_payload(topic, payload):
    '''publish to a topic with a payload'''
    c.publish(topic, str(payload))
    print("[Publish]\t%s => %s" % (topic, str(payload)))

def get_hsv_value(colors):
    '''returns value in hsv'''
    r, g, b = [int(color) / 255.0 for color in colors]
    h, s, v = rth(r, g, b)
    return h, s, v

def get_rgb_value(color, new_value):
    '''returns value in rgb'''
    h, s, _ = get_hsv_value(color)
    r, g, b = [int(round(color * 255)) for color in htr(h, s, new_value)]
    return r, g, b

def set_led(new=(0, 0, 0), smooth=50, transition=0):
    '''
    new is the new color (RED, GREEN, BLUE)
    smooth is how many "frames" of color to create and display
    transition is seconds to transit from one color to the next
    transition is 0 right now, but will be implimented with MQTT JSON
    '''
    global LIGHT_STATE
    for color in linspace(LIGHT_STATE, new, smooth):
        for led in range(NUM_OF_LEDS):
            NEOPIXEL[led] = color
        NEOPIXEL.write()
        sleep(transition/smooth)
    LIGHT_STATE = new

def linspace(old, new, n=50):
    if n < 2:
        yield new
    old_red, old_green, old_blue = old
    new_red, new_green, new_blue = new
    diff_red = (float(new_red) - old_red)/(n-1)
    diff_green = (float(new_green) - old_green)/(n-1)
    diff_blue = (float(new_blue) - old_blue)/(n-1)
    for i in range(n):
        red = int(round(diff_red * i + old_red))
        green = int(round(diff_green * i + old_green))
        blue = int(round(diff_blue * i + old_blue))
        yield (red, green, blue)

def sub_cb(topic, msg):
    global STATE
    global RGB_STATE
    if topic == COMMAND_TOPIC:
        if msg == b"ON" and STATE == "OFF":
            STATE = "ON"
            RGB_STATE = (255, 255, 255)
            publish_payload(STATE_TOPIC, "ON")
            publish_payload(BRIGHTNESS_STATE_TOPIC, 255)
            set_led(new=RGB_STATE, smooth=75)
        elif msg == b"OFF" and STATE == "ON":
            STATE = "OFF"
            RGB_STATE = (0, 0, 0)
            publish_payload(STATE_TOPIC, "OFF")
            publish_payload(BRIGHTNESS_STATE_TOPIC, 0)
            set_led()
    elif topic == BRIGHTNESS_COMMAND_TOPIC:
        brightness = int(msg)
        if brightness < 0 or brightness > 255:
            return
        else:
            colors = tuple(get_rgb_value(RGB_STATE, brightness/255.0))
            publish_payload(BRIGHTNESS_STATE_TOPIC, brightness)
            publish_payload(RGB_STATE_TOPIC, ",".join([str(color) for color in colors]))
            set_led(new=colors, smooth=75)
    elif topic == RGB_COMMAND_TOPIC:
        colors = msg.decode("utf-8").split(',')
        RGB_STATE = colors
        _, _, v = get_hsv_value(colors)
        publish_payload(BRIGHTNESS_STATE_TOPIC, int(v*255))
        publish_payload(RGB_STATE_TOPIC, ",".join(colors))
        set_led(new=tuple([int(color) for color in colors]), smooth=75)
    elif topic == KILL_COMMAND_TOPIC:
        if msg == b'dead':
            publish_payload(STATE_TOPIC, "OFF")
            publish_payload(BRIGHTNESS_STATE_TOPIC, 0)
            publish_payload(KILL_STATE_TOPIC, "dead")
            set_led()
            exit()
        else:
            publish_payload(KILL_STATE_TOPIC, "alive")

def reconnect():
    c.set_callback(sub_cb)
    c.connect()
    publish_payload(STATE_TOPIC, STATE)
    publish_payload(BRIGHTNESS_STATE_TOPIC, 0)
    publish_payload(RGB_STATE_TOPIC, LIGHT_STATE)
    publish_payload(KILL_STATE_TOPIC, "alive")
    c.subscribe(COMMAND_TOPIC)
    c.subscribe(BRIGHTNESS_COMMAND_TOPIC)
    c.subscribe(RGB_COMMAND_TOPIC)
    c.subscribe(KILL_COMMAND_TOPIC)
    c.subscribe(SCENES_COMMAND_TOPIC)

def main(server=SERVER):
    global c
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(SSID, PASS)
        while not wlan.isconnected():
            pass
    print('[Network Config]\n ', wlan.ifconfig())
    c = MQTTClient(CLIENT_ID, server)
    reconnect()
    set_led()       # sets led to off
    try:
        while True:
            if not wlan.isconnected():
                reconnect()
            c.wait_msg()
    finally:
        c.disconnect()
if __name__ == "__main__":
    main()