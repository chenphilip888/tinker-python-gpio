Python gpio experiments on the ASUS Tinkerboard.

The following 8 tests are included: ( see below for tests summary )
1. uart test
2. led test
3. button test
4. pwm led test
5. i2c lcd test
6. tongsong
7. servo
8. spi oled test

-------------------------------------------------------------------
To compile and flash to sd card:
cd tinker-python-gpio
Download OS:
wget https://dlcdnets.asus.com/pub/ASUS/mb/Embedded_IPC/TinkerBoard_S/Tinker_Board-Debian-Stretch-V2.1.16-20200813.zip
unzip Tinker_Board-Debian-Stretch-V2.1.16-20200813.zip
Use balenaEtcher to burn img to sd card.
eject sd card.
Plugin sd card to PC.
cp rk3288.conf /media/$USER/4C89-2DED/extlinux/extlinux.conf
sync
eject sd card.
Plugin the sd card to ASUS Tinkerboard.
Connect Tinkerboard gpio Pin 8 to serial USB cable TX.
Connect Tinkerboard gpio pin 10 to serial USB cable RX. 
Connect Tinkerboard gpio pin 39 to serial USB cable ground. 
Type "script ~/outputfile.txt" on PC.
Plugin serial USB cable to PC.
Type "sudo screen /dev/ttyUSB0 115200" on PC.
Power on ASUS Tinkerboard.
It should prompt login message.
user linaro
password linaro
sudo tinker-config
set password, locale, timezone etc.
vi nosleep.sh ( add following line to disable sleep feature )
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.ta
rget
./nosleep.sh
sudo dmesg -n 1
sudo vi /etc/rc.local ( add sudo dmesg -n 1 )
setup wifi:
nmcli dev wifi list
sudo nmcli con add con-name WiFi ifname wlan0 type wifi ssid mywifissid
sudo nmcli con modify WiFi wifi-sec.key-mgmt wpa-psk
sudo nmcli con modify WiFi wifi-sec.psk mypassword
sudo nmcli con up WiFi
sudo ifconfig
sudo apt-get update
sudo apt-get upgrade
sudo shutdown -h now
Power on ASUS tinkerboard
sudo apt-get install python-dev python-pip python-setuptools python3-dev python3-pip python3-setuptools dnsutils apache2 vsftpd

-------------------------------------------------------------------------
Install python gpio library on ASUS Tinkerboard:
git clone https://github.com/TinkerBoard/gpio_lib_python.git
cd ~/gpio_lib_python
sudo python setup.py install
cd ~/
pip install serial
pip install pyserial
pip install spidev
sudo apt-get install python-smbus
git clone https://github.com/doceme/py-spidev.git
cd ~/py-spidev
sudo python setup.py install
sudo python3 setup.py install

cd ~/tinker-python-gpio
./gpio_test.py
When done all tests, hit 'q' to exit tests.
sudo shutdown -h now
Power off the ASUS Tinkerboard.
Unplug serial USB cable from PC.
Type "exit" on PC.

-------------------------------------------------------------------------
Here are the summary of the tests: ( see tinker_gpio.png )
These tests used Seeed Grove  starter kit LED, button, buzzer, Grove-LCD RGB Backlight V3.0 JHD1313M2, Analog Servo and Adafruit SSD1306 128x32 SPI OLED Display.
1. uart test.
   This test will send uart3 tx to uart3 rx for loopback.
   It sends 0 to 255 to uart3 tx and receive 0 to 255 from uart3 rx.
   Connect gpio pin 36 to pin 37.
2. led test.
   This test will blink led 5 times. 
   Connect gpio pin 11 to led control. 
   Connect gpio pin 2 to led 5V. 
   Connect gpio pin 9 to led ground.
3. button test. 
   Connect gpio pin 11 to led control. 
   Connect gpio pin 2 to led 5V. 
   Connect gpio pin 9 to led ground. 
   Connect gpio pin 7 to button control.
   Connect gpio pin 4 to button 5V.
   Connect gpio pin 6 to button ground.
4. pwm led test.
   This test will dim led 10 times.
   Connect gpio pin 32 to led control.
   Connect gpio pin 2 to led 5V.
   Connect gpio pin 9 to led ground.
5. i2c lcd test.
   This test will change lcd backlight color for 5 cycles.
   Then it will display two sentences on lcd display.
   Connect gpio pin 3 to lcd display SDA.
   Connect gpio pin 5 to lcd display SCL.
   Connect gpio pin 2 to lcd display 5V.
   Connect gpio pin 9 to lcd display ground.
6. tongsong.
   This test will generate song using buzzer.
   Connect gpio pin 32 to buzzer control.
   Connect gpio pin 2 to buzzer 5V.
   Connect gpio pin 9 to buzzer ground. 
7. servo.
   This test will turn servo 90 degree - 180 degree - 90 degree - 0 degree etc.
   Connect gpio pin 32 to servo control.
   Connect gpio pin 2 to servo 5V.
   Connect gpio pin 9 to servo ground.
8. spi oled test.
   This test will show some ascii characters on the oled display.
   Connect gpio pin 11 to oled display DC.
   Connect gpio pin 24 to oled display CS.
   Connect gpio pin 19 to oled display TX.
   Connect gpio pin 23 to oled display CLK.
   Connect gpio pin 1 to oled display 3.3V.
   Connect gpio pin 9 to oled display ground.

-----------------------------------------------------------------------------
