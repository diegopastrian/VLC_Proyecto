import numpy as np
import matplotlib.pyplot as plt

# Importamos nuestros módulos (la estructura modular)
import config
import vlc_channel
import vlc_hostile
import vlc_metrics

# Intentamos importar tqdm para la barra de carga, si no existe, no falla.
try:
    from tqdm import tqdm
except ImportError:
    # Si no está instalado, definimos una función "dummy" que no hace nada visualmente pero permite que el código corra
    def tqdm(iterator, **kwargs):
        return iterator

def main_simulation():
    """
    Función principal que ejecuta la simulación del canal VLC.
    Recorre la fábrica punto a punto, calcula la potencia y genera el mapa de BER.
    """
    print("--- Iniciando Simulación VLC en Entorno Industrial ---")
    print(f"Dimensiones: {config.L}x{config.W}m | Resolución: {config.GRID_SIZE}x{config.GRID_SIZE}")

    # 1. Preparar la cuadrícula de simulación
    # Creamos vectores espaciales para el largo (X) y ancho (Y)
    x = np.linspace(0.1, config.L - 0.1, config.GRID_SIZE)
    y = np.linspace(0.1, config.W - 0.1, config.GRID_SIZE)
    
    # Matrices para guardar los resultados (Mapa de calor)
    # Usamos ceros inicialmente
    BER_map = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    SNR_map = np.zeros((config.GRID_SIZE, config.GRID_SIZE)) # Opcional, por si quieres graficar SNR luego
    
    # 2. Pre-cálculo de componentes constantes
    # La potencia NLOS (rebotes) se asume constante en toda la sala para este modelo
    P_rx_nlos = vlc_channel.calculate_nlos_gain()
    
    # 3. Bucle Principal: Mover el Cobot por toda la fábrica
    # tqdm envuelve el bucle para mostrar una barra de progreso en la consola
    for i, xi in tqdm(enumerate(x), total=config.GRID_SIZE, desc="Calculando"):
        for j, yj in enumerate(y):
            
            # --- A. Definir posición del receptor ---
            # El receptor está en (x, y) a la altura del cobot (H_RX)
            rx_coord = np.array([xi, yj, config.H_RX])
            
            # --- B. Módulo Canal (vlc_channel) ---
            # Calculamos la ganancia LOS "limpia" y obtenemos vectores de distancia
            P_rx_los_clean, H_los_vector, d_vector = vlc_channel.calculate_los_gain(rx_coord)
            
            # --- C. Módulo Hostil (vlc_hostile) ---
            # 1. Aplicar atenuación por polvo a cada enlace
            H_los_dusty_vector = vlc_hostile.apply_dust_attenuation(H_los_vector, d_vector)
            
            # 2. Verificar bloqueos (obstáculos) y sumar potencia total
            # Esto nos devuelve la potencia final sumando LOS (si existe) + NLOS
            P_rx_total, _ = vlc_hostile.get_final_power(H_los_dusty_vector, P_rx_nlos, rx_coord)
            
            # --- D. Módulo Métricas (vlc_metrics) ---
            # Calculamos la calidad de la señal final
            snr_db, ber = vlc_metrics.calculate_snr_ber(P_rx_total, config.T_AMBIENTE)
            
            # --- E. Guardar datos ---
            # Importante: [j, i] corresponde a (y, x) en matrices para graficar correctamente
            BER_map[j, i] = ber
            SNR_map[j, i] = snr_db

    # 4. Visualización de Resultados
    plot_results(x, y, BER_map)

def plot_results(x, y, BER_map):
    """Función auxiliar para generar los gráficos"""
    print("--- Generando Mapa de Calor ---")
    
    plt.figure(figsize=(10, 8))
    
    # Malla para el gráfico
    X, Y = np.meshgrid(x, y)
    
    # Aplicamos logaritmo base 10 al BER para visualizarlo mejor
    # (El BER varía de 10^-1 a 10^-12, el logaritmo lo hace lineal visualmente)
    # np.clip evita log(0) si el BER es perfecto (0)
    BER_log = np.log10(np.clip(BER_map, 1e-15, 1))
    
    # Dibujar contornos (Mapa de calor)
    # cmap='inferno_r' usa colores claros para buen BER (bajo) y oscuros para mal BER
    cp = plt.contourf(X, Y, BER_log, levels=20, cmap='inferno_r')
    cbar = plt.colorbar(cp)
    cbar.set_label(r'Log$_{10}$(BER) - Más negativo es mejor')
    
    # Dibujar el obstáculo si está activo para ver la correlación
    if config.OBSTACLE_PRESENTE:
        # Dibujamos un rectángulo rojo representando la obstrucción
        rect = plt.Rectangle(
            (config.OBSTACLE_X, config.OBSTACLE_Y), 
            config.OBSTACLE_WIDTH, 
            config.OBSTACLE_DEPTH,
            linewidth=2, edgecolor='red', facecolor='none', hatch='//',
            label='Zona Obstáculo'
        )
        plt.gca().add_patch(rect)
        plt.legend(loc='upper right')

    plt.title(f'Mapa de Calor BER - Escenario Hostil\n(Polvo: {config.COEF_EXTINCION_ALPHA} | Obstáculo: {config.OBSTACLE_PRESENTE})')
    plt.xlabel('Largo de la Fábrica (m)')
    plt.ylabel('Ancho de la Fábrica (m)')
    plt.axis('equal') # Para que la sala cuadrada se vea cuadrada
    
    print("Mostrando gráfico...")
    plt.show()

if __name__ == "__main__":
    main_simulation()