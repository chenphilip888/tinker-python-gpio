#!/usr/bin/python

import ASUS.GPIO as GPIO
import serial
from serial import Serial
import time
import sys
import smbus
import spidev

bus = smbus.SMBus(1)
spi = spidev.SpiDev()

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
led = 11
GPIO.setup(led,GPIO.OUT)
switch = 7
GPIO.setup(switch,GPIO.IN)
GPIO.setup(32, GPIO.OUT)

port = "/dev/ttyS3"    # Raspberry Pi uart 1,3,4

def readLine(port):
    s = ""
    while True:
        ch = port.read()
        s += ch
        if ch == '\r':
            return s

def uart_test(port):
    ser = serial.Serial(port, baudrate = 115200)
    s = "{0}\r\n"
    for i in range(256):
        time.sleep(0.05)
        ser.write(s.format(i))
        time.sleep(0.05)
        rcv = readLine(ser)
        print rcv
        #if rcv[0:3] == "Bye":
        #    break

    ser.close()

def led_test():
    for i in range(5):
        GPIO.output(led, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led, GPIO.LOW)
        time.sleep(0.5)

def button_test():
    print "Push button 10 times.\r\n"
    old_state = 0
    current_state = 0
    i = 0
    while i < 10:
        current_state = GPIO.input(switch)
        if old_state == 0 and current_state == 1:
            GPIO.output(led, GPIO.HIGH)
            old_state = current_state
        elif old_state == 1 and current_state == 0:
            GPIO.output(led, GPIO.LOW)
            old_state = current_state
            i += 1
        time.sleep(0.05)

def pwm_led_test():
    pwm = GPIO.PWM(32, 50)
    pwm.start(100)

    for i in range(0,10):
        for x in range(0,101,5):
            pwm.ChangeDutyCycle(x)
            time.sleep(0.05)
        for x in range(100,-1,-5):
            pwm.ChangeDutyCycle(x)
            time.sleep(0.05)

def tone (note, duration):
    if note == 0:
       time.sleep(duration)
       time.sleep(duration * 0.8)
    else:
       pwm = GPIO.PWM(32, note)
       pwm.start(50)
       time.sleep(duration)
       pwm.stop()
       time.sleep(duration * 0.8)

def tongsong():
    melody = [262, 196, 196, 220, 196, 0, 247, 262]
    noteDurations = [4, 8, 8, 4, 4, 4, 4, 4]
    thisNote = 0
    while thisNote < 8:
        noteDuration = 1.0 / noteDurations[thisNote];
        tone(melody[thisNote], noteDuration)
        thisNote = thisNote + 1

def servo():
    pwm = GPIO.PWM(32, 50)
    pwm.start(2.5)              # min 2.5, max 11.5 180 degrees

    for i in range(0,3):
        pwm.ChangeDutyCycle(2.5)
        print("0 degree")
        time.sleep(1.0)
        pwm.ChangeDutyCycle(7.0)
        print("90 degree")
        time.sleep(1.0)
        pwm.ChangeDutyCycle(11.5)
        print("180 degree")
        time.sleep(1.0)
        pwm.ChangeDutyCycle(7.0)
        print("90 degree")
        time.sleep(1.0)

    pwm.start(0)

# I2C LCD
# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)    
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)     
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count >= 16:
            count = 0
            row += 1
            if row >= 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

def i2c_lcd_test():
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)

    for i in range(0,5):
        setRGB( 255, 0, 0 )
        time.sleep(1)
        setRGB( 255, 255, 0 )
        time.sleep(1)
        setRGB( 0, 255, 0 )
        time.sleep(1)
        setRGB( 0, 255, 255 )
        time.sleep(1)
        setRGB( 0, 0, 255 )
        time.sleep(1)
        setRGB( 255, 0, 255 )
        time.sleep(1)

    setRGB( 128, 255, 0 )
    setText( "Hello world !\nIt works !\n" )

# SPI OLED

