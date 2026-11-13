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

1. A la izquierda cambie el viento, el radio de las aspas, el momento de inercia o el paso h.
2. Presione **▶ Reproducir**: el rotor arranca desde el reposo, el aire se frena cada vez más y los
   puntos negros recorren las gráficas al mismo tiempo. Con la barra `t` puede ir a cualquier instante.
3. Abajo compare Euler y RK4 con la solución exacta (errores absoluto y relativo, y tabla por paso h).

El botón **Volver al caso de estudio del documento** restablece los valores del documento
(ρ = 1.225 kg/m³, R = 2 m, v = 10 m/s, Cp,máx = 0.45, λ* = 7, J = 15 kg·m², b = 0.05 N·m·s,
k_g ≈ 2.777 N·m·s, ω₀ = 0, h = 1 s, 30 s). Con ellos el simulador da ω∞ = 35.0 rad/s (334 rpm),
τ = 2.65 s, 3.40 kW en el generador y, en t = 4 s, ω exacta = 27.2524 rad/s y los errores de la tabla de errores del documento.

## Parámetros

| Grupo | Parámetro | Qué se ve al cambiarlo |
|---|---|---|
| Viento | v (m/s) | Los puntos de aire van más rápido, las flechas v₁, v_d, v₄ crecen, sube la potencia (∝ v³) |
| Viento | Ráfaga (opcional) | El viento cambia de golpe; el rotor se acelera hasta un nuevo equilibrio |
| Turbina | R (m) | El rotor y el tubo de aire se dibujan más grandes; más área A = πR² |
| Turbina | J (kg·m²) | El rotor tarda más en arrancar (τ = J/K crece) |
| Turbina | k_g (N·m·s) | Por defecto se ajusta solo para trabajar en λ* = 7; si se desmarca, más carga = gira más lento |
| Numérico | h (s) | Cambian los puntos de Euler y RK4; con h > 2τ Euler se vuelve inestable |
| Numérico | Duración (s) | Largo de las gráficas |

ρ, Cp,máx, λ*, b y ω₀ están en "Otros valores" porque en el documento son fijos.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `modelo.py` | Física: potencia del viento, disco actuador (momentum), Cp(λ), torques, solución exacta |
| `metodos.py` | Euler y RK4 programados a mano (sin SciPy), errores y orden de convergencia |
| `graficos.py` | Dibujo animado (tubo de corriente y rotor) y gráficas sincronizadas, en HTML/JavaScript |
| `app.py` | Interfaz: parámetros, dibujo, gráficas y tabla de errores |
| `.streamlit/config.toml` | Colores de la interfaz |
