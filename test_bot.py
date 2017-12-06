import time
from serial import Serial

m = Serial("/dev/ttyACM0")

m.write('f')
time.sleep(1)

m.write('b')
time.sleep(1)

m.write('r')
time.sleep(1)

m.write('l')
time.sleep(1)

m.write('s')
