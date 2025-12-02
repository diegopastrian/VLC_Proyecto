# 🏭 Simulación de Sistema Híbrido VLC/RF para Entornos Industriales (Industria 4.0)

> **Proyecto de Ingeniería de Telecomunicaciones**
> Validación de robustez, cobertura y algoritmos de handover en sistemas Li-Fi bajo condiciones hostiles.

## 📋 Descripción del Proyecto

Este repositorio contiene el código fuente para la simulación y análisis de un sistema de comunicaciones inalámbricas híbrido **VLC (Visible Light Communication) + RF (Wi-Fi)**.

El objetivo es demostrar la viabilidad técnica de utilizar la infraestructura de iluminación LED para la transmisión de datos en entornos industriales severos, superando limitaciones físicas mediante una arquitectura de respaldo RF.

### 🚀 Características Principales (Versión 3.0)
* **Modelado de Canal Óptico:** Distribución Lambertiana (LOS) y reflexiones difusas (NLOS) basadas en el modelo de esfera integradora.
* **Simulación de Entorno Hostil:**
    * Atenuación por polvo en suspensión (Ley de Beer-Lambert).
    * Bloqueo físico por obstáculos (Shadowing geométrico AABB).
    * Ruido térmico dependiente de la temperatura industrial.
* **Validación Dinámica de Trayectoria:** Simulación de un Cobot (Robot Colaborativo) moviéndose a través de la fábrica en tiempo real.
* **Algoritmo de Handover Inteligente:** Control con **histéresis** para evitar el efecto "Ping-Pong" (conmutación inestable) en los bordes de cobertura.
* **Métricas de QoS:** Cálculo de BER (Bit Error Rate) y visualización de **Throughput (Caudal útil)** para validar la continuidad del servicio.
## 🛠️ Estructura del Proyecto

El código sigue una arquitectura modular para facilitar la escalabilidad y el mantenimiento:

| Archivo | Descripción |
| :--- | :--- |
| `config.py` | **Configuración Global:** Define geometría ($7 \times 7 \times 3$m), parámetros físicos de los LEDs, umbrales de BER, coeficientes de polvo ($\alpha$) y parámetros del obstáculo. |
| `main_simulation.py` | **Análisis Estático:** Genera mapas de calor 2D para BER y Throughput en toda la planta, visualizando zonas de corte y respaldo. |
| `simulation_trajectory.py` | **Análisis Dinámico (V3):** Simula el movimiento del robot, la lógica de control con histéresis y la conmutación de red (Handover). Genera gráficas de línea de tiempo. |
| `vlc_channel.py` | **Física Óptica:** Implementa las ecuaciones de ganancia de canal LOS y el cálculo de potencia difusa (NLOS). |
| `vlc_hostile.py` | **Modelos de Degradación:** Aplica las penalizaciones por polvo atmosférico y detecta colisiones rayo-obstáculo. |
| `vlc_metrics.py` | **Cálculo de Señal:** Estima SNR, BER (OOK) y selecciona la velocidad de enlace (Throughput) basada en la calidad del canal. |
| `rf_channel.py` | **Canal de Respaldo:** Simula la propagación Wi-Fi (Log-Normal Path Loss) para garantizar cobertura en zonas de sombra óptica. |

---

## 🚀 Guía de Instalación y Ejecución

### 1. Instalación de Dependencias
Asegúrate de tener el entorno virtual activo:

```bash
.\venv\Scripts\Activate
```

Instala las librerías necesarias:

```bash
pip install numpy scipy matplotlib tqdm
```

### 2. Ejecución de la Simulación

```bash
python main_simulation.py
```

La simulación generará:

- Barra de progreso  
- Resumen en consola  
- Mapa de calor del **Log10(BER)**  

---

## 🔬 Pruebas de Escenarios Hostiles (Análisis Requerido)

Modifica las variables en `config.py` y `main_simulation.py` para simular:

| Escenario | Modificación | Hallazgo Principal |
|----------|--------------|--------------------|
| **Bloqueo** | `OBSTACLE_PRESENTE = True` | El BER colapsa detrás del obstáculo; el bloqueo LOS es la mayor limitación. |
| **Polvo Denso** | `COEF_EXTINCION_ALPHA = 0.5` | El BER aumenta uniformemente en toda la sala. |
| **Temperatura Extrema** | Usar `T_EXTREMA` | El SNR disminuye por aumento del ruido térmico. |

---

## 📊 Análisis y Recomendaciones Finales

### ✔️ Conclusión sobre el rendimiento
La simulación confirma que la mayor debilidad de VLC en entornos industriales es la **vulnerabilidad a los obstáculos**.  
Mientras que RF (Wi-Fi) falla por **interferencia electromagnética (EMI)**, VLC falla en **zonas de sombra**.

### ✔️ Recomendación de Ingeniería
Implementar un **Sistema Híbrido VLC/RF**:

- **VLC** como canal principal (downlink) por su inmnunidad a EMI.  
- **RF** como canal de respaldo (uplink + failover).  

Los mapas de calor del BER sirven como base para un **algoritmo de handover**:  
Cuando el Cobot entra en una zona con **BER > 10⁻⁴**, debe cambiar inmediatamente a RF para mantener la fiabilidad.

---
