# Simulador eólico — Proyecto 7 (G3)

## Cómo ejecutarlo

1. Instale Python 3.10 o una versión posterior.
2. Abra una terminal en esta carpeta y ejecute:

```
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

En Windows use `python -m streamlit ...` (o `py -m streamlit ...`), porque el comando `streamlit` solo no suele estar en el PATH.

3. El simulador se abre en el navegador, en http://localhost:8501.

## Archivos

| Archivo | Qué contiene | Pareja |
|---|---|---|
| `modelo.py` | Física: potencia del viento, disco actuador (momentum), Cp(λ), torques, EDO del rotor, solución exacta y balance de energía | Equipo 1 |
| `metodos.py` | Euler y RK4 programados a mano, errores y orden de convergencia | Equipo 2 |
| `datos.py` | Curvas reales de potencia y de CT de las turbinas Vestas V52, Vestas V80 y Siemens SWT-2.3-93, y la tabla del artículo de Visión Académica | Equipo 3 |
| `graficos.py` | Dibujos animados: tubo de corriente, rotor que gira, medidores, flujo de potencia y cadena de conversión | Equipo 3 |
| `app.py` | Interfaz con cuatro pestañas | Equipo 3 |
| `.streamlit/config.toml` | Colores neutros de la interfaz | Equipo 3 |

## Pestañas

1. **Momentum:** al cambiar el viento, el radio o el factor de inducción, el dibujo se actualiza. El tubo de aire se ensancha, las líneas de viento se frenan detrás del rotor y las aspas crecen con R. Los medidores muestran la potencia, el Cp, el empuje y el flujo de masa, cada uno con su marca del límite de Betz.
2. **Turbinas reales frente al ideal de Betz:** se elige la turbina y la velocidad del viento. Se ven los medidores, el gráfico "¿a dónde va la potencia del viento?", las curvas y la tabla completa, que se puede descargar en CSV.
3. **Giro del rotor en el tiempo:** Euler y RK4 resuelven la ecuación del rotor. Con el control "instante" se elige el momento que muestran el dibujo (el rotor gira a la velocidad calculada), los medidores y la cadena viento → rotor → eje → generador → red.
4. **Precisión de los métodos:** tabla de errores, orden observado y gráfica de convergencia.
