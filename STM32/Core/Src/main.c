/* USER CODE BEGIN Header */
/**
 * AURHOR: MERT ELDEMIR
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_host.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "stdio.h"
#include "string.h"

#include "defines.h"
#include "MFRC522.h"
#include "lcd_util.h"
#include "buzzer_util.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
I2C_HandleTypeDef hi2c1;

SPI_HandleTypeDef hspi1;

UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_SPI1_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_I2C1_Init(void);
static void MX_USART2_UART_Init(void);
void MX_USB_HOST_Process(void);

/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

// MFRC522 GLOBAL VARIABLES
MFRC522_Status_t status;
uint8_t CardUID[5];

uint8_t TempCardUID[4];
char TempCardHexStr[12];
char LastCardHexStr[12];

// RFID MODE & SERIAL STATUS settings

SERIAL_Status Serial_Status = SERIAL_PENDING;

char HEARTBEAT_CODE[] = "STM32PY"; // Serial AUTH code
uint32_t LastReceivedHbTime = 0;
uint32_t hbReceiveCount = 0;

// Serial Receive buffer settings
uint8_t rxByte;
uint8_t rxBuffer[MAX_RX_BUFFER_SIZE];
uint8_t rxIndex = 0;

// RFID MODULE SETTINGS
RFID_Mode Rfid_Mode = RFID_READ;
uint8_t isRfidModeBtnPressed = 0;

uint32_t lastLcdMessageTime = 0;
uint8_t isLcdResetted = 1;

// Buzzer States
uint8_t isBuzzerBeep = 0;
uint8_t isBuzzerSaveBeep = 0;
uint8_t isBuzzerNotFoundBeep = 0;

void ResetAllLedsSTM();
void SetRfidModeLED();

// PROGRAM SERIAL STATES
void SetSerialPengingState() {
	Serial_Status = SERIAL_PENDING;
	HAL_GPIO_WritePin(STM_LED_PORT, SERIAL_PENGING_LED_PIN, GPIO_PIN_SET);
	printSerialWaitingMessage();
}

void SetSerialErrorState() {
	Serial_Status = SERIAL_ERR;
	HAL_UART_AbortReceive_IT(&huart2);
	ResetAllLedsSTM();
	HAL_GPIO_WritePin(STM_LED_PORT, SERIAL_ERR_LED_PIN, GPIO_PIN_SET);
	printSerialErrorMessage();
	SerialErrBeep();
}

void SetSerialOkayState() {
	Serial_Status = SERIAL_OK;
	ResetAllLedsSTM();
	SetRfidModeLED();
	printRfidModeMessage(Rfid_Mode);
	SerialOkBeep();
}

void WaitStartupHeartbeatSerial() {
	uint32_t startTime = HAL_GetTick();
	uint8_t remainingSec = 9;

	while ((HAL_GetTick() - startTime) < 10000) {
		if (HAL_UART_Receive(&huart2, rxBuffer, 10, 100) == HAL_OK) {
			// HB received
			printf("Hello world");
			char *msg = (char*) &rxBuffer[2];
			char *newline = strchr(msg, '\n');
			if (newline) {
				*newline = '\0';
			}

			if (strcmp(msg, HEARTBEAT_CODE) == 0) {
				LastReceivedHbTime = HAL_GetTick();
				++hbReceiveCount;
				SetSerialOkayState();
				memset(rxBuffer, 0, sizeof(rxBuffer));
				return;
			}
		}

		printSerialWaitingTimer(remainingSec);
		remainingSec = 9 - ((HAL_GetTick() - startTime) / 1000);
	}

	// No HB found
	SetSerialErrorState();
}

// RFID Mode Operations
void SetRfidModeLED() {
	if (Rfid_Mode == RFID_SAVE) {
		HAL_GPIO_WritePin(STM_LED_PORT, RFID_SAVE_LED_PIN, GPIO_PIN_SET);
	} else if (Rfid_Mode == RFID_READ) {
		HAL_GPIO_WritePin(STM_LED_PORT, RFID_READ_LED_PIN, GPIO_PIN_SET);
	}
}

void ResetAllLedsSTM() {
	HAL_GPIO_WritePin(STM_LED_PORT, RFID_READ_LED_PIN, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(STM_LED_PORT, RFID_SAVE_LED_PIN, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(STM_LED_PORT, SERIAL_PENGING_LED_PIN, GPIO_PIN_RESET);
	HAL_GPIO_WritePin(STM_LED_PORT, SERIAL_ERR_LED_PIN, GPIO_PIN_RESET);
}

void ToggleRfidMode() {
	if (Serial_Status != SERIAL_OK) {
		return;
	}

	Rfid_Mode = (Rfid_Mode + 1) % 2;
	ResetAllLedsSTM();
	SetRfidModeLED();
}

// Interrupt Callbacks

// Blue button push
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
	if (GPIO_Pin == GPIO_PIN_0 && Serial_Status == SERIAL_OK) {
		ToggleRfidMode();
		printRfidModeMessage(Rfid_Mode);
		isRfidModeBtnPressed = 1;
	}
}

// Serial messages & responses
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart) {
	if (huart->Instance == USART2) {
		if (rxByte != '\n' && rxIndex < MAX_RX_BUFFER_SIZE - 1) {
			rxBuffer[rxIndex++] = rxByte;
		} else {
			// Null-terminate the message
			rxBuffer[rxIndex] = '\0';
			rxIndex = 0;

			// Check message format: CODE|DATA\0
			if (rxBuffer[1] != '|') {
				// Invalid format
				HAL_UART_Receive_IT(&huart2, &rxByte, 1);
				return;
			}

			char code = rxBuffer[0];
			char *msg = (char*) &rxBuffer[2];

			switch (code) {
			case 'H':
				if (strcmp(msg, HEARTBEAT_CODE) == 0) {
					LastReceivedHbTime = HAL_GetTick();
					++hbReceiveCount;
					printf("msg: %s\n", msg);
				}
				break;

			case 'R':
				if (strcmp(msg, "ERR") == 0) {
					printUserNotFound();
					isBuzzerNotFoundBeep = 1;
				} else {
					printSerialReadResponse(msg);
					isBuzzerBeep = 1;
				}

				isLcdResetted = 0;
				lastLcdMessageTime = HAL_GetTick();
				break;

			case 'S':
				if (strcmp(msg, "OK") == 0) {
					printSerialSavedUID(TempCardHexStr);
					isBuzzerSaveBeep = 1;
				} else if (strcmp(msg, "DUP") == 0) {
					printDuplicateSave();
					isBuzzerNotFoundBeep = 1;
				} else {
					printSavingWentWrong();
				}

				isLcdResetted = 0;
				lastLcdMessageTime = HAL_GetTick();
				break;
			}

			memset(rxBuffer, 0, 32);
		}

		// Always re-enable interrupt for next byte
		HAL_UART_Receive_IT(&huart2, &rxByte, 1);
	}
}

/* USER CODE END 0 */

