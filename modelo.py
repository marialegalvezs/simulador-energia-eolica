"""
Física del Proyecto 7: potencia del viento, disco actuador (momentum) y giro del rotor.

Ecuación del rotor (segunda ley de Newton para la rotación):
    J dω/dt = T_viento - T_carga - b ω
con T_viento = α - γ ω  (por la aproximación parabólica de Cp(λ)) y T_carga = k_g ω.
"""
import numpy as np

BETZ_CP = 16 / 27   # máximo coeficiente de potencia (a = 1/3)

# Caso de estudio del documento (sección 2.7)
CASO_ESTUDIO = dict(v=10.0, R=2.0, rho=1.225, cp_max=0.45, lam_opt=7.0,
                    J=15.0, b=0.05, omega0=0.0)


def area(R):
    return np.pi * R**2


def potencia_viento(rho, R, v):
    """P_viento = 1/2 ρ A v³  [W]"""
    return 0.5 * rho * area(R) * np.asarray(v, dtype=float) ** 3


def disco_actuador(v1, a, rho, R):
    """Conservación de masa, impulso-momentum y energía para el factor de inducción a."""
    vd, v4 = v1 * (1 - a), v1 * (1 - 2 * a)
    m_dot = rho * area(R) * vd          # masa de aire por segundo [kg/s]
    F = m_dot * (v1 - v4)               # empuje = cambio de momentum por segundo [N]
    P = F * vd                          # potencia que recibe el rotor [W]
    return dict(vd=vd, v4=v4, m_dot=m_dot, F=F, P=P)


def a_desde_cp(cp):
    """Invierte Cp = 4a(1-a)² en la rama 0 <= a <= 1/3 (bisección)."""
    cp = np.clip(np.asarray(cp, dtype=float), 0.0, BETZ_CP)
    lo, hi = np.zeros_like(cp), np.full_like(cp, 1 / 3)
    for _ in range(50):
        mid = (lo + hi) / 2
        menor = 4 * mid * (1 - mid) ** 2 < cp
        lo, hi = np.where(menor, mid, lo), np.where(menor, hi, mid)
    return (lo + hi) / 2


def cp_parabolico(lam, cp_max, lam_opt):
    """Cp(λ) = Cp,max [2λ/λ* - (λ/λ*)²]  (ecuación 10 del documento)."""
    return cp_max * (2 * lam / lam_opt - (lam / lam_opt) ** 2)


def coef_torque(p, v):
    """α y γ de T_viento = α - γ ω  (ecuación 11 del documento)."""
    A = area(p["R"])
    alpha = p["rho"] * A * p["R"] * v**2 * p["cp_max"] / p["lam_opt"]
    gamma = p["rho"] * A * p["R"] ** 2 * v * p["cp_max"] / (2 * p["lam_opt"] ** 2)
    return alpha, gamma


def kg_optimo(p, v):
    """Constante del generador que deja el rotor girando en λ* con el viento v."""
    alpha, gamma = coef_torque(p, v)
    w_opt = p["lam_opt"] * v / p["R"]
    return alpha / w_opt - gamma - p["b"]


def viento(t, p):
    """Velocidad del viento v(t) [m/s].
    tipo "constante": v.   tipo "escalon": v hasta t_cambio y luego v2.
    tipo "rafaga": v + dv·exp(-((t - t_cambio)/2 s)²), una ráfaga que dura unos 4 s."""
    t = np.asarray(t, dtype=float)
    tipo = p.get("tipo", "constante")
    if tipo == "escalon":
        return np.where(t < p["t_cambio"], p["v"], p["v2"])
    if tipo == "rafaga":
        return p["v"] + p["dv"] * np.exp(-((t - p["t_cambio"]) / 2.0) ** 2)
    return np.full_like(t, p["v"])


def f_rotor(t, omega, p):
    """dω/dt = (T_viento - T_carga - b ω) / J"""
    alpha, gamma = coef_torque(p, float(viento(t, p)))
    return (alpha - gamma * omega - p["kg"] * omega - p["b"] * omega) / p["J"]


def equilibrio(p, v):
    """ω∞ = α/K y τ = J/K, con K = γ + k_g + b."""
    alpha, gamma = coef_torque(p, v)
    K = gamma + p["kg"] + p["b"]
    return alpha / K, p["J"] / K


def tiene_exacta(p):
    return p.get("tipo", "constante") in ("constante", "escalon")


def omega_exacta(t, p):
    """Solución exacta ω(t) = ω∞ + (ω0 - ω∞) e^{-t/τ}; con escalón se aplica por tramos.
    (Para la ráfaga no hay solución exacta: se usa una referencia numérica, ver omega_referencia.)"""
    t = np.asarray(t, dtype=float)
    w_inf, tau = equilibrio(p, p["v"])
    w = w_inf + (p["omega0"] - w_inf) * np.exp(-t / tau)
    if p.get("tipo") == "escalon":
        tc = p["t_cambio"]
        wc = w_inf + (p["omega0"] - w_inf) * np.exp(-tc / tau)
        w2, tau2 = equilibrio(p, p["v2"])
        w = np.where(t < tc, w, w2 + (wc - w2) * np.exp(-(t - tc) / tau2))
    return w


def omega_referencia(t, p, h_ref=0.001):
    """Exacta si existe; si no, RK4 con un paso muy pequeño (h = 0.001 s) interpolado en t."""
    if tiene_exacta(p):
        return omega_exacta(t, p)
    from metodos import rk4
    t = np.asarray(t, dtype=float)
    tt, ww = rk4(lambda s, w: f_rotor(s, w, p), 0.0, p["omega0"], h_ref, float(np.max(t)))
    return np.interp(t, tt, ww)


def estado(t, omega, p):
    """Todas las magnitudes físicas en cada instante, a partir de ω(t)."""
    v = viento(t, p)
    lam = omega * p["R"] / v
    cp = np.clip(cp_parabolico(lam, p["cp_max"], p["lam_opt"]), 0, None)
    a = a_desde_cp(cp)
    disco = disco_actuador(v, a, p["rho"], p["R"])
    Pv = potencia_viento(p["rho"], p["R"], v)
    return dict(v=v, lam=lam, cp=cp, a=a, vd=disco["vd"], v4=disco["v4"], F=disco["F"],
                F_betz=8 / 9 * 0.5 * p["rho"] * area(p["R"]) * v**2,
                P_viento=Pv, P_betz=BETZ_CP * Pv, P_aero=cp * Pv,
                P_gen=p["kg"] * omega**2, P_fric=p["b"] * omega**2)
