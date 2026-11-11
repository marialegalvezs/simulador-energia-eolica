"""
Simulador de generación eólica y conservación del momentum — Proyecto 7 (G3)
Ejecutar:  python -m streamlit run app.py
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

import modelo as m
import metodos as nm
import graficos as g
from datos import TURBINAS, ARTICULO, RHO_REF

st.set_page_config(page_title="Simulador eólico", layout="wide")


def dibujo(html, alto):
    """Muestra un dibujo animado (compatible con versiones nuevas y antiguas de Streamlit)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=alto)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=alto)

# ------------------------------------------------------------------ estilo
st.markdown("""
<style>
  .block-container {padding-top: 2.2rem; max-width: 1350px;}
  h1 {font-weight: 600; letter-spacing: -.5px; color:#2b2d2f;}
  h2, h3 {font-weight: 550; color:#2b2d2f;}
  [data-testid="stMetric"] {background:#fff;border:1px solid #e6e6e1;border-radius:14px;padding:10px 14px;}
  [data-testid="stMetricLabel"] p {color:#8a8d91;font-size:.82rem;}
  .stTabs [data-baseweb="tab-list"] {gap: 6px;}
  .stTabs [data-baseweb="tab"] {background:#f1f1ed;border-radius:10px 10px 0 0;padding:8px 16px;}
  .stTabs [aria-selected="true"] {background:#fff;}
  .nota {font-size:.86rem;color:#6b6e72;}
</style>""", unsafe_allow_html=True)

plt.rcParams.update({
    "font.size": 10, "axes.grid": True, "grid.alpha": 0.25, "axes.edgecolor": "#c9c9c4",
    "axes.facecolor": "#ffffff", "figure.facecolor": "#fbfbf9", "axes.spines.top": False,
    "axes.spines.right": False, "axes.titleweight": "normal", "axes.titlesize": 10.5,
    "axes.titlecolor": "#2b2d2f", "axes.labelcolor": "#4a4d50", "xtick.color": "#6b6e72", "ytick.color": "#6b6e72",
})
C_REAL, C_BETZ, C_DISP, C_AUX, C_AIRE = "#2f5d62", "#b5543c", "#a3a6a9", "#5b7f5a", "#3a8fa3"

st.title("Simulador de generación eólica y conservación del momentum")

tab1, tab2, tab3, tab4 = st.tabs([
    "1 · Momentum: cómo el viento empuja el rotor",
    "2 · Turbinas reales frente al ideal de Betz",
    "3 · Giro del rotor en el tiempo (Euler y RK4)",
    "4 · Precisión de los métodos numéricos",
])

