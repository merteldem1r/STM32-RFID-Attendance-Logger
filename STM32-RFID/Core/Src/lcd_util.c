/*
 * lcd_util.c
 *
 *  Created on: May 12, 2025
 *      Author: merteldem1r
 */

#include "lcd_util.h"
#include "stdio.h"

void printWelcomeMessage() {
	char firstLine[] = "STM32-RF AT LOG";
	char secondLine[] = "by MERT & AHSEN";

	uint8_t col = 0;

	for (uint8_t i = 0; i < sizeof(firstLine) - 1; ++i, ++col) {
		lcd_put_cur(0, col);
		lcd_send_data(firstLine[i]);
		HAL_Delay(75);
	}

	col = 0;

	for (uint8_t i = 0; i < sizeof(secondLine) - 1; ++i, ++col) {
		lcd_put_cur(1, col);
		lcd_send_data(secondLine[i]);
		HAL_Delay(75);
	}
}

void printSerialWaitingMessage() {
	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string("Waiting for");
	lcd_put_cur(1, 0);
	lcd_send_string("Serial connect ");
}

void printSerialWaitingTimer(uint8_t remainSec) {
	char timerBuffer[3];
	sprintf(timerBuffer, "%d", remainSec);
	lcd_put_cur(1, 15);
	lcd_send_string(timerBuffer);
}

void printSerialErrorMessage() {
	lcd_put_cur(0, 0);
	lcd_send_string("Serial failed");
	lcd_put_cur(1, 0);
	lcd_send_string("Press reset btn!");
}
