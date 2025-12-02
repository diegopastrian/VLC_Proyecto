import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches # Importamos esto para la leyenda segura
import config
import vlc_channel
import vlc_hostile
import vlc_metrics
import rf_channel

# Barra de progreso opcional
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterator, **kwargs): return iterator

def main_simulation():
    print("--- Simulación VLC/RF: Generando Mapas de BER y Throughput ---")
    
    # Vectores espaciales
    x = np.linspace(0.1, config.L - 0.1, config.GRID_SIZE)
    y = np.linspace(0.1, config.W - 0.1, config.GRID_SIZE)
    
    # Matrices de resultados
    BER_map_vlc = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    SNR_map_rf = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    Throughput_map = np.zeros((config.GRID_SIZE, config.GRID_SIZE)) # <--- NUEVA MÉTRICA
    
    P_rx_nlos = vlc_channel.calculate_nlos_gain()
    
    # Bucle Principal
    for i, xi in tqdm(enumerate(x), total=config.GRID_SIZE, desc="Simulando"):
        for j, yj in enumerate(y):
            rx_coord = np.array([xi, yj, config.H_RX])
            
            # 1. CÁLCULO VLC
            P_rx_los_clean, H_los, d_vec = vlc_channel.calculate_los_gain(rx_coord)
            H_los_dusty = vlc_hostile.apply_dust_attenuation(H_los, d_vec)
            
            # Sombra NLOS (Simulación simplificada para mapa estático)
            factor_sombra = 1.0
            if config.OBSTACLE_PRESENTE:
                 if config.OBSTACLE_X <= rx_coord[0] <= (config.OBSTACLE_X + config.OBSTACLE_WIDTH) and \
                    config.OBSTACLE_Y <= rx_coord[1] <= (config.OBSTACLE_Y + config.OBSTACLE_DEPTH):
                    factor_sombra = 1e-5 # Bloqueo severo en la zona del obstáculo
            
            P_total, _ = vlc_hostile.get_final_power(H_los_dusty, P_rx_nlos * factor_sombra, rx_coord)
            _, ber_vlc = vlc_metrics.calculate_snr_ber(P_total, config.T_AMBIENTE)
            
            # 2. CÁLCULO RF
            snr_rf = rf_channel.calculate_rf_signal(rx_coord)
            
            # 3. CÁLCULO DE THROUGHPUT (Segunda Métrica)
            tput = vlc_metrics.calculate_throughput_hybrid(ber_vlc, snr_rf)
            
            # Guardar (Transpuesta visual j, i)
            BER_map_vlc[j, i] = ber_vlc
            SNR_map_rf[j, i] = snr_rf
            Throughput_map[j, i] = tput

    # Visualización: Generar gráfico de Throughput
    plot_throughput_map(x, y, Throughput_map)

def plot_throughput_map(x, y, tput_map):
    """Genera el mapa de calor de la segunda métrica: Throughput"""
    plt.figure(figsize=(10, 8))
    X, Y = np.meshgrid(x, y)
    
    # Definimos colores explícitos para asegurar la correspondencia
    mis_colores = ['black', 'blue', 'green']
    mis_niveles = [0, 10, 50, 110]
    
    # Mapa de colores discreto
    plt.contourf(X, Y, tput_map, levels=mis_niveles, colors=mis_colores)
    
    # --- CORRECCIÓN: LEYENDA MANUAL SEGURA ---
    # Creamos "parches" de color manualmente para la leyenda
    patch_corte = mpatches.Patch(color='black', label='Corte (0 Mbps)')
    patch_rf = mpatches.Patch(color='blue', label='Respaldo RF (20 Mbps)')
    patch_vlc = mpatches.Patch(color='green', label='VLC (100 Mbps)')
    
    plt.legend(handles=[patch_corte, patch_rf, patch_vlc], loc='upper right')
    # ----------------------------------------
    
    if config.OBSTACLE_PRESENTE:
        rect = plt.Rectangle((config.OBSTACLE_X, config.OBSTACLE_Y), 
                             config.OBSTACLE_WIDTH, config.OBSTACLE_DEPTH,
                             linewidth=2, edgecolor='red', facecolor='none', hatch='//')
        plt.gca().add_patch(rect)

    plt.title(f'Segunda Métrica: Mapa de Throughput Híbrido\n(Polvo: {config.COEF_EXTINCION_ALPHA} | Obstáculo: {config.OBSTACLE_PRESENTE})')
    plt.xlabel('Largo (m)')
    plt.ylabel('Ancho (m)')
    plt.axis('equal')
    
    print("Guardando imagen de Throughput...")
    plt.savefig('throughput_map.png')
    plt.show()

if __name__ == "__main__":
    main_simulation()