/*
 * lcd_util.h
 *
 *  Created on: May 12, 2025
 *      Author: merteldem1r
 */

#include "i2c-lcd.h"
#include "defines.h"
#include "main.h"

void printWelcomeMessage();
void printSerialWaitingMessage();
void printSerialWaitingTimer(uint8_t passedSec);
void printSerialErrorMessage();
void printRfidModeMessage(RFID_Mode rfid_mode);
void printSerialReadResponse(char* msg);
void printSerialSaveResponse(char* msg);
void printUserNotFound();
void printSavingWentWrong();
void printDuplicateSave();
