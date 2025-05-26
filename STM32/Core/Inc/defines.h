// All global #defines for that project
// Created By: Mert Eldemir
// GitHub: https://github.com/merteldem1r

#ifndef DEFINES_H
#define DEFINES_H

// RC522 MODULE DEFINES

/* Default SPI used for*/
#define MFRC522_SPI 						&hspi1

/* Default CS (Chip Select & SDA Pin) pin used */
#define MFRC522_CS_PORT                 	GPIOD
#define MFRC522_CS_PIN                  	GPIO_PIN_7

// BUZZER MODULE DEFINES

#define BUZZER_PORT 						GPIOB
#define BUZZER_PIN 							GPIO_PIN_15

// STM32 BUILT-IN LED DEFINES

#define STM_LED_PORT						GPIOD

#define RFID_READ_LED_PIN					GPIO_PIN_12 // GREEN LED
#define RFID_SAVE_LED_PIN					GPIO_PIN_15 // BLUE LED

#define SERIAL_PENGING_LED_PIN				GPIO_PIN_13 // ORANGE LED
#define SERIAL_ERR_LED_PIN					GPIO_PIN_14 // RED LED

#define MAX_RX_BUFFER_SIZE					32
#define HEARTBEAT_TIMEOUT_MS				6000

#define LCD_MESSAGE_TIME_MS 				3000

// RFID Types

typedef enum {
	RFID_READ = 0, RFID_SAVE = 1
} RFID_Mode;

// SERIAL COMM Types

typedef enum {
	SERIAL_PENDING = 0, SERIAL_OK = 1, SERIAL_ERR = 2
} SERIAL_Status;

// LCD DEFINES

// MAIN LOGIC DEFINES

#endif // DEFINES_H
