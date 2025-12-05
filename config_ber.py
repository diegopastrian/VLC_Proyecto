import numpy as np

# ===============================================
# 1. PARÁMETROS GEOMÉTRICOS (COMUNES)
# ===============================================
L = 7.0
W = 7.0
H = 3.0

H_RX = 0.85

LED_COORDS = np.array([
    [1.75, 1.75, H],
    [1.75, 5.25, H],
    [5.25, 1.75, H],
    [5.25, 5.25, H]
])

# ===============================================
# 2. PARÁMETROS ÓPTICOS (COMUNES)
# ===============================================
P_TX         = 0.5
RESPONSIVITY = 0.5
A_RX         = 1.0e-4

PHI_HALF = np.deg2rad(60)
M_ORDER  = -np.log(2) / np.log(np.cos(PHI_HALF))

FOV_MAX = np.deg2rad(60)

# ===============================================
# 3. RUIDO Y SIMULACIÓN (COMUNES)
# ===============================================
B        = 100e6
R_LOAD   = 50
I_BG     = 10e-6

Q_ELECTRON  = 1.602e-19
K_BOLTZMANN = 1.38e-23
T_AMBIENTE  = 295.15
T_EXTREMA   = 310.15   # > 37 °C

GRID_SIZE = 50

# ===============================================
# 4. SELECTOR DE ESCENARIO BER
# ===============================================
# 1 -> Bloqueo por obstáculo (α = 0.1)  Fondo casi uniforme
# 2 -> Polvo denso (α = 0.8)           4 lóbulos claros
# 3 -> Temperatura extrema (> 37°C, α = 0.8)
# 4 -> Orientación 45° (α = 0.8)
ESCENARIO_BER = 4  # CAMBIA AQUÍ: 1, 2, 3, 4

# ===============================================
# 5. PARÁMETROS POR ESCENARIO
# ===============================================
# Valores por defecto (se sobreescriben abajo)
COEF_EXTINCION_ALPHA = 0.1
RHO_REFLECTION_1     = 0.4
RHO_AVG              = 0.4
TEMP_ACTUAL          = T_AMBIENTE
ORIENTACION_45       = False

if ESCENARIO_BER == 1:
    # Escenario 1: Bloqueo por obstáculo (α = 0.1)
    COEF_EXTINCION_ALPHA = 0.1        # poco polvo
    RHO_REFLECTION_1     = 0.8        # NLOS alto -> mapa casi plano amarillo
    RHO_AVG              = 0.7
    TEMP_ACTUAL          = T_AMBIENTE
    ORIENTACION_45       = False

elif ESCENARIO_BER == 2:
    # Escenario 2: Polvo denso (α = 0.8) con 4 lóbulos visibles
    COEF_EXTINCION_ALPHA = 0.8        # polvo fuerte
    RHO_REFLECTION_1     = 0.18       # NLOS muy bajo -> se notan los conos
    RHO_AVG              = 0.18
    TEMP_ACTUAL          = T_AMBIENTE
    ORIENTACION_45       = False

elif ESCENARIO_BER == 3:
    # Escenario 3: Temperatura extrema (> 37°C) con polvo denso
    COEF_EXTINCION_ALPHA = 0.8
    RHO_REFLECTION_1     = 0.18
    RHO_AVG              = 0.18
    TEMP_ACTUAL          = T_EXTREMA
    ORIENTACION_45       = False

elif ESCENARIO_BER == 4:
    # Escenario 4: Orientación 45° (polvo denso)
    COEF_EXTINCION_ALPHA = 0.8
    RHO_REFLECTION_1     = 0.05
    RHO_AVG              = 0.05
    TEMP_ACTUAL          = T_AMBIENTE
    ORIENTACION_45       = True

# ===============================================
# 6. OBSTÁCULO (COMÚN A TODOS)
# ===============================================
OBSTACLE_PRESENTE = True
OBSTACLE_X = 3.0
OBSTACLE_Y = 3.0
OBSTACLE_WIDTH  = 1.0
OBSTACLE_DEPTH  = 1.0
OBSTACLE_HEIGHT = 2.0

# ===============================================
# 7. ÁREA TOTAL PARA NLOS
# ===============================================
A_ROOM = 2 * (L*W + L*H + W*H)
