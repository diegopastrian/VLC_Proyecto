import numpy as np
import config

def calculate_rf_signal(rx_coord):
    """
    Simula la potencia recibida de un AP Wi-Fi usando Log-Distance Path Loss.
    RF penetra el obstáculo (no se bloquea), pero se atenúa con la distancia.
    """
    # 1. Distancia Euclideana al Router
    d_rf = np.linalg.norm(rx_coord - config.RF_TX_POS)
    
    # 2. Pérdida de Trayecto (Path Loss) en dB
    # FSPL (Free Space Path Loss) básico a 1 metro
    # L0 = 20log10(d) + 20log10(f) + 20log10(4pi/c) - Gtx - Grx... 
    # Simplificado para 2.4GHz: L0 approx 40 dB a 1 metro
    PL_d0 = 40.0 
    
    # Path Loss total = L0 + 10 * n * log10(d)
    # Evitamos log(0) con max(d, 0.1)
    path_loss_db = PL_d0 + 10 * config.RF_PATH_LOSS_EXP * np.log10(max(d_rf, 0.1))
    
    # 3. Potencia Recibida (dBm) = Potencia Tx - Path Loss
    rssi_dbm = config.RF_TX_POWER_DBM - path_loss_db
    
    # 4. Calcular SNR (dB)
    # SNR = RSSI - Piso de Ruido
    snr_rf_db = rssi_dbm - config.RF_NOISE_FLOOR_DBM
    
    return snr_rf_db