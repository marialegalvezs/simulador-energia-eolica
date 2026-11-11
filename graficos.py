"""
Dibujos dinámicos del simulador (SVG + CSS): escena de la turbina, medidores,
flujo de potencia y cadena de conversión. Todo se genera a partir de las
variables simuladas, de modo que el dibujo cambia cuando cambian las entradas.
"""
import math
import numpy as np

# Paleta neutra
TINTA = "#2b2d2f"
GRIS = "#8a8d91"
GRIS_CLARO = "#d9d9d4"
FONDO = "#fbfbf9"
AIRE = "#3a8fa3"        # líneas de viento (azul petróleo suave)
ACENTO = "#2f5d62"      # valores principales
BETZ = "#b5543c"        # marca del límite ideal (terracota)
VERDE = "#5b7f5a"

def _plano(html):
    """Quita la sangría para que Markdown no lo trate como bloque de código."""
    return " ".join(l.strip() for l in html.splitlines() if l.strip())


FUENTE = "font-family:'Inter','Segoe UI',Helvetica,Arial,sans-serif"


def _escala_radio(R, minimo=0.2, maximo=150.0):
    """Escala logarítmica 0..1 para dibujar radios de 0.2 m a 150 m."""
    R = min(max(R, minimo), maximo)
    return (math.log(R) - math.log(minimo)) / (math.log(maximo) - math.log(minimo))


