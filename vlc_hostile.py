import numpy as np
import config

def apply_dust_attenuation(H_los_vector, d_vector):
    """
    Aplica el factor de atenuación de la Ley de Beer-Lambert por la presencia de polvo. 
    
    Args:
        H_los_vector (np.array): Ganancias del canal LOS de cada LED (sin atenuar).
        d_vector (np.array): Distancias (m) de cada LED al receptor.
        
    Returns:
        np.array: Ganancias LOS atenuadas por el polvo.
    """
    alpha = config.COEF_EXTINCION_ALPHA
    
    # Factor de Transmitancia Atmosférica (T_atm = exp(-alpha * d))
    T_atm_vector = np.exp(-alpha * d_vector)
    
    # La atenuación se aplica multiplicando la ganancia LOS por la transmitancia
    H_los_dusty = H_los_vector * T_atm_vector
    
    return H_los_dusty

def check_geometric_blockage(tx_coord, rx_coord):
    """
    Verifica si la línea de vista (LOS) entre un transmisor y un receptor
    es bloqueada por un obstáculo estático usando geometría rayo-caja. 
    
    Args:
        tx_coord (np.array): Coordenadas 3D del Transmisor (LED).
        rx_coord (np.array): Coordenadas 3D del Receptor (Cobot).
        
    Returns:
        int: 1 si está bloqueado (Shadowing), 0 si está despejado.
    """
    if not config.OBSTACLE_PRESENTE:
        return 0 # No hay obstáculo, no hay bloqueo
        
    # 1. Definir la "Caja" del Obstáculo
    # Se basa en los parámetros definidos en config.py
    ox1 = config.OBSTACLE_X
    oy1 = config.OBSTACLE_Y
    oz1 = 0.0 # El obstáculo comienza en el suelo
    
    ox2 = ox1 + config.OBSTACLE_WIDTH
    oy2 = oy1 + config.OBSTACLE_DEPTH
    oz2 = config.OBSTACLE_HEIGHT
    
    # 2. Vector Rayo (Dirección)
    direction = rx_coord - tx_coord
    
    # 3. Prueba de Intersección (Versión simplificada para un proyecto abordable)
    # Se comprueba la intersección en 3D del segmento de línea (Tx a Rx) con la caja (Obstáculo)
    # Primero, comprueba si el rayo atraviesa el plano horizontal (X, Y) del obstáculo
    
    # Parámetros de la recta (rayo): P(t) = T + t * D, donde T=Tx y D=Direction
    # t_min y t_max representan dónde comienza y termina la línea dentro del obstáculo
    
    t_min = 0.0
    t_max = 1.0 # Solo nos interesa el segmento entre Tx y Rx
    
    # Chequeo para cada eje (X, Y, Z)
    for i in range(3):
        
        # Coordenadas del obstáculo
        o_min = [ox1, oy1, oz1][i]
        o_max = [ox2, oy2, oz2][i]
        
        # Componente de la posición y dirección del rayo
        T_i = tx_coord[i]
        D_i = direction[i]
        
        # Evitar división por cero si la dirección es paralela al plano
        if abs(D_i) < 1e-9:
            if T_i < o_min or T_i > o_max:
                return 0 # Paralelo y fuera: no hay bloqueo
            continue
            
        # Puntos de intersección del plano T+tD=O_min y T+tD=O_max
        t1 = (o_min - T_i) / D_i
        t2 = (o_max - T_i) / D_i
        
        # Asegurarse de que t1 sea el menor (intersección inicial)
        t_start = min(t1, t2)
        t_end = max(t1, t2)
        
        # Actualizar t_min y t_max para el rayo
        t_min = max(t_min, t_start)
        t_max = min(t_max, t_end)
        
        # Si t_min > t_max, la caja no es intersectada en este eje
        if t_min > t_max:
            return 0 # No hay bloqueo

    # Si t_min es menor que t_max, el rayo intersecta la caja
    # También debemos asegurarnos de que la intersección ocurra entre Tx y Rx (0 < t < 1)
    if t_min < t_max and t_max > 0 and t_min < 1:
        return 1 # Bloqueo
        
    return 0 # No hay bloqueo o la intersección está fuera del segmento Tx-Rx
    
def get_final_power(H_los_dusty_vector, P_rx_nlos, rx_coord):
    """
    Combina la atenuación por polvo y el bloqueo geométrico para obtener la potencia final.
    """
    
    P_rx_los_final = 0.0
    num_leds = len(H_los_dusty_vector)
    
    for i in range(num_leds):
        tx_coord = config.LED_COORDS[i]
        H_dusty = H_los_dusty_vector[i]
        
        # 1. Comprobar bloqueo (gamma = 1 si está bloqueado, 0 si no lo está)
        gamma = check_geometric_blockage(tx_coord, rx_coord)
        
        # 2. Si hay bloqueo, la ganancia LOS es cero (H_final = 0)
        # Si no hay bloqueo, la ganancia LOS es la atenuada por polvo (H_final = H_dusty)
        H_los_final = H_dusty * (1 - gamma)
        
        P_rx_los_final += config.P_TX * H_los_final
        
    # 3. Potencia Total Recibida = P_LOS_Final + P_NLOS [3]
    P_rx_total = P_rx_los_final + P_rx_nlos
    
    return P_rx_total, P_rx_los_final