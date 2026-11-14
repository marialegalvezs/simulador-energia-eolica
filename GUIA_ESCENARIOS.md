# Cómo configurar cada escenario (E1 a E5) en el simulador

Todo se hace en la misma página. Antes de cada escenario presione **↺ Volver al caso de estudio del
documento** (abajo a la izquierda) y luego cambie solo lo que dice la tabla. En la parte de arriba presione
**▶ Reproducir**: la simulación corre en **tiempo real** (30 s de simulación duran 30 s) y con la barra `t`
puede ir a cualquier instante.

Valores del caso de estudio (los que deja el botón ↺): v = 10 m/s, sin cambio de viento, ρ = 1.225 kg/m³,
R = 2 m, J = 15 kg·m², k_g = 2.777 N·m·s, ω₀ = 0, h = 0.5 s, 30 s (y fijos Cp,máx = 0.45, λ* = 7, b = 0.05 N·m·s).

| Escenario | Qué cambiar | Dónde mirar | Resultado esperado |
|---|---|---|---|
| **E1 · Base** | Nada (botón ↺). En la sección 5, opción *Ideal*, mueva el factor a de 0 a 0.5 | Tarjetas de arriba, dibujo y gráficas; sección 5 | ω∞ = 35.0 rad/s (334 rpm), τ = 2.65 s, **potencia entregada 3.40 kW** (75 % de Betz). Con a = 1/3: ṁ = 102.6 kg/s, F = 684 N, P = 4.56 kW, Cp = 0.593 |
| **E2 · Vientos constantes** | *Velocidad del viento* = 6, 8, 10 y 12 m/s (uno a la vez) | Tarjetas de arriba y gráficas | 6 m/s → 15.75 rad/s, τ = 3.32 s, 0.69 kW · 8 m/s → 24.89 rad/s, 2.95 s, 1.72 kW · 10 m/s → 35.00 rad/s, 2.65 s, 3.40 kW · 12 m/s → 45.82 rad/s, 2.41 s, 5.83 kW |
| **E3 · Viento variable** | *Velocidad del viento* = 6; *¿Cambia el viento?* = **Escalón**; *Viento después* = 10; *Instante* = 10 s; h = 0.5 s. Luego pruebe **Ráfaga**: v = 10, aumento 4 m/s, instante 15 s y ω₀ = 35 rad/s | Gráficas de ω(t) y potencia; mensaje "acelera / equilibrio" | Antes del cambio se acerca a 15.75 rad/s; después sube a 35.0 rad/s en unos 13 s (5τ) y entrega 3.40 kW. Con la ráfaga, ω llega a un pico de 51.9 rad/s en t ≈ 16.6 s (hasta 7.49 kW) y en t = 30 s sigue en 35.2 rad/s |
| **E4 · Ideal vs real** | Sección 5, opción **Real: Vestas V52**; velocidad de 4 a 16 m/s. Para Bogotá: *Densidad* = 0.91 a la izquierda | Tarjetas de la sección 5 | 8 m/s, 1.225: 304 kW frente a 395 kW de Betz (Cp = 0.456, 77 %), a = 0.288, v₄ = 3.39 m/s, F = 68.3 kN frente a 74.0 kN. Con 0.91: 228 kW. La turbina del caso de estudio con 0.91 y v = 10 m/s: 29.8 rad/s, τ = 3.04 s, 2.47 kW |
| **E5 · Precisión numérica** | *Paso h* = 1, 0.5, 0.25, 0.125, 0.0625 s; luego 5 y 6 s. *Instante en que se comparan* = 4 s | Sección 4: tabla del instante y "Tabla de errores al reducir el paso h" | En t = 4 s, ω exacta = 27.2536 rad/s; con h = 1 s, Eₐ Euler = 2.47 (9.08 %) y Eₐ RK4 = 2.7×10⁻³; órdenes ≈ 1 y ≈ 4. Con h = 5 s Euler oscila (0, 65.97, 7.60, 59.25…); con h = 6 s aparece el aviso y diverge (0, 79.17, −20.72, 105.32…) |

**Notas**

- E5 también se puede hacer sobre E3: deje el escalón de E3 y en la sección 4 elija un instante después del
  cambio (por ejemplo 14 s). Los métodos se reinician en el instante del escalón.
- El paso h solo cambia los puntos de Euler y RK4; la línea negra (solución exacta) no depende de h.
- Con ráfaga no hay solución exacta: la línea negra es RK4 con h = 0.001 s.
- La "potencia entregada" del rotor es la del generador, k_g ω². En la V52 es la potencia real del fabricante.
- Si cambia la densidad a 0.91 para E4, vuelva a 1.225 (o use ↺) antes de los otros escenarios.
