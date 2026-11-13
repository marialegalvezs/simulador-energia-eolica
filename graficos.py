"""
Dibujo animado del simulador: la situación física (tubo de corriente y rotor que gira)
sincronizada con la evolución numérica (gráficas de ω(t) y de la potencia).

Todo se dibuja en el navegador (HTML + JavaScript) a partir de los resultados que
calcula Python; así la animación es fluida y no hay que recalcular nada al reproducir.
"""
import json
import numpy as np


def _lista(x, dec=5):
    return [round(float(v), dec) for v in np.asarray(x, dtype=float)]


def escena(t, w, est, t_eu, w_eu, t_rk, w_rk, R, R_max, h):
    datos = dict(
        t=_lista(t, 4), w=_lista(w), v=_lista(est["v"], 3), lam=_lista(est["lam"], 3),
        cp=_lista(est["cp"], 4), a=_lista(est["a"], 4), vd=_lista(est["vd"], 3),
        v4=_lista(est["v4"], 3), F=_lista(est["F"], 2), Fb=_lista(est["F_betz"], 2),
        Pv=_lista(est["P_viento"], 1), Pb=_lista(est["P_betz"], 1),
        Pa=_lista(est["P_aero"], 1), Pg=_lista(est["P_gen"], 1),
        teu=_lista(t_eu, 4), weu=_lista(w_eu), trk=_lista(t_rk, 4), wrk=_lista(w_rk),
        R=float(R), Rmax=float(R_max), h=float(h),
    )
    return _PLANTILLA.replace("__DATOS__", json.dumps(datos))


