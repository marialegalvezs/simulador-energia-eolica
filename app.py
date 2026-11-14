"""
Simulador: energía eólica y conservación del momentum — Proyecto 7 (G3), Física 1
Ejecutar:  python -m streamlit run app.py
"""
import numpy as np
import pandas as pd
import streamlit as st

import modelo as m
import metodos as nm
import graficos as g

st.set_page_config(page_title="Simulador eólico", page_icon="🌬️", layout="wide")
st.markdown("""
<style>
  .block-container {padding-top: 2rem; max-width: 1250px;}
  [data-testid="stMetric"] {background:#fff;border:1px solid #e6e6e1;border-radius:12px;padding:8px 12px;}
  [data-testid="stMetricLabel"] p {color:#6b6e72;font-size:.85rem;}
</style>""", unsafe_allow_html=True)

R_MAX = 5.0
PASOS = [0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 6.0]
POR_DEFECTO = dict(v=10.0, R=2.0, J=15.0, kg_auto=True, kg=2.777, h=1.0, t_fin=30.0,
                   rafaga=False, v2=13.0, t_cambio=15.0,
                   rho=1.225, cp_max=0.45, lam_opt=7.0, b=0.05, omega0=0.0)
for clave, valor in POR_DEFECTO.items():
    st.session_state.setdefault(clave, valor)


def volver_al_caso_de_estudio():
    for clave, valor in POR_DEFECTO.items():
        st.session_state[clave] = valor


# ====================================================================== parámetros
with st.sidebar:
    st.header("Parámetros")
    st.caption("Mueva un control y observe cómo cambian el dibujo y las gráficas.")

    st.subheader("1. El viento")
    st.slider("Velocidad del viento, v (m/s)", 3.0, 20.0, step=0.5, key="v",
              help="Qué tan rápido llega el aire a la turbina.")
    st.checkbox("Agregar una ráfaga (el viento cambia de golpe)", key="rafaga")
    if st.session_state.rafaga:
        st.slider("Viento después de la ráfaga (m/s)", 3.0, 20.0, step=0.5, key="v2")
        st.slider("Instante de la ráfaga (s)", 1.0, 59.0, step=1.0, key="t_cambio")

    st.subheader("2. La turbina")
    st.slider("Radio de las aspas, R (m)", 1.0, R_MAX, step=0.1, key="R",
              help="Aspas más largas barren más área A = πR² y reciben más viento.")
    st.slider("Momento de inercia del rotor, J (kg·m²)", 1.0, 200.0, step=1.0, key="J",
              help="Qué tanto le cuesta al rotor cambiar su giro. Con J grande tarda más en arrancar.")
    st.checkbox("Ajustar el generador para que el rotor trabaje en su punto óptimo", key="kg_auto",
                help="Elige k_g para que la punta de las aspas gire λ* = 7 veces más rápido que el viento.")
    if not st.session_state.kg_auto:
        st.slider("Carga del generador, k_g (N·m·s)", 0.0, 30.0, step=0.1, key="kg",
                  help="Qué tanto frena el generador al rotor. Más carga: gira más lento.")

    st.subheader("3. El cálculo numérico")
    st.select_slider("Paso de tiempo de Euler y RK4, h (s)", PASOS, key="h",
                     help="Cada cuántos segundos calculan los métodos un nuevo valor de ω.")
    st.slider("Duración de la simulación (s)", 10.0, 60.0, step=5.0, key="t_fin")

    with st.expander("Otros valores (fijos en el caso de estudio)"):
        st.number_input("Densidad del aire, ρ (kg/m³)", 0.80, 1.40, step=0.005, format="%.3f", key="rho",
                        help="1.225 a nivel del mar; cerca de 0.91 en Bogotá.")
        st.number_input("Mejor coeficiente de potencia de las aspas, Cp,máx", 0.10, 0.59, step=0.01, key="cp_max")
        st.number_input("Razón de punta óptima, λ*", 3.0, 12.0, step=0.5, key="lam_opt")
        st.number_input("Fricción de los rodamientos, b (N·m·s)", 0.0, 5.0, step=0.01, key="b")
        st.number_input("Velocidad angular inicial, ω₀ (rad/s)", 0.0, 100.0, step=1.0, key="omega0")
    st.button("↺ Volver al caso de estudio del documento", on_click=volver_al_caso_de_estudio,
              width="stretch")