# -------------------------------------------------------------- escena
def escena_turbina(R, v1, a, omega=None, F=None, F_betz=None, titulo_extra=""):
    """
    Vista lateral (tubo de corriente con conservación de la masa) + vista frontal
    (rotor que gira con la velocidad angular simulada).
    """
    a_d = min(max(a, 0.0), 0.45)
    vd = v1 * (1 - a_d)
    v4 = v1 * (1 - 2 * a_d)
    s = _escala_radio(R)

    # ---------- vista lateral
    W, H, cy, x0 = 560, 320, 135, 250
    Rpx = 20 + 46 * s
    xs = np.linspace(-230, 300, 120)
    Rf = 1.3 * Rpx  # radio de referencia para el perfil u(x)
    u = 1 - a_d * (1 + xs / np.sqrt(xs**2 + Rf**2))       # u/v1 sobre el eje
    r_tubo = np.minimum(Rpx * np.sqrt((1 - a_d) / np.maximum(u, 0.05)), 118)

    def linea(frac, desde, hasta):
        m = (xs >= desde) & (xs <= hasta)
        pts = " ".join(f"{x0 + x:.1f},{cy - frac * r:.1f}" for x, r in zip(xs[m], r_tubo[m]))
        return pts

    dur_antes = max(0.25, 6.0 / max(v1, 0.3))
    dur_despues = max(0.25, 6.0 / max(v4, 0.3))
    fracs = [-0.85, -0.5, -0.17, 0.17, 0.5, 0.85]
    lineas = ""
    for f in fracs:
        lineas += (f'<polyline points="{linea(f, -230, 0)}" class="aire" '
                   f'style="animation-duration:{dur_antes:.2f}s"/>')
        lineas += (f'<polyline points="{linea(f, 0, 300)}" class="aire" '
                   f'style="animation-duration:{dur_despues:.2f}s"/>')
    borde_sup = " ".join(f"{x0 + x:.1f},{cy - r:.1f}" for x, r in zip(xs, r_tubo))
    borde_inf = " ".join(f"{x0 + x:.1f},{cy + r:.1f}" for x, r in zip(xs, r_tubo))

    def flecha(x, y, largo, color, grosor=2.2):
        largo = max(largo, 6)
        return (f'<line x1="{x}" y1="{y}" x2="{x + largo}" y2="{y}" stroke="{color}" stroke-width="{grosor}"/>'
                f'<polygon points="{x + largo},{y - 5} {x + largo + 9},{y} {x + largo},{y + 5}" fill="{color}"/>')

    k = 70 / 25.0  # px por m/s
    yb = H - 22
    flechas = (flecha(x0 - 225, yb, v1 * k, TINTA) +
               flecha(x0 - vd * k / 2 - 4, yb, vd * k, TINTA) +
               flecha(x0 + 200, yb, v4 * k, TINTA))
    etiquetas = (
        f'<text x="{x0 - 225}" y="{yb - 10}" class="et">antes: v₁ = {v1:.1f} m/s</text>'
        f'<text x="{x0}" y="{yb - 10}" class="et" text-anchor="middle">en el rotor: {vd:.1f} m/s</text>'
        f'<text x="{x0 + 200}" y="{yb - 10}" class="et">estela: v₄ = {v4:.1f} m/s</text>'
        f'<line x1="8" y1="{yb - 28}" x2="{W - 8}" y2="{yb - 28}" stroke="#eeeeea"/>'
        f'<text x="{x0 - 215}" y="{cy - r_tubo[0] - 6:.0f}" class="et2">A₁ (entrada)</text>'
        f'<text x="{x0 + 8}" y="{cy - Rpx - 6:.0f}" class="et2">A (rotor)</text>'
        f'<text x="{x0 + 200}" y="{max(cy - r_tubo[-1] - 6, 30):.0f}" class="et2">A₄ (estela)</text>')
    empuje = ""
    if F is not None and F_betz:
        L = 18 + 60 * min(F / F_betz, 1.2)
        empuje = (f'<line x1="{x0 + 14}" y1="{cy + 22}" x2="{x0 + 14 + L}" y2="{cy + 22}" stroke="{BETZ}" stroke-width="3"/>'
                  f'<polygon points="{x0 + 14 + L},{cy + 16} {x0 + 26 + L},{cy + 22} {x0 + 14 + L},{cy + 28}" fill="{BETZ}"/>'
                  f'<text x="{x0 + 16}" y="{cy + 42}" class="et" fill="{BETZ}">empuje F</text>')
    torre = (f'<rect x="{x0 - 3}" y="{cy}" width="6" height="{H - cy - 50}" fill="#c9cac6"/>'
             f'<ellipse cx="{x0 + 14}" cy="{cy}" rx="22" ry="9" fill="#e9e9e5" stroke="{GRIS}" stroke-width="1"/>'
             f'<line x1="{x0}" y1="{cy - Rpx}" x2="{x0}" y2="{cy + Rpx}" stroke="{TINTA}" stroke-width="5" stroke-linecap="round"/>'
             f'<circle cx="{x0}" cy="{cy}" r="6" fill="{TINTA}"/>')
    lateral = f"""
    <svg viewBox="0 0 {W} {H}" width="100%" style="max-width:{W}px">
      <polyline points="{borde_sup}" fill="none" stroke="{GRIS}" stroke-width="1.2" stroke-dasharray="4 4"/>
      <polyline points="{borde_inf}" fill="none" stroke="{GRIS}" stroke-width="1.2" stroke-dasharray="4 4"/>
      {lineas}{torre}{flechas}{empuje}{etiquetas}
      <text x="8" y="18" class="tit">Vista lateral · el aire se frena y el tubo se ensancha</text>
    </svg>"""

    # ---------- vista frontal
    W2, H2 = 300, 300
    cx, cyf = 150, 128
    L = 40 + 82 * s
    if omega is None:
        periodo, nota = 4.0, "giro ilustrativo"
    else:
        periodo = 2 * math.pi / max(abs(omega), 1e-3)
        nota = f"{omega:.2f} rad/s · {omega * 30 / math.pi:.0f} rpm"
        periodo = min(max(periodo, 0.45), 30.0)
    parado = omega is not None and abs(omega) < 1e-3
    aspa = (f'<path d="M -5 -8 C -9 -{L * 0.35:.0f}, -6 -{L * 0.8:.0f}, -1.5 -{L:.0f} '
            f'L 1.5 -{L:.0f} C 6 -{L * 0.8:.0f}, 9 -{L * 0.35:.0f}, 5 -8 Z" fill="#f2f2ef" stroke="{GRIS}" stroke-width="1"/>')
    rotor = "".join(f'<g transform="rotate({ang})">{aspa}</g>' for ang in (0, 120, 240))
    anim = "" if parado else f"animation: giro {periodo:.2f}s linear infinite;"
    frontal = f"""
    <svg viewBox="0 0 {W2} {H2}" width="100%" style="max-width:{W2}px">
      <circle cx="{cx}" cy="{cyf}" r="{L + 4:.0f}" fill="none" stroke="{GRIS_CLARO}" stroke-dasharray="3 5"/>
      <path d="M {cx - 5} {cyf + 6} L {cx - 9} {H2 - 22} L {cx + 9} {H2 - 22} L {cx + 5} {cyf + 6} Z" fill="#dcdcd8"/>
      <g transform="translate({cx},{cyf})"><g style="{anim} transform-origin: 0 0;">{rotor}</g>
      <circle r="9" fill="#e9e9e5" stroke="{GRIS}"/></g>
      <line x1="{cx}" y1="{cyf}" x2="{cx + L:.0f}" y2="{cyf}" stroke="{BETZ}" stroke-width="1" stroke-dasharray="2 3"/>
      <text x="{cx + L / 2:.0f}" y="{cyf - 5}" class="et" fill="{BETZ}" text-anchor="middle">R = {R:g} m</text>
      <text x="{cx}" y="{H2 - 6}" class="et2" text-anchor="middle">{nota}</text>
      <text x="8" y="18" class="tit">Vista frontal · rotor</text>
    </svg>"""

    return f"""
    <html><head><style>
      body {{ margin:0; background:{FONDO}; {FUENTE}; }}
      .fila {{ display:flex; gap:14px; align-items:flex-start; justify-content:space-between; }}
      .panel {{ background:#ffffff; border:1px solid #e6e6e1; border-radius:14px; padding:6px; }}
      .aire {{ fill:none; stroke:{AIRE}; stroke-width:1.8; stroke-dasharray:7 9; opacity:.85;
               animation-name: fluye; animation-timing-function: linear; animation-iteration-count: infinite; }}
      @keyframes fluye {{ from {{ stroke-dashoffset: 32; }} to {{ stroke-dashoffset: 0; }} }}
      @keyframes giro {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
      .et {{ font-size:12px; fill:{TINTA}; }} .et2 {{ font-size:11px; fill:{GRIS}; }}
      .tit {{ font-size:12px; fill:{GRIS}; letter-spacing:.3px; }}
    </style></head><body>
      <div class="fila"><div class="panel" style="flex:2">{lateral}</div>
      <div class="panel" style="flex:1">{frontal}</div></div>
      <div style="font-size:11px;color:{GRIS};margin-top:4px">{titulo_extra}</div>
    </body></html>"""


