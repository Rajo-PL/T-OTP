# LICENSE: AGPL-3.0
# PATENT PENDING: P.454742, P.457301 (T-OTP Architecture)
# OPIS: Symulacja stacji dystrybucyjnej offline i inicjalizacji węzła brzegowego.

import hashlib
import time

class FiscalOracle:
    """Symulacja zaplombowanego sprzętowego modułu RTC kasy fiskalnej."""
    @staticmethod
    def get_secure_rtc():
        # Zwraca deterministyczny znacznik czasu
        return int(time.time())

def initialize_edge_node(obj_id: str, operator_id: str, h_prev: str, private_key: str):
    """
    KROK 1-4: Generowanie pętli lokalnej w trybie offline.
    """
    print(f"[SYSTEM] Brak sieci. Tryb awaryjny T-OTP dla obiektu: {obj_id}")
    
    t_fiscal = FiscalOracle.get_secure_rtc()
    
    # Tworzenie nierozerwalnego bloku
    payload = f"{obj_id}|{operator_id}|{t_fiscal}|{h_prev}"
    h_curr = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    
    # Symulacja podpisu asymetrycznego
    sig_pos = hashlib.sha256(f"{h_curr}{private_key}".encode('utf-8')).hexdigest()
    
    blob_tx = {
        "payload": payload,
        "h_curr": h_curr,
        "sig_pos": sig_pos
    }
    
    # Ramka inicjalizacyjna dla węzła brzegowego (NFC transfer)
    init_frame = {
        "obj_id": obj_id,
        "t_zero": t_fiscal,
        "anchor_hash": h_curr
    }
    
    print(f"[NFC TX] Zapisano kotwicę {h_curr[:8]}... w pamięci węzła brzegowego.")
    print("[HARD LOCK] Zwolnienie blokady drukarki fiskalnej. Transakcja offline zabezpieczona.")
    
    return blob_tx, init_frame