s = st.session_state
p = dict(v=s.v, R=s.R, rho=s.rho, cp_max=s.cp_max, lam_opt=s.lam_opt, J=s.J, b=s.b,
         omega0=s.omega0, rafaga=s.rafaga, v2=s.v2, t_cambio=s.t_cambio)
p["kg"] = max(m.kg_optimo(p, p["v"]), 0.0) if s.kg_auto else s.kg
h, t_fin = s.h, s.t_fin

# ====================================================================== cálculos
t = np.linspace(0, t_fin, 601)
w = m.omega_exacta(t, p)
est = m.estado(t, w, p)
f = lambda tt, ww: m.f_rotor(tt, ww, p)
with np.errstate(over="ignore", invalid="ignore"):
    t_eu, w_eu = nm.euler(f, 0.0, p["omega0"], h, t_fin)
    t_rk, w_rk = nm.rk4(f, 0.0, p["omega0"], h, t_fin)
v_fin = p["v2"] if p["rafaga"] else p["v"]
w_inf, tau = m.equilibrio(p, v_fin)
tau_min = min(tau, m.equilibrio(p, p["v"])[1])
A = m.area(p["R"])

# ====================================================================== página
st.title("Energía eólica y conservación del momentum")
st.markdown(
    "La turbina **frena el aire y le quita momentum**; por la tercera ley de Newton, el aire empuja "
    "las aspas y las hace girar. Este simulador resuelve la ecuación del giro del rotor\n\n"
    r"$\qquad J\,\dfrac{d\omega}{dt}=T_{\text{viento}}-T_{\text{generador}}-b\,\omega$"
    "\n\nde forma **exacta** y con los métodos numéricos de **Euler** y **Runge–Kutta 4 (RK4)**.")
El simulador sirve para ver la situación física y su evolución.
st.info("**Cómo usarlo:** 1) cambie los parámetros de la izquierda; 2) presione **▶ Reproducir** "
        "para ver el rotor arrancar; 3) compare la solución exacta con Euler y RK4 en las gráficas. "
        "Los valores iniciales son los del caso de estudio del documento.", icon="👉")

if p["rafaga"]:
    st.caption("Con ráfaga, los valores de abajo son los del final, con el viento nuevo.")
c = st.columns(5)
c[0].metric("Potencia del viento", f"{est['P_viento'][-1] / 1e3:.2f} kW")
c[1].metric("Velocidad final ω∞", f"{w_inf:.1f} rad/s", f"{w_inf * 60 / (2 * np.pi):.0f} rpm", delta_color="off")
c[2].metric("Tiempo de respuesta τ", f"{tau:.2f} s")
c[3].metric("Potencia del generador", f"{est['P_gen'][-1] / 1e3:.2f} kW")
c[4].metric("Respecto al límite de Betz", f"{100 * est['P_gen'][-1] / est['P_betz'][-1]:.0f} %")

if h > 2.785 * tau_min:
    st.warning(f"Con h = {h:g} s, tanto Euler (necesita h < 2τ = {2 * tau_min:.2f} s) como RK4 "
               f"(necesita h < 2.78τ = {2.785 * tau_min:.2f} s) son **inestables**: sus valores oscilan y "
               "crecen sin control. Elija un h más pequeño.")
elif h > 2 * tau_min:
    st.warning(f"Con h = {h:g} s > 2τ = {2 * tau_min:.2f} s el método de Euler es **inestable**: sus valores "
               "oscilan y crecen sin control. RK4 y la solución exacta siguen bien. Pruebe un h más pequeño.")

g_html = g.escena(t, w, est, t_eu, w_eu, t_rk, w_rk, p["R"], R_MAX, h)
if hasattr(st, "iframe"):
    st.iframe(g_html, height=900)
else:
    import streamlit.components.v1 as components
    components.html(g_html, height=900)

