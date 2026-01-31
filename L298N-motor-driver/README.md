# L298N Motor Driver Teleop Test (Raspberry Pi 4)

This project provides a **real-time keyboard teleoperation (teleop)** script to test a **L298N dual H-bridge motor driver** using **2 DC motors** on a **Raspberry Pi 4**.
  
✅ Software PWM using `RPi.GPIO`  
✅ Single-motor debug controls  
✅ Runtime invert toggle (fix wrong wiring without rewiring)

---

## Features

- **WASD** movement test (both motors)
- **Single motor** test (left motor only / right motor only)
- **Speed control** (increase/decrease)
- **Invert toggle** for each motor direction during runtime
- Watchdog stop (robot stops automatically if no key is pressed)

---

## Install

### 1) Clone / copy files
Put these files in a folder, for example:

```
L298N-motor-driver/
  test_L298N.py
  requirements.txt
  README.md
```

### 2) Install dependency

**Recommended (APT):**
```bash
sudo apt update
sudo apt install -y python3-rpi.gpio
```

**Alternative (PIP):**
```bash
pip install -r requirements.txt
```

---

## Wiring (example)

> ⚠️ IMPORTANT: **Use common ground** between the motor power supply and the Raspberry Pi.

| L298N Pin | Raspberry Pi (BCM) | Notes |
|----------|---------------------|------|
| IN1      | GPIO5               | Left motor direction |
| IN2      | GPIO6               | Left motor direction |
| ENA      | GPIO17              | Left motor PWM (remove jumper!) |
| IN3      | GPIO16              | Right motor direction |
| IN4      | GPIO20              | Right motor direction |
| ENB      | GPIO27              | Right motor PWM (remove jumper!) |
| GND      | GND                 | Common ground |

### ENA / ENB Jumper
To control motor speed with PWM:

✅ Remove the **ENA jumper**  
✅ Remove the **ENB jumper**

Then connect ENA/ENB to GPIO pins.

---

## Run

### 1) Make executable (optional)
```bash
chmod +x teleop_l298n.py
```

### 2) Run
```bash
python test_L298N.py
```

If you get a GPIO permission error:
```bash
sudo python test_L298N.py
```

---

## Controls

### Main movement
- `W` : forward (both motors forward)
- `S` : backward (both motors backward)
- `A` : spin left (in place)
- `D` : spin right (in place)

### Single motor test
- `I` : left motor forward only
- `K` : left motor backward only
- `O` : right motor forward only
- `L` : right motor backward only

### Speed control
- `M` : speed up
- `N` : speed down

### Fix wiring direction
If a motor spins the wrong direction (mis-wired), you can invert it instantly:

- `Z` : toggle invert LEFT motor
- `X` : toggle invert RIGHT motor

### Safety
- `SPACE` : STOP immediately
- `Q` : quit

---

## Safety Notes

- Do NOT power DC motors from the Raspberry Pi 5V pin.
- Use a dedicated motor power supply.
- Always connect:
  - Raspberry Pi **GND**
  - L298N **GND**
  - Motor supply **GND**
  together.

---

## Files

- `test_L298N.py` - main teleop script
- `requirements.txt` - Python dependency list
- `README.md` - this documentation

---

## License
MIT (optional)

