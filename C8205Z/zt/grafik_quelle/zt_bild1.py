# zt_bild1.py - zeichnet Bild 1 (ZT-Trommelaufbau_1.png): vier Trommeln und Spur 0 von Trommel 0 (Stand md 0.01-061, kat5: Verzeichnis Spuren 1 bis 32, ohne Kennsatz).
# Voraussetzung: matplotlib. Aufruf: python3 zt_bild1.py  (schreibt ../ZT-Trommelaufbau_1.png, 2338 x 1654). Bild 2 bleibt unveraendert.
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
os.chdir(os.path.dirname(os.path.abspath(__file__)))
BL, GN, GE, GR = '#cfe2f3', '#d9ead3', '#fff2cc', '#d9d9d9'
fig = plt.figure(figsize=(11.69, 8.27), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 117); ax.set_ylim(83, 0); ax.axis('off')
def box(x, y, w, h, fc, txt='', fs=6.5, lw=0.8, bold=False):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec='black', lw=lw))
    if txt: ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', linespacing=1.5)
ax.text(58.5, 4, 'Bild 1: Aufbau der vier Zusatztrommeln und Spur 0 von Trommel 0', ha='center', fontsize=15, fontweight='bold')
ax.text(58.5, 8, 'Je Trommel 128 Spuren (0 bis 127 = 177 oktal) zu 32 Zellen; laufende Spur g = 128 · d + s, g = 0 bis 511 (777). Zahlen dezimal, oktal in Klammern.', ha='center', fontsize=7.5, color='#444444')
# Trommeln: Spur s von y0 (Spur 0) bis y0+h (Ende Spur 127)
y0, h = 21, 47; sp = h / 128.0
xs = [12, 29, 46, 63]; w = 15.5
for d, x in enumerate(xs):
    ax.text(x + w / 2, 15.3, 'Trommel %d' % d, ha='center', fontsize=10, fontweight='bold')
    ax.text(x + w / 2, 18.2, 'g %d bis %d' % (128 * d, 128 * d + 127), ha='center', fontsize=7.5)
    if d == 0:
        box(x, y0, w, 1.0, GE)
        box(x, y0 + 1.0, w, 32 * sp - 1.0 + sp, BL, 'Verzeichnis\nSpuren 1 bis 32\n(1 bis 40)')
        box(x, y0 + 33 * sp, w, h - 33 * sp, GN, 'Programme\nSpuren 33 bis 127\n(41 bis 177)\n\nZTD ab Spur 33\n(ID 1)\n\n95 Spuren')
    else:
        box(x, y0, w, h, GN, 'Programme\nSpuren 0 bis 127\n(0 bis 177)\n\n128 Spuren\n\nauch Spur 0 frei\nfür Programme')
ax.text(x0 := xs[0] - 1, y0 + 0.2, 'Spur 0 (Verwaltung)', ha='right', fontsize=6.5)
ax.text(xs[0] - 1, y0 + 33 * sp, 'Spur 33', ha='right', fontsize=6.5); ax.text(xs[0] - 1, y0 + h, 'Spur 127', ha='right', fontsize=6.5)
ax.text(xs[1] + 12, y0 + h + 2.5, va='top', s= 'Programme belegen volle Spuren ab Spurgrenze und dürfen\nüber das Ende einer Trommel in die nächste laufen\n(g zählt fortlaufend). Nutzbar: 95 + 3 · 128 = 479 Spuren (737)\n= 15 328 Sektoren.', ha='center', fontsize=7.5, linespacing=1.5)
# Spur 0 von Trommel 0
X = 100; ax.text(X - 3, 15.2, 'Spur 0 von Trommel 0 (32 Zellen, Worte zu 33 Bit)', ha='center', fontsize=9, fontweight='bold')
ax.text(X - 15, 19.2, 'Zelle', ha='center', fontsize=7); ax.text(X - 3, 19.2, 'Inhalt', ha='center', fontsize=7)
rows = [(0, BL, 'Repository-Kennzeichen (52525252525), erkennt repo')] + [(i, GR, 'nicht festgelegt (Kennsatz entfällt)' if i == 1 else '') for i in range(1, 16)] + \
       [(16, GE, 'Repository-Kopf'), (17, GE, 'höchste vergebene Programm-ID (Zähler)'), (18, GE, 'letzte belegte Trommel (initial 0)'),
        (19, GE, 'letzte belegte Spur (initial 32 (40))')] + [(i, GR, '20 bis 31: nicht festgelegt' if i == 20 else '') for i in range(20, 32)]
rx, rw, rh, ry = X - 15, 24, 1.5, 21
for i, fc, t in rows:
    ax.text(rx - 1, ry + i * rh + rh / 2, str(i), ha='right', va='center', fontsize=6.5)
    box(rx, ry + i * rh, rw, rh, fc, t, fs=6, lw=0.7)
ax.text(rx + rw / 2, ry + 32 * rh + 2, 'Zellen 0 (0), 1 bis 15 (1 bis 17), 16 (20), 17 (21), 18 (22), 19 (23), 20 bis 31 (24 bis 37)', fontsize=5.8, ha='center')
box(rx - 4, ry + 32 * rh + 5, 32, 6, '#ffffff', 'Der Trommelkennsatz (frühere Zellen 0 bis 15) entfällt.\nWie die Belegung der Spuren festgehalten wird: Abschnitt 8, Punkt 6.', fs=6.3, lw=0.6)
fig.savefig('../ZT-Trommelaufbau_1.png', dpi=200)
print('ZT-Trommelaufbau_1.png geschrieben')