# =====================================================================
# 1. MOMENTUM (DISCO ACTUADOR)
# =====================================================================
with tab1:
    c1, c2 = st.columns([1, 2.6], gap="large")
    with c1:
        st.markdown("##### Condiciones")
        v1 = st.slider("Velocidad del viento antes del rotor, v₁ (m/s)", 1.0, 25.0, 12.0, 0.5)
        R1 = st.slider("Radio de las aspas, R (m)", 0.5, 150.0, 45.0, 0.5)
        rho1 = st.number_input("Densidad del aire, ρ (kg/m³)", 0.70, 1.40, 1.225, 0.005, format="%.3f",
                               help="1.225 kg/m³ = nivel del mar a 15 °C. Bogotá (≈ 2600 m) ≈ 0.91 kg/m³.")
        modo = st.radio("¿Cuánto frena el rotor al aire?",
                        ["Elegir el factor de inducción a", "Punto ideal de Betz (a = 1/3)",
                         "Calcular a desde un Cp conocido", "Calcular a desde un CT conocido"])
        if modo.startswith("Elegir"):
            a = st.slider("Factor de inducción axial, a (fracción de velocidad que pierde el aire al llegar)",
                          0.0, 0.5, 0.25, 0.005)
        elif modo.startswith("Punto"):
            a = 1 / 3
        elif "Cp" in modo:
            cp_in = st.number_input("Coeficiente de potencia conocido, Cp", 0.0, float(m.BETZ_CP), 0.45, 0.005)
            a = float(m.a_desde_cp(cp_in))
        else:
            ct_in = st.number_input("Coeficiente de empuje conocido, CT", 0.0, 0.96, 0.80, 0.01)
            a = float(m.a_desde_ct(ct_in))
        st.caption(f"Factor de inducción usado: a = {a:.3f}")
        if a > 0.4:
            st.warning("Con a > 0.4 la teoría simple deja de ser válida: la estela se vuelve turbulenta.")

    A1 = np.pi * R1**2
    d = m.disco_actuador(v1, a, rho1, A1)
    betz = m.disco_actuador(v1, 1 / 3, rho1, A1)
    F_max = 0.5 * rho1 * A1 * v1**2  # empuje con CT = 1 (a = 0.5)

    with c2:
        dibujo(g.escena_turbina(R1, v1, a, omega=None, F=d["F"], F_betz=betz["F"],
                                         titulo_extra="Las líneas de viento avanzan más despacio detrás del rotor (v₄ < v₁). "
                                                      "Las aspas crecen con R; la flecha roja es el empuje sobre el rotor."),
                        alto=300)
        st.markdown(g.fila_medidores([
            g.medidor("Potencia extraída", d["P"] / 1e3, d["Pv"] / 1e3, "kW", 1, betz["P"] / 1e3, "Betz",
                      f"de {d['Pv'] / 1e3:,.1f} kW disponibles"),
            g.medidor("Coeficiente Cp", d["Cp"], 0.7, "", 3, m.BETZ_CP, "0.593", "fracción aprovechada"),
            g.medidor("Empuje del viento F", d["F"] / 1e3, F_max / 1e3, "kN", 1, betz["F"] / 1e3, "Betz",
                      "= momentum perdido por segundo"),
            g.medidor("Flujo de masa de aire ṁ", d["m_dot"], rho1 * A1 * v1, "kg/s", 0, None, "",
                      "masa que cruza el rotor cada segundo"),
        ]), unsafe_allow_html=True)

    st.markdown("##### Verificación de la conservación")
    ver = pd.DataFrame({
        "Principio": ["Conservación de la masa", "Impulso y momentum", "Diferencia de presión",
                      "Potencia por trabajo", "Potencia por energía cinética"],
        "Fórmula": ["ṁ = ρ · A · v_rotor", "F = ṁ · (v₁ − v₄)", "F = ½ ρ A (v₁² − v₄²)",
                    "P = F · v_rotor", "P = ½ ṁ (v₁² − v₄²)"],
        "Resultado con el a elegido": [f"{d['m_dot']:,.1f} kg/s", f"{d['F']:,.1f} N",
                                       f"{0.5 * rho1 * A1 * (v1**2 - d['v_w']**2):,.1f} N",
                                       f"{d['P']:,.1f} W", f"{d['P_energia']:,.1f} W"],
        "Ideal de Betz (a = 1/3)": [f"{betz['m_dot']:,.1f} kg/s", f"{betz['F']:,.1f} N",
                                    f"{0.5 * rho1 * A1 * (v1**2 - betz['v_w']**2):,.1f} N",
                                    f"{betz['P']:,.1f} W", f"{betz['P_energia']:,.1f} W"],
    })
    st.dataframe(ver, hide_index=True, width="stretch")
    st.markdown('<p class="nota">Las dos formas de calcular el empuje y las dos formas de calcular la potencia '
                'dan lo mismo: el modelo conserva masa, momentum y energía.</p>', unsafe_allow_html=True)

    fig, ax = plt.subplots(1, 2, figsize=(11, 3.1))
    aa = np.linspace(0, 0.5, 200)
    ax[0].plot(aa, m.cp_de_a(aa), color=C_REAL, label="Cp = 4a(1−a)²")
    ax[0].plot(aa, m.ct_de_a(aa), "--", color=C_AUX, label="CT = 4a(1−a)")
    ax[0].plot(a, m.cp_de_a(a), "o", color=C_REAL); ax[0].plot(a, m.ct_de_a(a), "o", color=C_AUX)
    ax[0].axvline(1 / 3, color=C_BETZ, ls=":", lw=1); ax[0].text(0.338, 0.05, "a = 1/3", color=C_BETZ, fontsize=8)
    ax[0].set_xlabel("factor de inducción a"); ax[0].legend(fontsize=8, frameon=False)
    ax[0].set_title("Punto de operación del rotor")
    vv = np.linspace(1, 25, 100)
    ax[1].plot(vv, m.potencia_viento(rho1, A1, vv) / 1e3, color=C_DISP, label="disponible ½ρAv³")
    ax[1].plot(vv, m.BETZ_CP * m.potencia_viento(rho1, A1, vv) / 1e3, "--", color=C_BETZ, label="máximo de Betz")
    ax[1].plot(vv, m.cp_de_a(a) * m.potencia_viento(rho1, A1, vv) / 1e3, color=C_REAL, label="con el a elegido")
    ax[1].plot(v1, d["P"] / 1e3, "o", color=C_REAL)
    ax[1].set_xlabel("velocidad del viento v₁ (m/s)"); ax[1].set_ylabel("potencia (kW)")
    ax[1].legend(fontsize=8, frameon=False); ax[1].set_title("La potencia crece con el cubo del viento")
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# =====================================================================
# 2. TURBINAS REALES
# =====================================================================
with tab2:
    st.markdown("Datos de fabricante: **potencia** medida según la norma IEC 61400-12-1 (a ρ = 1.225 kg/m³) y "
                "**coeficiente de empuje** CT entregado por el fabricante. Con ellos se calcula el cambio de momentum "
                "real y se compara con el ideal de Betz.")
    c1, c2 = st.columns([1, 2.6], gap="large")
    with c1:
        st.markdown("##### Turbina y sitio")
        nombre = st.selectbox("Turbina", list(TURBINAS.keys()) + ["Artículo Visión Académica (datos no medidos)"])
        rho2 = st.number_input("Densidad del aire en el sitio, ρ (kg/m³)", 0.70, 1.40, 1.225, 0.005, format="%.3f",
                               key="rho2", help="Cambie la densidad para simular un sitio de altura.")

    if nombre in TURBINAS:
        T = TURBINAS[nombre]
        R2 = T["D"] / 2; A2 = np.pi * R2**2
        v_tab = np.array(T["v"]); P_ref = np.array(T["P_kW"]) * 1e3; CT_tab = np.array(T["CT"])
        P_real_tab = np.interp(m.ajuste_densidad(v_tab, rho2, RHO_REF), v_tab, P_ref)
        msk = v_tab >= 4
        v, P_real, CT = v_tab[msk], P_real_tab[msk], CT_tab[msk]
        Pv = m.potencia_viento(rho2, A2, v)
        Cp_real = P_real / Pv
        a_real = m.a_desde_ct(CT)
        dr = m.disco_actuador(v, a_real, rho2, A2)
        db = m.disco_actuador(v, 1 / 3, rho2, A2)
        F_real = CT * 0.5 * rho2 * A2 * v**2
        with c1:
            vsel = st.select_slider("Velocidad del viento a observar, v₁ (m/s)", options=[float(x) for x in v], value=8.0)
            i = int(np.where(v == vsel)[0][0])
            st.metric("Diámetro del rotor", f"{T['D']:.0f} m")
            st.metric("Mejor Cp de esta turbina", f"{Cp_real.max():.3f}",
                      f"{Cp_real.max() / m.BETZ_CP * 100:.0f} % del límite de Betz", delta_color="off")
            st.caption("Fuente: " + T["fuente"])
        with c2:
            dibujo(g.escena_turbina(R2, vsel, float(a_real[i]), omega=None, F=float(F_real[i]),
                                             F_betz=float(db["F"][i]),
                                             titulo_extra="Factor de inducción calculado desde el CT del fabricante. "
                                                          "El giro es ilustrativo (los datos no incluyen rpm)."),
                            alto=300)
            st.markdown(g.fila_medidores([
                g.medidor("Potencia real", P_real[i] / 1e3, Pv[i] / 1e3, "kW", 0, m.BETZ_CP * Pv[i] / 1e3, "Betz",
                          f"de {Pv[i] / 1e3:,.0f} kW disponibles"),
                g.medidor("Cp real", Cp_real[i], 0.7, "", 3, m.BETZ_CP, "0.593",
                          f"{Cp_real[i] / m.BETZ_CP * 100:.0f} % del ideal"),
                g.medidor("Empuje real", F_real[i] / 1e3, 0.5 * rho2 * A2 * vsel**2 / 1e3, "kN", 1, db["F"][i] / 1e3,
                          "Betz", f"ideal: {db['F'][i] / 1e3:,.1f} kN"),
                g.medidor("Velocidad en la estela v₄", dr["v_w"][i], vsel, "m/s", 2, vsel / 3, "Betz",
                          f"llega con {vsel:.0f} m/s"),
            ]), unsafe_allow_html=True)
            st.markdown(g.flujo_potencia([
                ("Potencia que trae el viento", Pv[i], C_DISP, "½ ρ A v₁³"),
                ("Máximo ideal (límite de Betz)", m.BETZ_CP * Pv[i], C_BETZ, "16/27 de la disponible"),
                ("Extraída según el momentum (F · v_rotor)", dr["P"][i], C_AIRE, "con el a real de la turbina"),
                ("Potencia eléctrica real", P_real[i], C_REAL,
                 "la diferencia con la fila anterior son pérdidas: arrastre, remolinos de punta, giro de la estela y generador"),
            ]), unsafe_allow_html=True)

        fig, ax = plt.subplots(1, 3, figsize=(12, 3.3))
        ax[0].plot(v, Pv / 1e3, color=C_DISP, label="disponible")
        ax[0].plot(v, m.BETZ_CP * Pv / 1e3, "--", color=C_BETZ, label="máximo de Betz")
        ax[0].plot(v, P_real / 1e3, "o-", ms=3.5, color=C_REAL, label="real")
        ax[0].axvline(vsel, color="#c9c9c4", lw=1)
        ax[0].set_ylim(0, 2.5 * P_real.max() / 1e3); ax[0].set_xlabel("viento v₁ (m/s)"); ax[0].set_ylabel("kW")
        ax[0].legend(fontsize=8, frameon=False); ax[0].set_title("Potencia")
        ax[1].axhline(m.BETZ_CP, ls="--", color=C_BETZ, lw=1, label="Cp de Betz")
        ax[1].axhline(m.BETZ_CT, ls=":", color=C_AUX, lw=1, label="CT de Betz")
        ax[1].plot(v, Cp_real, "o-", ms=3.5, color=C_REAL, label="Cp real")
        ax[1].plot(v, CT, "s-", ms=3.5, color=C_AUX, label="CT real")
        ax[1].axvline(vsel, color="#c9c9c4", lw=1)
        ax[1].set_xlabel("viento v₁ (m/s)"); ax[1].legend(fontsize=8, frameon=False); ax[1].set_title("Coeficientes")
        ax[2].plot(v, db["F"] / 1e3, "--", color=C_BETZ, label="ideal de Betz")
        ax[2].plot(v, F_real / 1e3, "o-", ms=3.5, color=C_REAL, label="real")
        ax[2].axvline(vsel, color="#c9c9c4", lw=1)
        ax[2].set_xlabel("viento v₁ (m/s)"); ax[2].set_ylabel("kN"); ax[2].legend(fontsize=8, frameon=False)
        ax[2].set_title("Empuje = momentum que pierde el aire por segundo")
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)

        df = pd.DataFrame({
            "Velocidad del viento v₁ (m/s)": v,
            "Potencia disponible del viento (kW)": Pv / 1e3,
            "Potencia máxima ideal, Betz (kW)": m.BETZ_CP * Pv / 1e3,
            "Potencia real de la turbina (kW)": P_real / 1e3,
            "Coeficiente de potencia real Cp": Cp_real,
            "Porcentaje del límite de Betz (%)": Cp_real / m.BETZ_CP * 100,
            "Coeficiente de empuje CT": CT,
            "Factor de inducción a": a_real,
            "Velocidad en el rotor (m/s)": dr["v_r"],
            "Velocidad en la estela v₄ (m/s)": dr["v_w"],
            "Flujo de masa de aire (kg/s)": dr["m_dot"],
            "Empuje real (kN)": F_real / 1e3,
            "Empuje ideal de Betz (kN)": db["F"] / 1e3,
            "Potencia según momentum F·v_rotor (kW)": dr["P"] / 1e3,
        })
        st.markdown("##### Tabla completa")
        st.dataframe(df.style.format(precision=3), hide_index=True, width="stretch")
        st.download_button("Descargar tabla (CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name=f"comparacion_{nombre.split()[1]}.csv")
    else:
        R2 = ARTICULO["R"]; A2 = np.pi * R2**2
        v = np.array(ARTICULO["v"]); P = np.array(ARTICULO["P_MW"]) * 1e6
        Pv = m.potencia_viento(rho2, A2, v); Cp_calc = P / Pv
        rho_nec = 2 * P / (np.array(ARTICULO["Cp_reportado"]) * A2 * v**3)
        a_min = m.a_desde_cp(Cp_calc)
        dmin = m.disco_actuador(v, a_min, rho2, A2); db = m.disco_actuador(v, 1 / 3, rho2, A2)
        df = pd.DataFrame({
            "Velocidad del viento v₁ (m/s)": v, "Velocidad angular ω (rad/s)": ARTICULO["omega"],
            "Razón de velocidad de punta λ = ωR/v": np.array(ARTICULO["omega"]) * R2 / v,
            "Potencia reportada (MW)": P / 1e6, "Cp reportado por el artículo": ARTICULO["Cp_reportado"],
            "Cp calculado = P / (½ρAv³)": Cp_calc, "Densidad que haría cuadrar el Cp (kg/m³)": rho_nec,
            "Factor de inducción a (desde Cp)": a_min, "Empuje mínimo (kN)": dmin["F"] / 1e3,
            "Empuje ideal de Betz (kN)": db["F"] / 1e3})
        with c2:
            st.warning("Esta tabla fue elaborada por los autores del artículo (no es una medición). Su Cp no es coherente "
                       "con la potencia y la velocidad: la densidad necesaria para que cuadre cambia en cada fila.")
        st.dataframe(df.style.format(precision=3), hide_index=True, width="stretch")

# =====================================================================
# 3. DINÁMICA DEL ROTOR
# =====================================================================
with st.sidebar:
    st.markdown("### Turbina de las pestañas 3 y 4")
    R = st.number_input("Radio de las aspas, R (m)", 0.2, 100.0, 2.0, 0.1)
    rho = st.number_input("Densidad del aire, ρ (kg/m³)", 0.70, 1.40, 1.225, 0.005, format="%.3f", key="rho3")
    cp_max = st.slider("Mejor coeficiente de potencia del rotor, Cp máx", 0.10, float(round(m.BETZ_CP, 3)), 0.45, 0.005)
    lam_opt = st.slider("Razón de punta óptima, λ* (velocidad de la punta / viento)", 3.0, 12.0, 7.0, 0.5)
    J = st.number_input("Momento de inercia del rotor, J (kg·m²)", 0.01, 1e8, 15.0, 1.0)
    b = st.number_input("Fricción en los rodamientos, b (N·m·s)", 0.0, 1e5, 0.05, 0.01)
    st.markdown("**Generador:** torque de frenado = T₀ + k_g · ω")
    T0 = st.number_input("Torque fijo del generador, T₀ (N·m)", 0.0, 1e7, 0.0, 1.0)
    auto_kg = st.checkbox("Ajustar k_g para trabajar en λ* con el viento de diseño", True)
    v_dis = st.number_input("Viento de diseño (m/s)", 1.0, 25.0, 10.0, 0.5)
    p = dict(R=R, rho=rho, cp_max=cp_max, lam_opt=lam_opt, J=J, b=b, T0=T0, kg=0.0, omega0=0.0)
    kg_auto = max(m.kg_optimo(p, v_dis), 0.0)
    kg = kg_auto if auto_kg else st.number_input("Constante del generador, k_g (N·m·s)", 0.0, 1e7,
                                                  float(round(kg_auto, 3)), 0.1)
    p["kg"] = kg
    st.caption(f"k_g = {kg:.4f} N·m·s")

with tab3:
    c1, c2 = st.columns([1, 2.6], gap="large")
    with c1:
        st.markdown("##### Viento y simulación")
        tipo = st.selectbox("Cómo cambia el viento", ["constante", "escalón", "ráfaga senoidal"])
        v0 = st.slider("Velocidad del viento inicial, v₀ (m/s)", 1.0, 25.0, 10.0, 0.5)
        dv = st.slider("Cambio de la velocidad del viento, Δv (m/s)", -8.0, 8.0, 3.0, 0.5, disabled=(tipo == "constante"))
        t_esc = st.slider("Instante del cambio brusco (s)", 0.0, 60.0, 15.0, 1.0, disabled=(tipo != "escalón"))
        periodo = st.slider("Duración de cada ráfaga (s)", 1.0, 60.0, 8.0, 1.0, disabled=(tipo != "ráfaga senoidal"))
        omega0 = st.number_input("Velocidad angular inicial del rotor, ω₀ (rad/s)", 0.0, 1000.0, 0.0, 1.0)
        t_fin = st.slider("Duración de la simulación (s)", 5.0, 120.0, 30.0, 1.0)
        h = st.select_slider("Paso de tiempo de los métodos, h (s)",
                             [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 4.0, 6.0], value=0.5)
        p["omega0"] = omega0

    viento = lambda t: m.perfil_viento(t, tipo, v0, dv, periodo, t_esc)
    f = lambda t, w: m.f_rotor(t, w, p, viento)
    tE, wE = nm.euler(f, 0.0, omega0, h, t_fin)
    tR, wR = nm.rk4(f, 0.0, omega0, h, t_fin)
    if tipo == "constante":
        t_ref = np.linspace(0, t_fin, 1000)
        w_ref, w_inf, tau = m.solucion_analitica(t_ref, p, v0)
        etiqueta_ref = "solución exacta"
        w_ref_E = m.solucion_analitica(tE, p, v0)[0]
    else:
        t_ref, w_ref = nm.rk4(f, 0.0, omega0, 1e-3, t_fin)
        etiqueta_ref = "referencia (RK4 con h = 0.001 s)"
        w_ref_E = np.interp(tE, t_ref, w_ref)
        alpha, gamma = m.coef_torque(rho, R, v0, cp_max, lam_opt); K = gamma + kg + b
        w_inf, tau = (alpha - T0) / K, J / K

    bal = m.balance_energia(tR, wR, p, viento)
    vv_t = viento(tR); lam_t = wR * R / np.maximum(vv_t, 1e-9)
    Pv_t = m.potencia_viento(rho, np.pi * R**2, vv_t)

    with c1:
        t_obs = st.slider("Instante que muestran el dibujo y los medidores (s)", 0.0, float(t_fin), float(min(t_fin, 20.0)), 0.5)
    j = int(np.argmin(np.abs(tR - t_obs)))
    w_j, v_j = float(wR[j]), float(vv_t[j])
    T_vto = float(m.torque_turbina(w_j, v_j, p)); T_gen = float(m.torque_carga(w_j, p))
    cp_j = max(float(m.cp_parabolico(w_j * R / v_j, cp_max, lam_opt)), 0.0)
    a_j = float(m.a_desde_cp(cp_j))
    A3 = np.pi * R**2
    dj = m.disco_actuador(v_j, a_j, rho, A3); bj = m.disco_actuador(v_j, 1 / 3, rho, A3)

    with c2:
        dibujo(g.escena_turbina(R, v_j, a_j, omega=w_j, F=dj["F"], F_betz=bj["F"],
                                         titulo_extra=f"Instante t = {tR[j]:.1f} s · el rotor gira con la velocidad angular "
                                                      f"calculada con RK4 · a estimado desde el Cp del rotor."),
                        alto=300)
        st.markdown(g.fila_medidores([
            g.medidor("Velocidad del rotor", w_j * 30 / np.pi, max(w_inf * 30 / np.pi * 1.3, 1), "rpm", 0,
                      w_inf * 30 / np.pi, "final", f"ω = {w_j:.2f} rad/s"),
            g.medidor("Potencia eléctrica", bal["P_gen"][j] / 1e3, max(Pv_t.max() / 1e3, 1e-6), "kW", 2,
                      m.BETZ_CP * Pv_t[j] / 1e3, "Betz", f"viento: {Pv_t[j] / 1e3:,.2f} kW"),
            g.medidor("Coeficiente Cp", cp_j, 0.7, "", 3, m.BETZ_CP, "0.593", f"λ = {lam_t[j]:.2f}"),
            g.medidor("Torque del viento", T_vto, max(m.coef_torque(rho, R, max(vv_t.max(), 0.1), cp_max, lam_opt)[0], 1e-6),
                      "N·m", 1, None, "", f"generador: {T_gen:,.1f} N·m"),
        ]), unsafe_allow_html=True)
        st.markdown(g.cadena_conversion(v_j, w_j, T_vto, T_gen, Pv_t[j], bal["P_aero"][j], bal["P_gen"][j],
                                        bal["P_fric"][j]), unsafe_allow_html=True)

    k = st.columns(4)
    k[0].metric("Velocidad final del rotor ω∞ (con v₀)", f"{w_inf:.2f} rad/s", f"{w_inf * 30 / np.pi:.0f} rpm",
                delta_color="off")
    k[1].metric("Constante de tiempo τ = J / K", f"{tau:.3f} s")
    k[2].metric("Euler es estable si el paso h <", f"{2 * tau:.3f} s")
    k[3].metric("Razón de punta final λ", f"{w_inf * R / v0:.2f}")
    if h >= 2 * tau:
        st.error(f"El paso h = {h} s es mayor que 2τ = {2 * tau:.2f} s: Euler se vuelve inestable (oscila y diverge).")
    if w_inf <= 0:
        st.warning("El torque del viento no vence al generador: la turbina no arranca.")
    Ea_E, Er_E = nm.errores(w_ref_E, wE); Ea_R, Er_R = nm.errores(w_ref_E, wR)
    st.markdown(f"**Error absoluto máximo** frente a la {etiqueta_ref}: Euler = `{Ea_E.max():.3e}` rad/s · "
                f"RK4 = `{Ea_R.max():.3e}` rad/s")

    fig, ax = plt.subplots(2, 2, figsize=(12, 6.2))
    ax[0, 0].plot(t_ref, w_ref, color="#2b2d2f", lw=1.6, label=etiqueta_ref)
    ax[0, 0].plot(tE, wE, "s--", ms=3, color=C_BETZ, label=f"Euler (h = {h} s)")
    ax[0, 0].plot(tR, wR, "o:", ms=3, color=C_REAL, label=f"RK4 (h = {h} s)")
    ax[0, 0].axvline(tR[j], color="#c9c9c4", lw=1)
    ax[0, 0].set_ylabel("velocidad angular ω (rad/s)"); ax[0, 0].legend(fontsize=8, frameon=False)
    ax[0, 0].set_title("Velocidad angular del rotor")
    if h >= 2 * tau:
        ax[0, 0].set_ylim(min(w_ref.min(), 0) - 5, w_ref.max() * 1.5 + 5)
    ax[0, 1].plot(tR, Pv_t / 1e3, color=C_DISP, label="del viento")
    ax[0, 1].plot(tR, m.BETZ_CP * Pv_t / 1e3, "--", color=C_BETZ, label="máximo de Betz")
    ax[0, 1].plot(tR, bal["P_aero"] / 1e3, color=C_AIRE, label="captada por el rotor")
    ax[0, 1].plot(tR, bal["P_gen"] / 1e3, color=C_REAL, label="eléctrica")
    ax[0, 1].axvline(tR[j], color="#c9c9c4", lw=1)
    ax[0, 1].set_ylabel("potencia (kW)"); ax[0, 1].legend(fontsize=8, frameon=False); ax[0, 1].set_title("Potencias")
    ax[1, 0].plot(tR, lam_t, color=C_REAL, label="razón de punta λ(t)")
    ax[1, 0].axhline(lam_opt, ls=":", color=C_BETZ, label="λ* óptima")
    ax2 = ax[1, 0].twinx(); ax2.plot(tR, vv_t, color=C_AIRE, alpha=.7); ax2.set_ylabel("viento v (m/s)", color=C_AIRE)
    ax2.grid(False); ax2.spines["top"].set_visible(False)
    ax[1, 0].set_xlabel("tiempo t (s)"); ax[1, 0].set_ylabel("λ"); ax[1, 0].legend(fontsize=8, frameon=False, loc="lower right")
    ax[1, 0].set_title("Razón de velocidad de punta y viento")
    ax[1, 1].plot(tR, bal["E_aero"] / 1e3, color=C_AIRE, label="energía que entrega el viento")
    ax[1, 1].plot(tR, (bal["E_gen"] + bal["E_fric"] + bal["dEk"]) / 1e3, "--", color=C_BETZ,
                  label="eléctrica + fricción + cinética del rotor")
    ax[1, 1].plot(tR, bal["E_gen"] / 1e3, color=C_REAL, label="energía eléctrica")
    ax[1, 1].set_xlabel("tiempo t (s)"); ax[1, 1].set_ylabel("energía (kJ)"); ax[1, 1].legend(fontsize=8, frameon=False)
    ax[1, 1].set_title("Conservación de la energía")
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
    res = (bal["E_aero"][-1] - bal["E_gen"][-1] - bal["E_fric"][-1] - bal["dEk"][-1]) / max(abs(bal["E_aero"][-1]), 1e-12)
    st.markdown(
        f"**Balance de energía (RK4):** viento → rotor = {bal['E_aero'][-1] / 1e3:,.2f} kJ · eléctrica = "
        f"{bal['E_gen'][-1] / 1e3:,.2f} kJ · fricción = {bal['E_fric'][-1] / 1e3:,.2f} kJ · aumento de energía cinética "
        f"= {bal['dEk'][-1] / 1e3:,.2f} kJ · diferencia relativa = {res:.1e}  \n"
        f"**Eficiencia global** (energía eléctrica / energía del viento) = "
        f"{bal['E_gen'][-1] / max(np.trapezoid(Pv_t, tR), 1e-12) * 100:.1f} % (límite de Betz: 59.3 %)")

    st.markdown("##### Comparación de escenarios de viento (estado final, solución exacta)")
    esc = st.multiselect("Velocidades del viento a comparar (m/s)", [3, 4, 5, 6, 7, 8, 10, 12, 15, 18, 20], default=[5, 10, 15])
    filas = []
    for ve in sorted(esc):
        _, wi, ta = m.solucion_analitica(np.array([0.0]), p, ve)
        wi = max(wi, 0.0); lam_e = wi * R / ve
        cp_e = max(m.cp_parabolico(lam_e, cp_max, lam_opt), 0.0)
        Pv_e = m.potencia_viento(rho, np.pi * R**2, ve)
        Pg = m.torque_carga(wi, p) * wi
        filas.append({"Velocidad del viento (m/s)": ve, "Potencia disponible (kW)": Pv_e / 1e3,
                      "Potencia máxima de Betz (kW)": m.BETZ_CP * Pv_e / 1e3,
                      "Velocidad final del rotor (rad/s)": wi, "Velocidad final (rpm)": wi * 30 / np.pi,
                      "Constante de tiempo τ (s)": ta, "Razón de punta λ": lam_e, "Coeficiente de potencia Cp": cp_e,
                      "Potencia eléctrica (kW)": Pg / 1e3, "Eficiencia global (%)": Pg / Pv_e * 100})
    if filas:
        st.dataframe(pd.DataFrame(filas).style.format(precision=3), hide_index=True, width="stretch")
        fig, ax = plt.subplots(figsize=(12, 3.0))
        tt = np.linspace(0, t_fin, 400)
        tonos = ["#9fb7b9", "#6f9497", "#2f5d62", "#24474b", "#a3a6a9", "#b5543c", "#5b7f5a"]
        for n, ve in enumerate(sorted(esc)):
            ax.plot(tt, m.solucion_analitica(tt, p, ve)[0], color=tonos[n % len(tonos)], label=f"v = {ve} m/s")
        ax.set_xlabel("tiempo t (s)"); ax.set_ylabel("ω (rad/s)"); ax.legend(fontsize=8, ncol=6, frameon=False)
        ax.set_title("Arranque del rotor con distintos vientos")
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# =====================================================================
# 4. CONVERGENCIA
# =====================================================================
with tab4:
    st.markdown("Se usa el viento inicial v₀ de la pestaña 3 constante. El **valor real** es la solución exacta "
                "ω(t) = ω∞ + (ω₀ − ω∞)·e^(−t/τ).")
    t_eval = st.slider("Instante en que se miden los errores (s)", 0.5, 30.0, 4.0, 0.5)
    pasos = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
    fc = lambda t, w: m.f_rotor(t, w, p, lambda tt: v0)
    y_real = float(m.solucion_analitica(t_eval, p, v0)[0])
    filas, ordenes = nm.estudio_convergencia(fc, 0.0, p["omega0"], t_eval, pasos, y_real)
    dfc = pd.DataFrame([{"Paso h (s)": h_, "ω con Euler (rad/s)": ye, "Error absoluto Euler": eE,
                         "Error relativo Euler (%)": eE / abs(y_real) * 100, "ω con RK4 (rad/s)": yr,
                         "Error absoluto RK4": eR, "Error relativo RK4 (%)": eR / abs(y_real) * 100}
                        for h_, ye, eE, yr, eR in filas])
    dfc["Orden observado Euler"] = [np.nan] + [o[0] for o in ordenes]
    dfc["Orden observado RK4"] = [np.nan] + [o[1] for o in ordenes]
    k = st.columns(3)
    k[0].metric(f"Valor real de ω en t = {t_eval} s", f"{y_real:.6f} rad/s")
    k[1].metric("Orden de Euler (teoría: 1)", f"{np.nanmean(dfc['Orden observado Euler'].values[-3:]):.2f}")
    k[2].metric("Orden de RK4 (teoría: 4)", f"{np.nanmean(dfc['Orden observado RK4'].values[1:4]):.2f}")
    st.dataframe(dfc.style.format({"Paso h (s)": "{:.5f}", "ω con Euler (rad/s)": "{:.6f}", "ω con RK4 (rad/s)": "{:.9f}",
                                   "Error absoluto Euler": "{:.3e}", "Error absoluto RK4": "{:.3e}",
                                   "Error relativo Euler (%)": "{:.3e}", "Error relativo RK4 (%)": "{:.3e}",
                                   "Orden observado Euler": "{:.3f}", "Orden observado RK4": "{:.3f}"}),
                 hide_index=True, width="stretch")
    st.markdown('<p class="nota">Orden observado = log₂[E(h) / E(h/2)]: cada vez que el paso se divide por 2, '
                'el error de Euler se divide por ≈ 2 y el de RK4 por ≈ 16.</p>', unsafe_allow_html=True)
    c1, _ = st.columns([1, 1])
    with c1:
        fig, ax = plt.subplots(figsize=(5.6, 3.8))
        hh = dfc["Paso h (s)"].values
        ax.loglog(hh, dfc["Error absoluto Euler"], "s-", color=C_BETZ, label="Euler")
        ax.loglog(hh, np.maximum(dfc["Error absoluto RK4"], 1e-16), "o-", color=C_REAL, label="RK4")
        ax.loglog(hh, dfc["Error absoluto Euler"].iloc[0] * hh, ":", color="#8a8d91", lw=1, label="pendiente 1")
        ax.loglog(hh, dfc["Error absoluto RK4"].iloc[0] * hh**4, "--", color="#8a8d91", lw=1, label="pendiente 4")
        ax.set_xlabel("paso h (s)"); ax.set_ylabel("error absoluto (rad/s)"); ax.legend(fontsize=8, frameon=False)
        ax.set_title("Convergencia de los métodos")
        fig.tight_layout(); st.pyplot(fig); plt.close(fig)
