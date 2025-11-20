import numpy as np
import config

def calculate_nlos_gain():
    """
    Calcula la potencia del componente No-Línea de Vista (NLOS) usando el
    'Modelo de Esfera' o de reflexión difusa simplificada.
    Se asume que esta potencia es un 'piso' constante en toda la sala.
    
    Returns:
        float: Potencia óptica total NLOS recibida (W).
    """
    # 1. Calcular la Ganancia del Canal NLOS (H_nlos)
    # Fórmula: H_nlos = (rho * A_rx) / (A_room * (1 - rho_avg))
    # Esta fórmula asume que la luz rebota y se distribuye uniformemente.
    numerator = config.RHO_REFLECTION_1 * config.A_RX
    denominator = config.A_ROOM * (1 - config.RHO_AVG)
    
    H_nlos = numerator / denominator
    
    # 2. Calcular la Potencia Total Transmitida (todos los LEDs suman al ambiente)
    num_leds = len(config.LED_COORDS)
    P_total_tx = config.P_TX * num_leds
    
    # 3. Potencia Recibida NLOS
    P_rx_nlos = P_total_tx * H_nlos
    
    return P_rx_nlos

def calculate_los_gain(rx_coord):
    """
    Calcula la ganancia de Línea de Vista (LOS) para un punto específico.
    Usa el modelo Lambertiano estándar.
    
    Args:
        rx_coord (np.array): Coordenadas [x, y, z] del receptor (Cobot).
        
    Returns:
        tuple: (P_rx_los_clean, H_los_vector, d_vector)
            - P_rx_los_clean: Suma de potencia LOS de todos los LEDs (W).
            - H_los_vector: Array con la ganancia H individual de cada LED.
            - d_vector: Array con la distancia de cada LED al receptor.
    """
    num_leds = len(config.LED_COORDS)
    
    # Inicializamos acumuladores y vectores
    P_rx_los_clean = 0.0
    H_los_vector = np.zeros(num_leds)
    d_vector = np.zeros(num_leds)
    
    # Definimos las normales (vectores de orientación)
    # LED mira hacia abajo (Z negativo)
    n_tx = np.array([0, 0, -1]) 
    # Receptor mira hacia arriba (Z positivo)
    n_rx = np.array([0, 0, 1])  
    
    for i in range(num_leds):
        tx_coord = config.LED_COORDS[i]
        
        # 1. Vector de distancia (Desde Tx hacia Rx)
        vec_d = rx_coord - tx_coord
        distance = np.linalg.norm(vec_d)
        d_vector[i] = distance
        
        # 2. Calcular Ángulos (Irradiancia y Incidencia)
        # Coseno de phi (ángulo de salida en Tx)
        # Producto punto entre vector distancia y normal Tx, dividido por norma
        cos_phi = np.dot(vec_d, n_tx) / distance
        
        # Para el ángulo de incidencia (psi), necesitamos el vector opuesto (Rx -> Tx)
        # o simplemente usamos la proyección sobre la normal del Rx.
        # vec_inc es el vector que llega al receptor
        vec_inc = tx_coord - rx_coord
        cos_psi = np.dot(vec_inc, n_rx) / distance
        
        # 3. Verificar condiciones de visibilidad (FOV)
        # Si cos_phi <= 0, significa que el LED está "detrás" de su punto de emisión (físicamente imposible en techo)
        # Si psi > FOV, el receptor no lo "ve".
        
        # Convertimos coseno a ángulo para comparar con FOV
        # Clip para evitar errores numéricos fuera de [-1, 1]
        psi = np.arccos(np.clip(cos_psi, -1, 1))
        
        if cos_phi > 0 and psi <= config.FOV_MAX:
            # 4. Aplicar Fórmula Lambertiana
            # H = [(m+1)A / 2pi d^2] * cos^m(phi) * cos(psi)
            
            # Parte constante
            const_term = ((config.M_ORDER + 1) * config.A_RX) / (2 * np.pi * distance**2)
            
            # Parte angular
            angular_term = (cos_phi ** config.M_ORDER) * cos_psi
            
            h_val = const_term * angular_term
            
            # Guardar valores
            H_los_vector[i] = h_val
            P_rx_los_clean += config.P_TX * h_val
        else:
            # Fuera de rango o FOV
            H_los_vector[i] = 0.0
            
    return P_rx_los_clean, H_los_vector, d_vector