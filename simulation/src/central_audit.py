# LICENSE: AGPL-3.0
# PATENT PENDING: P.454742, P.457301 (T-OTP Architecture)
# OPIS: Rekoncyliacja asynchroniczna w chmurze (CROK) po przywróceniu sieci.

import hashlib

def verify_offline_transaction(blob_tx: dict, h_last_known: str, deadline_timestamp: int):
    """
    Weryfikacja ciągłości i legalności czasu ze stacji stacjonarnej.
    """
    payload_parts = blob_tx["payload"].split("|")
    t_fiscal = int(payload_parts[2])
    h_prev = payload_parts[3]
    
    # Weryfikacja łańcucha
    if h_prev != h_last_known:
        raise ValueError("ALARM: Przerwanie łańcucha Localchain. Podejrzenie wstrzyknięcia transakcji.")
        
    # Weryfikacja czasu prawnego
    if t_fiscal > deadline_timestamp:
        raise ValueError("ALARM: Transakcja przeterminowana.")
        
    # Weryfikacja integralności hasha
    recalc_hash = hashlib.sha256(blob_tx["payload"].encode('utf-8')).hexdigest()
    if recalc_hash != blob_tx["h_curr"]:
        raise ValueError("ALARM: Uszkodzony skrót transakcji.")
        
    print(f"[AUDIT] Transakcja stacjonarna ważna. Czas operacji: {t_fiscal}")
    return True

def verify_edge_tamper_event(anchor_hash: str, edge_payload: str, h_tamper: str, otp_flag: int):
    """
    Ostateczna weryfikacja dowodu naruszenia wyekstrahowanego z układu fizycznego.
    """
    if otp_flag != 1:
        raise ValueError("ALARM: Brak sprzętowej flagi naruszenia (eFuse intact).")
        
    if not edge_payload.startswith(anchor_hash):
        raise ValueError("ALARM: Niezgodność kotwicy kryptograficznej układu brzegowego z bazą.")
        
    check_hash = hashlib.sha256(edge_payload.encode('utf-8')).hexdigest()
    
    if check_hash == h_tamper:
        print("[AUDIT ZGODNY] Naruszenie przestrzeni potwierdzone sprzętowo z niezaprzeczalnym czasem.")
        return True
    else:
        raise ValueError("ALARM: Błąd integralności kryptograficznej węzła brzegowego.")
