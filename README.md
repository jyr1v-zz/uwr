# uwr
Underwater rugby time &amp; score app

PC / Mac desktop app, that connects to UWR (underwater rugby board ment for keeping scores, counting game time, penalties etc...) and shows needed info in the screen. UWR board is shown in picture below. The board has old serial port, so aten usb-to-serial converter was used to connect it to PC. Aten USB-serial-converter used can be found here: http://www.aten.com/global/en/products/usb-&-thunderbolt/usb-converters/uc232a/#.WdpH-ztx2po.

The app was developed to European championships in underwater rugby: http://www.cmas.org/news/the-european-championships-in-underwater-rugby-helsinki-finland-26.6.-1.7.2017. The showed data was integrated to live video taken from the games. Here's link to game videos: https://drive.google.com/drive/folders/0B1z_FJ2xJH6mZWFNNXVMVzBzNTA.

## How to get it up and running

Software is made with python. So install it. In addition two libs are needed from python:

* wxPython (https://wxpython.org/)
* pySerial (https://github.com/pyserial/pyserial)

Install both libraries and you're good to go with following command:

```shell
python uwr.py
```

If you want to create .exe binary (for windows) run:

```shell
python setup.py
```

After the command you will find the uwr.exe from created "dist"-folder.

![Game](doc/game.png)
Picture from live feed from a game in European cahmpionships. Game time & score from software is shown with red rectangle.

![UWR spec](doc/pic.png)
Picture about the UWR board and spec.
