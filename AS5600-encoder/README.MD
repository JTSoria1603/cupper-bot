# AS5600 agnetic Encoder (Raspberry Pi)

Read the angular position of an **AS5600 magnetic encoder** over I²C and display it as a **live bar + degrees** in the terminal.

### Example Output
`[--------|-----------------------------] 82.14°  raw: 934`

---

##  Wiring (Raspberry Pi 40-pin)

| Pi Pin | Function | AS5600 Pin |
| :--- | :--- | :--- |
| 1 | 3.3V | VCC |
| 3 | SDA (GPIO2) | SDA |
| 5 | SCL (GPIO3) | SCL |
| 9 | GND | GND |
| Optional | Direction | DIR |

> [!CAUTION]
> **Use 3.3V only** — do not connect to the 5V rail as it may damage the Raspberry Pi GPIO.

---

## Setup & Installation

### 1. Check I²C Connection
Ensure I²C is enabled in `sudo raspi-config` and run:

```bash
sudo i2cdetect -y 1 ```

You should see the device at address **0x36**.

### 2. Install Dependencies
Install the required Python libraries using pip:

```bash
pip install -r requirements.txt```

## 3. Usage

Once the hardware is connected and dependencies are installed, run the monitor script:

```bash
python as5600_monitor.py```
