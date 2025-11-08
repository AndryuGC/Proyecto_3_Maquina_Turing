# 🧠 Simulador Visual de Máquina de Turing + Evaluador de Expresiones Regulares

Andry González Cantoral - 2000924  
Este simulador permite **visualizar el funcionamiento de una Máquina de Turing determinista** y **evaluar expresiones regulares** como casos de prueba para validar su comportamiento.

---

## 🎯 Objetivo

Mostrar de forma gráfica cómo una Máquina de Turing:
- Lee símbolos en una cinta.
- Cambia de estado.
- Se mueve a la izquierda o derecha.
- Determina si una cadena es **ACEPTADA** o **RECHAZADA**.

A la vez, incluye un **panel de expresiones regulares** para comprobar si una cadena cumple con diferentes patrones formales.

---

## 🖥️ Interfaz

La aplicación está desarrollada en **Python (Tkinter)** con una interfaz intuitiva:

1. **Cadena de entrada** y **Demo** de autómata seleccionable.  
2. **Estado actual** y **resultado final** mostrados en pantalla.  
3. **Cinta central** animada que representa la memoria de la máquina.  
4. **Controles**:  
   - `Reset` → reinicia la simulación.  
   - `Paso` → ejecuta una transición.  
   - `Run / Pausa` → inicia o detiene la animación.  
   - `Velocidad` → ajusta la rapidez del movimiento.  
5. **Panel inferior** con 10 expresiones regulares predefinidas para probar cadenas.

---

## ⚙️ Instalación

### Requisitos
- **Python 3.10 o superior**
- **Tkinter** (ya incluido en Windows y macOS)
