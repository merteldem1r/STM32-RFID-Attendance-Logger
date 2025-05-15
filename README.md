# STM32-RFID-Attendance-Logger

## Overview

This is a **RFID-based attendance logging system** project using the **STM32F407G-DISC1** microcontroller and an **RFID-RC522** module. It enables both **reading**, **saving** and **attendance-logging** RFID card data through **UART serial communication** with a **Python-based Serial Server**. The STM32 handles all hardware interactions, including:

This project consists of **two main parts**:

- **STM32 Firmware**: Handles RFID card scanning, LCD display, buzzer control, and UART communication.

- **Serial Server (Python)**: Receives scanned card **UIDs** via **UART**, save user UID into **CSV database**, sends back user info to STM32 for display and create day by day CSV file for read cards in **attendance_lists** folder.

## Project Structure

- **STM32 Side:**

  - Sends UID to Serial Server as requests and interprets responses.
  - Reads **RFID** card using **MFRC522** and sends UID to the **Serial-Server** via **UART** (as **READ request**).
  - Displays user name and ID on **LCD** which in database, from **Serial-Server** (as **READ response**).
  - Plays buzzer on actions.
  - Receiving Hearbeat code every 2 seconds to keep Serial Communication.

- **Serial-Server Side (Python):**

  - Receives UID from STM32 as **READ** or **SAVE** mode
  - Responds with user info or error based on local `.csv` **database**
  - Saves new UID if in SAVE mode
  - **Logs attendance** entries under a date-named file in `Attendance List/`

---

## App Preview
// images

## Hardware Used

- **STM32F407G-DISC1** microcontroller
- **RFID-RC522** module
- **LCD** with I2C (PCF8574T)
- **Buzzer**
- **USB to TTL (FT232RL)** converter

## Communication Protocol (between STM32 and Serial Server)

### 1) From SERIAL-SERVER to STM32

String Format: `{CODE}|{MSG}`

**CODE:** Type of response

- `H`: Heartbeat (every 2 seconds)
- `R`: Read response
- `S`: Save response

**MSG:** Response message

- For `R` (Read):

  - `ERR`: User not found
  - `{USER_INFO}`: e.g. `Mert Eldemir-220201019`

- For `S` (Save):

  - `OK`: UID saved
  - `DUP`: Duplicate UID
  - `ERR`: Save failed

**Examples:**

- `H|STM32PY`
- `R|Ahsen Yenisey-220201019`
- `S|DUP`

### 2) From STM32 to SERIAL-SERVER

String Format: `{CODE} {UID}`

**CODE:** Type of request

- `0`: Read (check user info)
- `1`: Save (store UID)

**UID:** 4-byte UID (space separated)

**Examples:**

- `0 D6 97 71 AF`
- `1 D6 97 71 AF`

---

## Python Serial Server

### Libraries Used

- `numpy`
- `pandas`
- `pyserial`
- `python-dateutil`
- `pytz`
- `six`
- `tzdata`
