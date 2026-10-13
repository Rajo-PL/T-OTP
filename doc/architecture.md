```
graph TD
    subgraph Power_Domain [Subsystem Zasilania i Energii]
        CNANO["Nanokondensator C_nano<br/>(Magazyn Impulsowy)"]
        HARVEST["Obwód Wzbudzenia RF / NFC<br/>(Energy Harvesting)"]
        HARVEST -->|Ładowanie impulsowe| CNANO
    end

    subgraph Core_Domain [Koprocesor Kryptograficzny T-OTP]
        MCU["Mikrokontroler Ultra-Low Power / MCU<br/>(Secure Enclave)"]
        RTC["Hardware Time Base / RTC<br/>(Wektor Czasu)"]
        CRYPTO["Silnik Kryptograficzny<br/>(Generowanie Tokenów T-OTP)"]
        ZERO["Obwód Zerowania Klucza<br/>(Zeroization Circuit)"]
        
        CNANO -->|Zasilanie podtrzymujące| MCU
        MCU --- RTC
        MCU --- CRYPTO
        MCU --- ZERO
    end

    subgraph Physical_Tamper [Warstwa Fizyczna & Telemetria P.457301]
        CODE["Kod Przewodzący (305)<br/>(Wierzchnia warstwa weryfikacyjna)"]
        LOOP["Plomba Zrywalna / Tamper Loop<br/>(Obwód niszczalny przy otwarciu)"]
        PROBE["Elastyczna Sonda FPC (307)<br/>(Telemetria głęboka: Temp / Status)"]
        
        LOOP -->|Przerwanie ciągłości| ZERO
        PROBE -->|Wektor telemetryczny| MCU
        CODE -->|Weryfikacja optyczno-konduktywna| MCU
    end
```
```
stateDiagram-v2
    [*] --> FACTORY_PROVISIONED: Wgranie klucza prywatnego & konfiguracja RTC
    FACTORY_PROVISIONED --> ARMED_SEALED: Aplikacja plomby na opakowanie / naczepę
    
    state ARMED_SEALED {
        [*] --> MONITORING_LOOP: Pętla nienaruszona
        MONITORING_LOOP --> TELEMETRY_CAPTURE: Odczyt z sondy 307
        TELEMETRY_CAPTURE --> GENERATE_VALID_TOTP: Obliczenie tokenu T-OTP
        GENERATE_VALID_TOTP --> MONITORING_LOOP: Czas T + delta
    }

    ARMED_SEALED --> TAMPER_TRIGGERED: Przerwanie pętli / Otwarcie nakrętki (FIG. 2)
    ARMED_SEALED --> BREACH_DETECTED: Przecięcie kodu przewodzącego 305 (FIG. 3)

    state TAMPER_TRIGGERED {
        [*] --> ZEROIZATION: Natychmiastowe rozładowanie C_nano
        ZEROIZATION --> DESTROY_KEY: Wymazanie pamięci Secure Enclave
        DESTROY_KEY --> PERMANENT_FLAG: Zapis trwałej flagi naruszenia
    }

    state BREACH_DETECTED {
        [*] --> ZEROIZATION
    }

    PERMANENT_FLAG --> COMPROMISED_AUDIT: Generowanie fałszywego tokenu / Odmowa weryfikacji
    COMPROMISED_AUDIT --> [*]: Alert incydentu w łańcuchu dostaw (NIS2 Art. 21)
```

```
sequenceDiagram
    autonumber
    actor Inspector as Inspektor / Odbiorca
    participant Node as T-OTP Edge Node (FPC / Nakrętka)
    participant Reader as Terminal Kontrolny / App
    participant Ledger as Rejestr Weryfikacyjny (DORA / NIS2 Node)

    Inspector->>Node: Zbliżenie czytnika / Odczyt sygnału
    Node->>Node: Sprawdzenie stanu pętli niszczalnej & telemetrii (307)
    alt Integralność zachowana (Loop Closed)
        Node-->>Reader: Wygenerowany T-OTP Token + Wektor Czasu + Status
        Reader->>Ledger: Przekazanie tokenu do weryfikacji kryptograficznej
        Ledger-->>Reader: Potwierdzenie autentyczności: STATUS 200 OK
        Reader-->>Inspector: Zielone światło: Łańcuch chłodniczy i plomba nienaruszone
    else Plomba naruszona (Tamper Loop Open)
        Node-->>Reader: Token Niepoprawny / Flaga Sabotażu (Zeroized Key)
        Reader->>Ledger: Zgłoszenie natychmiastowego incydentu integralności
        Ledger-->>Reader: ALERT: Naruszenie łańcucha dostaw (NIS2 Compliance Breach)
        Reader-->>Inspector: Czerwone światło: Towar skompromitowany
    end

```
