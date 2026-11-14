"""
Datos de una turbina real para el escenario E4 (ideal frente a real).

Vestas V52-850 kW (D = 52 m): curvas de potencia y de coeficiente de empuje del fabricante,
tal como están en la librería abierta PyWake (DTU Wind Energy, versión 2.6.20, archivo v52.py).
La curva de potencia está referida a la densidad estándar ρ = 1.225 kg/m³ (norma IEC 61400-12-1).
"""
RHO_REF = 1.225
V52 = {
    "D": 52.0,
    "v": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
    "P_kW": [0.0, 25.5, 67.4, 125.0, 203.0, 304.0, 425.0, 554.0, 671.0, 759.0, 811.0, 836.0, 846.0, 849.0],
    "CT": [0.058, 0.82, 0.82, 0.82, 0.82, 0.82, 0.79, 0.751, 0.675, 0.602, 0.418, 0.323, 0.256, 0.209],
}
