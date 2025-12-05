import numpy as np
try:
    import config_ber as config
except ImportError:
    import config


def calculate_nlos_gain():
    numerator = config.RHO_REFLECTION_1 * config.A_RX
    denominator = config.A_ROOM * (1 - config.RHO_AVG)
    H_nlos = numerator / denominator

    num_leds = len(config.LED_COORDS)
    P_total_tx = config.P_TX * num_leds
    P_rx_nlos = P_total_tx * H_nlos
    return P_rx_nlos


def calculate_los_gain(rx_coord):
    num_leds = len(config.LED_COORDS)

    P_rx_los_clean = 0.0
    H_los_vector = np.zeros(num_leds)
    d_vector = np.zeros(num_leds)

    # LED mira hacia abajo
    n_tx = np.array([0, 0, -1])

    # Receptor: según escenario (orientación 45° o vertical)
    if hasattr(config, "ORIENTACION_45") and config.ORIENTACION_45:
        angle = np.deg2rad(45)
        n_rx = np.array([np.sin(angle), 0, np.cos(angle)])
    else:
        n_rx = np.array([0, 0, 1])

    for i in range(num_leds):
        tx_coord = config.LED_COORDS[i]
        vec_d = rx_coord - tx_coord
        distance = np.linalg.norm(vec_d)
        d_vector[i] = distance

        cos_phi = np.dot(vec_d, n_tx) / distance
        vec_inc = tx_coord - rx_coord
        cos_psi = np.dot(vec_inc, n_rx) / distance

        psi = np.arccos(np.clip(cos_psi, -1, 1))

        if cos_phi > 0 and psi <= config.FOV_MAX:
            const_term = ((config.M_ORDER + 1) * config.A_RX) / (2 * np.pi * distance**2)
            angular_term = (cos_phi ** config.M_ORDER) * cos_psi
            h_val = const_term * angular_term

            H_los_vector[i] = h_val
            P_rx_los_clean += config.P_TX * h_val
        else:
            H_los_vector[i] = 0.0

    return P_rx_los_clean, H_los_vector, d_vector
