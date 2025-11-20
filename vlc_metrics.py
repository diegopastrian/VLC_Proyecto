import numpy as np
from scipy.special import erfc # Función de error complementaria para el cálculo de Q(x)
import config

def calculate_snr_ber(P_rx_total, T_kelvin):
    """
    Calcula la Relación Señal-Ruido (SNR) y la Tasa de Error de Bits (BER).
    
    Args:
        P_rx_total (float): Potencia óptica total recibida (W).
        T_kelvin (float): Temperatura de simulación (K).
        
    Returns:
        tuple: (snr_db, ber)
    """
    
    # 1. Cálculo de la Señal Eléctrica (Cuadrado de la corriente)
    # I_signal = Responsividad * Potencia_Optica
    # S = I_signal^2
    i_signal = config.RESPONSIVITY * P_rx_total
    signal_power_elec = i_signal ** 2
    
    # 2. Cálculo del Ruido (Varianza de la corriente)
    
    # A. Ruido de Disparo (Shot Noise) [Cite: 2, 3]
    # Se debe a la naturaleza cuántica de los fotones.
    # Depende de la señal recibida Y de la corriente de fondo (luz ambiental).
    # sigma_shot^2 = 2 * q * (I_signal + I_bg) * B
    sigma_shot_sq = 2 * config.Q_ELECTRON * (i_signal + config.I_BG) * config.B
    
    # B. Ruido Térmico (Johnson-Nyquist) [Cite: 3]
    # Generado por la temperatura en la resistencia de carga.
    # sigma_thermal^2 = (4 * k * T * B) / R_load
    sigma_thermal_sq = (4 * config.K_BOLTZMANN * T_kelvin * config.B) / config.R_LOAD
    
    # Ruido Total
    noise_total_sq = sigma_shot_sq + sigma_thermal_sq
    
    # 3. Cálculo de SNR
    # Evitamos división por cero si el ruido es extremadamente bajo (caso ideal)
    if noise_total_sq == 0:
        snr_linear = 0
    else:
        snr_linear = signal_power_elec / noise_total_sq
        
    # Convertir a decibelios (dB) para visualización
    if snr_linear > 0:
        snr_db = 10 * np.log10(snr_linear)
    else:
        snr_db = -100.0 # Piso de ruido arbitrario para log(0)
        
    # 4. Cálculo de BER (Modulación OOK)
    # Para OOK, BER = Q(sqrt(SNR))
    # Numéricamente aproximado como: 0.5 * erfc(sqrt(SNR/2))
    if snr_linear > 0:
        ber = 0.5 * erfc(np.sqrt(snr_linear / 2))
    else:
        ber = 0.5 # Si no hay señal, la probabilidad de error es 50% (azar)
        
    return snr_db, ber