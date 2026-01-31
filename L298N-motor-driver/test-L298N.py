#!/usr/bin/env python3
import time
import sys
import termios
import tty
import select
import RPi.GPIO as GPIO


class Motor:
    def __init__(self, in1: int, in2: int, en: int, invert: bool = False, pwm_hz: int = 1000):
        self.in1 = in1
        self.in2 = in2
        self.en = en
        self.invert = invert

        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.en, GPIO.OUT)

        self.pwm = GPIO.PWM(self.en, pwm_hz)  # software PWM
        self.pwm.start(0)

        self.last_value = 0.0
        self.stop()

    def toggle_invert(self):
        self.invert = not self.invert

    def set(self, value: float):
        """
        value in [-1.0, 1.0]
        + = forward
        - = backward
        """
        value = max(-1.0, min(1.0, value))
        if self.invert:
            value = -value

        # deadband
        if abs(value) < 0.02:
            self.stop()
            return

        forward = value > 0
        duty = int(abs(value) * 100)

        GPIO.output(self.in1, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW if forward else GPIO.HIGH)
        self.pwm.ChangeDutyCycle(duty)

        self.last_value = value

    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)
        self.last_value = 0.0


def get_key_nonblocking(timeout=0.02):
    """Returns one char if available, else None."""
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.read(1)
    return None


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # -----------------------
    # PIN MAP (BCM) EXAMPLE
    # -----------------------
    LEFT = Motor(in1=5,  in2=6,  en=17, invert=False, pwm_hz=1000)
    RIGHT = Motor(in1=16, in2=20, en=27, invert=False, pwm_hz=1000)

    speed = 0.60
    speed_step = 0.05
    min_speed = 0.10
    max_speed = 1.00

    current_motion = "STOP"

    def stop_all():
        nonlocal current_motion
        LEFT.stop()
        RIGHT.stop()
        current_motion = "STOP"

    # --- combined commands ---
    def forward():
        nonlocal current_motion
        LEFT.set(+speed)
        RIGHT.set(+speed)
        current_motion = "FORWARD"

    def backward():
        nonlocal current_motion
        LEFT.set(-speed)
        RIGHT.set(-speed)
        current_motion = "BACKWARD"

    def turn_left():
        nonlocal current_motion
        LEFT.set(-speed)
        RIGHT.set(+speed)
        current_motion = "LEFT"

    def turn_right():
        nonlocal current_motion
        LEFT.set(+speed)
        RIGHT.set(-speed)
        current_motion = "RIGHT"

    # --- single-motor commands ---
    def left_forward_only():
        nonlocal current_motion
        LEFT.set(+speed)
        RIGHT.stop()
        current_motion = "L_ONLY_F"

    def left_backward_only():
        nonlocal current_motion
        LEFT.set(-speed)
        RIGHT.stop()
        current_motion = "L_ONLY_B"

    def right_forward_only():
        nonlocal current_motion
        LEFT.stop()
        RIGHT.set(+speed)
        current_motion = "R_ONLY_F"

    def right_backward_only():
        nonlocal current_motion
        LEFT.stop()
        RIGHT.set(-speed)
        current_motion = "R_ONLY_B"

    def reapply_motion():
        if current_motion == "FORWARD":
            forward()
        elif current_motion == "BACKWARD":
            backward()
        elif current_motion == "LEFT":
            turn_left()
        elif current_motion == "RIGHT":
            turn_right()
        elif current_motion == "L_ONLY_F":
            left_forward_only()
        elif current_motion == "L_ONLY_B":
            left_backward_only()
        elif current_motion == "R_ONLY_F":
            right_forward_only()
        elif current_motion == "R_ONLY_B":
            right_backward_only()
        else:
            stop_all()

    print("""
L298N Teleop Test (real-time)
--------------------------------------
MAIN:
  W : forward
  S : backward
  A : spin left
  D : spin right

SINGLE MOTOR TEST:
  I : left motor forward only
  K : left motor backward only
  O : right motor forward only
  L : right motor backward only

SPEED:
  M : speed up
  N : speed down

INVERT (fix wrong wiring direction):
  Z : toggle invert LEFT motor
  X : toggle invert RIGHT motor

SAFETY:
  SPACE : stop
  Q     : quit
""")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        last_cmd_time = time.time()
        watchdog_timeout = 0.20
        last_print = 0

        while True:
            key = get_key_nonblocking(timeout=0.02)

            if key is not None:
                k = key.lower()
                last_cmd_time = time.time()

                if k == "q":
                    stop_all()
                    break

                elif k == " ":
                    stop_all()

                # invert toggles
                elif k == "z":
                    LEFT.toggle_invert()
                    reapply_motion()
                    print(f"\nLEFT invert = {LEFT.invert}")

                elif k == "x":
                    RIGHT.toggle_invert()
                    reapply_motion()
                    print(f"\nRIGHT invert = {RIGHT.invert}")

                # combined
                elif k == "w":
                    forward()
                elif k == "s":
                    backward()
                elif k == "a":
                    turn_left()
                elif k == "d":
                    turn_right()

                # single motor
                elif k == "i":
                    left_forward_only()
                elif k == "k":
                    left_backward_only()
                elif k == "o":
                    right_forward_only()
                elif k == "l":
                    right_backward_only()

                # speed adjust
                elif k == "m":
                    speed = clamp(speed + speed_step, min_speed, max_speed)
                    reapply_motion()
                elif k == "n":
                    speed = clamp(speed - speed_step, min_speed, max_speed)
                    reapply_motion()

            # watchdog stop
            if time.time() - last_cmd_time > watchdog_timeout:
                stop_all()

            # status line
            if time.time() - last_print > 0.2:
                last_print = time.time()
                sys.stdout.write(
                    f"\rMotion={current_motion:<10}  Speed={speed:.2f}  "
                    f"L_inv={LEFT.invert}  R_inv={RIGHT.invert}   "
                )
                sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    finally:
        stop_all()
        GPIO.cleanup()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nExited safely.")


if __name__ == "__main__":
    main()

