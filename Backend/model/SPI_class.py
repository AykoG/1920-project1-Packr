from RPi import GPIO
import os
import time
import spidev

class SPI_class:
    def __init__(self, bus = 0, device = 0):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 10 ** 5

    def lees_kanaal(self, kanaal):
        SPI_class.__init__(self)
        adc = self.spi.xfer2([1,(8+kanaal) << 4,0])
        data = ((adc[1]&3) << 8) + adc[2]
        self.spi.close()
        return data

    def omzetten_naar_temperatuur(self, data, rest):
        volt = round((data * 3.3) / float(1023), rest)
        temperatuur = (volt - 0.5) * 100
        return temperatuur