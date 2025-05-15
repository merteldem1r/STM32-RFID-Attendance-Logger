/*
 * lcd_util.c
 *
 *  Created on: May 12, 2025
 *      Author: merteldem1r
 */

#include "defines.h"
#include "lcd_util.h"
#include "stdio.h"
#include "string.h"

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
	char timerBuffer[4];
	sprintf(timerBuffer, "%d", remainSec);
	lcd_put_cur(1, 15);
	lcd_send_string(timerBuffer);
}

void printSerialErrorMessage() {
	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string("Serial FAILED");
	lcd_put_cur(1, 0);
	lcd_send_string("Press reset btn!");
}

void printRfidModeMessage(RFID_Mode rfid_mode) {
	char msgBuffer[16];
	char *rfidModeStr;

	if (rfid_mode == RFID_READ) {
		rfidModeStr = "READ";
	} else {
		rfidModeStr = "SAVE";
	}

	sprintf(msgBuffer, "RFID Mode: %s", rfidModeStr);

	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string(msgBuffer);
	lcd_put_cur(1, 0);
	lcd_send_string("Put your card");
}

void printSerialReadResponse(char *msg) {
	char *pos = strchr(msg, '-');

	lcd_clear();
	if (pos) {
		*pos = '\0';

		lcd_put_cur(0, 0);
		lcd_send_string(msg);
		lcd_put_cur(1, 0);
		lcd_send_string(++pos);
	} else {
		lcd_put_cur(0, 0);
		lcd_send_string("Wrong message");
		lcd_put_cur(1, 0);
		lcd_send_string("Format");
	}

}

void printUserNotFound() {
	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string("Provided UID");
	lcd_put_cur(1, 0);
	lcd_send_string("Not found!");
}

void printSerialSavedUID(char *uid) {
	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string("UID Saved:");
	lcd_put_cur(1, 0);
	lcd_send_string(uid);
}

void printSavingWentWrong() {
	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string("Something went");
	lcd_put_cur(1, 0);
	lcd_send_string("wrong on Save!");
}

void printDuplicateSave() {
	lcd_clear();
	lcd_put_cur(0, 0);
	lcd_send_string("Provided UID");
	lcd_put_cur(1, 0);
	lcd_send_string("Already saved!");
}
