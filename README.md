# esp8266_micropython

Setup the Board:

I used [esptool.py](https://github.com/themadinventor/esptool) to flash the micropython to the board

This is the version of [MicroPython](https://github.com/micropython/micropython/releases/tag/v1.8.5) I used. I'd say just use the most recent one.
Flashing the board is pretty straight forward, the docs for MicroPython tell you what settings you'd need to change if any.


Connecting to the Board:

I used Adafruits [ampy](https://github.com/adafruit/ampy) to put all my files onto the board.

Check out this [tutorial](https://home-assistant.io/blog/2016/07/28/esp8266-and-micropython-part1/) as well.


Issues:

When the nodemcu boots up with MicroPython, it runs "boot.py" and then "main.py". If you run the main function of "colors.py" in "main.py", you'll get stuck in an infinite loop, since its going to be waiting for a publish to a mqtt topic it subscribed to. In order to get rid of this, I just flashed "colors.py" onto the board, typed "screen /dev/tty.SLAB_USBtoUART 115200" and automatically started and stopped the script (helpful for debugging). Another option would be to just add a break, when a certain topic is called. then you'd be able to access the board via ampy, or screen or whatever you're using.


Bugs:

When setting the color in Home Assistant's dev tools, if you send something like "{"color":"red"}" it while go to white then if you press it again, it will go to red. Not sure why.

Brightness of the colors. If you have a color on and then change the brightness, it turns to white.

Purchase List:
[NodeMCU v2](http://www.ebay.com/itm/like/251980906073?lpid=82&chn=ps&ul_noapp=true)
	any NodeMCU should be good, but make sure its the [official kind](http://frightanic.com/iot/comparison-of-esp8266-nodemcu-development-boards/)

[WS2812](http://www.aliexpress.com/w/wholesale-ws2812.html)
    any of these work, you'll need a power supply, 5V,
    if it's a small strip you might be able to do what I did and cut an old phone changer and solder to female ends of wires to them and connect it with that.