/**
 * @brief  The application entry point.
 * @retval int
 */
int main(void) {

	/* USER CODE BEGIN 1 */

	/* USER CODE END 1 */

	/* MCU Configuration--------------------------------------------------------*/

	/* Reset of all peripherals, Initializes the Flash interface and the Systick. */
	HAL_Init();

	/* USER CODE BEGIN Init */

	/* USER CODE END Init */

	/* Configure the system clock */
	SystemClock_Config();

	/* USER CODE BEGIN SysInit */

	/* USER CODE END SysInit */

	/* Initialize all configured peripherals */
	MX_GPIO_Init();
	MX_SPI1_Init();
	MX_USB_HOST_Init();
	MX_USART1_UART_Init();
	MX_I2C1_Init();
	MX_USART2_UART_Init();
	/* USER CODE BEGIN 2 */
	HAL_UART_Init(&huart2);
	MFRC522_Init(); 		// RFID Module
	lcd_init(); 			// LCD Module

// FIRST STARTUP FUNCTIONS
	printWelcomeMessage();
	HAL_Delay(2000);

// start Heartbeat receive handler before run the main program
	SetSerialPengingState();
	WaitStartupHeartbeatSerial();

	HAL_UART_Receive_IT(&huart2, rxBuffer, 1);

// int main() variables

// e.g. str = 1 D6 97 71 AF rfidModePrefix = "1" -> SAVE
// e.g. str = 0 D6 97 71 AF rfidModePrefix = "0" -> READ
	char SerialSendStr[14];
	char rfidModePrefix[2]; // "1 " -> SAVE | "0 " -> READ

	/* USER CODE END 2 */

	/* Infinite loop */
	/* USER CODE BEGIN WHILE */
	while (1) {
		// STATE CONTROLS

		// Buzzer sound states
		if (isBuzzerBeep) {
			Beep();
			isBuzzerBeep = 0;
		} else if (isBuzzerNotFoundBeep) {
			UserNotFoundBeep();
			isBuzzerNotFoundBeep = 0;
		} else if (isBuzzerSaveBeep) {
			UserSavedBeep();
			isBuzzerSaveBeep = 0;
		}

		if (Serial_Status != SERIAL_OK) {
			HAL_GPIO_TogglePin(STM_LED_PORT, SERIAL_ERR_LED_PIN);
			HAL_Delay(300);
			continue;
		}

		// chech Heartbeat
		if ((HAL_GetTick() - LastReceivedHbTime) > HEARTBEAT_TIMEOUT_MS) {
			SetSerialErrorState();
			continue;
		}

		// Reset LCD
		if (isLcdResetted
				!= 1&& (HAL_GetTick() - lastLcdMessageTime) > LCD_MESSAGE_TIME_MS) {
			printRfidModeMessage(Rfid_Mode);
			isLcdResetted = 1;
		}

		if (isRfidModeBtnPressed == 1) {
			memset(LastCardHexStr, 0, sizeof(LastCardHexStr)); // Reset last read UID
			HAL_Delay(200);
			isRfidModeBtnPressed = 0;
		}

		// MAIN RFID LOGIC

		// Check if card is presented
		if (MFRC522_Check(CardUID) == MI_OK) {
			memcpy(TempCardUID, CardUID, 4);

			snprintf(TempCardHexStr, sizeof(TempCardHexStr),
					"%02X %02X %02X %02X", TempCardUID[0], TempCardUID[1],
					TempCardUID[2], TempCardUID[3]);

			// if new card not detected
			if (strcmp(LastCardHexStr, TempCardHexStr) == 0) {
				continue;
			}

			strcpy(LastCardHexStr, TempCardHexStr);

			// prepare string to send via UART
			if (Rfid_Mode == RFID_READ) {
				rfidModePrefix[0] = '0';
			} else if (Rfid_Mode == RFID_SAVE) {
				rfidModePrefix[0] = '1';
			}
			rfidModePrefix[1] = ' ';

			snprintf(SerialSendStr, sizeof(SerialSendStr), "%s%s",
					rfidModePrefix, TempCardHexStr);

			HAL_UART_Transmit(&huart2, (uint8_t*) SerialSendStr,
					strlen(SerialSendStr), 100);

			// lcd_clear();
			// lcd_put_cur(0, 0);
			// lcd_send_string("CARD UID:");
			// lcd_put_cur(1, 0);
			// lcd_send_string(TempCardHexStr);
		}

		/* USER CODE END WHILE */
		MX_USB_HOST_Process();

		/* USER CODE BEGIN 3 */
	}
	/* USER CODE END 3 */
}

