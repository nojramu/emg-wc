# Colegio de Montalban, Rodriguez, Rizal, Phil. - BSCpE 2018-2022
""" This Python code was created for a capstone project titled
    "Electromyography(EMG) on maneuvering wheelchair." A completion
    requirement for a computer engineering degree."""

import numpy as np
import time
from datetime import datetime
import RPi.GPIO as gpio
import Adafruit_ADS1x15
import Adafruit_CharLCD as LCD
from bluedot import BlueDot
adc = Adafruit_ADS1x15.ADS1115()
bd = BlueDot()


class Value:
    """The receiver's value analyzer"""
    def __init__(self):
        self.value = 0
        self.count = 0
        self.mark = 0
        self.line = []
        self.tres = []
        self.new_min = 0
        self.new_max = 0

    def scanner(self, limit):
        """Function to determine the command based on input signals"""
        mark_requirement = 20
        smoother_value = 3
        pass_requirement = 75

        self.tres.append(self.value)  # smoothens values
        if len(self.tres) > smoother_value:
            self.tres.pop(0)
            self.line.append(int(np.mean(self.tres[:])))

        if len(self.line) > limit:  # normal range analyzer
            self.line.pop(0)
            min1 = min(self.line[:limit//5])
            max1 = max(self.line[:limit//5])
            min2 = min(self.line[(limit//5)-1:limit*2//5])
            max2 = max(self.line[(limit//5)-1:limit*2//5])
            min3 = min(self.line[(limit*2//5)-1:limit*3//5])
            max3 = max(self.line[(limit*2//5)-1:limit*3//5])
            min4 = min(self.line[(limit*3//5)-1:limit*4//5])
            max4 = max(self.line[(limit*3//5)-1:limit*4//5])
            min5 = min(self.line[(limit*4//5)-1:])
            max5 = max(self.line[(limit*4//5)-1:])
            observer = int(np.mean(self.tres[:]))

            if (min(self.line)+pass_requirement >
                int((min1+min2+min3+min4+min5)/5) and
                    max(self.line)-pass_requirement <
                    int((max1+max2+max3+max4+max5)/5)):
                self.new_min = min(self.line)
                self.new_max = max(self.line)
            print(self.new_min, self.new_max, observer)

        if (v0.new_max != 0 and v1.new_max != 0 and
                v2.new_max != 0):  # signal finder
            self.mark = 0 if (observer > self.new_min and observer <
                              self.new_max) else self.mark + 1
            if self.mark == mark_requirement:
                self.count += 1

    def reset(self):
        self.line = []
        self.tres = []
        self.new_min = 0
        self.new_max = 0
        self.mark = 0
        self.count = 0

v0, v1, v2 = Value(), Value(), Value()


class Hbridge:
    """Decleration of output device variables"""
    def __init__(self, dir1, dir2):
        self.dir1 = dir1
        self.dir2 = dir2
        self.message = 'message'

    def move(self, pwm_speed):
        """Controlling the display and motor movements"""
        print(self.message)

        gpio.setmode(gpio.BCM)
        gpio.setup(17, gpio.OUT)
        gpio.setup(27, gpio.OUT)
        gpio.setup(18, gpio.OUT)
        gpio.setup(22, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        pwm = gpio.PWM(18, 5000)
        pwm.start(0)

        """ lcd pin configuration: (lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6,
            lcd_d7, lcd_columns, lcd_rows)"""
        lcd = LCD.Adafruit_CharLCD(26, 19, 13, 6, 5, 11, 16, 2)

        if gpio.input(22) == gpio.HIGH:
            v0.reset()
            v1.reset()
            v2.reset()
        gpio.output(17, self.dir1)
        gpio.output(27, self.dir2)
        pwm.ChangeDutyCycle(pwm_speed)
        lcd.message(self.message)
        time.sleep(0.01)  # adjustable
        pwm.stop()
        lcd.clear()
        gpio.cleanup()

forward = Hbridge(True, True)
backward = Hbridge(False, False)
turn_left = Hbridge(False, True)
turn_right = Hbridge(True, False)
stop = Hbridge(False, False)


class Flipper:
    """Smoothen bluedot button command"""
    def __init__(self, flip):
        self.flip = flip
flips = Flipper(0)


def main(limit, pwm_speed):
    def main_loop():
        """Reading data and grouping them in lists forms"""
        GAIN = 1
        values = np.array([0]*4)
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN)
            # values[i] = np.random.randint(0, 1000)
        print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))

        v0.value, v1.value, v2.value = values[0], values[1], values[2]

        v0.scanner(limit)
        v1.scanner(limit)
        v2.scanner(limit)

        if bd.is_connected is True:
            bd.when_pressed = dpad
            move_flip(flips.flip, pwm_speed)
            bd.when_released = pause_flip
        else:
            command(pwm_speed)

        print(len(v0.line))
        print('mark  {} {} {}'.format(v0.mark, v1.mark, v2.mark))
        print('count {} {} {}'.format(v0.count, v1.count, v2.count))

    starts = False
    message = ('PRESS THE BUTTON TO START' + 10*' ' +
               'ELECTROMYOGRAPHY ON MANEUVERING WHEELCHAIR' + 10*' ')

    while starts is False:
        gpio.setmode(gpio.BCM)
        gpio.setup(22, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        lcd = LCD.Adafruit_CharLCD(26, 19, 13, 6, 5, 11, 16, 2)

        if gpio.input(22) == gpio.HIGH:
            starts = True
            break

        lcd.set_cursor(0, 0)
        lcd.message(message[:16])
        lcd.set_cursor(0, 1)
        lcd.message(datetime.now().strftime('%b %d  %H:%M:%S'))
        time.sleep(0.2)
        message = message[1:] + message[0]
        lcd.clear()
        gpio.cleanup()

    while starts is True:
        main_loop()
        # time.sleep(.1)# delay for testing


def command(pwm_speed):
    """EMG control center"""
    if v0.count > 0 and v1.count == 0 and v2.count == 0:
        if v0.count == 2:
            forward.message = '     FORWARD\n      MOVE'
            forward.move(pwm_speed)
        elif v0.count == 3:
            backward.message = '    BACKWARD\n      MOVE'
            backward.move(pwm_speed)
        else:
            stop.message = ' FORW. & BACKW.\n     MARKED'
            stop.move(0)
    elif v1.count > 0 and v0.count == 0 and v2.count == 0:
        if v1.count == 2:
            turn_left.message = '   TURN LEFT\n      MOVE'
            turn_left.move(pwm_speed)
        else:
            stop.message = '   TURN LEFT\n     MARKED'
            stop.move(0)
    elif v2.count > 0 and v0.count == 0 and v1.count == 0:
        if v2.count == 2:
            turn_right.message = '   TURN RIGHT\n      MOVE'
            turn_right.move(pwm_speed)
        else:
            stop.message = '   TURN RIGHT\n     MARKED'
            stop.move(0)
    else:
        if v0.new_max == 0 or v1.new_max == 0 or v2.new_max == 0:
            stop.message = '  CALIBRATING\n    SENSORS'
            stop.move(0)
        else:
            v0.count, v1.count, v2.count = 0, 0, 0
            stop.message = '      STOP\n'
            stop.move(0)


def dpad(pos):
    if pos.top:
        flips.flip = 1
    elif pos.bottom:
        flips.flip = 2
    elif pos.left:
        flips.flip = 3
    elif pos.right:
        flips.flip = 4


def pause_flip():
        flips.flip = 0


def move_flip(i, pwm_speed):
    """Bluetooth commander"""
    if i == 1:
        forward.message = '    FORWARD\n   BLUETOOTH'
        forward.move(pwm_speed)
    elif i == 2:
        backward.message = '    BACKWARD\n   BLUETOOTH'
        backward.move(pwm_speed)
    elif i == 3:
        turn_left.message = '   TURN LEFT\n   BLUETOOTH'
        turn_left.move(pwm_speed)
    elif i == 4:
        turn_right.message = '   TURN RIGHT\n   BLUETOOTH'
        turn_right.move(pwm_speed)
    elif i == 0:
        stop.message = '      STOP\n   BLUETOOTH'
        stop.move(0)


if __name__ == '__main__':
    main(40, 100)
else:
    print('main(array_limit, pwm_speed)')
