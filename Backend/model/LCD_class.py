from RPi import GPIO
import time

cursorB = True
display = True

class LCD_class:
    def __init__(self, par_E, par_RS, par_pinnen):
        GPIO.setup(par_RS,GPIO.OUT)
        GPIO.setup(par_E,GPIO.OUT)
        for pin in par_pinnen:
            GPIO.setup(pin,GPIO.OUT)
        GPIO.output(par_E,GPIO.HIGH)
        self.E = par_E
        self.RS = par_RS
        self.pinnen = par_pinnen

    def set_data_bits(self, value):
        GPIO.output(self.E,GPIO.HIGH)
        mask = 1
        for i in range(0, 8):
            bit = value & mask
            bit >>= i
            if bit == 1:
                GPIO.output(self.pinnen[i],GPIO.HIGH)
            elif bit == 0:
                GPIO.output(self.pinnen[i],GPIO.LOW)
            mask <<= 1
        time.sleep(0.01)
        GPIO.output(self.E,GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.E,GPIO.HIGH)

    def send_instruction(self, value):
        GPIO.output(self.RS,GPIO.LOW)
        self.set_data_bits(value)

    def send_character(self, value):
        GPIO.output(self.RS,GPIO.HIGH)
        self.set_data_bits(value)

    def init_LCD(self):
        global cursorB
        global display
        self.send_instruction(56)
        self.send_instruction(15)
        cursorB = True
        display	= True
        self.send_instruction(1)

    def write_message(self, message, lijn):
        aantal = len(message)
        if aantal < 40:
            if lijn == "1":
                self.send_instruction(2)
                for i in range(0, aantal):
                    self.send_character(ord(message[i]))
            elif lijn == "2":
                self.send_instruction(168)
                for i in range(0, aantal):
                    self.send_character(ord(message[i]))
            else:
                print("Probeer het nog eens!")
        else:
            print("Probeer het nog eens!")

    def cursor_aanpassen(self):
        global cursorB
        if cursorB == True:
            self.send_instruction(14)
            cursorB = False
        elif cursorB == False:
            self.send_instruction(15)
            cursorB = True

    def scroll(self):
        self.send_instruction(24)
        time.sleep(0.01)

    def reverse_scroll(self):
        self.send_instruction(28)
        time.sleep(0.01)

    def display_on_off(self):
        global cursorB
        global display
        if display == True:
            self.send_instruction(8)
            display = False
        elif display == False:
            self.send_instruction(15)
            cursorB = True
            display = True

    def clear_display(self):
        self.send_instruction(1)
