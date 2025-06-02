# STM32 RFID Attendance Logger

![1](https://github.com/user-attachments/assets/b07f7912-5de1-409c-9380-9c9f6b6055af)

## Project Description

This is an **RFID-based attendance logging system** built using the **STM32F407G-DISC1** microcontroller and an **RFID-RC522** module. It enables **reading**, **saving**, and **logging attendance** of RFID cards through **UART serial communication** with a **Python-based Serial Server**.

This is school project for **Embedded Systems** class.

**AUTHORS**:
</br>
 **[Mert Eldemir](https://github.com/merteldem1r) | Student No: 220201019**
 </br>
 **[Ahsen Yenisey](https://github.com/ahsenyenisey) | Student No: 220201014**

## System Overview

### STM32

- Reads RFID cards using the **MFRC522** module.
- Sends UID to the Serial Server via **UART** (for READ or SAVE).
- Displays the received user information (**user_name** and **user_id**) on the **LCD**.
- Plays buzzer tones for feedback.
- Listens for a heartbeat signal every 2 seconds to maintain serial connection health.

### Serial-Server (Python)

- Receives UIDs from STM32 as either **READ** or **SAVE** requests.
- For **READ**: Looks up the UID in a local CSV database and responds with user information.
- For **SAVE**: Appends the UID to the database (if it's not already stored).
- Logs all READ operations in a date-based `.csv` file in the `attendance_lists/` folder.

## Project Flawchart

![710F8E9D-DAC3-4D02-ABF5-22CAD0B8E89C_1_201_a](https://github.com/user-attachments/assets/47f69778-43fb-4a11-be02-e5f067d4f07b)

## Device & App Preview

### STM32 SERIAL STATUS

Serial Status define in which stage the serial communication between **STM32 and Serial-Server**. STM32 listens for the **Hearbeat** (special heartbeat code) signals from the **Serial-Server** to maintain connection during the operation.

![11809138-2D02-4C6D-9ABF-94417818FC74_1_201_a](https://github.com/user-attachments/assets/273fc12b-dbd5-4602-a528-72e7e875f8bc)

### STM32 RFID MODES (Toggle Blue Button)

While the Serial connection is stable we configured the the built-in **STM32 Blue Button** to switch between **RFID modes** and process the wanted operation.

![F935037A-E725-43DC-BD95-C0906572A4D3_1_201_a](https://github.com/user-attachments/assets/a4d029a3-059f-48dc-ad56-b186f9eaec93)

### STM32 - Serial Server Operations

- ### STM32

![stm32-serial-server](https://github.com/user-attachments/assets/f4ec4899-bcc6-44c0-b811-514adefafa27)

- ### Serial-Server Logs
 
![688C16BF-270A-434B-B773-F1BC6148472F_1_201_a](https://github.com/user-attachments/assets/0dba6936-cde8-4040-905a-1b09e786b66e)

### Database

![828E024E-9857-46B3-82CC-006DA0FFBAF6_1_201_a](https://github.com/user-attachments/assets/0d7e3045-f512-46d9-b30b-aed6ad9998d5)

## Used Hardware and Software

### STM32

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

### Serial-Server

- **Libraries Used**:

  - `pyserial`
  - `numpy` `pandas`
  - `pytz` `six` `python-dateutil` `tzdata`

## How the RFID-RC522 Module Works

### 1. RFID Technology Overview

RFID (Radio-Frequency Identification) is a wireless communication technology that enables contactless data exchange between an RFID reader and a tag/card. Each RFID card has a unique identifier (UID). When the card is brought near the reader, the reader generates an electromagnetic field to power the passive RFID tag and communicate with it over radio waves.

---

### 2. RFID-RC522 Module Components and Role

The **RFID-RC522** module is based on the MFRC522 chip and operates at 13.56 MHz. It communicates with the STM32 microcontroller via **SPI** interface. Key components include:

- **Antenna Coil**: Emits the electromagnetic field that powers the RFID card.
- **MFRC522 Chip**: Handles RFID communication protocols, reading/writing card data, and detecting cards.
- **SPI Interface**: Enables communication with the STM32 microcontroller.

---

### 3. Communication Flow

1. The STM32 continuously checks for nearby RFID cards.
2. When a card is detected, the MFRC522 reads its UID.
3. The UID is sent over UART to the Serial Server (Python).
4. Based on the server's response, the STM32 triggers actions such as displaying user info or logging attendance.

This module is essential for enabling secure, contactless identification in the attendance system.

## Communication between STM32 & Serial Server

**IMPORTANT NOTE**: Unlike the Nucleo boards, the **STM32F407G-DISC1** microcontroller not has a virtual COM port to ST-LINK for UART communication. That's why our messages transmits via external **USB to TTL** converter (FT232RL) from connected **TX** and **RX pins**.

**Baud Rate**: 115200 bits/s

We have created our own **communication protocol** between **STM32** and **Serial-Server** for: heartbeat signals, save & read requests and responses, error handling.

We shown below the **Communication Protocol** between two separated parts of our project:

### 1) From SERIAL-SERVER to STM32

**String Format:** `"{CODE}|{MSG}"`

**CODE:** Type of response

- `H`: Heartbeat (every 2 seconds to keep communication)
- `R`: Read response
- `S`: Save response

**MSG:** Response message

- For `R` (Read):

  - `ERR`: User not found in database
  - `{USER_INFO}`: user_name and user_id from database
    - e.g. `Mert Eldemir-220201019`

- For `S` (Save):

  - `OK`: UID saved successfuly
  - `DUP`: Duplicate UID
  - `ERR`: Saving failed

**Examples:**

- `H|STM32PY` (**HEARBEAT_CODE** used as code for **Handshake Mechanism**)
- `R|Ahsen Yenisey-220201019` (**user_name**-**user_id**)
- `R|ERR`
- `S|OK`
- `S|DUP`

### 2) From STM32 to SERIAL-SERVER

**String Format:** `"{CODE} {UID}"`

**CODE:** Type of request rather read or save

- `0`: **Read** (check user and response the info & log the attendance data)
- `1`: **Save** (add UID to the database)

**UID:** 4-byte UID (space separated in HEX format)

**Examples:**

- `0 D6 97 71 AF`
- `1 D6 97 71 AF`
