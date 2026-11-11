"""
Datos de turbinas reales para comparar con el modelo ideal (Betz).

Fuente de las tablas: curvas de potencia y de coeficiente de empuje publicadas
por los fabricantes, tal como están incluidas en la librería abierta PyWake
(DTU Wind Energy, licencia MIT, versión 2.6.20, módulo py_wake/examples/data):
  - Vestas V52-850 kW (v52.py, "data copied from VindPro")
  - Vestas V80-2.0 MW, parque eólico Horns Rev 1 (hornsrev1.py)
  - Siemens SWT-2.3-93, parque eólico Lillgrund (lillgrund.py)

IMPORTANTE:
  * La curva de POTENCIA de un fabricante se obtiene con mediciones en campo
    según la norma IEC 61400-12-1 y se refiere a la densidad estándar
    rho = 1.225 kg/m^3.
  * La curva de EMPUJE (C_T) la entrega el fabricante; normalmente es calculada
    con sus modelos aerodinámicos validados, no medida directamente.
  * La tabla del artículo de Visión Académica (2026) NO es medida
    ("Elaborado: Autores") y su columna de C_p es inconsistente; se incluye solo
    para mostrar esa inconsistencia.
"""

RHO_REF = 1.225  # kg/m^3, densidad de referencia de las curvas de potencia

_ws = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0,
       16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0]

TURBINAS = {
    "Vestas V52-850 kW": {
        "D": 52.0,
        "v": _ws,
        "P_kW": [0.0, 25.5, 67.4, 125.0, 203.0, 304.0, 425.0, 554.0, 671.0, 759.0,
                 811.0, 836.0, 846.0, 849.0, 850.0, 850.0, 850.0, 850.0, 850.0,
                 850.0, 850.0, 850.0, 850.0],
        "CT": [0.058, 0.82, 0.82, 0.82, 0.82, 0.82, 0.79, 0.751, 0.675, 0.602,
               0.418, 0.323, 0.256, 0.209, 0.174, 0.147, 0.126, 0.108, 0.094,
               0.083, 0.073, 0.065, 0.058],
        "fuente": "Vestas V52 (catálogo WindPRO), vía PyWake 2.6.20",
    },
    "Vestas V80-2.0 MW (Horns Rev 1)": {
        "D": 80.0,
        "v": _ws,
        "P_kW": [0.0, 66.6, 154.0, 282.0, 460.0, 696.0, 996.0, 1341.0, 1661.0,
                 1866.0, 1958.0, 1988.0, 1997.0, 1999.0, 2000.0, 2000.0, 2000.0,
                 2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0],
        "CT": [0.0, 0.818, 0.806, 0.804, 0.805, 0.806, 0.807, 0.793, 0.739, 0.709,
               0.409, 0.314, 0.249, 0.202, 0.167, 0.14, 0.119, 0.102, 0.088,
               0.077, 0.067, 0.06, 0.053],
        "fuente": "Vestas V80, parque Horns Rev 1, vía PyWake 2.6.20",
    },
    "Siemens SWT-2.3-93 (Lillgrund)": {
        "D": 93.0,
        "v": _ws,
        "P_kW": [0.0, 65.0, 180.0, 352.0, 590.0, 906.0, 1308.0, 1767.0, 2085.0,
                 2234.0, 2283.0, 2296.0, 2299.0, 2300.0, 2300.0, 2300.0, 2300.0,
                 2300.0, 2300.0, 2300.0, 2300.0, 2300.0, 2300.0],
        "CT": [0.0, 0.81, 0.84, 0.83, 0.85, 0.86, 0.87, 0.79, 0.67, 0.45, 0.34,
               0.26, 0.21, 0.17, 0.14, 0.12, 0.10, 0.09, 0.07, 0.07, 0.06, 0.05,
               0.05],
        "fuente": "Siemens SWT-2.3-93, parque Lillgrund, vía PyWake 2.6.20",
    },
}

# Tabla 1 del artículo de Visión Académica (2026): R = 45 m. No es medición.
ARTICULO = {
    "R": 45.0,
    "v": [4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0],
    "omega": [0.22, 0.55, 0.98, 1.51, 2.00, 2.00, 2.00, 2.00, 2.00],
    "Cp_reportado": [0.185, 0.310, 0.425, 0.471, 0.482, 0.385, 0.291, 0.222, 0.174],
    "P_MW": [0.03, 0.21, 0.92, 1.98, 2.88, 2.88, 2.88, 2.88, 2.88],
}