font7x14 = [
  0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,  #  space
  0X00,0X00,0X00,0XFC,0X00,0X00,0X00,0X00,0X00,0X0D,0X00,0X00,  #  exclam
  0X00,0X00,0X1E,0X00,0X1E,0X00,0X00,0X00,0X00,0X00,0X00,0X00,  #  quotedbl
  0X00,0X20,0XFC,0X20,0XFC,0X20,0X00,0X01,0X0F,0X01,0X0F,0X01,  #  numbersign
  0X30,0X48,0X88,0XFC,0X88,0X30,0X06,0X08,0X08,0X1F,0X08,0X07,  #  dollar
  0X18,0X24,0XA4,0X78,0X10,0X0C,0X0C,0X02,0X07,0X09,0X09,0X06,  #  percent
  0X00,0XB8,0XC4,0X44,0X38,0X80,0X07,0X08,0X08,0X05,0X06,0X09,  #  ampersand
  0X00,0X00,0X00,0X1E,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,  #  quotesingle
  0X00,0X00,0XE0,0X18,0X04,0X02,0X00,0X00,0X03,0X0C,0X10,0X20,  #  parenleft
  0X00,0X02,0X04,0X18,0XE0,0X00,0X00,0X20,0X10,0X0C,0X03,0X00,  #  parenright
  0X00,0X20,0X40,0XF0,0X40,0X20,0X00,0X02,0X01,0X07,0X01,0X02,  #  asterisk
  0X00,0X80,0X80,0XF0,0X80,0X80,0X00,0X00,0X00,0X07,0X00,0X00,  #  plus
  0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X24,0X1C,0X00,0X00,  #  comma
  0X00,0X80,0X80,0X80,0X80,0X80,0X00,0X00,0X00,0X00,0X00,0X00,  #  hyphen
  0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X00,0X08,0X1C,0X08,0X00,  #  period
  0X00,0X00,0X00,0XE0,0X18,0X06,0X30,0X0C,0X03,0X00,0X00,0X00,  #  slash
  0XF0,0X08,0X04,0X04,0X08,0XF0,0X03,0X04,0X08,0X08,0X04,0X03,  #  zero
  0X00,0X10,0X08,0XFC,0X00,0X00,0X00,0X08,0X08,0X0F,0X08,0X08,  #  one
  0X18,0X04,0X04,0X04,0XC4,0X38,0X08,0X0C,0X0A,0X09,0X08,0X08,  #  two
  0X04,0X04,0X44,0X64,0X54,0X8C,0X06,0X08,0X08,0X08,0X08,0X07,  #  three
  0X00,0XC0,0X30,0X08,0XFC,0X00,0X03,0X02,0X02,0X02,0X0F,0X02,  #  four
  0X7C,0X24,0X24,0X24,0X24,0XC4,0X06,0X08,0X08,0X08,0X08,0X07,  #  five
  0XF0,0X88,0X44,0X44,0X44,0X80,0X07,0X08,0X08,0X08,0X08,0X07,  #  six
  0X04,0X04,0X04,0XC4,0X34,0X0C,0X00,0X0C,0X03,0X00,0X00,0X00,  #  seven
  0X18,0XA4,0X44,0X44,0XA4,0X18,0X07,0X08,0X08,0X08,0X08,0X07,  #  eight
  0X78,0X84,0X84,0X84,0X44,0XF8,0X06,0X08,0X08,0X08,0X04,0X03,  #  nine
  0X00,0X00,0X20,0X70,0X20,0X00,0X00,0X00,0X04,0X0E,0X04,0X00,  #  colon
  0X00,0X00,0X60,0X60,0X00,0X00,0X00,0X00,0X12,0X0E,0X00,0X00,  #  semicolon
  0X00,0X80,0X40,0X20,0X10,0X08,0X00,0X00,0X01,0X02,0X04,0X08,  #  less
  0X20,0X20,0X20,0X20,0X20,0X20,0X01,0X01,0X01,0X01,0X01,0X01,  #  equal
  0X00,0X08,0X10,0X20,0X40,0X80,0X00,0X08,0X04,0X02,0X01,0X00,  #  greater
  0X18,0X04,0X04,0XC4,0X24,0X18,0X00,0X00,0X00,0X0D,0X00,0X00,  #  question
  0XF0,0X08,0XE4,0X14,0X14,0XF8,0X03,0X04,0X09,0X0A,0X0A,0X0B,  #  at
  0XF0,0X88,0X84,0X84,0X88,0XF0,0X0F,0X00,0X00,0X00,0X00,0X0F,  #  A
  0XFC,0X44,0X44,0X44,0XA8,0X10,0X0F,0X08,0X08,0X08,0X04,0X03,  #  B
  0XF8,0X04,0X04,0X04,0X04,0X18,0X07,0X08,0X08,0X08,0X08,0X06,  #  C
  0XFC,0X04,0X04,0X04,0X08,0XF0,0X0F,0X08,0X08,0X08,0X04,0X03,  #  D
  0XFC,0X44,0X44,0X44,0X04,0X04,0X0F,0X08,0X08,0X08,0X08,0X08,  #  E
  0XFC,0X44,0X44,0X44,0X04,0X04,0X0F,0X00,0X00,0X00,0X00,0X00,  #  F
  0XF8,0X04,0X04,0X84,0X84,0X98,0X07,0X08,0X08,0X08,0X04,0X0F,  #  G
  0XFC,0X40,0X40,0X40,0X40,0XFC,0X0F,0X00,0X00,0X00,0X00,0X0F,  #  H
  0X00,0X04,0X04,0XFC,0X04,0X04,0X00,0X08,0X08,0X0F,0X08,0X08,  #  I
  0X00,0X00,0X00,0X04,0XFC,0X04,0X06,0X08,0X08,0X08,0X07,0X00,  #  J
  0XFC,0X40,0XA0,0X10,0X08,0X04,0X0F,0X00,0X00,0X01,0X02,0X0C,  #  K
  0XFC,0X00,0X00,0X00,0X00,0X00,0X0F,0X08,0X08,0X08,0X08,0X08,  #  L
  0XFC,0X18,0X60,0X60,0X18,0XFC,0X0F,0X00,0X00,0X00,0X00,0X0F,  #  M
  0XFC,0X30,0X40,0X80,0X00,0XFC,0X0F,0X00,0X00,0X00,0X03,0X0F,  #  N
  0XF8,0X04,0X04,0X04,0X04,0XF8,0X07,0X08,0X08,0X08,0X08,0X07,  #  O
  0XFC,0X84,0X84,0X84,0X84,0X78,0X0F,0X00,0X00,0X00,0X00,0X00,  #  P
  0XF8,0X04,0X04,0X04,0X04,0XF8,0X07,0X09,0X09,0X0A,0X1C,0X27,  #  Q
  0XFC,0X84,0X84,0X84,0X84,0X78,0X0F,0X00,0X00,0X01,0X02,0X0C,  #  R
  0X38,0X44,0X44,0X84,0X84,0X18,0X06,0X08,0X08,0X08,0X08,0X07,  #  S
  0X04,0X04,0X04,0XFC,0X04,0X04,0X00,0X00,0X00,0X0F,0X00,0X00,  #  T
  0XFC,0X00,0X00,0X00,0X00,0XFC,0X07,0X08,0X08,0X08,0X08,0X07,  #  U
  0X3C,0XC0,0X00,0X00,0XC0,0X3C,0X00,0X01,0X0E,0X0E,0X01,0X00,  #  V
  0X00,0XFC,0X00,0X00,0X00,0XFC,0X00,0X07,0X08,0X07,0X08,0X07,  #  W
  0X0C,0X30,0XC0,0XC0,0X30,0X0C,0X0C,0X03,0X00,0X00,0X03,0X0C,  #  X
  0X00,0X1C,0X60,0X80,0X60,0X1C,0X00,0X00,0X00,0X0F,0X00,0X00,  #  Y
  0X04,0X04,0X84,0X64,0X14,0X0C,0X0C,0X0B,0X08,0X08,0X08,0X08,  #  Z
  0X00,0X00,0XFE,0X02,0X02,0X02,0X00,0X00,0X3F,0X20,0X20,0X20,  #  bracketleft
  0X06,0X18,0XE0,0X00,0X00,0X00,0X00,0X00,0X00,0X03,0X0C,0X30,  #  backslash
  0X00,0X02,0X02,0X02,0XFE,0X00,0X00,0X20,0X20,0X20,0X3F,0X00,  #  bracketright
  0X08,0X04,0X02,0X02,0X04,0X08,0X00,0X00,0X00,0X00,0X00,0X00,  #  asciicircum
  0X00,0X00,0X00,0X00,0X00,0X00,0X20,0X20,0X20,0X20,0X20,0X20,  #  underscore
  0X00,0X00,0X02,0X04,0X08,0X00,0X00,0X00,0X00,0X00,0X00,0X00,  #  grave
  0X40,0X20,0X20,0X20,0X20,0XC0,0X06,0X09,0X09,0X09,0X09,0X0F,  #  a
  0XFC,0X40,0X20,0X20,0X20,0XC0,0X0F,0X04,0X08,0X08,0X08,0X07,  #  b
  0XC0,0X20,0X20,0X20,0X20,0X40,0X07,0X08,0X08,0X08,0X08,0X04,  #  c
  0XC0,0X20,0X20,0X20,0X40,0XFC,0X07,0X08,0X08,0X08,0X04,0X0F,  #  d
  0XC0,0X20,0X20,0X20,0X20,0XC0,0X07,0X09,0X09,0X09,0X09,0X05,  #  e
  0X40,0X40,0XF8,0X44,0X44,0X08,0X00,0X00,0X0F,0X00,0X00,0X00,  #  f
  0XC0,0X20,0X20,0X20,0XC0,0X20,0X19,0X26,0X2A,0X2A,0X29,0X10,  #  g
  0XFC,0X40,0X20,0X20,0X20,0XC0,0X0F,0X00,0X00,0X00,0X00,0X0F,  #  h
  0X00,0X00,0X20,0XEC,0X00,0X00,0X00,0X08,0X08,0X0F,0X08,0X08,  #  i
  0X00,0X00,0X00,0X00,0X20,0XEC,0X00,0X18,0X20,0X20,0X20,0X1F,  #  j
  0XFC,0X00,0X80,0X40,0X20,0X00,0X0F,0X01,0X01,0X02,0X04,0X08,  #  k
  0X00,0X00,0X04,0XFC,0X00,0X00,0X00,0X08,0X08,0X0F,0X08,0X08,  #  l
  0X00,0XE0,0X20,0XC0,0X20,0XC0,0X00,0X0F,0X00,0X07,0X00,0X0F,  #  m
  0XE0,0X40,0X20,0X20,0X20,0XC0,0X0F,0X00,0X00,0X00,0X00,0X0F,  #  n
  0XC0,0X20,0X20,0X20,0X20,0XC0,0X07,0X08,0X08,0X08,0X08,0X07,  #  o
  0XE0,0X40,0X20,0X20,0X20,0XC0,0X3F,0X04,0X08,0X08,0X08,0X07,  #  p
  0XC0,0X20,0X20,0X20,0X40,0XE0,0X07,0X08,0X08,0X08,0X04,0X3F,  #  q
  0XE0,0X40,0X20,0X20,0X20,0XC0,0X0F,0X00,0X00,0X00,0X00,0X00,  #  r
  0X40,0XA0,0X20,0X20,0X20,0X40,0X04,0X08,0X09,0X09,0X0A,0X04,  #  s
  0X20,0X20,0XFC,0X20,0X20,0X00,0X00,0X00,0X07,0X08,0X08,0X04,  #  t
  0XE0,0X00,0X00,0X00,0X00,0XE0,0X07,0X08,0X08,0X08,0X04,0X0F,  #  u
  0X00,0XE0,0X00,0X00,0X00,0XE0,0X00,0X00,0X03,0X0C,0X03,0X00,  #  v
  0X00,0XE0,0X00,0X80,0X00,0XE0,0X00,0X07,0X08,0X07,0X08,0X07,  #  w
  0X60,0X80,0X00,0X00,0X80,0X60,0X0C,0X02,0X01,0X01,0X02,0X0C,  #  x
  0XE0,0X00,0X00,0X00,0X00,0XE0,0X13,0X24,0X24,0X24,0X22,0X1F,  #  y
  0X20,0X20,0X20,0XA0,0X60,0X20,0X08,0X0C,0X0B,0X08,0X08,0X08,  #  z
  0X00,0X00,0X80,0X7C,0X02,0X02,0X00,0X00,0X00,0X1F,0X20,0X20,  #  braceleft
  0X00,0X00,0X00,0XFE,0X00,0X00,0X00,0X00,0X00,0X3F,0X00,0X00,  #  bar
  0X00,0X02,0X02,0X7C,0X80,0X00,0X00,0X20,0X20,0X1F,0X00,0X00,  #  braceright
  0X0C,0X02,0X04,0X08,0X10,0X0C,0X00,0X00,0X00,0X00,0X00,0X00,  #  asciitilde
  0XFE,0XFE,0XFE,0XFE,0XFE,0XFE,0X3F,0X3F,0X3F,0X3F,0X3F,0X3F   #  del
]

