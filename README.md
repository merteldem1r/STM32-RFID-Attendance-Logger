# STM32 RFID Attendance Logger

![preview](https://github.com/user-attachments/assets/d679b11e-f3bc-4dff-b29e-ed7bd3e67ba4)

## Project Description

This is an **RFID-based attendance logging system** built using the **STM32F407G-DISC1** microcontroller and an **RFID-RC522** module. It enables **reading**, **saving**, and **logging attendance** of RFID cards through **UART serial communication** with a **Python-based Serial Server**.

**AUTHORS**: **[Mert Eldemir](https://github.com/merteldem1r) & [Ahsen Yenisey](https://github.com/ahsenyenisey)**

## System Overview

### STM32 Side

- Reads RFID cards using the **MFRC522** module.
- Sends UID to the Serial Server via **UART** (for READ or SAVE).
- Displays the received user information (name and ID) on the **LCD**.
- Plays buzzer tones for feedback.
- Listens for a heartbeat signal every 2 seconds to maintain serial connection health.

### Serial-Server Side (Python)

- Receives UIDs from STM32 as either **READ** or **SAVE** requests.
- For **READ**: Looks up the UID in a local CSV database and responds with user information.
- For **SAVE**: Appends the UID to the database (if it's not already stored).
- Logs all READ operations in a date-based `.csv` file in the `attendance_lists/` folder.

## Project Flawchart

![710F8E9D-DAC3-4D02-ABF5-22CAD0B8E89C_1_201_a](https://github.com/user-attachments/assets/47f69778-43fb-4a11-be02-e5f067d4f07b)

## Device & App Preview

// image

## STM32 Side

- **Hardware Used**:

  - **STM32F407G-DISC1** microcontroller
  - **RFID-RC522** module
  - **LCD with I2C interface** (PCF8574T)
  - **Buzzer**
  - **USB to TTL converter** (FT232RL)

- **Libraries & Drivers Used**:

  - Default `HAL Drivers` (STM32f4xx)
  - [MFRC522 Library](https://github.com/MaJerle/stm32f429/tree/main/23-STM32F429_MFRC522) - This is **Standard Peripheral Library (SPL)** which some parts we rewrite for converting it to **HAL-compatible** code
  - `I2C-LCD` library to dislay messages on 16x2 LCD (PCF8574T)

## Serial-Server Side

- **Libraries Used**:

  - `pyserial`
  - `numpy` `pandas`
  - `pytz` `six` `python-dateutil` `tzdata`

## Communication Protocol between STM32 & Serial Server

### 1) From SERIAL-SERVER to STM32

**String Format:** `"{CODE}|{MSG}"`

**CODE:** Type of response

- `H`: Heartbeat (every 2 seconds to keep serial communication)
- `R`: Read response
- `S`: Save response

**MSG:** Response message

- For `R` (Read):

  - `ERR`: User not found in database
  - `{USER_INFO}`: User name and user id
    - e.g. `Mert Eldemir-220201019`

- For `S` (Save):

  - `OK`: UID saved
  - `DUP`: Duplicate UID
  - `ERR`: Save failed

**Examples:**

- `H|STM32PY`
- `R|Ahsen Yenisey-220201019`
- `R|ERR`
- `S|OK`
- `S|DUP`

### 2) From STM32 to SERIAL-SERVER

**String Format:** `"{CODE} {UID}"`

**CODE:** Type of request

- `0`: Read (check user and response info & log the attendance data)
- `1`: Save (add UID to database)

**UID:** 4-byte UID (space separated as HEX format)

**Examples:**

- `0 D6 97 71 AF`
- `1 D6 97 71 AF`
