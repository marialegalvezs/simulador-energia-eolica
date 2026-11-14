# Simulador eólico — Proyecto 7 (G3)

Simulador de la turbina del caso de estudio: muestra **la situación física** (el aire que se frena en
un tubo que se ensancha y el rotor que gira) **junto con su evolución numérica** (gráficas de ω(t) con la
solución exacta, Euler y RK4, y de la potencia). Cada parámetro que se cambia se ve en el dibujo y en las
gráficas al mismo tiempo.

## Cómo ejecutarlo

1. Instale Python 3.10 o una versión posterior.
2. Abra una terminal en esta carpeta y ejecute:

```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

3. Se abre en el navegador, en http://localhost:8501.

## Cómo usarlo

1. A la izquierda cambie el viento (y si quiere un escalón o una ráfaga), la densidad, el radio, el momento
   de inercia, la carga del generador, ω₀ o el paso h.
2. Presione **▶ Reproducir**: el rotor arranca en tiempo real y un punto recorre al mismo tiempo las gráficas
   de ω(t) (exacta, Euler y RK4) y de la potencia entregada.
3. Abajo: la sección 4 compara Euler y RK4 con la solución exacta (con la tabla de errores al reducir h) y la
   sección 5 muestra el momentum, con la turbina ideal (factor a) o la Vestas V52 real.

Cómo hacer los escenarios E1 a E5 del proyecto: ver `GUIA_ESCENARIOS.md`.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `modelo.py` | Física: potencia del viento, disco actuador (momentum), Cp(λ), torques, solución exacta |
| `metodos.py` | Euler y RK4 programados a mano (sin SciPy), errores y orden de convergencia |
| `graficos.py` | Dibujo animado (tubo de corriente y rotor) y gráficas sincronizadas, en HTML/JavaScript |
| `datos.py` | Curvas de potencia y de C_T de la Vestas V52 (fabricante, vía PyWake), para E4 |
| `app.py` | Interfaz de una sola página: parámetros, dibujo, gráficas, errores y momentum |
| `GUIA_ESCENARIOS.md` | Cómo configurar cada escenario y qué resultados debe dar |
| `.streamlit/config.toml` | Colores de la interfaz |
