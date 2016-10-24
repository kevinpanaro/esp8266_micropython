from machine import Pin
from neopixel import NeoPixel
from time import sleep

LED_PIN = 5
NUM_OF_LEDS = 6
PIN = Pin(LED_PIN, Pin.OUT)
NEOPIXEL = NeoPixel(PIN, NUM_OF_LEDS)

def init():
	states = {}
	leds = list(range(0, NUM_OF_LEDS))
	for led in leds:
		states[led] = 0
	return states, leds

def on_off(states, leds):
	while True:
		user_input = input("Select an LED to turn on (q to quit): ")
		if user_input == "q":
			print("Bye!")
			return False
		else:
			try:
				user_input = int(user_input)-1
			except:
				print("Not a valid entry")
				return True
			if user_input not in leds:
				print("Not a valid LED")
				return True
			if states[(user_input)] == 0:	
				NEOPIXEL[(user_input)] = (255, 255, 255)
				states[(user_input)] = 1
			elif states[(user_input)] == 1:	
				NEOPIXEL[(user_input)] = (0, 0, 0)
				states[(user_input)] = 0
		NEOPIXEL.write()

def main():
	run = True
	states, leds = init()
	while run:
		run = on_off(states, leds)

if __name__ == '__main__':
	main()