/**
 * @brief System Clock Configuration
 * @retval None
 */
void SystemClock_Config(void) {
	RCC_OscInitTypeDef RCC_OscInitStruct = { 0 };
	RCC_ClkInitTypeDef RCC_ClkInitStruct = { 0 };

	/** Configure the main internal regulator output voltage
	 */
	__HAL_RCC_PWR_CLK_ENABLE();
	__HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

	/** Initializes the RCC Oscillators according to the specified parameters
	 * in the RCC_OscInitTypeDef structure.
	 */
	RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
	RCC_OscInitStruct.HSEState = RCC_HSE_ON;
	RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
	RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
	RCC_OscInitStruct.PLL.PLLM = 4;
	RCC_OscInitStruct.PLL.PLLN = 72;
	RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
	RCC_OscInitStruct.PLL.PLLQ = 3;
	if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
		Error_Handler();
	}

	/** Initializes the CPU, AHB and APB buses clocks
	 */
	RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
			| RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
	RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
	RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
	RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
	RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

	if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK) {
		Error_Handler();
	}
}

/**
 * @brief I2C1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_I2C1_Init(void) {

	/* USER CODE BEGIN I2C1_Init 0 */

	/* USER CODE END I2C1_Init 0 */

	/* USER CODE BEGIN I2C1_Init 1 */

	/* USER CODE END I2C1_Init 1 */
	hi2c1.Instance = I2C1;
	hi2c1.Init.ClockSpeed = 100000;
	hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
	hi2c1.Init.OwnAddress1 = 0;
	hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
	hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
	hi2c1.Init.OwnAddress2 = 0;
	hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
	hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
	if (HAL_I2C_Init(&hi2c1) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN I2C1_Init 2 */

	/* USER CODE END I2C1_Init 2 */

}