def ssd1306_init():
    GPIO.output(led, GPIO.LOW)
    myData = [0xa8, 0x3f, 0xd3, 0x0, 0x40, 0xa0, 0xc0, 0xda, 0x2, 0x81, 0x7f, 0xa4, 0xa6, 0xd5, 0x80, 0x8d, 0x14, 0xaf]
    spi.writebytes( myData )

def set_col_addr( col_start, col_end ):
    GPIO.output(led, GPIO.LOW)
    D0 = 0x21
    D1 = col_start & 0x7f
    D2 = col_end & 0x7f
    myData = [D0, D1, D2]
    spi.writebytes( myData )

def set_page_addr( page_start, page_end ):
    GPIO.output(led, GPIO.LOW)
    D0 = 0x22
    D1 = page_start & 0x3
    D2 = page_end & 0x3
    myData = [D0, D1, D2]
    spi.writebytes( myData )

def set_horizontal_mode():
    GPIO.output(led, GPIO.LOW)
    myData = [0x20, 0x00]
    spi.writebytes( myData )

def set_start_page( page ):
    GPIO.output(led, GPIO.LOW)
    myData = 0xB0 | (page & 0x3)
    spi.writebytes( myData )

def set_start_col( col ):
    GPIO.output(led, GPIO.LOW)
    D0 = 0xf & col
    D1 = (0xf & (col >> 4)) | 0x10
    myData = [D0, D1]
    spi.writebytes( myData )

