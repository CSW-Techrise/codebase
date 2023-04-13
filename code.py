import time
import board
import analogio
import digitalio
from radiation import Radiation
import adafruit_sdcard
import busio
import storage

# !IMPORTANT! Create instances of AnalogIn and DigitalInOut for both geiger counters (change these accordingly) -------------------------!
sensor_pin_1 = analogio.AnalogIn(board.A0)
ns_pin_1 = digitalio.DigitalInOut(board.D0)
ns_pin_1.switch_to_input(pull=digitalio.Pull.DOWN)
sensor_pin_2 = analogio.AnalogIn(board.A1)
ns_pin_2 = digitalio.DigitalInOut(board.D1)
ns_pin_2.switch_to_input(pull=digitalio.Pull.DOWN)
sensor_pin_3 = analogio.AnalogIn(board.A2)
ns_pin_3 = digitalio.DigitalInOut(board.D2)
ns_pin_3.switch_to_input(pull=digitalio.Pull.DOWN)
sensor_pin_4 = analogio.AnalogIn(board.A3)
ns_pin_4 = digitalio.DigitalInOut(board.D3)
ns_pin_4.switch_to_input(pull=digitalio.Pull.DOWN)

# !IMPORTANT! This is the SD Card pin (change this accordingly) Use any pin that is not taken by SPI -------------------------------------------------------------------------!
SD_CS = board.D10

# !IMPORTANT! These are the SPI Flash pins that will be used for bitflip detection (change these accordingly) ------------------------------------------------------!
bit = board.D8

# Create instances of the Radiation class for both geiger counters
rad_1 = Radiation(sensor_pin_1, ns_pin_1)
rad_2 = Radiation(sensor_pin_2, ns_pin_2)
rad_3 = Radiation(sensor_pin_3, ns_pin_3)
rad_4 = Radiation(sensor_pin_4, ns_pin_4)


# Connect to the card and mount the filesystem
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Connect to bitflip pins
bspi = busio.SPI(board.SCK, board.MOSI, board.MISO)
bcs = digitalio.DigitalInOut(bit)
b = SPIDevice(bspi, bcs)

# Writing a 100000 bit buffer to each pin

x = bytearray(100000)


while True:
    # Call the get_total_radiation() method for all geiger counters
    total_uSv_h_1 = rad_1.get_total_radiation()
    total_uSv_h_2 = rad_2.get_total_radiation()
    total_uSv_h_3 = rad_3.get_total_radiation()
    total_uSv_h_4 = rad_4.get_total_radiation()

    # Checking the current status of the flips
    flips = []

    # Reading the current status of the flips
    b.readinto(flips)

    # Number of bit flips
    num = 0


    # Iterating through and checking for flips
    for i in range(100000):
        if x[i] != flips[i]:
            num += 1


    # Write the total radiation value in microsieverts for all geiger counters to SD Card
    with open("/sd/SDtest.txt", "a") as f:
        f.write(time.monotonic_ns())
        f.write("Total uSv/h Geiger 1: {0:.4f}".format(total_uSv_h_1))
        f.write("Total uSv/h Geiger 2: {0:.4f}".format(total_uSv_h_2))
        f.write("Total uSv/h Geiger 3: {0:.4f}".format(total_uSv_h_3))
        f.write("Total uSv/h Geiger 4: {0:.4f}".format(total_uSv_h_4))
        f.write("Number of flips (1): {}".format(num))

    # Replacing the old arrays with the current arrays
    # !QUESTION! Does this force the flips arrays to become references for the x arrays? ------------------------------------------------------!
    x = [i for i in flips]

    time.sleep(10)