# ------------------------------------------------------------ medidores
def medidor(titulo, valor, maximo, unidad, decimales=1, marca=None, marca_txt="", subtitulo=""):
    """Medidor semicircular (SVG). 'marca' dibuja una línea de referencia (p. ej., Betz)."""
    maximo = max(maximo, 1e-12)
    f = min(max(valor / maximo, 0.0), 1.0)
    cx, cy, r = 100, 108, 72

    def punto(fr, rr=r):
        th = math.pi * (1 - fr)
        return cx + rr * math.cos(th), cy - rr * math.sin(th)

    x0, y0 = punto(0); x1, y1 = punto(f); xe, ye = punto(1)
    arco_fondo = f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 0 1 {xe:.1f} {ye:.1f}" stroke="#ecece8" stroke-width="13" fill="none" stroke-linecap="round"/>'
    arco_val = (f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 0 1 {x1:.1f} {y1:.1f}" stroke="{ACENTO}" stroke-width="13" '
                f'fill="none" stroke-linecap="round"/>' if f > 0.002 else "")
    ticks = ""
    for i in range(11):
        xa, ya = punto(i / 10, r + 10); xb, yb = punto(i / 10, r + 15 if i % 5 == 0 else r + 12)
        ticks += f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#c7c7c2" stroke-width="1"/>'
    m = ""
    if marca is not None and 0 < marca / maximo <= 1:
        fm = marca / maximo
        xa, ya = punto(fm, r - 11); xb, yb = punto(fm, r + 12); xt, yt = punto(fm, r + 24)
        m = (f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="{BETZ}" stroke-width="2.4"/>'
             f'<text x="{xt:.1f}" y="{yt:.1f}" font-size="9.5" fill="{BETZ}" text-anchor="middle">{marca_txt}</text>')
    xa, ya = punto(f, r - 22)
    aguja = (f'<line x1="{cx}" y1="{cy}" x2="{xa:.1f}" y2="{ya:.1f}" stroke="{TINTA}" stroke-width="2.2" stroke-linecap="round"/>'
             f'<circle cx="{cx}" cy="{cy}" r="4.5" fill="{TINTA}"/>')
    txt = f"{valor:,.{decimales}f}".replace(",", " ")
    return _plano(f"""
    <div style="background:#fff;border:1px solid #e6e6e1;border-radius:14px;padding:8px 6px 6px;text-align:center;{FUENTE}">
      <div style="font-size:12.5px;color:{GRIS};letter-spacing:.3px">{titulo}</div>
      <svg viewBox="0 0 200 140" width="100%" style="max-width:220px">
        {ticks}{arco_fondo}{arco_val}{m}{aguja}
        <text x="100" y="135" font-size="19" fill="{TINTA}" text-anchor="middle" font-weight="600">{txt}
          <tspan font-size="11" fill="{GRIS}" font-weight="400"> {unidad}</tspan></text>
      </svg>
      <div style="font-size:11px;color:{GRIS};min-height:14px">{subtitulo}</div>
    </div>""")


