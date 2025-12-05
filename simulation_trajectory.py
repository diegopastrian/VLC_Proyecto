import numpy as np
import matplotlib.pyplot as plt
import config


def simulate_trajectory():
    print("--- Simulación V3: Trayectoria con Histéresis y Throughput (perfil idealizado) ---")

    # 1. Trayectoria: línea horizontal que cruza el obstáculo
    num_steps = 200
    path_x = np.linspace(0.5, 6.5, num_steps)
    path_y = np.full(num_steps, 3.5)

    # 2. Umbrales de histéresis
    THRESH_TO_RF  = 1e-4   # cambio a RF  (línea roja)
    THRESH_TO_VLC = 1e-6   # retorno a VLC (línea verde)

    # Velocidades (Mbps)
    SPEED_VLC_MAX = 100.0
    SPEED_RF_MAX  = 20.0

    # Estado inicial: 1 = VLC, 0 = RF
    current_system = 1

    ber_list = []
    throughput_list = []
    system_state_list = []

    # 3. Bucle de simulación (BER idealizado)
    for k in range(num_steps):
        rx_coord = np.array([path_x[k], path_y[k], config.H_RX])

        # ¿Está dentro del obstáculo (x e y)?
        en_obstaculo = (
            config.OBSTACLE_PRESENTE and
            config.OBSTACLE_X <= rx_coord[0] <= config.OBSTACLE_X + config.OBSTACLE_WIDTH and
            config.OBSTACLE_Y <= rx_coord[1] <= config.OBSTACLE_Y + config.OBSTACLE_DEPTH
        )

        # PERFIL IDEALIZADO DE BER:
        # - Muy bueno y constante fuera del obstáculo
        # - Muy malo y constante dentro del obstáculo
        if en_obstaculo:
            ber = 1e-1      # log10 = -1 (tramo alto plano)
        else:
            ber = 1e-7      # log10 ≈ -7 (tramo bajo plano)

        # --- Histéresis ---
        if current_system == 1:  # VLC activo
            if ber > THRESH_TO_RF:
                current_system = 0  # handover a RF
        else:  # RF activo
            if ber < THRESH_TO_VLC:
                current_system = 1  # vuelta a VLC

        # --- Throughput resultante ---
        throughput = SPEED_VLC_MAX if current_system == 1 else SPEED_RF_MAX

        ber_list.append(ber)
        throughput_list.append(throughput)
        system_state_list.append(current_system)

    # 4. Gráfica final
    plot_advanced_handover(
        path_x, ber_list, throughput_list,
        system_state_list, THRESH_TO_RF, THRESH_TO_VLC
    )


def plot_advanced_handover(dist, ber, tput, state, th_bad, th_good):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True)

    # --- Panel 1: BER + umbrales ---
    ber_log = np.log10(np.clip(ber, 1e-16, 1))
    ax1.plot(dist, ber_log, 'k-', linewidth=1.5, label='VLC BER (Físico)')

    ax1.axhline(np.log10(th_bad), color='red', linestyle='--',
                label=f'Umbral Cambio a RF ({th_bad})')
    ax1.axhline(np.log10(th_good), color='green', linestyle='--',
                label=f'Umbral Retorno a VLC ({th_good})')

    # Zona de obstáculo
    if config.OBSTACLE_PRESENTE:
        ax1.axvspan(config.OBSTACLE_X,
                    config.OBSTACLE_X + config.OBSTACLE_WIDTH,
                    color='gray', alpha=0.2, label='Obstáculo Físico')

    ax1.set_ylabel('Log10(BER)')
    ax1.set_title('Disparador de Handover con Histéresis')
    ax1.legend(loc='lower right', fontsize='small')
    ax1.grid(True, alpha=0.3)

    # --- Panel 2: Throughput 100–20–100 ---
    ax2.plot(dist, tput, color='purple', linewidth=3,
             label='Velocidad de Usuario (Mbps)')
    ax2.fill_between(dist, 0, tput, color='purple', alpha=0.1)

    ax2.text(1.5, 50, "VLC (100 Mbps)", color='green',
             fontweight='bold', ha='center')
    ax2.text(3.5, 30, "RF RESPALDO\n(20 Mbps)", color='blue',
             fontweight='bold', ha='center')
    ax2.text(5.5, 50, "VLC (100 Mbps)", color='green',
             fontweight='bold', ha='center')

    ax2.set_ylabel('Throughput (Mbps)')
    ax2.set_xlabel('Distancia Recorrida (m)')
    ax2.set_title('Impacto en la Experiencia de Usuario (Redundancia)')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    print("Generando gráfico V3...")
    plt.show()


if __name__ == "__main__":
    simulate_trajectory()
