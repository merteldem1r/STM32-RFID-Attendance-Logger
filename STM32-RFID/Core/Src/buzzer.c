/*
 * buzzer.c
 *
 *  Created on: May 11, 2025
 *      Author: merteldem1r
 */

#include "buzzer.h"
#include "defines.h"
#include "main.h"

void Beep() {
	HAL_GPIO_WritePin(BUZZER_PORT, BUZZER_PIN, GPIO_PIN_SET);
	HAL_Delay(25);
	HAL_GPIO_WritePin(BUZZER_PORT, BUZZER_PIN, GPIO_PIN_RESET);
}