def fila_medidores(lista):
    celdas = "".join(f'<div style="flex:1;min-width:150px">{m}</div>' for m in lista)
    return _plano(f'<div style="display:flex;gap:10px;flex-wrap:wrap">{celdas}</div>')


# ------------------------------------------------------- flujo de potencia


def flujo_potencia(etapas):
    """etapas: lista de (nombre, potencia_W, color, comentario). La primera es el 100 %."""
    total = max(etapas[0][1], 1e-12)
    filas = ""
    for nombre, P, color, com in etapas:
        pct = 100 * P / total
        filas += f"""
        <div style="display:flex;align-items:center;gap:10px;margin:5px 0">
          <div style="width:210px;font-size:12.5px;color:{TINTA}">{nombre}</div>
          <div style="flex:1;background:#f0f0ec;border-radius:7px;height:18px;position:relative">
            <div style="width:{max(min(pct, 100), 0):.2f}%;background:{color};height:18px;border-radius:7px"></div></div>
          <div style="width:150px;font-size:12.5px;color:{TINTA};text-align:right">
            {P / 1e3:,.2f} kW · <b>{pct:.1f} %</b></div>
        </div>
        <div style="margin:-3px 0 4px 220px;font-size:10.5px;color:{GRIS}">{com}</div>"""
    return _plano((f'<div style="background:#fff;border:1px solid #e6e6e1;border-radius:14px;padding:10px 14px;{FUENTE}">'
            f'<div style="font-size:12.5px;color:{GRIS};margin-bottom:4px">¿A dónde va la potencia del viento?</div>{filas}</div>'))


# ---------------------------------------------------- cadena de conversión


def cadena_conversion(v, omega, T_viento, T_gen, P_viento, P_aero, P_gen, P_fric):
    """Diagrama de bloques viento → rotor → eje → generador → red, con valores actuales."""
    def caja(x, titulo, l1, l2, icono):
        return f"""
        <g transform="translate({x},30)">
          <rect width="150" height="96" rx="12" fill="#fff" stroke="#dcdcd6"/>
          <text x="75" y="22" text-anchor="middle" font-size="12.5" fill="{GRIS}">{titulo}</text>
          <text x="75" y="52" text-anchor="middle" font-size="22" fill="#2f5d62">{icono}</text>
          <text x="75" y="72" text-anchor="middle" font-size="11.5" fill="{TINTA}">{l1}</text>
          <text x="75" y="88" text-anchor="middle" font-size="11.5" fill="{TINTA}">{l2}</text>
        </g>"""

    def flecha(x, txt):
        return (f'<line x1="{x}" y1="78" x2="{x + 34}" y2="78" stroke="{GRIS}" stroke-width="2"/>'
                f'<polygon points="{x + 34},73 {x + 42},78 {x + 34},83" fill="{GRIS}"/>'
                f'<text x="{x + 21}" y="66" text-anchor="middle" font-size="8.5" fill="{AIRE}">{txt}</text>')

    x = [0, 196, 392, 588, 784]
    return _plano(f"""
    <div style="background:#fff;border:1px solid #e6e6e1;border-radius:14px;padding:8px;{FUENTE}">
    <div style="font-size:12.5px;color:{GRIS};padding-left:6px">Cadena de conversión en el instante elegido</div>
    <svg viewBox="0 0 940 140" width="100%">
      {caja(x[0], "Viento", f"v = {v:.1f} m/s", f"{P_viento / 1e3:,.2f} kW", "≋")}
      {flecha(154, "momentum")}
      {caja(x[1], "Rotor (aspas)", f"T viento = {T_viento:,.1f} N·m", f"{P_aero / 1e3:,.2f} kW", "✢")}
      {flecha(350, "torque")}
      {caja(x[2], "Eje y rodamientos", f"ω = {omega:.2f} rad/s", f"fricción {P_fric / 1e3:,.3f} kW", "◎")}
      {flecha(546, "giro")}
      {caja(x[3], "Generador", f"T generador = {T_gen:,.1f} N·m", f"{P_gen / 1e3:,.2f} kW", "ϟ")}
      {flecha(742, "electricidad")}
      {caja(x[4], "Red eléctrica", "potencia entregada", f"{P_gen / 1e3:,.2f} kW", "⌂")}
    </svg></div>""")

