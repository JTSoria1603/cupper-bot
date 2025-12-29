import time
import board
import busio
from adafruit_as5600 import AS5600

BAR_LEN = 40

i2c = busio.I2C(board.SCL, board.SDA)
sensor = AS5600(i2c)

print("Rotate the magnet (Ctrl+C to stop)\n")

while True:
    raw = sensor.raw_angle              # 0..4095
    angle = (raw * 360.0) / 4096.0       # compute clean angle

    # clamp angle to [0, 360)
    angle = max(0.0, min(angle, 359.999))

    pos = int((angle / 360.0) * BAR_LEN)

    # safety clamp
    if pos < 0:
        pos = 0
    if pos >= BAR_LEN:
        pos = BAR_LEN - 1

    bar = ["-"] * BAR_LEN
    bar[pos] = "|"

    print(f"\r[{''.join(bar)}]  {angle:7.2f}°   raw:{raw:4d}", end="", flush=True)
    time.sleep(0.05)

