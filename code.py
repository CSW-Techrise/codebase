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
bit_one = board.D11
bit_two = board.D12
bit_three = board.D13
bit_four = board.D9

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

bspi_one = busio.SPI(board.SCK, board.MOSI, board.MISO)
bcs_one = digitalio.DigitalInOut(bit_one)
b_one = SPIDevice(bspi_one, bcs_one)
bspi_two = busio.SPI(board.SCK, board.MOSI, board.MISO)
bcs_two = digitalio.DigitalInOut(bit_two)
b_two = SPIDevice(bspi_two, bcs_two)
bspi_three = busio.SPI(board.SCK, board.MOSI, board.MISO)
bcs_three = digitalio.DigitalInOut(bit_three)
b_three = SPIDevice(bspi_three, bcs_three)
bspi_four = busio.SPI(board.SCK, board.MOSI, board.MISO)
bcs_four = digitalio.DigitalInOut(bit_four)
b_four = SPIDevice(bspi_four, bcs_four)

# Writing a 100000 bit buffer to each pin

x_one = bytearray(100000)
x_two = bytearray(100000)
x_three = bytearray(100000)
x_four = bytearray(100000)
b_one.write(x_one)
b_two.write(x_two)
b_three.write(x_three)
b_four.write(x_four)


# Sparse maps for bitflips and their position
bitflips_one = {}
bitflips_two = {}
bitflips_three = {}
bitflips_four = {}

while True:
    # Call the get_total_radiation() method for all geiger counters
    total_uSv_h_1 = rad_1.get_total_radiation()
    total_uSv_h_2 = rad_2.get_total_radiation()
    total_uSv_h_3 = rad_3.get_total_radiation()
    total_uSv_h_4 = rad_4.get_total_radiation()

    # Checking the current status of the flips
    flips_one = []
    flips_two = []
    flips_three = []
    flips_four = []

    # Reading the current status of the flips
    b_one.readinto(flips_one)
    b_two.readinto(flips_two)
    b_three.readinto(flips_three)
    b_four.readinto(flips_four)

    # Number of bit flips
    num_one = 0
    num_two = 0
    num_three = 0
    num_four = 0


    # Iterating through and checking for flips
    for i in range(100000):
        if x_one[i] != flips_one[i]:
            num_one += 1
        if x_two[i] != flips_two[i]:
            num_two += 1
        if x_three[i] != flips_three[i]:
            num_three += 1
        if x_four[i] != flips_four[i]:
            num_four += 1


    # Write the total radiation value in microsieverts for all geiger counters to SD Card
    with open("/sd/SDtest.txt", "a") as f:
        f.write(time.monotonic_ns())
        f.write("Total uSv/h Geiger 1: {0:.4f}".format(total_uSv_h_1))
        f.write("Total uSv/h Geiger 2: {0:.4f}".format(total_uSv_h_2))
        f.write("Total uSv/h Geiger 3: {0:.4f}".format(total_uSv_h_3))
        f.write("Total uSv/h Geiger 4: {0:.4f}".format(total_uSv_h_4))
        f.write("Number of flips (1): {}".format(num_one))
        f.write("Number of flips (2): {}".format(num_two))
        f.write("Number of flips (3): {}".format(num_three))
        f.write("Number of flips (4): {}".format(num_four))

    # Replacing the old arrays with the current arrays
    # !QUESTION! Does this force the flips arrays to become references for the x arrays? ------------------------------------------------------!
    x_one = flips_one
    x_two = flips_two
    x_three = flips_three
    x_four = flips_four

    time.sleep(0.6)
