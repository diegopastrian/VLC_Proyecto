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
    # Si alpha es 0 (limpio), esto será 1.0 (sin cambios)
    T_atm_vector = np.exp(-alpha * d_vector)
    
    # La atenuación se aplica multiplicando la ganancia LOS por la transmitancia
    H_los_dusty = H_los_vector * T_atm_vector
    
    return H_los_dusty

def check_geometric_blockage(tx_coord, rx_coord):
    """
    Verifica si la línea de vista (LOS) entre un transmisor y un receptor
    es bloqueada por un obstáculo estático usando geometría rayo-caja (AABB).
    
    Args:
        tx_coord (np.array): Coordenadas 3D del Transmisor (LED).
        rx_coord (np.array): Coordenadas 3D del Receptor (Cobot).
        
    Returns:
        int: 1 si está bloqueado, 0 si está despejado.
    """
    if not config.OBSTACLE_PRESENTE:
        return 0 # No hay obstáculo activado
        
    # 1. Definir la "Caja" del Obstáculo desde config
    ox1 = config.OBSTACLE_X
    oy1 = config.OBSTACLE_Y
    oz1 = 0.0 # El obstáculo comienza en el suelo
    
    ox2 = ox1 + config.OBSTACLE_WIDTH
    oy2 = oy1 + config.OBSTACLE_DEPTH
    oz2 = config.OBSTACLE_HEIGHT
    
    # 2. Definir el Rayo
    # Dirección del rayo
    direction = rx_coord - tx_coord
    
    # Parámetros t para la intersección (t=0 es Tx, t=1 es Rx)
    t_min = 0.0
    t_max = 1.0 
    
    # 3. Algoritmo "Slab Method" para intersección Rayo-Caja
    # Iteramos sobre los 3 ejes (x, y, z)
    for i in range(3):
        o_min = [ox1, oy1, oz1][i]
        o_max = [ox2, oy2, oz2][i]
        
        # Posición inicial (Tx) y componente de dirección
        start = tx_coord[i]
        comp_dir = direction[i]
        
        if abs(comp_dir) < 1e-9:
            # El rayo es paralelo al plano. Si está fuera de los límites, no hay intersección.
            if start < o_min or start > o_max:
                return 0 
        else:
            # Calcular intersecciones con los planos del eje actual
            t1 = (o_min - start) / comp_dir
            t2 = (o_max - start) / comp_dir
            
            # Queremos t_start y t_end ordenados
            if t1 > t2:
                t1, t2 = t2, t1
            
            # Acotar el intervalo de intersección global
            t_min = max(t_min, t1)
            t_max = min(t_max, t2)
            
            # Si el intervalo se cierra (min > max), el rayo no pasa por la caja
            if t_min > t_max:
                return 0

    # Si llegamos aquí, el rayo intersecta la caja infinita en t_min y t_max.
    # Verificamos si esa intersección ocurre DENTRO del segmento Tx-Rx (0 a 1)
    # Como ya inicializamos t_min=0 y t_max=1, si t_min <= t_max, hubo intersección válida.
    return 1 # ¡Bloqueo detectado!

def get_final_power(H_los_dusty_vector, P_rx_nlos, rx_coord):
    """
    Combina la atenuación por polvo (ya aplicada en H) y el bloqueo geométrico 
    para obtener la potencia final total.
    """
    
    P_rx_los_final = 0.0
    num_leds = len(H_los_dusty_vector)
    
    for i in range(num_leds):
        tx_coord = config.LED_COORDS[i]
        
        # Ganancia que ya tiene el polvo aplicado
        H_dusty = H_los_dusty_vector[i]
        
        # Si la ganancia ya es 0 (por estar fuera del FOV), no gastamos tiempo calculando bloqueo
        if H_dusty > 0:
            # 1. Comprobar bloqueo (1 si bloqueado, 0 si libre)
            is_blocked = check_geometric_blockage(tx_coord, rx_coord)
            
            if is_blocked:
                # Si hay bloqueo, la potencia de este LED es 0
                H_los_final = 0.0
            else:
                # Si no hay bloqueo, pasa la potencia con polvo
                H_los_final = H_dusty
                
            P_rx_los_final += config.P_TX * H_los_final
        
    # 3. Potencia Total = LOS (sobreviviente) + NLOS (fondo)
    P_rx_total = P_rx_los_final + P_rx_nlos
    
    return P_rx_total, P_rx_los_final