def clearDisplay():
    set_col_addr( 0, 127 )
    set_page_addr( 0, 3 )
    GPIO.output(led, GPIO.HIGH)
    for j in range(4):
        for k in range(8):
            myData = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            spi.writebytes( myData )

def oledprintf( ch ):
  start_col = 0
  page2_3 = 0

  for j in range(len(ch)):
      if ch[j] != '\n' and ch[j] != '\r':
          mychar = [None] * 12
          tmp = ord(ch[j]) - ord(' ')
          tmp1 = (tmp << 3) + (tmp << 2)  #  tmp x 12
          for i in range(12):
              mychar[i] = font7x14[tmp1]
              tmp1 += 1
          end_col = start_col + 5
          set_col_addr( start_col, end_col )
          if page2_3 == 0:
              set_page_addr( 0, 1 )
          else:
              set_page_addr( 2, 3 )
          
          GPIO.output(led, GPIO.HIGH)
          spi.writebytes( mychar )
          start_col += 7
      else:
          page2_3 = 1
          start_col = 0
      j += 1

def oledascii():
    for k in range(3):
        start_col = 0
        for j in range(32):              # 16 characters per two pages
            mychar = [None] * 12
            tmp = j + (k << 5)
            tmp1 = (tmp << 3) + (tmp << 2)  # tmp x 12
            for i in range(12):
                mychar[i] = font7x14[tmp1]
                tmp1 += 1
            
            end_col = start_col + 5
            set_col_addr( start_col, end_col )
            if j < 16:
                set_page_addr( 0, 1 )
            else:
                set_page_addr( 2, 3 )
            
            GPIO.output(led, GPIO.HIGH)
            spi.writebytes( mychar )
            start_col += 7
            if start_col >= 112:
                start_col = 0
        
        time.sleep( 2 )
        clearDisplay()

