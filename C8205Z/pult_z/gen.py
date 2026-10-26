# Generator: Bedienpult C8205 als SVG (viewBox 1024x461)
import sys
NUM='--num' in sys.argv
reg=[];bad=[]
def R(id,typ,label,bx,by):
    n=len(reg)+1; reg.append((n,id,typ,label)); bad.append((n,bx,by))
W,H=1024,461
o=[]
a=o.append
a(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="DejaVu Sans, Verdana, Arial, sans-serif">
<defs>
<linearGradient id="gPanel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c4bdb0"/><stop offset="1" stop-color="#aaa396"/></linearGradient>
<linearGradient id="gBlue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2b3a52"/><stop offset="1" stop-color="#1a2536"/></linearGradient>
<linearGradient id="gGrey" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2ddd2"/><stop offset="1" stop-color="#c3bdb0"/></linearGradient>
<linearGradient id="gOr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ecc983"/><stop offset="1" stop-color="#cf9f55"/></linearGradient>
<radialGradient id="rOff" cx=".4" cy=".35" r=".7"><stop offset="0" stop-color="#f3dcc0"/><stop offset="1" stop-color="#b79a78"/></radialGradient>
<radialGradient id="rOn" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="#fffbe0"/><stop offset=".6" stop-color="#ffd25a"/><stop offset="1" stop-color="#e8962a"/></radialGradient>
<radialGradient id="rRed" cx=".45" cy=".4" r=".7"><stop offset="0" stop-color="#fff0e0"/><stop offset=".5" stop-color="#ff5a3c"/><stop offset="1" stop-color="#c01810"/></radialGradient>
<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<style>
.lbl{{font-weight:700;fill:#e9e4d6;text-anchor:middle}}
.kt{{font-weight:700;fill:#2a2a2a;text-anchor:middle}}
.cap{{font-weight:700;fill:#3a3a3a;text-anchor:middle;font-size:9px}}
.key .face{{transition:transform .06s}}
.key.down .face{{transform:translateY(2px)}}
.key{{cursor:pointer}}
.lamp .lens{{fill:url(#rOff)}}
.lamp .halo{{opacity:0}}
.lamp.on .lens{{fill:url(#rOn)}}
.lamp.on .halo{{opacity:.85}}
.lamp.red.on .lens{{fill:url(#rRed)}}
.led{{fill:#0b0b0d}}
.led.on{{fill:#ff3b2a}}
</style>
<rect width="{W}" height="{H}" fill="#0d0d0f"/>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#gPanel)"/>
<rect x="0" y="0" width="{W}" height="182" fill="url(#gBlue)"/>
<rect x="0" y="180" width="{W}" height="3" fill="#0c121b"/>
<rect x="0" y="0" width="12" height="{H}" fill="#15181c"/><rect x="{W-12}" y="0" width="12" height="{H}" fill="#15181c"/>
''')
# ---- Lampen oberste Reihe ----
lamps=['H','R','AR','AL','A','W','FG','E','FP','OP','K7','K6','K5','K4','K3','K2','K1']+[f'L{i}' for i in range(18,31)]
n=len(lamps); x0,x1=70,994; p=(x1-x0)/(n-1)
for i,l in enumerate(lamps):
    x=x0+i*p; R('lamp-'+l,'Lampe',l,x+10,73); cls='lamp red on' if l=='H' else 'lamp'
    a(f'<g class="{cls}" id="lamp-{l}"><ellipse class="halo" cx="{x:.1f}" cy="85" rx="16" ry="19" fill="#ffb347" filter="url(#glow)"/>'
      f'<ellipse class="lens" cx="{x:.1f}" cy="85" rx="12" ry="14.5" stroke="#6d5a44" stroke-width="1"/>'
      f'<ellipse cx="{x-3:.1f}" cy="79" rx="4" ry="3" fill="#fff" opacity=".35"/>'
      f'<text class="lbl" x="{x:.1f}" y="112" font-size="10.5">{l}</text></g>')
for i,l in enumerate(['T4','T3','T2','T1']):
    x=70+i*32.7; R('lamp-'+l,'Lampe',l,x+10,127)
    a(f'<g class="lamp" id="lamp-{l}"><ellipse class="halo" cx="{x:.1f}" cy="139" rx="16" ry="19" fill="#ffb347" filter="url(#glow)"/>'
      f'<ellipse class="lens" cx="{x:.1f}" cy="139" rx="12" ry="14.5" stroke="#6d5a44" stroke-width="1"/>'
      f'<ellipse cx="{x-3:.1f}" cy="133" rx="4" ry="3" fill="#fff" opacity=".35"/>'
      f'<text class="lbl" x="{x:.1f}" y="166" font-size="10.5">{l}</text></g>')
# ---- kleine LEDs (AR / zweite Gruppe) ----
def leds(xs,y,pref):
    for i,x in enumerate(xs):
        R(f'{pref}{i}','LED','',x,122)
        a(f'<circle class="led" id="{pref}{i}" cx="{x}" cy="{y}" r="3.6" stroke="#000" stroke-width=".8"/>')
leds([286,313,340,378,403,428,467,492,517,556,580,605],133,'ar-led')
a('<line x1="268" y1="146" x2="616" y2="146" stroke="#8d9bb0" stroke-width="1"/>'
  '<text class="lbl" x="442" y="160" font-size="10.5">AR</text>')
leds([698,723,749,787,812,837,874,900],133,'ur-led')
R('ur-led-red','LED (rot)','',926,122)
a('<circle class="led" id="ur-led-red" cx="926" cy="133" r="3.6" fill="#7a1a14" stroke="#000" stroke-width=".8"/>')
a('<line x1="676" y1="146" x2="934" y2="146" stroke="#8d9bb0" stroke-width="1"/>'
  '<text class="lbl" x="805" y="160" font-size="10.5">UR</text>')
# Schlüsselschalter
R('keyswitch','Schlüsselschalter','',978,116)
a('<g id="keyswitch"><circle cx="958" cy="132" r="14" fill="#2a2d33" stroke="#555" stroke-width="1.5"/><circle cx="958" cy="132" r="9" fill="#c9c9c9" stroke="#777"/>'
  '<rect x="956" y="127" width="4" height="10" rx="1" fill="#444"/><rect x="962" y="139" width="8" height="26" rx="2" fill="#a8a8a8" stroke="#666" transform="rotate(-14 962 139)"/></g>')
# ---- Tasten ----
def key(id,label,cx,cy,w=24,h=24,kind='g',fs=10.5):
    R('key-'+id,'Taste ('+{'o':'orange','g':'grau'}[kind]+')',label,cx-w/2+9,cy-h/2-1)
    g='url(#gOr)' if kind=='o' else 'url(#gGrey)'
    base='#6f5a35' if kind=='o' else '#7a766c'
    a(f'<g class="key" id="key-{id}" data-key="{id}">'
      f'<rect x="{cx-w/2-1:.1f}" y="{cy-h/2+2:.1f}" width="{w+2}" height="{h}" rx="3" fill="#47443d"/>'
      f'<g class="face"><rect x="{cx-w/2:.1f}" y="{cy-h/2:.1f}" width="{w}" height="{h}" rx="3" fill="{g}" stroke="{base}" stroke-width="1"/>'
      f'<rect x="{cx-w/2+1.5:.1f}" y="{cy-h/2+1.5:.1f}" width="{w-3}" height="3" rx="1.5" fill="#fff" opacity=".35"/>'
      f'<text class="kt" x="{cx:.1f}" y="{cy+fs*0.36:.1f}" font-size="{fs}">{label}</text></g></g>')
# Matrix links
xs=[75,101,128,154,180]; ys=[203,231,258,285,313,342]
rows=[['T4','T3','T2','T1','6'],['','','','','40'],['1','1','1','1','100'],['2','2','2','2','200'],['4','4','4','4','400'],['10','10','10','10','1000']]
for r,row in enumerate(rows):
    for c,l in enumerate(row):
        w=24 if c<4 else 28
        key(f'M{r}{c}',l,xs[c]+(2 if c==4 else 0),ys[r],w,24,fs=9.5 if len(l)>2 else 10.5)
# orange Datentasten
og=[[283,309,335],[372,398,423],[457,485,511],[543,570,598],[684,711,739]]
for gi,g in enumerate(og):
    for ki,x in enumerate(g): key(f'D{gi}{ki}','',x,205,24,28,'o')
for gi,g in enumerate([[771,797,823],[859,885,910]]):
    for ki,x in enumerate(g): key(f'E{gi}{ki}','',x,205,24,28,'g')
# Reihe 2 & 3
r2=[(['L','SR','SP'],[286,314,341]),(['UW','S2','S1'],[375,401,427]),(['','A','F'],[463,491,517]),(['SP','A','S'],[556,584,610])]
r3=[(['L','SP',''],[292,318,344]),(['OP','K7','K6'],[386,409,433]),(['K5','K4','K3'],[473,499,523]),(['K2','K1','K0'],[558,584,610])]
for gi,(ls,xx) in enumerate(r2):
    for l,x in zip(ls,xx): key(f'R2{gi}{l or "x"}',l,x,256,24,24)
for gi,(ls,xx) in enumerate(r3):
    for l,x in zip(ls,xx): key(f'R3{gi}{l or "x"}',l,x,314,24,24)
def cap(t,x,y,x1=None,x2=None):
    if x1: a(f'<line x1="{x1}" y1="{y-3}" x2="{x2}" y2="{y-3}" stroke="#555" stroke-width="1"/>')
    a(f'<rect x="{x-len(t)*4-3}" y="{y-9}" width="{len(t)*8+6}" height="12" fill="#b6afa2"/><text class="cap" x="{x}" y="{y}">{t}</text>')
cap('AR',298,285,278,335);cap('HS',335,285);cap('SWI',481,282,455,525);cap('SWII',572,282,550,615);cap('OR',296,343,278,330)
# OR-Block
key('OR-H','H',322,360,80,24,fs=11); key('OR-R','R',325,392,80,24,fs=11)
for l,x in zip(['E','M','D','SP','BS'],[376,401,427,453,479]): key('OR-'+l,l,x,360,24,24)
key('OR-G','G',404,392,72,24,fs=11); key('OR-ST','ST',456,392,24,24,fs=10); key('OR-LD','LD',481,392,24,24,fs=10)
# Zifferntasten rechts (hex, Beschriftung zu prüfen)
hx=[['C','D','E','F'],['8','9','A','B'],['4','5','6','7'],['0','1','2','3']]
for r,row in enumerate(hx):
    for c,l in enumerate(row): key('N'+l,l,[845,873,901,929][c],[238,264,290,316][r],24,23)
key('N-wide','',900,350,108,22)
if NUM:
    for n,bx,by in bad:
        t=str(n); pw=6*len(t)+5
        a(f'<g class="badge"><rect x="{bx-pw/2:.1f}" y="{by-5.5:.1f}" width="{pw}" height="11" rx="5.5" fill="#d6212a" stroke="#fff" stroke-width=".8"/><text x="{bx:.1f}" y="{by+3:.1f}" font-size="8.5" font-weight="700" fill="#fff" text-anchor="middle">{n}</text></g>')
a('</svg>')
open('/home/claude/bedienpult_nummeriert.svg' if NUM else '/home/claude/bedienpult.svg','w').write('\n'.join(o))

if NUM:
    import csv
    with open('/home/claude/elemente.csv','w',newline='',encoding='utf-8') as f:
        w=csv.writer(f,delimiter=';'); w.writerow(['Nr','ID','Typ','Beschriftung (aktuell)','Beschreibung (von dir)'])
        for n,i,t,l in reg: w.writerow([n,i,t,l,''])
    print(len(reg),'Elemente')
