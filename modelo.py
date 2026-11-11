"""Modelo físico de la turbina: potencia del viento, disco actuador y dinámica del rotor."""
import numpy as np

BETZ_CP = 16 / 27      # coeficiente de potencia máximo (a = 1/3)
BETZ_CT = 8 / 9        # coeficiente de empuje en el punto de Betz


# ---------------------------------------------------------------- viento
def potencia_viento(rho, A, v):
    """P = 1/2 rho A v^3  [W]"""
    return 0.5 * rho * A * np.asarray(v, dtype=float) ** 3


def perfil_viento(t, tipo="constante", v0=10.0, dv=2.0, periodo=10.0, t_esc=10.0):
    """Velocidad del viento v(t) [m/s]."""
    t = np.asarray(t, dtype=float)
    if tipo == "escalón":
        return np.where(t < t_esc, v0, v0 + dv)
    if tipo == "ráfaga senoidal":
        return v0 + dv * np.sin(2 * np.pi * t / periodo)
    return np.full_like(t, v0)


# ------------------------------------------------- disco actuador (momentum)
def disco_actuador(v_u, a, rho, A):
    """Teoría de Rankine-Froude: velocidades, flujo de masa, empuje y potencia."""
    v_r = v_u * (1 - a)              # velocidad en el rotor
    v_w = v_u * (1 - 2 * a)          # velocidad en la estela lejana
    m_dot = rho * A * v_r            # flujo de masa [kg/s]
    F = m_dot * (v_u - v_w)          # empuje = cambio de momentum por segundo [N]
    P = F * v_r                      # potencia extraída [W]
    P_energia = 0.5 * m_dot * (v_u**2 - v_w**2)   # comprobación por energía
    Pv = potencia_viento(rho, A, v_u)
    return dict(v_r=v_r, v_w=v_w, m_dot=m_dot, F=F, P=P, P_energia=P_energia,
                Pv=Pv, Cp=P / Pv, CT=F / (0.5 * rho * A * v_u**2))


def cp_de_a(a):
    return 4 * a * (1 - a) ** 2


def ct_de_a(a):
    return 4 * a * (1 - a)


def a_desde_ct(ct):
    """Invierte C_T = 4a(1-a) (rama a <= 1/2)."""
    ct = np.clip(np.asarray(ct, dtype=float), 0, 1)
    return (1 - np.sqrt(1 - ct)) / 2


def a_desde_cp(cp, iter_=60):
    """Invierte C_p = 4a(1-a)^2 en la rama 0 <= a <= 1/3 (bisección)."""
    cp = np.minimum(np.asarray(cp, dtype=float), BETZ_CP)
    lo, hi = np.zeros_like(cp), np.full_like(cp, 1 / 3)
    for _ in range(iter_):
        m = (lo + hi) / 2
        menor = cp_de_a(m) < cp
        lo, hi = np.where(menor, m, lo), np.where(menor, hi, m)
    return (lo + hi) / 2


def velocidad_eje(x, a, R):
    """Velocidad axial sobre el eje del disco (u/v), x en metros (x<0 aguas arriba)."""
    return 1 - a * (1 + x / np.sqrt(x**2 + R**2))


# --------------------------------------------------------- dinámica del rotor
def cp_parabolico(lam, cp_max, lam_opt):
    return cp_max * (2 * lam / lam_opt - (lam / lam_opt) ** 2)


def coef_torque(rho, R, v, cp_max, lam_opt):
    """T_turbina = alpha - gamma*omega  (C_p parabólico)."""
    A = np.pi * R**2
    alpha = rho * A * R * v**2 * cp_max / lam_opt
    gamma = 0.5 * rho * A * R**2 * v * cp_max / lam_opt**2
    return alpha, gamma


def torque_turbina(omega, v, p):
    alpha, gamma = coef_torque(p["rho"], p["R"], v, p["cp_max"], p["lam_opt"])
    return alpha - gamma * omega


def torque_carga(omega, p):
    return p["T0"] + p["kg"] * omega


def f_rotor(t, omega, p, viento):
    """Lado derecho de J dω/dt = T_turbina - T_carga - b ω."""
    v = viento(t)
    return (torque_turbina(omega, v, p) - torque_carga(omega, p) - p["b"] * omega) / p["J"]


def solucion_analitica(t, p, v):
    """ω(t) = ω∞ + (ω0 - ω∞) e^{-t/τ}  (viento constante)."""
    alpha, gamma = coef_torque(p["rho"], p["R"], v, p["cp_max"], p["lam_opt"])
    K = gamma + p["kg"] + p["b"]
    w_inf = (alpha - p["T0"]) / K
    tau = p["J"] / K
    return w_inf + (p["omega0"] - w_inf) * np.exp(-np.asarray(t) / tau), w_inf, tau


def kg_optimo(p, v_diseno):
    """Constante del generador que lleva al rotor a λ* con el viento de diseño."""
    w_opt = p["lam_opt"] * v_diseno / p["R"]
    alpha, gamma = coef_torque(p["rho"], p["R"], v_diseno, p["cp_max"], p["lam_opt"])
    return (alpha - gamma * w_opt - p["T0"]) / w_opt - p["b"]


def balance_energia(t, omega, p, viento):
    """Energías acumuladas: aerodinámica, generador, fricción y cinética (regla del trapecio)."""
    v = viento(t)
    P_aero = torque_turbina(omega, v, p) * omega
    P_gen = torque_carga(omega, p) * omega
    P_fric = p["b"] * omega**2
    trap = lambda y: np.concatenate([[0], np.cumsum(0.5 * (y[1:] + y[:-1]) * np.diff(t))])
    E_aero, E_gen, E_fric = trap(P_aero), trap(P_gen), trap(P_fric)
    dEk = 0.5 * p["J"] * (omega**2 - omega[0] ** 2)
    return dict(P_aero=P_aero, P_gen=P_gen, P_fric=P_fric, E_aero=E_aero,
                E_gen=E_gen, E_fric=E_fric, dEk=dEk)


def ajuste_densidad(v, rho, rho_ref=1.225):
    """Corrección IEC 61400-12-1: velocidad equivalente a la densidad de referencia."""
    return np.asarray(v) * (rho / rho_ref) ** (1 / 3)
