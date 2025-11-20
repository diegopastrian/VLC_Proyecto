# VLC_Proyecto: Simulación de Comunicaciones por Luz Visible (VLC) en un Entorno Industrial Hostil

## 💡 Resumen del Proyecto
Este repositorio contiene el código de simulación desarrollado en Python para modelar y evaluar el rendimiento de un sistema de **Comunicaciones por Luz Visible (VLC)** en un entorno industrial (Fábrica Inteligente) de **7 m × 7 m × 3 m**.

El proyecto se enfoca en cuantificar el impacto de condiciones hostiles típicas de la Industria 4.0:

- Polvo (*Scattering*)
- Obstáculos (*Shadowing*)
- Temperaturas extremas

La metodología es modular, combinando modelos físicos estándar del canal óptico y generando métricas clave de fiabilidad.

**Entregable principal:**  
➡️ *Mapas de calor 2D del BER (Tasa de Error de Bits)*, que muestran la distribución de calidad de comunicación en el plano de trabajo del robot colaborativo (Cobot).

---

## 🛠️ Estructura Modular del Repositorio

| Archivo | Función Principal | Metodología y Conceptos |
|--------|-------------------|--------------------------|
| `config.py` | Configuración Global | Define las dimensiones de la sala, coordenadas de los LEDs, parámetros ópticos (m, FOV) y coeficientes hostiles (p. ej., α del polvo). |
| `vlc_channel.py` | Canal Base | Implementa el modelo LOS (Lambertiano) y el modelo NLOS simplificado (modelo de esfera). |
| `vlc_hostile.py` | Factores Hostiles | Aplica atenuación por Polvo (Ley de Beer–Lambert) y Bloqueo Geométrico por obstáculos (*Shadowing*). |
| `vlc_metrics.py` | Métricas de Rendimiento | Calcula varianza del ruido (incluye efecto de temperatura) y deriva SNR y BER (OOK basado en `erfc`). |
| `main_simulation.py` | Orquestador y Visualización | Ejecuta la simulación 50×50, integra todos los módulos y genera el mapa de calor del Log10(BER). |

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
