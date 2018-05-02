Micropython Build Monitor Slave
===============================

Creating JenkinsPi clients (not necessarily build monitors) from [Micropython](https://docs.micropython.org/en/latest/esp8266/esp8266/tutorial/intro.html) 
boards - in this case the super-affordable [Wemos d1 mini](https://wiki.wemos.cc/products:d1:d1_mini
) which has wifi and a nice bunch of I/O ports.

I've stolen the Micropython libraries for MQTT 
and the [Adafruit segment display](https://www.adafruit.com/product/1911) from 
[Micropython UMQTT](https://github.com/micropython/micropython-lib/tree/master/umqtt.simple) and 
[Adafruit](https://github.com/adafruit/micropython-adafruit-ht16k33) respectively.

![Build Monster Photo](imgs/BM.png)


Installing
----------
1. Connect the micropython board's wifi connection.
2. Update the `server` parameter in `main.py` if you've renamed the Raspberry Pi running the Jenkins Monitor MQTT.
3. Copy the `*.py` files and `umqtt` folder to the micropython board.
4. Get the board's ID 
```python
import ubinascii
import machine
ubinascii.hexlify(machine.unique_id())
```
5. Solder LEDs, segment displays or APA106 RGBs and remember which pins you soldered them to
6. Stuff everything into the monitor container of your choice and make sure you can plug it in.

Configuring
-----------

1. Install a copy of the [example configuration file](https://github.com/testingtony/jenkinspi/blob/control/files/programs/board_config/config/micro_be486e00.yml)
into the `\\monitor\apps\board_config\config` and change the `be486e00` to the board's id from above. 
2. Change the configuration to match the pins and flashing things you've soldered onto the board.
3. Plug in the board and hope for the best.

Debugging
---------
* Make sure the board's hitting the wifi and you can resolve the Raspberry pi's address from `main.py`
* There's some logging in the scripts which you can watch on the board's USB terminal
* Watch what's happening on MQTT on the Raspberry pi
  I use [MQTT-SPY](https://kamilfb.github.io/mqtt-spy/) because I can just run the executable jar
  file without installing anything.
* Subscribe to the `#` topic and you should see
  * Updates from the jenkins monitors
  * A request from the board for it config (it'll have the board id in the request)
  * A response from the Raspberry pi with the contents of the configuration file.
  * Updates from the pi being reflected on the board.

