#!/usr/bin/env python3
import time
import sys
import termios
import tty
import select
import RPi.GPIO as GPIO


class Motor:
    def __init__(self, in1, in2, en, invert=False, pwm_hz=1000):
        self.in1 = in1
        self.in2 = in2
        self.en = en
        self.invert = invert

        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(en, GPIO.OUT)

        self.pwm = GPIO.PWM(en, pwm_hz)  # software PWM
        self.pwm.start(0)

    def toggle_invert(self):
        self.invert = not self.invert

    def set(self, value):
        """
        value in [-1..1]
        sign = direction
        magnitude = speed
        """
        value = max(-1.0, min(1.0, value))
        if self.invert:
            value = -value

        if abs(value) < 0.02:
            self.stop()
            return

        forward = value > 0
        duty = int(abs(value) * 100)

        GPIO.output(self.in1, GPIO.HIGH if forward else GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW if forward else GPIO.HIGH)
        self.pwm.ChangeDutyCycle(duty)

    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)


def get_key_nonblocking(timeout=0.02):
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
    # YOUR EXISTING PIN MAP
    # -----------------------
    LF = Motor(5, 6, 17)       # Left Front
    RF = Motor(16, 20, 27)     # Right Front
    LR = Motor(23, 24, 22)     # Left Rear
    RR = Motor(25, 21, 10)     # Right Rear

    wheels = {"LF": LF, "RF": RF, "LR": LR, "RR": RR}

    speed = 0.60
    speed_step = 0.05

    def stop_all():
        for m in wheels.values():
            m.stop()

    def apply_pattern(pattern):
        """
        pattern is dict like: {"LF": +1, "RF": -1, "LR": +1, "RR": -1}
        We multiply by 'speed' and send to each motor.
        """
        for name, direction in pattern.items():
            wheels[name].set(direction * speed)

    # -----------------------
    # TABLE-BASED MOVEMENTS
    # -----------------------
    # NOTE: We interpret:
    #   +1  == CW
    #   -1  == CCW
    # If your robot goes opposite, use invert keys 1/2/3/4 per wheel.
    FORWARD       = {"LF": +1, "RF": +1, "LR": +1, "RR": +1}
    BACKWARD      = {"LF": -1, "RF": -1, "LR": -1, "RR": -1}
    STRAFE_LEFT   = {"LF": -1, "RF": +1, "LR": +1, "RR": -1}
    STRAFE_RIGHT  = {"LF": +1, "RF": -1, "LR": -1, "RR": +1}
    ROTATE_LEFT   = {"LF": -1, "RF": +1, "LR": -1, "RR": +1}
    ROTATE_RIGHT  = {"LF": +1, "RF": -1, "LR": +1, "RR": -1}

    current_motion = "STOP"

    print("""
===== MECANUM TELEOP (Table Based) =====
No Enter needed.

Move:
  W : Forward
  S : Backward
  A : Strafe Left
  D : Strafe Right
  Q : Rotate Left
  E : Rotate Right

Speed:
  M : Speed up
  N : Speed down

Invert wheel direction (to match CW/CCW table):
  1 : toggle invert LF
  2 : toggle invert RF
  3 : toggle invert LR
  4 : toggle invert RR

Safety:
  SPACE : Stop
  X     : Stop (alt)
  Ctrl+C : Exit
""")

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)

        last_cmd = time.time()
        watchdog_timeout = 0.25
        last_print = 0

        while True:
            key = get_key_nonblocking(timeout=0.02)

            if key:
                k = key.lower()
                last_cmd = time.time()

                if k == " " or k == "x":
                    stop_all()
                    current_motion = "STOP"

                elif k == "w":
                    apply_pattern(FORWARD)
                    current_motion = "FORWARD"

                elif k == "s":
                    apply_pattern(BACKWARD)
                    current_motion = "BACKWARD"

                elif k == "a":
                    apply_pattern(STRAFE_LEFT)
                    current_motion = "STRAFE_L"

                elif k == "d":
                    apply_pattern(STRAFE_RIGHT)
                    current_motion = "STRAFE_R"

                elif k == "q":
                    apply_pattern(ROTATE_LEFT)
                    current_motion = "ROTATE_L"

                elif k == "e":
                    apply_pattern(ROTATE_RIGHT)
                    current_motion = "ROTATE_R"

                elif k == "m":
                    speed = clamp(speed + speed_step, 0.10, 1.00)
                    # re-apply last motion so speed changes while moving
                    # (just trigger the same command again)
                    if current_motion == "FORWARD": apply_pattern(FORWARD)
                    elif current_motion == "BACKWARD": apply_pattern(BACKWARD)
                    elif current_motion == "STRAFE_L": apply_pattern(STRAFE_LEFT)
                    elif current_motion == "STRAFE_R": apply_pattern(STRAFE_RIGHT)
                    elif current_motion == "ROTATE_L": apply_pattern(ROTATE_LEFT)
                    elif current_motion == "ROTATE_R": apply_pattern(ROTATE_RIGHT)

                elif k == "n":
                    speed = clamp(speed - speed_step, 0.10, 1.00)
                    if current_motion == "FORWARD": apply_pattern(FORWARD)
                    elif current_motion == "BACKWARD": apply_pattern(BACKWARD)
                    elif current_motion == "STRAFE_L": apply_pattern(STRAFE_LEFT)
                    elif current_motion == "STRAFE_R": apply_pattern(STRAFE_RIGHT)
                    elif current_motion == "ROTATE_L": apply_pattern(ROTATE_LEFT)
                    elif current_motion == "ROTATE_R": apply_pattern(ROTATE_RIGHT)

                # Toggle invert per wheel
                elif k == "1":
                    LF.toggle_invert()
                    print(f"\nLF invert = {LF.invert}")
                elif k == "2":
                    RF.toggle_invert()
                    print(f"\nRF invert = {RF.invert}")
                elif k == "3":
                    LR.toggle_invert()
                    print(f"\nLR invert = {LR.invert}")
                elif k == "4":
                    RR.toggle_invert()
                    print(f"\nRR invert = {RR.invert}")

            # watchdog stop if no key pressed recently
            if time.time() - last_cmd > watchdog_timeout:
                stop_all()
                current_motion = "STOP"

            # status line
            if time.time() - last_print > 0.2:
                last_print = time.time()
                sys.stdout.write(
                    f"\rMotion={current_motion:<9} Speed={speed:.2f} | "
                    f"inv LF={LF.invert} RF={RF.invert} LR={LR.invert} RR={RR.invert}   "
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

