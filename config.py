import numpy as np

# ===============================================
# 1. PARÁMETROS GEOMÉTRICOS DEL ESCENARIO [1]
# ===============================================

# Dimensiones de la Fábrica (m)
L = 7.0  # Largo
W = 7.0  # Ancho
H = 3.0  # Alto

# Altura del Receptor (Plano del Cobot)
H_RX = 0.85 # Receptor a 0.85m del suelo [1]

# Coordenadas de los 4 LEDs (Transmisores) en el techo (MIMO 4x1)
# ¡CORRECCIÓN CRÍTICA: Añadimos corchetes exteriores para que sea una matriz!
LED_COORDS = np.array([1.75, 1.75, H],
    [1.75, 5.25, H],
    [5.25, 1.75, H],
    [5.25, 5.25, H])

# ===============================================
# 2. PARÁMETROS ÓPTICOS Y DE TRANSMISOR
# ===============================================

P_TX = 0.5                      # Potencia Óptica Transmitida por cada LED (W)
RESPONSIVITY = 0.5              # Responsividad del Fotodiodo (R) (A/W)
A_RX = 1.0e-4                   # Área Física del Fotodiodo (m^2) [1]

# Parámetros Lambertianos (Modelo del Haz)
PHI_HALF = np.deg2rad(60)       # Ángulo de semi-potencia del LED (60 grados)
M_ORDER = -np.log(2) / np.log(np.cos(PHI_HALF)) # Orden Lambertiano (m) [1]

# Parámetros del Receptor
FOV_MAX = np.deg2rad(60)        # Campo de Visión máximo (FOV) del receptor (radianes) [1]

# Parámetros para NLOS Simplificado (Modelo de esfera) [1]
RHO_REFLECTION_1 = 0.8          # Reflectividad de primer rebote
RHO_AVG = 0.7                   # Reflectividad ponderada promedio
A_ROOM = 2 * (L*W + L*H + W*H)  # Área total de la superficie de la sala

# ===============================================
# 3. PARÁMETROS DE RUIDO Y SIMULACIÓN [2]
# ===============================================

B = 100e6                       # Ancho de banda del sistema (Hz)
R_LOAD = 50                     # Resistencia de carga (Ohmios)
I_BG = 10e-6                    # Corriente de fondo por luz ambiental (A)

# Constantes Físicas
Q_ELECTRON = 1.602e-19          # Carga del electrón (C)
K_BOLTZMANN = 1.38e-23          # Constante de Boltzmann (J/K)
T_AMBIENTE = 295.15             # Temperatura ambiente BASE (22°C en Kelvin)

# Parámetro de Simulación de Temperatura Extrema [2]
T_EXTREMA = 310.15              # Ejemplo de temperatura elevada (37°C en Kelvin)

# 5. Parámetros de la Cuadrícula de Simulación
GRID_SIZE = 50                  # <--- ¡ESTA ES LA VARIABLE FALTANTE! (50x50 = 2500 puntos)

# ===============================================
# 4. VARIABLES DEL ENTORNO HOSTIL [2]
# ===============================================

# 4.1. Atenuación por Polvo (Beer-Lambert)
COEF_EXTINCION_ALPHA = 0.1      # Coeficiente de extinción (m^-1) - 0.0 para simulación limpia

# 4.2. Bloqueo por Obstáculo (Shadowing)
OBSTACLE_PRESENTE = True        # Activar el módulo de bloqueo
OBSTACLE_X = 3.0                # Coordenada X del inicio del obstáculo
OBSTACLE_Y = 3.0                # Coordenada Y del inicio del obstáculo
OBSTACLE_WIDTH = 1.0            # Ancho del obstáculo (m)
OBSTACLE_DEPTH = 1.0            # Profundidad del obstáculo (m)
OBSTACLE_HEIGHT = 2.0           # Altura del obstáculo (m)