/**
 * @brief SPI1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_SPI1_Init(void) {

	/* USER CODE BEGIN SPI1_Init 0 */

	/* USER CODE END SPI1_Init 0 */

	/* USER CODE BEGIN SPI1_Init 1 */

	/* USER CODE END SPI1_Init 1 */
	/* SPI1 parameter configuration*/
	hspi1.Instance = SPI1;
	hspi1.Init.Mode = SPI_MODE_MASTER;
	hspi1.Init.Direction = SPI_DIRECTION_2LINES;
	hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
	hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
	hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
	hspi1.Init.NSS = SPI_NSS_SOFT;
	hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_8;
	hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
	hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
	hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
	hspi1.Init.CRCPolynomial = 10;
	if (HAL_SPI_Init(&hspi1) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN SPI1_Init 2 */

	/* USER CODE END SPI1_Init 2 */

}

/**
 * @brief USART1 Initialization Function
 * @param None
 * @retval None
 */
static void MX_USART1_UART_Init(void) {

	/* USER CODE BEGIN USART1_Init 0 */

	/* USER CODE END USART1_Init 0 */

	/* USER CODE BEGIN USART1_Init 1 */

	/* USER CODE END USART1_Init 1 */
	huart1.Instance = USART1;
	huart1.Init.BaudRate = 115200;
	huart1.Init.WordLength = UART_WORDLENGTH_8B;
	huart1.Init.StopBits = UART_STOPBITS_1;
	huart1.Init.Parity = UART_PARITY_NONE;
	huart1.Init.Mode = UART_MODE_TX_RX;
	huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	huart1.Init.OverSampling = UART_OVERSAMPLING_16;
	if (HAL_UART_Init(&huart1) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN USART1_Init 2 */

	/* USER CODE END USART1_Init 2 */

}

/**
 * @brief USART2 Initialization Function
 * @param None
 * @retval None
 */
static void MX_USART2_UART_Init(void) {

	/* USER CODE BEGIN USART2_Init 0 */

	/* USER CODE END USART2_Init 0 */

	/* USER CODE BEGIN USART2_Init 1 */

	/* USER CODE END USART2_Init 1 */
	huart2.Instance = USART2;
	huart2.Init.BaudRate = 115200;
	huart2.Init.WordLength = UART_WORDLENGTH_8B;
	huart2.Init.StopBits = UART_STOPBITS_1;
	huart2.Init.Parity = UART_PARITY_NONE;
	huart2.Init.Mode = UART_MODE_TX_RX;
	huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	huart2.Init.OverSampling = UART_OVERSAMPLING_16;
	if (HAL_UART_Init(&huart2) != HAL_OK) {
		Error_Handler();
	}
	/* USER CODE BEGIN USART2_Init 2 */

	/* USER CODE END USART2_Init 2 */

}

/**
 * @brief GPIO Initialization Function
 * @param None
 * @retval None
 */
static void MX_GPIO_Init(void) {
	GPIO_InitTypeDef GPIO_InitStruct = { 0 };
	/* USER CODE BEGIN MX_GPIO_Init_1 */

	/* USER CODE END MX_GPIO_Init_1 */

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOE_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOH_CLK_ENABLE();
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOD_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(CS_I2C_SPI_GPIO_Port, CS_I2C_SPI_Pin, GPIO_PIN_RESET);

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(OTG_FS_PowerSwitchOn_GPIO_Port, OTG_FS_PowerSwitchOn_Pin,
			GPIO_PIN_SET);

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(BUZZER_OUTPUT_GPIO_Port, BUZZER_OUTPUT_Pin,
			GPIO_PIN_RESET);

	/*Configure GPIO pin Output Level */
	HAL_GPIO_WritePin(GPIOD,
	LD4_Pin | LD3_Pin | LD5_Pin | LD6_Pin | Audio_RST_Pin | RFID_SDA_Pin,
			GPIO_PIN_RESET);

	/*Configure GPIO pin : CS_I2C_SPI_Pin */
	GPIO_InitStruct.Pin = CS_I2C_SPI_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(CS_I2C_SPI_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : OTG_FS_PowerSwitchOn_Pin */
	GPIO_InitStruct.Pin = OTG_FS_PowerSwitchOn_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(OTG_FS_PowerSwitchOn_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : PDM_OUT_Pin */
	GPIO_InitStruct.Pin = PDM_OUT_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	GPIO_InitStruct.Alternate = GPIO_AF5_SPI2;
	HAL_GPIO_Init(PDM_OUT_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : PA0 */
	GPIO_InitStruct.Pin = GPIO_PIN_0;
	GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

	/*Configure GPIO pin : I2S3_WS_Pin */
	GPIO_InitStruct.Pin = I2S3_WS_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	GPIO_InitStruct.Alternate = GPIO_AF6_SPI3;
	HAL_GPIO_Init(I2S3_WS_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : BOOT1_Pin */
	GPIO_InitStruct.Pin = BOOT1_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(BOOT1_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : CLK_IN_Pin */
	GPIO_InitStruct.Pin = CLK_IN_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	GPIO_InitStruct.Alternate = GPIO_AF5_SPI2;
	HAL_GPIO_Init(CLK_IN_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : BUZZER_OUTPUT_Pin */
	GPIO_InitStruct.Pin = BUZZER_OUTPUT_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(BUZZER_OUTPUT_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pins : LD4_Pin LD3_Pin LD5_Pin LD6_Pin
	 Audio_RST_Pin RFID_SDA_Pin */
	GPIO_InitStruct.Pin = LD4_Pin | LD3_Pin | LD5_Pin | LD6_Pin | Audio_RST_Pin
			| RFID_SDA_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

	/*Configure GPIO pins : I2S3_MCK_Pin I2S3_SCK_Pin I2S3_SD_Pin */
	GPIO_InitStruct.Pin = I2S3_MCK_Pin | I2S3_SCK_Pin | I2S3_SD_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
	GPIO_InitStruct.Alternate = GPIO_AF6_SPI3;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

	/*Configure GPIO pin : OTG_FS_OverCurrent_Pin */
	GPIO_InitStruct.Pin = OTG_FS_OverCurrent_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(OTG_FS_OverCurrent_GPIO_Port, &GPIO_InitStruct);

	/*Configure GPIO pin : MEMS_INT2_Pin */
	GPIO_InitStruct.Pin = MEMS_INT2_Pin;
	GPIO_InitStruct.Mode = GPIO_MODE_EVT_RISING;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	HAL_GPIO_Init(MEMS_INT2_GPIO_Port, &GPIO_InitStruct);

	/* EXTI interrupt init*/
	HAL_NVIC_SetPriority(EXTI0_IRQn, 0, 0);
	HAL_NVIC_EnableIRQ(EXTI0_IRQn);

	/* USER CODE BEGIN MX_GPIO_Init_2 */

	/* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
int _write(int file, char *ptr, int len) {
	(void) file;
	int DataIdx;

	for (DataIdx = 0; DataIdx < len; DataIdx++) {
		ITM_SendChar(*ptr++);
	}
	return len;
}

/* USER CODE END 4 */

/**
 * @brief  This function is executed in case of error occurrence.
 * @retval None
 */
void Error_Handler(void) {
	/* USER CODE BEGIN Error_Handler_Debug */
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1) {
	}
	/* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
