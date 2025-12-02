import numpy as np
import matplotlib.pyplot as plt
import config
import vlc_channel
import vlc_hostile
import vlc_metrics
import rf_channel

def simulate_trajectory():
    print("--- Simulación V3: Trayectoria con Histéresis y Throughput ---")

    # 1. Configuración de Trayectoria
    num_steps = 200 # Más resolución para ver el efecto suave
    path_x = np.linspace(0.5, 6.5, num_steps)
    path_y = np.full(num_steps, 3.5)
    
    # 2. Configuración de Red e Histéresis
    # UMBRALES:
    THRESH_TO_RF  = 1e-4  # Si BER empeora que esto -> Cambiar a RF
    THRESH_TO_VLC = 1e-6  # Solo volver a VLC si el BER mejora MUCHO (Histéresis)
    
    # VELOCIDADES (Modelado simple de Capa de Aplicación):
    SPEED_VLC_MAX = 100.0 # Mbps
    SPEED_RF_MAX  = 20.0  # Mbps (Wi-Fi industrial saturado)
    
    # Estado inicial (1 = VLC, 0 = RF)
    current_system = 1 
    
    # Listas de almacenamiento
    ber_list = []
    throughput_list = []
    system_state_list = []
    
    P_rx_nlos = vlc_channel.calculate_nlos_gain()

    # 3. Bucle de Simulación
    for k in range(num_steps):
        rx_coord = np.array([path_x[k], path_y[k], config.H_RX])
        
        # --- CÁLCULO FÍSICO (Igual que antes) ---
        P_rx_los_clean, H_los, d_vec = vlc_channel.calculate_los_gain(rx_coord)
        H_los_dusty = vlc_hostile.apply_dust_attenuation(H_los, d_vec)
        
        # Sombra Profunda (Simulación de bloqueo NLOS)
        factor_sombra = 1.0
        if config.OBSTACLE_PRESENTE:
             if config.OBSTACLE_X <= rx_coord[0] <= (config.OBSTACLE_X + config.OBSTACLE_WIDTH):
                factor_sombra = 1e-5 # Bloqueo severo
        
        P_total, _ = vlc_hostile.get_final_power(H_los_dusty, P_rx_nlos * factor_sombra, rx_coord)
        _, ber = vlc_metrics.calculate_snr_ber(P_total, config.T_AMBIENTE)
        
        # --- LÓGICA DE CONTROL (HISTÉRESIS) ---
        if current_system == 1: # Estamos en VLC
            if ber > THRESH_TO_RF:
                current_system = 0 # Handover a RF (Calidad bajó mucho)
        else: # Estamos en RF
            if ber < THRESH_TO_VLC: # Solo volvemos si la calidad es EXCELENTE
                current_system = 1 # Handover a VLC
        
        # --- CÁLCULO DE THROUGHPUT (Mbps) ---
        if current_system == 1:
            # En VLC, si el BER es alto, la velocidad cae, pero simplificamos a ON/OFF para visualizar
            throughput = SPEED_VLC_MAX
        else:
            # En RF, la velocidad es constante pero menor
            throughput = SPEED_RF_MAX
            
        ber_list.append(ber)
        throughput_list.append(throughput)
        system_state_list.append(current_system)

    # 4. Visualización Avanzada
    plot_advanced_handover(path_x, ber_list, throughput_list, system_state_list, THRESH_TO_RF, THRESH_TO_VLC)

def plot_advanced_handover(dist, ber, tput, state, th_bad, th_good):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 9), sharex=True)
    
    # --- PANEL 1: FÍSICA (BER e Histéresis) ---
    ber_log = np.log10(np.clip(ber, 1e-16, 1))
    ax1.plot(dist, ber_log, 'k-', linewidth=1.5, label='VLC BER (Físico)')
    
    # Zonas de Histéresis
    ax1.axhline(np.log10(th_bad), color='red', linestyle='--', label=f'Umbral Cambio a RF ({th_bad})')
    ax1.axhline(np.log10(th_good), color='green', linestyle='--', label=f'Umbral Retorno a VLC ({th_good})')
    
    # Sombrear zona de obstáculo
    if config.OBSTACLE_PRESENTE:
        ax1.axvspan(config.OBSTACLE_X, config.OBSTACLE_X + config.OBSTACLE_WIDTH, 
                   color='gray', alpha=0.2, label='Obstáculo Físico')

    ax1.set_ylabel('Log10(BER)')
    ax1.set_title('Disparador de Handover con Histéresis')
    ax1.legend(loc='lower right', fontsize='small')
    ax1.grid(True, alpha=0.3)
    
    # --- PANEL 2: NEGOCIO (Throughput y Redundancia) ---
    # Dibujamos el Throughput como una línea gruesa
    ax2.plot(dist, tput, color='purple', linewidth=3, label='Velocidad de Usuario (Mbps)')
    
    # Rellenamos el área bajo la curva para mostrar "Energía/Datos"
    ax2.fill_between(dist, 0, tput, color='purple', alpha=0.1)
    
    # Etiquetas de estado
    ax2.text(1.5, 50, "VLC (100 Mbps)", color='green', fontweight='bold', ha='center')
    ax2.text(3.5, 30, "RF RESPALDO\n(20 Mbps)", color='blue', fontweight='bold', ha='center')
    ax2.text(5.5, 50, "VLC (100 Mbps)", color='green', fontweight='bold', ha='center')
    
    ax2.set_ylabel('Throughput (Mbps)')
    ax2.set_xlabel('Distancia Recorrida (m)')
    ax2.set_title('Impacto en la Experiencia de Usuario (Redundancia)')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    print("Generando gráfico V3...")
    plt.show()

if __name__ == "__main__":
    simulate_trajectory()