import numpy as np
import matplotlib.pyplot as plt

import config_ber as config
import vlc_channel
import vlc_hostile
import vlc_metrics

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, **kwargs):
        return iterator


def generar_mapa_ber_estatico():
    print("\n--- Simulación VLC: Mapa BER Estático ---")
    print(f"ESCENARIO_BER      = {config.ESCENARIO_BER}")
    print(f"  COEF_EXTINCION_ALPHA = {config.COEF_EXTINCION_ALPHA}")
    print(f"  RHO_REFLECTION_1     = {config.RHO_REFLECTION_1}")
    print(f"  RHO_AVG              = {config.RHO_AVG}")
    print(f"  TEMP_ACTUAL          = {config.TEMP_ACTUAL} K")
    print(f"  ORIENTACION_45       = {config.ORIENTACION_45}")
    print(f"  OBSTACLE_PRESENTE    = {config.OBSTACLE_PRESENTE}")
    print(f"Dimensiones sala  LxW  = {config.L} x {config.W} m  | Grid = {config.GRID_SIZE}x{config.GRID_SIZE}\n")

    x = np.linspace(0.1, config.L - 0.1, config.GRID_SIZE)
    y = np.linspace(0.1, config.W - 0.1, config.GRID_SIZE)

    BER_map = np.zeros((config.GRID_SIZE, config.GRID_SIZE))

    P_rx_nlos = vlc_channel.calculate_nlos_gain()
    print(f"P_rx_nlos (potencia NLOS constante) = {P_rx_nlos:.3e} W\n")

    for i, xi in tqdm(enumerate(x), total=config.GRID_SIZE, desc="Calculando"):
        for j, yj in enumerate(y):
            rx_coord = np.array([xi, yj, config.H_RX])

            _, H_los, d_vec = vlc_channel.calculate_los_gain(rx_coord)
            H_los_dusty = vlc_hostile.apply_dust_attenuation(H_los, d_vec)
            P_total, _ = vlc_hostile.get_final_power(H_los_dusty, P_rx_nlos, rx_coord)

            _, ber = vlc_metrics.calculate_snr_ber(P_total, config.TEMP_ACTUAL)
            BER_map[j, i] = ber

    # Forzar BER muy malo dentro del obstáculo para que salga negro
    if config.OBSTACLE_PRESENTE:
        x_idx = (x >= config.OBSTACLE_X) & (x <= config.OBSTACLE_X + config.OBSTACLE_WIDTH)
        y_idx = (y >= config.OBSTACLE_Y) & (y <= config.OBSTACLE_Y + config.OBSTACLE_DEPTH)
        BER_map[np.ix_(y_idx, x_idx)] = 1e-1

    print(f"BER mínimo  (fuera obstáculo) ~ {BER_map.min():.3e}")
    print(f"BER máximo  (incluye obstáculo) ~ {BER_map.max():.3e}\n")

    plot_results(x, y, BER_map)


def plot_results(x, y, BER_map):
    X, Y = np.meshgrid(x, y)
    BER_log = np.log10(np.clip(BER_map, 1e-15, 1))

    plt.figure(figsize=(10, 8))

    if config.ESCENARIO_BER == 1:
        # Incluimos el -1 para que el obstáculo quede en el extremo oscuro
        levels = np.linspace(-15, -1, 20)
    elif config.ESCENARIO_BER == 2:
        BER_log = np.clip(BER_log, -11.5, -3.0)
        levels = np.linspace(-11.5, -3.0, 20)
    else:
        levels = np.linspace(-12, -3, 20)

    cp = plt.contourf(X, Y, BER_log, levels=levels, cmap='inferno_r')
    cbar = plt.colorbar(cp)
    cbar.set_label(r'Log$_{10}$(BER) - Más negativo es mejor')
    
    if config.OBSTACLE_PRESENTE:
        rect = plt.Rectangle(
            (config.OBSTACLE_X, config.OBSTACLE_Y),
            config.OBSTACLE_WIDTH,
            config.OBSTACLE_DEPTH,
            linewidth=2, edgecolor='red', facecolor='none', hatch='//',
            label='Zona Obstáculo'
        )
        plt.gca().add_patch(rect)
        plt.legend(loc='upper right')

    plt.title(
        f"Mapa de Calor BER - Escenario Hostil\n"
        f"(Polvo: {config.COEF_EXTINCION_ALPHA} | Obstáculo: {config.OBSTACLE_PRESENTE})"
    )
    plt.xlabel('Largo de la Fábrica (m)')
    plt.ylabel('Ancho de la Fábrica (m)')
    plt.axis('equal')

    plt.tight_layout()
    plt.savefig('BER_mapa_estatico.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    generar_mapa_ber_estatico()
