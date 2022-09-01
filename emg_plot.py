#Colegio de Montalban, Rodriguez, Rizal, Phil. - BSCpE 2018-2022
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import time
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115()


class Value:
    '''The analyzer of the values received'''
    def __init__(self):
        self.value = 0
        self.line = []
        self.tres = []

    def scanner(self, limit):
        self.tres.append(self.value)
        if len(self.tres) > 3:
            self.tres.pop(0)
            self.line.append(int(np.mean(self.tres[:])))
        print(self.line)

        if len(self.line) > limit:
            self.line.pop(0)

v0, v1, v2, v3 = Value(), Value(), Value(), Value()


def main(max_val, min_val, limit):
    '''visualself.fliping the values from sensors'''
    style.use('fast')
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_ylim(min_val,max_val)
    ax1.set_title('Sensors')
    ax1.grid(True)

    line0, = ax1.plot([], 'ro-', label='sensor_forward 0')
    line1, = ax1.plot([], 'yo-', label='sensor_left 1')
    line2, = ax1.plot([], 'mo-', label='sensor_right 2')
    line3, = ax1.plot([], 'co-', label='sensor_N/A 3')
    ax1.legend(loc='upper left')


    def animate(cnt):
        '''reading data and grouping them in lists forms'''
        GAIN = 1
        values = np.array([0]*4)
        for i in range(4):
            values[i] = adc.read_adc(i, gain=GAIN)
            #values[i] = np.random.randint(0, 2000)
        print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))

        v0.value, v1.value, v2.value, v3.value = values[0], values[1], values[2], values[3]

        line0.set_data(list(range(len(v0.line))), v0.line)
        line1.set_data(list(range(len(v1.line))), v1.line)
        line2.set_data(list(range(len(v2.line))), v2.line)
        line3.set_data(list(range(len(v3.line))), v3.line)

        ax1.relim()
        ax1.autoscale_view()

        v0.scanner(limit)
        v1.scanner(limit)
        v2.scanner(limit)
        v3.scanner(limit)

    ani = animation.FuncAnimation(fig, animate, interval=1)
    plt.show()

main(5000, 0, 40)