# ---------------------------------------------------------------- comparación en un instante
st.subheader("4. ¿Qué tan cerca están Euler y RK4 de la solución exacta?")
t_def = max(h, round(4.0 / h) * h)
t_comp = st.slider("Instante en que se comparan (s)", h, float(t_fin), float(t_def), h)
i = int(round(t_comp / h))
w_ex = float(m.omega_exacta(t_comp, p))
fila = lambda nombre, val: (nombre, val, abs(val - w_ex), abs(val - w_ex) / abs(w_ex) * 100 if w_ex else np.nan)
tabla = pd.DataFrame([("Exacta", w_ex, 0.0, 0.0), fila("Euler", w_eu[i]), fila("RK4", w_rk[i])],
                     columns=["Método", "ω (rad/s)", "Error absoluto Eₐ (rad/s)", "Error relativo Eᵣ (%)"])
st.dataframe(tabla.style.format({"ω (rad/s)": "{:.4f}", "Error absoluto Eₐ (rad/s)": "{:.2e}",
                                 "Error relativo Eᵣ (%)": "{:.2e}"}),
             hide_index=True, width="stretch")
st.caption(r"$E_a=|\omega_{\text{num}}-\omega_{\text{exacta}}|$,  $E_r=E_a/|\omega_{\text{exacta}}|\times100$. "
           "Euler usa una pendiente por paso; RK4 usa cuatro y por eso se equivoca mucho menos.")

with st.expander("Ver cómo baja el error al reducir el paso h (tabla de errores del documento)"):
    pasos = [1.0, 0.5, 0.25, 0.125, 0.0625]
    filas, ordenes = nm.estudio_convergencia(f, 0.0, p["omega0"], t_comp, pasos, w_ex)
    df = pd.DataFrame([(hh, ea, ea / w_ex * 100, er, er / w_ex * 100) for hh, _, ea, _, er in filas],
                      columns=["h (s)", "Eₐ Euler", "Eᵣ Euler (%)", "Eₐ RK4", "Eᵣ RK4 (%)"])
    st.dataframe(df.style.format({"h (s)": "{:g}", "Eₐ Euler": "{:.3g}", "Eᵣ Euler (%)": "{:.3g}",
                                  "Eₐ RK4": "{:.2e}", "Eᵣ RK4 (%)": "{:.2e}"}),
                 hide_index=True, width="stretch")
    oe = np.nanmean([o[0] for o in ordenes])
    orr = np.nanmean([o[1] for o in ordenes])
    st.markdown(f"En t = {t_comp:g} s: al dividir h entre 2, el error de Euler se divide más o menos entre 2 "
                f"(orden observado ≈ {oe:.2f}) y el de RK4 entre 16 (orden observado ≈ {orr:.2f}).")

with st.expander("Ver las ecuaciones que usa el simulador"):
    alpha, gamma = m.coef_torque(p, p["v"])
    K = gamma + p["kg"] + p["b"]
    st.markdown("**Momentum (disco actuador):** el aire se frena de $v_1$ a $v_4=v_1(1-2a)$; en el rotor pasa con "
                "$v_d=v_1(1-a)$. Empuje $F=\\dot m(v_1-v_4)$ y $C_p=4a(1-a)^2\\le 16/27$ (límite de Betz).")
    st.markdown("**Aspas:** $C_p(\\lambda)=C_{p,\\max}[2\\lambda/\\lambda^*-(\\lambda/\\lambda^*)^2]$ con "
                "$\\lambda=\\omega R/v$, de modo que $T_{\\text{viento}}=\\alpha-\\gamma\\omega$.")
    st.markdown("**Ecuación del rotor:** $J\\,d\\omega/dt=\\alpha-K\\omega$, con $K=\\gamma+k_g+b$. "
                "Solución exacta: $\\omega(t)=\\omega_\\infty+(\\omega_0-\\omega_\\infty)e^{-t/\\tau}$.")
    st.markdown(f"Con los valores actuales: A = {A:.2f} m², α = {alpha:.1f} N·m, γ = {gamma:.3f} N·m·s, "
                f"k_g = {p['kg']:.3f} N·m·s, K = {K:.3f} N·m·s, ω∞ = {w_inf:.2f} rad/s, τ = {tau:.2f} s.")
    st.markdown("**Euler:** $\\omega_{n+1}=\\omega_n+h\\,f(t_n,\\omega_n)$.  "
                "**RK4:** $\\omega_{n+1}=\\omega_n+\\tfrac{h}{6}(k_1+2k_2+2k_3+k_4)$. "
                "Ambos están programados a mano en `metodos.py`.")
