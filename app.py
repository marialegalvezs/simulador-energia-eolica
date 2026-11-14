"""
Simulador: energía eólica y conservación del momentum — Proyecto 7 (G3), Física 1
Ejecutar:  python -m streamlit run app.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

import modelo as m
import metodos as nm
import graficos as g
from datos import V52, RHO_REF

st.set_page_config(page_title="Simulador eólico", page_icon="🌬️", layout="wide")
st.markdown("""
<style>
  .block-container {padding-top: 2rem; max-width: 1250px;}
  [data-testid="stMetric"] {background:#fff;border:1px solid #e6e6e1;border-radius:12px;padding:8px 12px;}
  [data-testid="stMetricLabel"] p {color:#6b6e72;font-size:.85rem;}
</style>""", unsafe_allow_html=True)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.25, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "#fbfbf9"})

R_MAX = 5.0
PASOS_TABLA = [1.0, 0.5, 0.25, 0.125, 0.0625]                # los pasos de la tabla de errores del documento
PASOS = sorted(PASOS_TABLA + [2.0, 6.0])                      # 6 s > 2τ: para ver que Euler diverge
KG_CASO = m.kg_optimo(dict(m.CASO_ESTUDIO), 10.0)            # ≈ 2.777 N·m·s (rotor en λ* con 10 m/s)
POR_DEFECTO = dict(v=10.0, cambio="Ninguno", v2=10.0, dv=4.0, t_cambio=10.0,
                   R=2.0, J=15.0, kg=KG_CASO, h=1.0, t_fin=30.0,
                   rho=1.225, cp_max=0.45, lam_opt=7.0, b=0.05, omega0=0.0)
for clave, valor in POR_DEFECTO.items():
    st.session_state.setdefault(clave, valor)


def volver_al_caso_de_estudio():
    for clave, valor in POR_DEFECTO.items():
        st.session_state[clave] = valor


def mostrar(html, alto):
    if hasattr(st, "iframe"):
        st.iframe(html, height=alto)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=alto)


def integrar(metodo, p, h, t_fin):
    """Euler o RK4. Si el viento cambia de golpe (escalón), el método se reinicia en el instante del
    cambio para que ningún paso mezcle el viento de antes con el de después."""
    paso = nm.euler if metodo == "Euler" else nm.rk4
    tc = p.get("t_cambio", 0.0)
    if p.get("tipo") == "escalon" and 0 < tc < t_fin and abs(tc / h - round(tc / h)) < 1e-9:
        f1 = lambda tt, ww: m.f_rotor(min(tt, tc - 1e-12), ww, p)
        f2 = lambda tt, ww: m.f_rotor(max(tt, tc), ww, p)
        t1, w1 = paso(f1, 0.0, p["omega0"], h, tc)
        t2, w2 = paso(f2, tc, w1[-1], h, t_fin)
        return np.concatenate([t1, t2[1:]]), np.concatenate([w1, w2[1:]])
    return paso(lambda tt, ww: m.f_rotor(tt, ww, p), 0.0, p["omega0"], h, t_fin)


# ====================================================================== parámetros
with st.sidebar:
    st.header("Parámetros")
    st.caption("Mueva un control y observe cómo cambian el dibujo y las gráficas.")

    st.subheader("1. El viento")
    st.slider("Velocidad del viento, v (m/s)", 3.0, 20.0, step=0.5, key="v",
              help="Qué tan rápido llega el aire a la turbina.")
    st.radio("¿Cambia el viento?", ["Ninguno", "Escalón", "Ráfaga"], key="cambio", horizontal=True,
             help="Escalón: el viento pasa de v a otro valor y se queda. Ráfaga: sube unos segundos y vuelve.")
    if st.session_state.cambio == "Escalón":
        st.slider("Viento después del escalón (m/s)", 3.0, 20.0, step=0.5, key="v2")
    elif st.session_state.cambio == "Ráfaga":
        st.slider("Aumento del viento en la ráfaga (m/s)", 1.0, 8.0, step=0.5, key="dv")
    if st.session_state.cambio != "Ninguno":
        st.slider("Instante del cambio (s)", 2.0, 50.0, step=1.0, key="t_cambio")
    st.radio("Densidad del aire, ρ (kg/m³)", [1.225, 0.91], key="rho", horizontal=True,
             format_func=lambda r: "1.225 (nivel del mar)" if r == 1.225 else "0.91 (Bogotá)")

    st.subheader("2. La turbina")
    st.slider("Radio de las aspas, R (m)", 1.0, R_MAX, step=0.1, key="R",
              help="Aspas más largas barren más área A = πR² y reciben más viento.")
    st.slider("Momento de inercia del rotor, J (kg·m²)", 1.0, 200.0, step=1.0, key="J",
              help="Qué tanto le cuesta al rotor cambiar su giro. Con J grande tarda más en arrancar.")
    st.number_input("Carga del generador, k_g (N·m·s)", 0.0, 30.0, step=0.1, format="%.3f", key="kg",
                    help="Qué tanto frena el generador al rotor. 2.777 deja el rotor en su punto óptimo con 10 m/s.")
    st.slider("Velocidad angular inicial, ω₀ (rad/s)", 0.0, 60.0, step=1.0, key="omega0")

    st.subheader("3. El cálculo numérico")
    st.select_slider("Paso de tiempo de Euler y RK4, h (s)", PASOS, key="h", format_func=lambda x: f"{x:g}",
                     help="Cada cuántos segundos calculan los métodos un nuevo valor de ω.")
    st.slider("Duración de la simulación (s)", 10.0, 60.0, step=5.0, key="t_fin")

    with st.expander("Otros valores (fijos en el caso de estudio)"):
        st.number_input("Mejor coeficiente de potencia de las aspas, Cp,máx", 0.10, 0.59, step=0.01, key="cp_max")
        st.number_input("Razón de punta óptima, λ*", 3.0, 12.0, step=0.5, key="lam_opt")
        st.number_input("Fricción de los rodamientos, b (N·m·s)", 0.0, 5.0, step=0.01, key="b")
    st.button("↺ Volver al caso de estudio del documento", on_click=volver_al_caso_de_estudio, width="stretch")

s = st.session_state
tipo = {"Ninguno": "constante", "Escalón": "escalon", "Ráfaga": "rafaga"}[s.cambio]
p = dict(v=s.v, R=s.R, rho=s.rho, cp_max=s.cp_max, lam_opt=s.lam_opt, J=s.J, b=s.b, kg=s.kg,
         omega0=s.omega0, tipo=tipo, v2=s.v2 if tipo == "escalon" else s.v, dv=s.dv, t_cambio=s.t_cambio)
h, t_fin = s.h, s.t_fin

# ====================================================================== cálculos
t = np.linspace(0, t_fin, 601)
w = m.omega_referencia(t, p)
est = m.estado(t, w, p)
with np.errstate(over="ignore", invalid="ignore"):
    t_eu, w_eu = integrar("Euler", p, h, t_fin)
    t_rk, w_rk = integrar("RK4", p, h, t_fin)
w_inf, tau = m.equilibrio(p, float(est["v"][-1]))
tau_min = min(m.equilibrio(p, p["v"])[1], m.equilibrio(p, p["v2"])[1])
ref = "Exacta" if m.tiene_exacta(p) else "Referencia (RK4 con h = 0.001 s)"

# ====================================================================== página
st.title("🌬️ ¿Cuánta energía le saca una turbina al viento?")
st.markdown(
    "La turbina **frena el aire y le quita momentum**; por la tercera ley de Newton, el aire empuja "
    "las aspas y las hace girar. Este simulador resuelve la ecuación del giro del rotor\n\n"
    r"$\qquad J\,\dfrac{d\omega}{dt}=T_{\text{viento}}-T_{\text{generador}}-b\,\omega$"
    "\n\nde forma **exacta** y con los métodos numéricos de **Euler** y **Runge–Kutta 4 (RK4)**.")
st.info("**Cómo usarlo:** 1) cambie los parámetros de la izquierda; 2) presione **▶ Reproducir** "
        "para ver el rotor arrancar en tiempo real; 3) compare la solución exacta con Euler y RK4 en las gráficas. "
        "Los valores iniciales son los del caso de estudio del documento. La guía de escenarios E1–E5 está "
        "en `GUIA_ESCENARIOS.md`.", icon="👉")

if tipo != "constante":
    st.caption("Con cambio de viento, los valores de abajo son los del final de la simulación.")
c = st.columns(5)
c[0].metric("Potencia del viento", f"{est['P_viento'][-1] / 1e3:.2f} kW")
c[1].metric("Velocidad final ω∞", f"{w[-1]:.1f} rad/s", f"{w[-1] * 60 / (2 * np.pi):.0f} rpm", delta_color="off")
c[2].metric("Tiempo de respuesta τ", f"{tau:.2f} s")
c[3].metric("Potencia entregada", f"{est['P_gen'][-1] / 1e3:.2f} kW")
c[4].metric("Respecto al límite de Betz", f"{100 * est['P_gen'][-1] / est['P_betz'][-1]:.0f} %")

if h > 2.785 * tau_min:
    st.warning(f"Con h = {h:g} s, tanto Euler (necesita h < 2τ = {2 * tau_min:.2f} s) como RK4 "
               f"(necesita h < 2.78τ = {2.785 * tau_min:.2f} s) son **inestables**. Elija un h más pequeño.")
elif h > 2 * tau_min:
    st.warning(f"Con h = {h:g} s > 2τ = {2 * tau_min:.2f} s el método de Euler es **inestable**: sus valores "
               "oscilan y crecen sin control. RK4 y la solución exacta siguen bien.")

mostrar(g.escena(t, w, est, t_eu, w_eu, t_rk, w_rk, p["R"], R_MAX, h, ref=ref), 950)

# ---------------------------------------------------------------- comparación en un instante
st.subheader("4. ¿Qué tan cerca están Euler y RK4 de la solución exacta?")
t_def = max(h, round(4.0 / h) * h)
t_comp = st.slider("Instante en que se comparan (s)", h, float(t_fin), float(min(t_def, t_fin)), h)
i = int(round(t_comp / h))
w_ex = float(m.omega_referencia(np.array([t_comp]), p)[0])
fila = lambda nombre, val: (nombre, val, abs(val - w_ex), abs(val - w_ex) / abs(w_ex) * 100 if w_ex else np.nan)
tabla = pd.DataFrame([(ref.split(" (")[0], w_ex, 0.0, 0.0), fila("Euler", w_eu[i]), fila("RK4", w_rk[i])],
                     columns=["Método", "ω (rad/s)", "Error absoluto Eₐ (rad/s)", "Error relativo Eᵣ (%)"])
st.dataframe(tabla.style.format({"ω (rad/s)": "{:.4f}", "Error absoluto Eₐ (rad/s)": "{:.2e}",
                                 "Error relativo Eᵣ (%)": "{:.2e}"}), hide_index=True, width="stretch")
st.caption(r"$E_a=|\omega_{\text{num}}-\omega_{\text{exacta}}|$,  $E_r=E_a/|\omega_{\text{exacta}}|\times100$. "
           "Euler usa una pendiente por paso; RK4 usa cuatro y por eso se equivoca mucho menos.")

st.markdown(f"**Tabla de errores al reducir el paso h** (en t = {t_comp:g} s, con los mismos parámetros)")
filas = []
for hh in PASOS_TABLA:
    if abs(t_comp / hh - round(t_comp / hh)) > 1e-9:
        continue
    ea = abs(integrar("Euler", p, hh, t_comp)[1][-1] - w_ex)
    er = abs(integrar("RK4", p, hh, t_comp)[1][-1] - w_ex)
    filas.append((hh, ea, ea / w_ex * 100, er, er / w_ex * 100))
df = pd.DataFrame(filas, columns=["h (s)", "Eₐ Euler", "Eᵣ Euler (%)", "Eₐ RK4", "Eᵣ RK4 (%)"])
orden = lambda e: ["–"] + [f"{np.log2(e[k] / e[k + 1]):.2f}" if e[k + 1] > 1e-13 else "–" for k in range(len(e) - 1)]
df["Orden Euler"], df["Orden RK4"] = orden(df["Eₐ Euler"].values), orden(df["Eₐ RK4"].values)
st.dataframe(df.style.format({"h (s)": "{:g}", "Eₐ Euler": "{:.3g}", "Eᵣ Euler (%)": "{:.3g}",
                              "Eₐ RK4": "{:.2e}", "Eᵣ RK4 (%)": "{:.2e}"}), hide_index=True, width="stretch")
st.caption("Al dividir h entre 2, el error de Euler se divide entre 2 (orden 1) y el de RK4 entre 16 (orden 4).")

# ---------------------------------------------------------------- momentum: ideal frente a real
st.subheader("5. Momentum: turbina ideal (Betz) frente a una turbina real")
modo = st.radio("Qué turbina ver", ["Ideal: elegir cuánto se frena el aire (factor a)",
                                    "Real: Vestas V52 (R = 26 m)"], horizontal=True, label_visibility="collapsed")
if modo.startswith("Ideal"):
    opciones_a = sorted({round(x, 2) for x in np.arange(0, 0.501, 0.02)} | {1 / 3})
    a = st.select_slider("Factor de inducción a (cuánto se frena el aire)", opciones_a, value=1 / 3,
                         format_func=lambda x: "1/3 (Betz)" if abs(x - 1 / 3) < 1e-9 else f"{x:.2f}")
    v1, R_d = p["v"], p["R"]
    d = m.disco_actuador(v1, a, p["rho"], R_d)
    betz = m.disco_actuador(v1, 1 / 3, p["rho"], R_d)
    Pv = float(m.potencia_viento(p["rho"], R_d, v1))
    a_d, F_d, Fb_d, P_d, Pb_d, w_d, Rmax_d = a, d["F"], betz["F"], d["P"], betz["P"], 7 * v1 / R_d, R_MAX
    st.caption(f"Con v = {v1:g} m/s, R = {R_d:g} m y ρ = {p['rho']} kg/m³ (los de la izquierda).")
else:
    v1 = st.select_slider("Velocidad del viento para la V52 (m/s)", [float(x) for x in range(4, 17)], value=8.0)
    R_d = V52["D"] / 2
    A = np.pi * R_d ** 2
    v_eq = v1 * (p["rho"] / RHO_REF) ** (1 / 3)               # corrección de densidad IEC 61400-12-1
    P_d = float(np.interp(v_eq, V52["v"], V52["P_kW"])) * 1e3
    CT = float(np.interp(v_eq, V52["v"], V52["CT"]))
    a_d = (1 - np.sqrt(1 - min(CT, 1.0))) / 2
    q = 0.5 * p["rho"] * A * v1 ** 2
    F_d, Fb_d, Pv = CT * q, 8 / 9 * q, q * v1
    Pb_d, w_d, Rmax_d = 16 / 27 * Pv, 7 * v1 / R_d, R_d
    st.caption(f"Densidad ρ = {p['rho']} kg/m³ (se cambia a la izquierda). Datos del fabricante vía PyWake.")
dos = lambda x: np.full(2, float(x))
est_d = dict(v=dos(v1), lam=dos(7), cp=dos(P_d / Pv), a=dos(a_d), vd=dos(v1 * (1 - a_d)), v4=dos(v1 * (1 - 2 * a_d)),
             F=dos(F_d), F_betz=dos(Fb_d), P_viento=dos(Pv), P_betz=dos(Pb_d), P_aero=dos(P_d), P_gen=dos(P_d))
z = np.zeros(2)
mostrar(g.escena(np.array([0, 1.0]), dos(w_d), est_d, z, z, z, z, R_d, Rmax_d, 1.0, modo="tubo",
                 texto_barra="Potencia extraída" if modo.startswith("Ideal") else "Potencia entregada (real)"), 440)
c = st.columns(3) + st.columns(3)
fmtP = lambda P: f"{P / 1e3:.2f} kW" if P < 1e5 else f"{P / 1e3:.0f} kW"
fmtF = lambda F: f"{F:.0f} N" if F < 1e4 else f"{F / 1e3:.1f} kN"
c[0].metric("Potencia", fmtP(P_d), f"Betz: {fmtP(Pb_d)}", delta_color="off")
c[1].metric("Cp", f"{P_d / Pv:.3f}", f"{100 * P_d / Pb_d:.0f} % de Betz (0.593)", delta_color="off")
c[2].metric("Masa por segundo ṁ = ρAv_d", (lambda md: f"{md:.1f} kg/s" if md < 1e3 else f"{md:,.0f} kg/s".replace(",", " "))(p['rho'] * np.pi * R_d ** 2 * v1 * (1 - a_d)))
c[3].metric("Factor a", f"{a_d:.3f}", "Betz: 0.333", delta_color="off")
c[4].metric("Viento detrás v₄", f"{v1 * (1 - 2 * a_d):.2f} m/s", f"Betz: {v1 / 3:.2f}", delta_color="off")
c[5].metric("Empuje F", fmtF(F_d), f"Betz: {fmtF(Fb_d)}", delta_color="off")

with st.expander("Ver las ecuaciones que usa el simulador"):
    alpha, gamma = m.coef_torque(p, p["v"])
    K = gamma + p["kg"] + p["b"]
    st.markdown("**Momentum (disco actuador):** el aire se frena de $v_1$ a $v_4=v_1(1-2a)$; en el rotor pasa con "
                "$v_d=v_1(1-a)$. Empuje $F=\\dot m(v_1-v_4)$ y $C_p=4a(1-a)^2\\le 16/27$ (límite de Betz).")
    st.markdown("**Aspas:** $C_p(\\lambda)=C_{p,\\max}[2\\lambda/\\lambda^*-(\\lambda/\\lambda^*)^2]$ con "
                "$\\lambda=\\omega R/v$, de modo que $T_{\\text{viento}}=\\alpha-\\gamma\\omega$.")
    st.markdown("**Ecuación del rotor:** $J\\,d\\omega/dt=\\alpha-K\\omega$, con $K=\\gamma+k_g+b$. "
                "Solución exacta: $\\omega(t)=\\omega_\\infty+(\\omega_0-\\omega_\\infty)e^{-t/\\tau}$. "
                "Potencia entregada: $P=k_g\\omega^2$.")
    st.markdown(f"Con los valores actuales (viento inicial): A = {m.area(p['R']):.2f} m², α = {alpha:.1f} N·m, "
                f"γ = {gamma:.3f} N·m·s, k_g = {p['kg']:.3f} N·m·s, K = {K:.3f} N·m·s.")
    st.markdown("**Euler:** $\\omega_{n+1}=\\omega_n+h\\,f(t_n,\\omega_n)$.  "
                "**RK4:** $\\omega_{n+1}=\\omega_n+\\tfrac{h}{6}(k_1+2k_2+2k_3+k_4)$. "
                "Ambos están programados a mano en `metodos.py`.")