_PLANTILLA = r"""
<!doctype html><html><head><meta charset="utf-8">
<style>
  :root{--tinta:#2b2d2f;--suave:#6b6e72;--linea:#e3e3de;--fondo:#ffffff;--aire:#3a8fa3;
        --exacta:#2b2d2f;--euler:#c0603f;--rk4:#3a6ea5;--gen:#2f5d62;--betz:#b5543c}
  body{margin:0;font-family:"Source Sans Pro",system-ui,sans-serif;color:var(--tinta);background:#fbfbf9}
  .caja{background:var(--fondo);border:1px solid var(--linea);border-radius:14px;padding:10px 12px;margin-bottom:10px}
  .tit{font-size:14px;font-weight:600;margin:0 0 4px}
  .sub{font-size:12.5px;color:var(--suave);margin:0 0 6px}
  canvas{width:100%;display:block}
  .controles{display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-size:14px}
  button{font:inherit;border:1px solid #c9c9c4;background:#f1f1ed;border-radius:8px;padding:5px 12px;cursor:pointer}
  button.prim{background:#2f5d62;color:#fff;border-color:#2f5d62}
  input[type=range]{flex:1;min-width:160px;accent-color:#2f5d62}
  select{font:inherit;border-radius:6px;padding:3px}
  .fila{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  .datos{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:8px}
  .dato{background:#f6f6f3;border-radius:10px;padding:6px 8px}
  .dato b{display:block;font-size:17px;font-weight:600}
  .dato span{font-size:11.5px;color:var(--suave)}
  .estado{font-size:13.5px;margin-top:8px;padding:6px 10px;border-radius:8px;background:#eef4f3}
  .ley{font-size:12px;color:var(--suave);display:flex;gap:14px;flex-wrap:wrap;margin-top:2px}
  .ley i{display:inline-block;width:18px;height:3px;vertical-align:middle;margin-right:4px}
  @media (max-width:820px){.fila{grid-template-columns:1fr}.datos{grid-template-columns:repeat(3,1fr)}}
</style></head><body>

<div class="caja">
  <p class="tit">1. La situación física</p>
  <p class="sub">Izquierda: el aire (puntos azules) llega con v₁, se frena al pasar por el rotor y sale más lento con v₄;
  por eso el tubo de aire se ensancha. Derecha: el rotor visto de frente gira con la ω calculada.</p>
  <canvas id="escena" height="330"></canvas>
  <div class="controles" style="margin-top:6px">
    <button id="play" class="prim">▶ Reproducir</button>
    <button id="reini">↺ Desde t = 0</button>
    <span>t =</span><input id="barra" type="range" min="0" max="1000" value="0">
    <span id="treloj" style="min-width:64px;font-weight:600">0.0 s</span>
    <span>velocidad</span>
    <select id="vel"><option value="1">×1 (tiempo real)</option><option value="2" selected>×2</option><option value="5">×5</option></select>
  </div>
  <div class="datos">
    <div class="dato"><span>Viento v</span><b id="d_v">–</b></div>
    <div class="dato"><span>Velocidad angular ω</span><b id="d_w">–</b></div>
    <div class="dato"><span>Razón de punta λ</span><b id="d_l">–</b></div>
    <div class="dato"><span>Coef. de potencia Cp</span><b id="d_cp">–</b></div>
    <div class="dato"><span>Empuje sobre el rotor F</span><b id="d_F">–</b></div>
    <div class="dato"><span>Potencia del generador</span><b id="d_P">–</b></div>
  </div>
  <div class="estado" id="estado">–</div>
</div>

<div class="fila">
  <div class="caja">
    <p class="tit">2. Evolución numérica: velocidad angular ω(t)</p>
    <p class="sub">Línea negra: solución exacta. Puntos: Euler y RK4 con el paso h elegido.</p>
    <canvas id="g1" height="250"></canvas>
    <div class="ley"><span><i style="background:var(--exacta)"></i>Exacta</span>
      <span><i style="background:var(--euler)"></i>Euler</span><span><i style="background:var(--rk4)"></i>RK4</span>
      <span><i style="background:#999;height:1px;border-top:1px dashed #999"></i>ω∞ (equilibrio)</span></div>
  </div>
  <div class="caja">
    <p class="tit">3. Evolución numérica: potencia P(t)</p>
    <p class="sub">Cuánta potencia trae el viento, el máximo posible (Betz) y lo que entrega el generador.</p>
    <canvas id="g2" height="250"></canvas>
    <div class="ley"><span><i style="background:#a3a6a9"></i>Viento ½ρAv³</span>
      <span><i style="background:var(--betz)"></i>Límite de Betz (59.3 %)</span>
      <span><i style="background:var(--gen)"></i>Generador k_g ω²</span></div>
  </div>
</div>

<script>
const D = __DATOS__;
const N = D.t.length, TF = D.t[N-1];
const $ = id => document.getElementById(id);
const fmt = (x, d=1) => x.toLocaleString('es-CO', {minimumFractionDigits:d, maximumFractionDigits:d});
const potTxt = P => Math.abs(P) >= 1e6 ? fmt(P/1e6,2)+' MW' : (Math.abs(P) >= 1e3 ? fmt(P/1e3,2)+' kW' : fmt(P,0)+' W');
const fTxt = F => F >= 1e3 ? fmt(F/1e3,2)+' kN' : fmt(F,0)+' N';

// ------------------------------------------------------------------ utilidades
function prep(c){ const r = window.devicePixelRatio||1, w = c.clientWidth, h = c.height/(c._r||1);
  if(!c._h) c._h = c.height; c.width = w*r; c.height = c._h*r; c._r = r;
  const x = c.getContext('2d'); x.setTransform(r,0,0,r,0,0); return [x, w, c._h]; }
function interp(arr, t){ const i = Math.min(N-2, Math.max(0, Math.floor(t/TF*(N-1)))); const t0 = D.t[i], t1 = D.t[i+1];
  const s = t1>t0 ? Math.min(1,Math.max(0,(t-t0)/(t1-t0))) : 0; return arr[i]*(1-s)+arr[i+1]*s; }
function flecha(x, X, Y, L, col, grosor=2.4){ if(L<2) return; x.strokeStyle=col; x.fillStyle=col; x.lineWidth=grosor;
  x.beginPath(); x.moveTo(X,Y); x.lineTo(X+L,Y); x.stroke(); x.beginPath(); x.moveTo(X+L+9,Y); x.lineTo(X+L,Y-5); x.lineTo(X+L,Y+5); x.fill(); }

// ------------------------------------------------------------------ escena
const cE = $('escena');
let parts = [];
for(let k=0;k<90;k++) parts.push({x:Math.random(), f:(Math.random()*2-1)*0.92});
let theta = 0;
const vmaxAll = Math.max(...D.v);
const wmax = Math.max(1e-6, ...D.w);

function escena(t, dtReal, vel){
  const [x, W, H] = prep(cE);
  x.clearRect(0,0,W,H);
  const v = interp(D.v,t), a = interp(D.a,t), w = interp(D.w,t), F = interp(D.F,t), Fb = interp(D.Fb,t);
  const vd = v*(1-a), v4 = v*(1-2*a);
  // --- vista lateral
  const WL = W*0.64, x0 = WL*0.40, cy = 140;
  const Rpx = 22 + 70*(D.R/D.Rmax);            // el dibujo crece con R
  const pxm = Rpx/D.R;                           // píxeles por metro
  const u = X => 1 - a*(1 + X/Math.sqrt(X*X + D.R*D.R));     // v(x)/v1 sobre el eje
  const rt = X => D.R*Math.sqrt((1-a)/u(X))*pxm;               // radio del tubo (masa constante)
  // suelo
  x.fillStyle='#f3f1ea'; x.fillRect(0,H-38,W,38);
  // tubo
  x.fillStyle='rgba(58,143,163,0.08)'; x.strokeStyle='rgba(58,143,163,0.55)'; x.lineWidth=1.4;
  x.beginPath(); for(let px=10;px<=WL-10;px+=4){ const X=(px-x0)/pxm; x.lineTo(px, cy-rt(X)); }
  for(let px=WL-10;px>=10;px-=4){ const X=(px-x0)/pxm; x.lineTo(px, cy+rt(X)); } x.closePath(); x.fill(); x.stroke();
  // partículas de aire
  const k = 130/Math.max(vmaxAll,1);           // px/s por m/s
  x.fillStyle='#3a8fa3';
  for(const p of parts){ const px = 10 + p.x*(WL-20); const X=(px-x0)/pxm;
    p.x += u(X)*v*k*dtReal*vel/4/(WL-20); if(p.x>1){p.x-=1; p.f=(Math.random()*2-1)*0.92;}
    x.beginPath(); x.arc(px, cy + p.f*rt(X), 2.1, 0, 7); x.fill(); }
  // torre y rotor lateral
  x.fillStyle='#9a9c9f'; x.fillRect(x0-3, cy, 6, H-38-cy);
  x.fillStyle='#4a4d50'; x.fillRect(x0-2, cy-Rpx, 5, 2*Rpx);
  x.fillStyle='#6b6e72'; x.beginPath(); x.ellipse(x0+12, cy, 16, 7, 0, 0, 7); x.fill();
  // empuje sobre el rotor
  const LF = 60*F/Math.max(Fb,1);
  flecha(x, x0+30, cy-Rpx-14, LF, '#b5543c', 3);
  x.fillStyle='#b5543c'; x.font='600 12px sans-serif'; x.fillText('Empuje F = '+fTxt(F), x0+30, cy-Rpx-24);
  // flechas de velocidad (proporcionales)
  const kv = 60/Math.max(vmaxAll,1), yb = H-52;
  x.font='12px sans-serif';
  [[18, v, 'antes  v₁ = '], [x0+12, vd, 'en el rotor  v_d = '], [WL-185, v4, 'después  v₄ = ']].forEach(([X0,val,txt])=>{
    flecha(x, X0, yb, val*kv, '#2b2d2f', 2); x.fillStyle='#2b2d2f'; x.fillText(txt+fmt(val,1)+' m/s', X0, yb-9); });
  x.fillStyle='#6b6e72'; x.font='12px sans-serif';
  x.fillText('Viento →', 14, 22); x.fillText('R = '+fmt(D.R,1)+' m', x0+8, cy+Rpx+14);
  x.fillText('a = '+fmt(a,3)+' (cuánto se frena el aire)', WL-215, 22);
  // separador
  x.strokeStyle='#e3e3de'; x.lineWidth=1; x.beginPath(); x.moveTo(WL,10); x.lineTo(WL,H-44); x.stroke();
  // --- vista frontal
  const xf = WL + (W-WL)/2, cf = 140;
  const lento = Math.max(1, Math.ceil(wmax*vel/5));    // cámara lenta para que el giro se vea
  theta += w*dtReal*vel/lento;
  x.fillStyle='#9a9c9f'; x.fillRect(xf-3, cf, 6, H-66-cf);
  x.strokeStyle='rgba(43,45,47,0.12)'; x.setLineDash([3,4]); x.beginPath(); x.arc(xf,cf,Rpx,0,7); x.stroke(); x.setLineDash([]);
  for(let b=0;b<3;b++){ const ang = theta + b*2*Math.PI/3;
    x.save(); x.translate(xf,cf); x.rotate(ang); x.fillStyle='#4a4d50';
    x.beginPath(); x.moveTo(0,-4); x.quadraticCurveTo(Rpx*0.35,-9,Rpx,-2); x.lineTo(Rpx,2); x.quadraticCurveTo(Rpx*0.35,5,0,4); x.fill(); x.restore(); }
  x.fillStyle='#2f5d62'; x.beginPath(); x.arc(xf,cf,7,0,7); x.fill();
  x.fillStyle='#2b2d2f'; x.font='600 13px sans-serif'; x.textAlign='center';
  x.fillText('ω = '+fmt(w,1)+' rad/s  ('+fmt(w*60/(2*Math.PI),0)+' rpm)', xf, 22);
  x.fillStyle='#6b6e72'; x.font='11.5px sans-serif';
  x.fillText(lento>1 ? 'giro mostrado '+lento+' veces más lento' : 'giro en tiempo real', xf, 38);
  // generador: barra de potencia
  const Pg = interp(D.Pg,t), Pv = interp(D.Pv,t), Pb = interp(D.Pb,t);
  const bx = WL+16, bw = W-WL-32, by = H-30;
  x.textAlign='left'; x.fillStyle='#e9e9e4'; x.fillRect(bx,by,bw,10);
  x.fillStyle='#2f5d62'; x.fillRect(bx,by,bw*Math.max(0,Math.min(1,Pg/Pv)),10);
  x.strokeStyle='#b5543c'; x.lineWidth=2; x.beginPath(); x.moveTo(bx+bw*Pb/Pv,by-4); x.lineTo(bx+bw*Pb/Pv,by+14); x.stroke();
  x.fillStyle='#2b2d2f'; x.font='12px sans-serif';
  x.fillText('Generador: '+potTxt(Pg)+' = '+fmt(100*Pg/Pv,0)+' % del viento', bx, by-6);
  x.fillStyle='#b5543c'; x.fillText('límite de Betz', bx+bw*Pb/Pv+4, by+21);
}

// ------------------------------------------------------------------ gráficas
function ejes(x, W, H, xmax, ymin, ymax, ylab){
  const m = {l:52, r:12, t:10, b:34}; const pw = W-m.l-m.r, ph = H-m.t-m.b;
  const X = t => m.l + t/xmax*pw, Y = y => m.t + (1-(y-ymin)/(ymax-ymin))*ph;
  x.strokeStyle='#ececE7'; x.fillStyle='#6b6e72'; x.font='11px sans-serif'; x.lineWidth=1;
  const paso = (r => { const p = Math.pow(10, Math.floor(Math.log10(r/5))); return [1,2,5,10].map(k=>k*p).find(s=>r/s<=6); });
  const sy = paso(ymax-ymin), sx = paso(xmax);
  x.textAlign='right';
  for(let y=Math.ceil(ymin/sy)*sy; y<=ymax+1e-9; y+=sy){ x.beginPath(); x.moveTo(m.l,Y(y)); x.lineTo(W-m.r,Y(y)); x.stroke(); x.fillText(fmt(y, sy<1?1:0), m.l-5, Y(y)+4); }
  x.textAlign='center';
  for(let s=0; s<=xmax+1e-9; s+=sx){ x.beginPath(); x.moveTo(X(s),m.t); x.lineTo(X(s),H-m.b); x.stroke(); x.fillText(fmt(s,0), X(s), H-m.b+14); }
  x.fillText('tiempo t (s)', m.l+pw/2, H-4);
  x.save(); x.translate(12, m.t+ph/2); x.rotate(-Math.PI/2); x.fillText(ylab, 0, 0); x.restore();
  x.textAlign='left';
  return {X, Y, m, pw, ph};
}
function linea(x, A, tt, yy, col, ancho=2, guiones=null){ x.strokeStyle=col; x.lineWidth=ancho; if(guiones) x.setLineDash(guiones);
  x.beginPath(); for(let i=0;i<tt.length;i++){ const px=A.X(tt[i]), py=A.Y(yy[i]); i?x.lineTo(px,py):x.moveTo(px,py);} x.stroke(); x.setLineDash([]); }
function puntos(x, A, tt, yy, col, ymin, ymax){ x.fillStyle=col; x.strokeStyle=col; x.lineWidth=1.2;
  const ok = y => isFinite(y) && y>=ymin && y<=ymax;
  x.beginPath(); for(let i=0;i<tt.length;i++){ if(!ok(yy[i])) continue; const px=A.X(tt[i]), py=A.Y(yy[i]);
    (i>0 && ok(yy[i-1])) ? x.lineTo(px,py) : x.moveTo(px,py); } x.stroke();
  const r = tt.length > 150 ? 1.6 : 3.2;
  for(let i=0;i<tt.length;i++){ if(!ok(yy[i])) continue; x.beginPath(); x.arc(A.X(tt[i]),A.Y(yy[i]),r,0,7); x.fill(); }
  return yy.some(y => !ok(y)); }
function cursor(x, A, t, H){ x.strokeStyle='rgba(47,93,98,0.6)'; x.lineWidth=1.5; x.setLineDash([4,3]);
  x.beginPath(); x.moveTo(A.X(t),A.m.t); x.lineTo(A.X(t),H-A.m.b); x.stroke(); x.setLineDash([]); }

const wTop = 1.25*Math.max(...D.w);
const winf_final = D.w[N-1];
function grafica1(t){
  const c = $('g1'); const [x, W, H] = prep(c); x.clearRect(0,0,W,H);
  const A = ejes(x, W, H, TF, 0, wTop, 'ω (rad/s)');
  linea(x, A, [0,TF], [winf_final,winf_final], '#999', 1, [5,4]);
  const fueraE = puntos(x, A, D.teu, D.weu, '#c0603f', -0.05*wTop, wTop);
  const fueraR = puntos(x, A, D.trk, D.wrk, '#3a6ea5', -0.05*wTop, wTop);
  linea(x, A, D.t, D.w, '#2b2d2f', 2);
  const fuera = [fueraE?'Euler':'', fueraR?'RK4':''].filter(Boolean).join(' y ');
  if(fuera){ x.fillStyle='#c0603f'; x.font='600 12px sans-serif'; x.fillText(fuera+' se sale de la gráfica: es inestable con este paso h', A.m.l+8, A.m.t+14); }
  cursor(x, A, t, H);
  x.fillStyle='#2b2d2f'; x.beginPath(); x.arc(A.X(t), A.Y(interp(D.w,t)), 4.5, 0, 7); x.fill();
}
const pTop = 1.12*Math.max(...D.Pv);
const esc = pTop >= 3e6 ? [1e6,'MW'] : (pTop >= 3e3 ? [1e3,'kW'] : [1,'W']);
function grafica2(t){
  const c = $('g2'); const [x, W, H] = prep(c); x.clearRect(0,0,W,H);
  const s = a => a.map(p => p/esc[0]);
  const A = ejes(x, W, H, TF, 0, pTop/esc[0], 'P ('+esc[1]+')');
  linea(x, A, D.t, s(D.Pv), '#a3a6a9', 2, [6,4]);
  linea(x, A, D.t, s(D.Pb), '#b5543c', 1.6, [3,3]);
  linea(x, A, D.t, s(D.Pg), '#2f5d62', 2.4);
  cursor(x, A, t, H);
  x.fillStyle='#2f5d62'; x.beginPath(); x.arc(A.X(t), A.Y(interp(D.Pg,t)/esc[0]), 4.5, 0, 7); x.fill();
}

// ------------------------------------------------------------------ datos y estado
function tablero(t){
  const v=interp(D.v,t), w=interp(D.w,t), l=interp(D.lam,t), cp=interp(D.cp,t), F=interp(D.F,t), Pg=interp(D.Pg,t);
  $('d_v').textContent = fmt(v,1)+' m/s'; $('d_w').textContent = fmt(w,2)+' rad/s';
  $('d_l').textContent = fmt(l,2); $('d_cp').textContent = fmt(cp,3);
  $('d_F').textContent = fTxt(F); $('d_P').textContent = potTxt(Pg);
  $('treloj').textContent = fmt(t,1)+' s';
  // ¿acelera o está en equilibrio?
  const i = Math.min(N-2, Math.floor(t/TF*(N-1))); const dw = (D.w[i+1]-D.w[i])/(D.t[i+1]-D.t[i]);
  let txt;
  if (Math.abs(dw) < 0.01*Math.max(1e-6, Math.abs(w))) txt = '⚖️ <b>Equilibrio:</b> el torque del viento es igual al del generador más la fricción, así que ω ya no cambia (ω ≈ ω∞).';
  else if (dw > 0) txt = '⬆️ <b>El rotor acelera:</b> el torque del viento es mayor que el del generador más la fricción (J dω/dt > 0).';
  else txt = '⬇️ <b>El rotor frena:</b> el torque del generador más la fricción es mayor que el del viento (J dω/dt < 0).';
  $('estado').innerHTML = txt;
}

// ------------------------------------------------------------------ reproducción
let t = 0, corriendo = true, ultimo = null;
const barra = $('barra'), bPlay = $('play');
function pintar(dt){ const vel = +$('vel').value; escena(t, dt, vel); grafica1(t); grafica2(t); tablero(t); barra.value = Math.round(1000*t/TF); }
function cuadro(ts){
  const dt = ultimo===null ? 0 : Math.min(0.05,(ts-ultimo)/1000); ultimo = ts;
  if(corriendo){ t += dt*(+$('vel').value); if(t>=TF){ t=TF; corriendo=false; bPlay.textContent='▶ Reproducir'; } }
  pintar(dt); requestAnimationFrame(cuadro);
}
bPlay.onclick = () => { if(t>=TF) t=0; corriendo=!corriendo; bPlay.textContent = corriendo ? '⏸ Pausa' : '▶ Reproducir'; };
$('reini').onclick = () => { t=0; corriendo=true; bPlay.textContent='⏸ Pausa'; };
barra.oninput = () => { t = barra.value/1000*TF; corriendo=false; bPlay.textContent='▶ Reproducir'; };
window.irA = s => { t = s; corriendo=false; bPlay.textContent='▶ Reproducir'; };
bPlay.textContent='⏸ Pausa';
requestAnimationFrame(cuadro);
</script></body></html>
"""
