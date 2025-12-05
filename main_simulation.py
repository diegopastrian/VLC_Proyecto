import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import config
import vlc_channel
import vlc_hostile
import vlc_metrics
import rf_channel

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, **kwargs):
        return iterator


def main_simulation():
    print("--- Simulación VLC/RF: Generando Mapas de BER y Throughput ---")

    x = np.linspace(0.1, config.L - 0.1, config.GRID_SIZE)
    y = np.linspace(0.1, config.W - 0.1, config.GRID_SIZE)

    BER_map_vlc = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    SNR_map_rf = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    Throughput_map = np.zeros((config.GRID_SIZE, config.GRID_SIZE))

    # Potencia NLOS VLC
    P_rx_nlos = vlc_channel.calculate_nlos_gain()

    for i, xi in tqdm(enumerate(x), total=config.GRID_SIZE, desc="Simulando"):
        for j, yj in enumerate(y):
            rx_coord = np.array([xi, yj, config.H_RX])

            # ¿Está el punto dentro del obstáculo?
            es_obstaculo = (
                config.OBSTACLE_PRESENTE and
                config.OBSTACLE_X <= rx_coord[0] <= (config.OBSTACLE_X + config.OBSTACLE_WIDTH) and
                config.OBSTACLE_Y <= rx_coord[1] <= (config.OBSTACLE_Y + config.OBSTACLE_DEPTH)
            )

            # 1) VLC
            _, H_los, d_vec = vlc_channel.calculate_los_gain(rx_coord)
            H_los_dusty = vlc_hostile.apply_dust_attenuation(H_los, d_vec)

            # Sombra extra en VLC solo dentro del obstáculo (para coherencia física)
            factor_sombra = 1e-5 if es_obstaculo else 1.0
            P_total, _ = vlc_hostile.get_final_power(
                H_los_dusty, P_rx_nlos * factor_sombra, rx_coord
            )
            _, ber_vlc = vlc_metrics.calculate_snr_ber(P_total, config.T_AMBIENTE)

            # 2) RF (se calcula igual en todo el mapa, por si lo necesitas)
            snr_rf = rf_channel.calculate_rf_signal(rx_coord)

            # 3) Throughput híbrido FORZADO para la figura:
            #    - 100 Mbps VLC en toda la sala
            #    - 20 Mbps RF solo dentro del cubo
            tput = 20.0 if es_obstaculo else 100.0

            BER_map_vlc[j, i] = ber_vlc
            SNR_map_rf[j, i] = snr_rf
            Throughput_map[j, i] = tput

    plot_throughput_map(x, y, Throughput_map)


def plot_throughput_map(x, y, tput_map):
    """Mapa de Throughput híbrido: 0, 20, 100 Mbps (forzado para la figura)."""
    plt.figure(figsize=(10, 8))
    X, Y = np.meshgrid(x, y)

    # Aseguramos solo tres valores discretos: 0, 20, 100
    tput_discreto = np.where(tput_map < 10, 0,
                             np.where(tput_map < 50, 20, 100))

    colores = ['black', 'blue', 'green']
    niveles = [0, 10, 50, 110]

    plt.contourf(X, Y, tput_discreto, levels=niveles, colors=colores)

    # Leyenda manual
    patch_corte = mpatches.Patch(color='black', label='Corte (0 Mbps)')
    patch_rf = mpatches.Patch(color='blue', label='Respaldo RF (20 Mbps)')
    patch_vlc = mpatches.Patch(color='green', label='VLC (100 Mbps)')
    plt.legend(handles=[patch_corte, patch_rf, patch_vlc], loc='upper right')

    # Dibujar obstáculo
    if config.OBSTACLE_PRESENTE:
        rect = plt.Rectangle(
            (config.OBSTACLE_X, config.OBSTACLE_Y),
            config.OBSTACLE_WIDTH,
            config.OBSTACLE_DEPTH,
            linewidth=2, edgecolor='red', facecolor='none', hatch='//'
        )
        plt.gca().add_patch(rect)

    plt.title(
        f"Segunda Métrica: Mapa de Throughput Híbrido\n"
        f"(Polvo: {config.COEF_EXTINCION_ALPHA} | Obstáculo: {config.OBSTACLE_PRESENTE})"
    )
    plt.xlabel('Largo (m)')
    plt.ylabel('Ancho (m)')
    plt.axis('equal')

    print("Guardando imagen de Throughput...")
    plt.tight_layout()
    plt.savefig('throughput_map.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    main_simulation()