def ssd1306_test():
    GPIO.setup(led,GPIO.OUT)
    GPIO.output(led, GPIO.HIGH)
    spi.open(2, 0)
    spi.max_speed_hz = 5000000
    ssd1306_init()

    # set_page_mode()
    set_horizontal_mode()
    set_col_addr( 0, 127 )
    set_page_addr( 0, 3 )
  
    GPIO.output(led, GPIO.HIGH)
    for j in range(4):
        i = 0
        while i < 128:
	    myData = [0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81]
            spi.writebytes( myData )
            i=i+8

    time.sleep( 2 )
    clearDisplay()
    oledascii()
    time.sleep( 2 )
    clearDisplay()
    oledprintf( "This is a test !\nIt works !\n" )
    spi.close()


item = ""
while item != 'q':
    item = raw_input("-- select a test --\r\n1. uart test\r\n2. led test\r\n3. button test\r\n4. pwm led test\r\n5. i2c lcd test\r\n6. tongsong\r\n7. servo\r\n8. spi oled test\r\nq. quit\r\n")
    if item == '1':
        uart_test(port)
    elif item == '2':
        led_test()
    elif item == '3':
        button_test()
    elif item == '4':
        pwm_led_test()
    elif item == '5':
        i2c_lcd_test()
    elif item == '6':
        tongsong()
    elif item == '7':
        servo()
    elif item == '8':
        ssd1306_test()
    elif item == 'q':
        print "Goodbye!"
        break
