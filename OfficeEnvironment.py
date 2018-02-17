#!/usr/bin/env python
# http://wiki.sunfounder.cc/index.php?title=OLED-SSD1306_Module
# https://learn.adafruit.com/ssd1306-oled-displays-with-raspberry-pi-and-beaglebone-black/usage
# Crontab - @reboot python /home/pi/python/PlantTelemetry.py &
# scp PlantTelemetry.py pi@192.168.0.23:/home/pi/python/
import sys
import time
import Adafruit_DHT
import datetime
import Adafruit_SSD1306
import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from envirophat import light, weather, motion, analog

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
# Load default font.
font = ImageFont.load_default()

def write(line):
    sys.stdout.write(line)
    sys.stdout.flush()

def disp_stats():
    write("--- Enviro pHAT Monitoring ---")
    rgb = light.rgb()
    analog_values = analog.read_all()
    mag_values = motion.magnetometer()
    acc_values = [round(x,2) for x in motion.accelerometer()]
    humidity, temp2 = Adafruit_DHT.read_retry(11, 17)
    currentDT = datetime.datetime.now()

    output = """
Time: {tm}; Temp: {t}c; Plant Temp: {t2}c; Humd: {hd}%; Pressure: {p}Pa; Light: {c}, RGB: {r}, {g}, {b}; Soil: {a0}%
""".format(
    tm = currentDT.strftime("%Y-%m-%d %H:%M:%S"),
    t = abs(weather.temperature() * 9/5.0 + 32),
    t2 = abs((temp2 * 9/5.0 + 32)),
    hd = round(humidity,0),
    p = round(weather.pressure(),0),
    c = light.light(),
    r = rgb[0],
    g = rgb[1],
    b = rgb[2],
    h = motion.heading(),
    a0 = round((analog_values[0]* 100)/434,2)*100,
    a1 = analog_values[1],
    a2 = analog_values[2],
    a3 = analog_values[3],
    mx = mag_values[0],
    my = mag_values[1],
    mz = mag_values[2],
    ax = acc_values[0],
    ay = acc_values[1],
    az = acc_values[2]
)
    #output = output.replace("\n","\n\033[K")
    write(output)
    #lines = len(output.split("\n"))
    #write("\033[{}A".format(lines - 1))

#    time.sleep(10)
        
def disp_OLED():
    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )

    rgb = light.rgb()

    analog_values = analog.read_all()
    humidity, temp2 = Adafruit_DHT.read_retry(11, 17)
    #currentDT = datetime.datetime.now()
    #tm = currentDT.strftime("%m-%d-%y")
    # Days since watering
    d2 = datetime.datetime.strptime('1-1-18','%m-%d-%y')
    d_diff = abs((datetime.datetime.now() - d2).days)

    t = int(weather.temperature() * 9/5.0 + 32)
    t2 = int((temp2 * 9/5.0 + 32))
    hd = int(round(humidity,0))
    lgt = light.light()
    soil = int(((analog_values[0] * 100)/434)*100)

    # 128 x 32

    draw.text((x, top),       "Lst: " + str(d_diff), font=font, fill=255)
    draw.text((60, top),       "Lgt: " + str(lgt), font=font, fill=255)

    draw.text((x, top+8),     "Tmp1: " + str(t), font=font, fill=255)
    draw.text((60, top+8),    "Tmp2: " + str(t2), font=font, fill=255)

    draw.text((x, top+16),    "Soil: " + str(soil),  font=font, fill=255)
    draw.text((60, top+16),    "Humd: " + str(hd)+"%",  font=font, fill=255)

    draw.text((x, top+25),    "IP: " + str(IP),  font=font, fill=255)

    # Display image.
    disp.image(image)
    disp.display()

def main():
    try:
        while True:
            #disp_stats()
            disp_OLED()
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        exit()

if __name__ == "__main__":
    main()
