"""Métodos numéricos programados manualmente (sin usar solvers de SciPy)."""
import numpy as np


def euler(f, t0, y0, h, t_final):
    n = int(round((t_final - t0) / h))
    t = t0 + h * np.arange(n + 1)
    y = np.zeros(n + 1)
    y[0] = y0
    for i in range(n):
        y[i + 1] = y[i] + h * f(t[i], y[i])
    return t, y


def rk4(f, t0, y0, h, t_final):
    n = int(round((t_final - t0) / h))
    t = t0 + h * np.arange(n + 1)
    y = np.zeros(n + 1)
    y[0] = y0
    for i in range(n):
        k1 = f(t[i], y[i])
        k2 = f(t[i] + h / 2, y[i] + h / 2 * k1)
        k3 = f(t[i] + h / 2, y[i] + h / 2 * k2)
        k4 = f(t[i] + h, y[i] + h * k3)
        y[i + 1] = y[i] + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


def errores(y_real, y_aprox):
    Ea = np.abs(np.asarray(y_real) - np.asarray(y_aprox))
    Er = Ea / np.maximum(np.abs(y_real), 1e-12) * 100
    return Ea, Er


def estudio_convergencia(f, t0, y0, t_eval, pasos, y_ref):
    """Error de Euler y RK4 en t_eval para cada paso h; y_ref es el valor 'real'."""
    filas = []
    for h in pasos:
        ye = euler(f, t0, y0, h, t_eval)[1][-1]
        yr = rk4(f, t0, y0, h, t_eval)[1][-1]
        filas.append((h, ye, abs(y_ref - ye), yr, abs(y_ref - yr)))
    ordenes = []
    for i in range(len(filas) - 1):
        r = filas[i][0] / filas[i + 1][0]
        pe = np.log(filas[i][2] / filas[i + 1][2]) / np.log(r) if filas[i + 1][2] > 0 else np.nan
        pr = np.log(filas[i][4] / filas[i + 1][4]) / np.log(r) if filas[i + 1][4] > 1e-13 else np.nan
        ordenes.append((pe, pr))
    return filas, ordenes
