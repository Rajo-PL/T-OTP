/*
 * LICENSE: AGPL-3.0
 * PATENT PENDING: P.454742, P.457301
 * MODULE: Edge Node NMI (Non-Maskable Interrupt) Handler
 * DESC: Procedura ratunkowa T-OTP wyzwalana przerwaniem ciągłości obwodu mostkującego.
 * OGRANICZENIA: Czas wykonania < 50ms, zasilanie wyłącznie z C_nano.
 */

#include <stdint.h>
#include "localchain.h"
#include "hardware_regs.h"
#include "sha256.h"

// Zmienne w pamięci nieulotnej (zapisane wcześniej przez terminal)
extern uint8_t EEPROM_AnchorHash[32]; 

void __attribute__((interrupt)) NMI_Tamper_Handler(void) {
    // KROK 1: Izolacja zasilania awaryjnego
    // Natychmiastowe odcięcie prądożernych peryferiów (NFC/RF) w celu oszczędzania ładunku nanokondensatora
    PWR_CTRL_REG |= (PWR_ISO_NFC | PWR_ISO_ADC); 
    
    // KROK 2: Odczyt brzegowego znacznika czasu i telemetrii
    uint32_t t_tamper = SECURE_RTC_GetTime();
    uint16_t temp_val = SENSOR_ReadTempFast(); 
    
    // KROK 3: Kalkulacja sprzętowego bloku uwiarygadniającego
    uint8_t payload[64];
    uint8_t h_tamper[32];
    
    // Konkatenacja: Anchor_Hash (32 bajty) + Czas (4 bajty) + Telemetria (2 bajty)
    memcpy(payload, EEPROM_AnchorHash, 32);
    memcpy(payload + 32, &t_tamper, 4);
    memcpy(payload + 36, &temp_val, 2);
    
    // Obliczenie SHA-256 w akceleratorze sprzętowym
    HW_SHA256_Calculate(payload, 38, h_tamper);
    
    // KROK 4: Cyfrowe zapieczętowanie w pamięci trwałej (Flash)
    // Zapis musi zakończyć się przed spadkiem napięcia na VDD poniżej 1.8V
    FLASH_WriteBlock_Fast(TAMPER_LOG_ADDR, payload, 38);
    FLASH_WriteBlock_Fast(TAMPER_HASH_ADDR, h_tamper, 32);
    
    // KROK 5: Zeroizacja i trwała dezaktywacja (Hard Lock)
    OTP_STATUS_REG = 0x01;              // Ustawienie flagi naruszenia
    EFUSE_BURN(SYMMETRIC_KEY_ADDR);     // Trwałe zniszczenie pierwotnego klucza (eFuse)
    
    // Zatwierdzenie śmierci układu (System Halt)
    CLK_CTRL_REG = CLK_HALT_ALL;
    while(1) {
        // Oczekiwanie na ostateczny zanik napięcia z nanokondensatora
    }
}
