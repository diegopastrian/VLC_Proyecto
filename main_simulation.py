import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm # Utilidad para mostrar una barra de progreso en el terminal

# Importar todos nuestros módulos
import config
import vlc_channel
import vlc_hostile
import vlc_metrics

def main_simulation():
    """
    Función principal que ejecuta el bucle de simulación,
    calcula el BER en cada punto de la fábrica y genera el mapa de calor.
    """
    
    print("--- Iniciando Simulación VLC en Entorno Industrial ---")
    
    # 1. Preparar la cuadrícula de simulación (Eje X y Y)
    grid_points = config.GRID_SIZE
    # Creamos un espacio lineal para X y Y desde 0.1 hasta L/W
    x = np.linspace(0.1, config.L - 0.1, grid_points)
    y = np.linspace(0.1, config.W - 0.1, grid_points)
    
    # Inicializar las matrices para almacenar los resultados
    BER_map = np.zeros((grid_points, grid_points))
    SNR_map = np.zeros((grid_points, grid_points))
    
    # Obtener la potencia NLOS, que es constante [1]
    P_rx_nlos = vlc_channel.calculate_nlos_gain()
    
    # Definir la temperatura ambiente (usamos la base para la simulación inicial) [2]
    T_simulacion = config.T_AMBIENTE # Cambiar a config.T_EXTREMA para simular impacto de altas temperaturas
    
    # 2. Bucle principal sobre la cuadrícula (recorriendo el piso con el Cobot)
    # Usamos tqdm para tener una barra de progreso visual
    for i, xi in tqdm(enumerate(x), desc="Calculando BER", total=grid_points):
        for j, yj in enumerate(y):
            
            # 2.1. Definir la coordenada 3D del receptor (Cobot)
            # El receptor se mueve en el plano x, y a una altura H_RX
            rx_coord = np.array()
            
            # 2.2. FASE 1: Obtener Ganancia LOS y Distancia
            P_rx_los_clean, H_los_vector, d_vector = vlc_channel.calculate_los_gain(rx_coord)
            
            # 2.3. FASE 2: Aplicar Factores Hostiles (Polvo y Obstáculo)
            
            # Atenuación por polvo (Beer-Lambert)
            H_los_dusty_vector = vlc_hostile.apply_dust_attenuation(H_los_vector, d_vector)
            
            # Bloqueo geométrico y Potencia Final (combina polvo + obstáculo + NLOS)
            P_rx_total, _ = vlc_hostile.get_final_power(H_los_dusty_vector, P_rx_nlos, rx_coord)
            
            # 2.4. FASE 3: Cálculo de Métricas (SNR y BER)
            
            snr_db, ber = vlc_metrics.calculate_snr_ber(P_rx_total, T_simulacion)
            
            # 2.5. Almacenar Resultados
            # Usamos BER_map[j, i] para que Matplotlib lo grafique correctamente (Y, X)
            BER_map[j, i] = ber 
            SNR_map[j, i] = snr_db
            
    # 3. Presentación de Resultados (Mapa de Calor del BER)
    print("--- Simulación Completa. Generando Mapa de Calor del BER ---")
    
    X, Y = np.meshgrid(x, y)
    
    # Configuración de la figura para el mapa de calor
    plt.figure(figsize=(10, 8))
    
    # Graficamos el Logaritmo en base 10 del BER para visualizar mejor el rango (e.g., de 1e-3 a 1e-12)
    # Los valores más bajos (más negativos) son MEJORES.
    # Clip es para asegurar que no haya log(0)
    BER_map_log = np.log10(np.clip(BER_map, 1e-12, 1)) 
    
    cp = plt.contourf(X, Y, BER_map_log, levels=20, cmap='inferno_r') # El mapa de calor 'inferno_r' hace que lo bueno sea amarillo/blanco
    
    plt.colorbar(cp, label=r'Log$_{10}$(BER)')
    
    # Dibujar el Obstáculo (Visualiza la "Sombra")
    if config.OBSTACLE_PRESENTE:
        rect = plt.Rectangle((config.OBSTACLE_X, config.OBSTACLE_Y), 
                             config.OBSTACLE_WIDTH, config.OBSTACLE_DEPTH, 
                             edgecolor='red', facecolor='red', alpha=0.5, 
                             label='Obstáculo')
        plt.gca().add_patch(rect)
    
    # Configuración de Etiquetas y Título
    plt.title(f'Distribución de BER VLC en Fábrica (Polvo $\\alpha$={config.COEF_EXTINCION_ALPHA})')
    plt.xlabel('Eje X de la Fábrica (m)')
    plt.ylabel('Eje Y de la Fábrica (m)')
    plt.axis('equal') # Asegura que la sala 7x7 se vea cuadrada
    plt.legend()
    plt.show()
    
    # Mostrar métricas resumen en la consola
    print(f"\nResumen de Resultados:")
    print(f"Temperatura de Simulación: {T_simulacion-273.15:.2f} °C")
    print(f"Polvo (Alpha): {config.COEF_EXTINCION_ALPHA} m^-1")
    print(f"BER Mínimo (mejor zona): {BER_map.min():.2e}")
    print(f"BER Máximo (peor zona/sombra): {BER_map.max():.2e}")
    print(f"Tasa de Servicio (BER < 1e-6): {np.sum(BER_map < 1e-6) / (grid_points**2) * 100:.2f}% del área")


if __name__ == '__main__':
    # Este chequeo asegura que la librería tqdm esté instalada
    try:
        from tqdm import tqdm
    except ImportError:
        print("Instalando tqdm...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'tqdm'])
        from tqdm import tqdm
        
    main_simulation()