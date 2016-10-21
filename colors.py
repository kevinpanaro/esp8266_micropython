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
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, 6)
LIGHT_BRIGHTNESS = 255
STATE = 0
NUM_OF_LEDS = 6

def publish_light_state():
    if STATE == 1:
        c.publish(STATE_TOPIC, "ON")
        print("Publish ON to %s" % STATE_TOPIC)
    else:
        c.publish(STATE_TOPIC, "OFF")
        print("Publish ON to %s" % STATE_TOPIC)

def publish_rgb_brightness():
    c.publish(BRIGHTNESS_STATE_TOPIC, str(LIGHT_BRIGHTNESS))
    print("Publish %s to %s" % (str(LIGHT_BRIGHTNESS), BRIGHTNESS_STATE_TOPIC))

def publish_rbg_state(colors):
    colors = ",".join(colors)
    c.publish(RGB_STATE_TOPIC, colors)
    print("Publish %s to %s" % (colors, RGB_STATE_TOPIC))

def set_brightness(on, brightness):
    if on and brightness != 0:
        for led in range(NUM_OF_LEDS):
            NEOPIXEL[led]=(brightness,brightness,brightness)
    else:
        for led in range(NUM_OF_LEDS):
            NEOPIXEL[led]=(0,0,0)
    NEOPIXEL.write()

def set_color(color, brightness):
    red = int(color[0]*(brightness/255))
    green = int(color[0]*(brightness/255))
    blue = int(color[0]*(brightness/255))
    for led in range(NUM_OF_LEDS):
        NEOPIXEL[led] = (red, green, blue)
    NEOPIXEL.write()

def set_led(on=True, brightness=255, color=False):
    '''on is True or False
    brightness is 0-255
    color is list [red, green, blue]
    '''
    if not on:
        for led in range(NUM_OF_LEDS):
            NEOPIXEL[led]=(0,0,0)
    elif on:
        if color:
            red = int(color[0])
            green = int(color[1])
            blue = int(color[2])
            for led in range(NUM_OF_LEDS):
                NEOPIXEL[led] = (red, green, blue)
            NEOPIXEL.write()
            return
        else:
            for led in range(NUM_OF_LEDS):
                NEOPIXEL[led] = (brightness, brightness, brightness)
    NEOPIXEL.write()

def set_light(brightness=255):
    if STATE == 1:
        set_brightness(True, brightness)
    else:
        set_brightness(False, brightness)

def sub_cb(topic, msg):
    global STATE
    print((topic, msg))
    if topic == COMMAND_TOPIC:
        if msg == b"ON":
            if STATE == 0:
                STATE = 1
                set_led(on=True, brightness=255, color=False)
                publish_light_state()
                publish_rgb_brightness()
        elif msg == b"OFF":
            if STATE == 1:
                STATE = 0
                LIGHT_BRIGHTNESS = 0
                set_led(on=False)
                publish_light_state()
                publish_rgb_brightness()
    elif topic == BRIGHTNESS_COMMAND_TOPIC:
        brightness = int(msg)
        if brightness < 0 or brightness > 255:
            return
        else:
            set_led(on=True, brightness=brightness, color=False)
            publish_rgb_brightness()
    elif topic == RGB_COMMAND_TOPIC:
        colors = msg.decode("utf-8").split(',')
        try:
            set_led(on=True, brightness=LIGHT_BRIGHTNESS, color=colors)
        except NameError:
            LIGHT_BRIGHTNESS = 255
            set_led(on=True, brightness=LIGHT_BRIGHTNESS, color=colors)
        publish_rbg_state(colors)

def reconnect():
    c.connect()
    publish_light_state()
    publish_rgb_brightness()
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
    print('network config:', wlan.ifconfig())
    c = MQTTClient(CLIENT_ID, server)
    # Subscribed messages will be delivered to this callback
    c.set_callback(sub_cb)
    reconnect()
    print("Connected to %s, subscribed to %s topic" % (server, COMMAND_TOPIC))
    try:
        while True:
            if not wlan.isconnected():
                reconnect()
            c.wait_msg()
    finally:
        c.disconnect()
if __name__ == "__main__":
    main()