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
import ujson
# ESP8266 ESP-12 modules have blue, active-low LED on GPIO2, replace
# with something else if needed.
'''
light:
  - platform: mqtt_json
    name: mqtt_json_light_test
    state_topic: "home/light/mqtt_json/rgb1"
    command_topic: "home/light/mqtt_json/rgb1/set"
    rgb: true
    brightness: true
'''
# WiFi
SSID = ""
PASS = ""

# MQTT server to connect to 
SERVER = "192.168.0.102" 
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
STATE_TOPIC= b"home/light/mqtt_json/rgb1"
COMMAND_TOPIC = b"home/light/mqtt_json/rgb1/set"

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)
BRIGHTNESS_STATE = 0    # last known brightness state (DO NOT NEED)
STATE = "OFF"           # last known state (ON, OFF)
RGB_STATE = (0, 0, 0)   # last known set RGB state 
LIGHT_STATE = (0, 0, 0) # last known light state

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

def set_led(new=(0, 0, 0), smooth=50.0, transition=0):
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

def publish_payload(pub_payload):
    '''publish to a topic with a payload'''
    c.publish(STATE_TOPIC, ujson.dumps(pub_payload))
    print("[Publish]\t%s" % ujson.dumps(pub_payload))

def sub_cb(topic, payload):
    '''
      Callback function:
        takes payload handles it, posts it back

      TODO(kev): bring transition out from.

    '''

    global STATE
    global RGB_STATE

    payload = ujson.loads(payload.decode("utf-8"))

    def get_color():            # Get color from payload dict/json
        return (payload["color"]["r"], payload["color"]["g"], payload["color"]["b"])

    def get_brightness(color, brightness):  # returns rgb value
        return tuple(get_rgb_value(color, brightness/255.0))

    try:    # get transition
        transition = payload['transition']
    except KeyError:
        transition = 0

    if payload["state"] == "OFF": # STATE maybe not needed
        # Turn off only if on. 
        STATE = "OFF"
        RGB_STATE = (0, 0, 0)
        pub_payload = {"state": "OFF"}
        publish_payload(pub_payload)
        set_led(transition=transition)
    elif payload["state"] == "ON" and len(payload) == 1:
        # turn on but look for other variables first
        STATE = "ON"
        RGB_STATE = (255, 255, 255)
        pub_payload = {"state": "ON", "brightness": 255, "color": {"r": 255, "g": 255, "b": 255}}
        publish_payload(pub_payload)
        set_led(new = RGB_STATE, transition=transition)
    elif payload["state"] == "ON":
        try:        # happens only when a scene is set and the 
                    # user puts in a brightness and color
            if payload["brightness"] and payload["color"]:
                color = get_color()
                brightness = get_brightness(color, payload['brightness'])
                RGB_STATE = brightness
                pub_payload = {"state": "ON", "brightness": payload["brightness"], "color": payload['color']}
                publish_payload(pub_payload)
                set_led(new=brightness, smooth=75.0, transition=transition)
        except KeyError:
            pass # not both brightness and color

        try:
            if payload["color"]:
                color = get_color()
                _, _, v = get_hsv_value(color)
                RGB_STATE = color
                pub_payload = {"state": "ON", "brightness": int(v * 255.0),"color": payload["color"]}
                publish_payload(pub_payload)
                set_led(new=color, smooth=75.0, transition=transition)
        except KeyError:
            pass # not just color

        try:
            if payload["brightness"]:
                brightness = payload["brightness"]
                if brightness < 0 or brightness > 255:
                    return
                else:
                    color = get_rgb_value(RGB_STATE, brightness/255.0)
                    pub_payload = {"state": "ON", "brightness": int(payload["brightness"]), "color": {"r": color[0], "g": color[1], "b": color[2]}}
                    publish_payload(pub_payload)
                    set_led(new=color, smooth=75.0, transition=transition)
        except KeyError:
            pass


def reconnect():
    c.set_callback(sub_cb)
    c.connect()
    c.subscribe(COMMAND_TOPIC)

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