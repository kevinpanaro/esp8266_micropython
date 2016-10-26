from umqtt.simple import MQTTClient
from machine import Pin
from neopixel import NeoPixel
import ubinascii
import machine
import micropython
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
'''
# Wifi 
SSID = ""
PASS = ""

# Default MQTT server to connect to
SERVER = "192.168.0.14"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
STATE_TOPIC= b"led/status"
COMMAND_TOPIC = b"led/switch"
BRIGHTNESS_STATE_TOPIC = b'led/brightness/status'
BRIGHTNESS_COMMAND_TOPIC = b'led/brightness/set'
RGB_STATE_TOPIC = b'led/rgb/status'
RGB_COMMAND_TOPIC = b'led/rgb/set'

# Pin for NODEMCU and Neopixel
LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)
BRIGHTNESS_STATE = 0
STATE = "OFF"       # I don't know but this is really important for some reason.
RGB_STATE = (0,0,0)

def publish_payload(topic, payload):
    '''publish to a topic with a payload'''
    c.publish(topic, str(payload))
    print("[Publish]\t%s => %s" % (topic, str(payload)))

def set_led(on=True, brightness=255, color=False):
    '''on is True or False
    brightness is 0-255
    color is list [red, green, blue]
    '''
    global RGB_STATE
    if not on:
        new = (0, 0, 0)
        smooth(RGB_STATE, new, 50)
    elif on:
        if color:
            smooth(RGB_STATE, color, 75)
        else:
            new = (brightness, brightness, brightness)
            smooth(RGB_STATE, new, 75)

def smooth(old, new, smooth, transition=0):
    '''old is deprecated, probably going to be replaced by RGB_STATE
    new is the new color (RED, GREEN, BLUE)
    smooth is how many "frames" of color to create and display
    transition is seconds to transit from one color to the next
    transition is 0 right now, but will be implimented with MQTT JSON'''
    global RGB_STATE
    red = list(linspace(RGB_STATE[0], new[0], smooth))
    green = list(linspace(RGB_STATE[1], new[1], smooth))
    blue = list(linspace(RGB_STATE[2], new[2], smooth))
    for color in zip(red,green,blue):
        for led in range(NUM_OF_LEDS):
            NEOPIXEL[led] = color
        NEOPIXEL.write()
    RGB_STATE = new


def linspace(a,b, n=100):
    if n < 2:
        yield b
    diff = (float(b) - a)/(n - 1)
    for i in range(n):
        yield int(round(diff * i + a))

def sub_cb(topic, msg):
    global STATE
    if topic == COMMAND_TOPIC:
        if msg == b"ON" and STATE == "OFF":
            STATE = "ON"
            set_led(on=True, brightness=255, color=False)
            publish_payload(STATE_TOPIC, "ON")
            publish_payload(BRIGHTNESS_STATE_TOPIC, 255)
        elif msg == b"OFF" and STATE == "ON":
            STATE = "OFF"
            BRIGHTNESS_STATE = 0
            set_led(on=False)
            publish_payload(STATE_TOPIC, "OFF")
            publish_payload(BRIGHTNESS_STATE_TOPIC, 0)
    elif topic == BRIGHTNESS_COMMAND_TOPIC:
        brightness = int(msg)
        if brightness < 0 or brightness > 255:
            return
        else:
            set_led(on=True, brightness=brightness, color=False)
            publish_payload(BRIGHTNESS_STATE_TOPIC, brightness)
    elif topic == RGB_COMMAND_TOPIC:
        colors = msg.decode("utf-8").split(',')
        set_led(on=True, brightness=False, color=tuple([int(color) for color in colors]))
        publish_payload(RGB_STATE_TOPIC, ",".join(colors))
        

def reconnect():
    c.set_callback(sub_cb)
    c.connect()
    publish_payload(STATE_TOPIC, STATE)
    publish_payload(BRIGHTNESS_STATE_TOPIC, BRIGHTNESS_STATE)
    publish_payload(RGB_STATE_TOPIC, RGB_STATE)
    c.subscribe(COMMAND_TOPIC)
    c.subscribe(BRIGHTNESS_COMMAND_TOPIC)
    c.subscribe(RGB_COMMAND_TOPIC)

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
    try:
        while True:
            if not wlan.isconnected():
                reconnect()
            c.wait_msg()
    finally:
        c.disconnect()
if __name__ == "__main__":
    main()