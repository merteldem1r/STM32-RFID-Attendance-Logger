# STM32 RFID Attendance Logger

<img width="1920" height="1080" alt="stm32-thumbnail" src="https://github.com/user-attachments/assets/4f9dc8ce-15d2-4708-9930-c0000b67822e" />

## Project Description

This is an **RFID-based attendance logging system** built using the **STM32F407G-DISC1** microcontroller and an **RFID-RC522** module. It enables **reading**, **saving**, and **logging attendance** of RFID cards through **UART serial communication** with a **Python-based Serial Server**.

Self project for  **COME412 - Embedded Systems** class.

**AUTHORS**: [Mert Eldemir](https://github.com/merteldem1r) & [Ahsen Yenisey](https://github.com/ahsenyenisey) 

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

![DB403673-F6D5-4C11-8866-822FF09EDC76_1_201_a](https://github.com/user-attachments/assets/34f92bf9-b25d-43de-b375-1f7a963f02b3)

## Device & App Preview

### STM32 SERIAL STATUS

Serial Status define in which stage the serial communication between **STM32 and Serial-Server**. STM32 listens for the **Hearbeat** (special heartbeat code) signals from the **Serial-Server** to maintain connection during the operation.

![11809138-2D02-4C6D-9ABF-94417818FC74_1_201_a](https://github.com/user-attachments/assets/273fc12b-dbd5-4602-a528-72e7e875f8bc)

### STM32 RFID MODES (Toggle Blue Button)

While the Serial connection is stable we configured the the built-in **STM32 Blue Button** to switch between **RFID modes** and process the wanted operation.

![F935037A-E725-43DC-BD95-C0906572A4D3_1_201_a](https://github.com/user-attachments/assets/a4d029a3-059f-48dc-ad56-b186f9eaec93)

### STM32 - Serial Server Operations

Here is the example of **saving new user to the database**, **getting same user from database** and **logging attendance** information. Also some error and duplicate responce examples shown below.

- ### STM32
  
![4](https://github.com/user-attachments/assets/a03a760b-a557-4ce3-b810-0b3b78337c26)

- ### Serial-Server Logs
 
![688C16BF-270A-434B-B773-F1BC6148472F_1_201_a](https://github.com/user-attachments/assets/0dba6936-cde8-4040-905a-1b09e786b66e)

### Database

Local **CSV** based database where we store main user information in **uid.csv** and the **attendance_lists** folder where we have date by date attendance logs.

![828E024E-9857-46B3-82CC-006DA0FFBAF6_1_201_a](https://github.com/user-attachments/assets/0d7e3045-f512-46d9-b30b-aed6ad9998d5)

### Statistics

The **stats.ipynb** notebook includes basic data visualizations. Those bar, line, and column charts that display various user **statistics** and attendance metrics based on dates, counts, and distributions.

![7](https://github.com/user-attachments/assets/ae27169c-e7b1-463d-9eaf-a2706acf54fb)

## Used Hardware and Software

### STM32

- **Hardware Used**:

  - **STM32F407G-DISC1** microcontroller
  - **RFID-RC522** module (13,56 MHz)
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
  - `numpy` `pandas` `matplotlib`
  - `pytz` `six` `python-dateutil` `tzdata`

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
