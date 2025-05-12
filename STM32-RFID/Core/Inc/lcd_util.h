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
