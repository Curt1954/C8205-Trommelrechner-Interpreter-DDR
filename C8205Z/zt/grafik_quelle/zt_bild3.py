# zt_bild3.py - zeichnet Bild 3 (ZT-Trommelaufbau_3.png): Aufbau eines Datensatzes je Typ (Typ 00, Typ 10, Typ 11), Stand md 0.01-040.
# Voraussetzung: matplotlib. Aufruf: python3 zt_bild3.py  (schreibt ../ZT-Trommelaufbau_3.png, 2338 x 1654). Stil wie Bild 1 und 2.
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
os.chdir(os.path.dirname(os.path.abspath(__file__)))
BL, GN, GE, GR, RT, WS = '#cfe2f3', '#d9ead3', '#fff2cc', '#d9d9d9', '#f4cccc', '#ffffff'
fig = plt.figure(figsize=(11.69, 8.27), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 117); ax.set_ylim(83, 0); ax.axis('off')
def box(x, y, w, h, fc, txt='', fs=6.5, lw=0.8, bold=False):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec='black', lw=lw))
    if txt: ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', linespacing=1.4)
X0, BW = 17.0, 2.9                      # linker Rand, Breite je Bit; 33 Bit = 95.7
def bx(b): return X0 + b * BW           # x-Lage des Bits zb (z0 links)
def feld(y, h, z0, z1, fc, txt, fs=6.3):  # Feld von Bit z0 bis z1 (einschliesslich)
    box(bx(z0), y, (z1 - z0 + 1) * BW, h, fc, txt, fs)
def kopf(y):                            # Ziffernleiste t0..t10 mit z-Bereichen
    for t in range(11):
        ax.text(bx(3 * t) + 1.5 * BW, y, 't%d' % t, ha='center', fontsize=6.5, fontweight='bold', color='#444444')
        ax.text(bx(3 * t) + 1.5 * BW, y + 1.6, 'z%d–z%d' % (3 * t, 3 * t + 2), ha='center', fontsize=5.2, color='#666666')
def wort(y, name, h=5.2):
    ax.text(X0 - 1.5, y + h / 2, name, ha='right', va='center', fontsize=7.5, fontweight='bold')
def streifen(y, labels, farben, w=6.2, h=3.4, x=X0 + 14, kopf_txt='Zellen (Sektoren) der Spur'):
    ax.text(x - 1, y + h / 2, kopf_txt, ha='right', va='center', fontsize=5.8)
    for i, (l, f) in enumerate(zip(labels, farben)):
        box(x + i * w, y, w, h, f, l, fs=5.3, lw=0.6)
ax.text(58.5, 4, 'Bild 3: Aufbau eines Datensatzes je Typ (Typ 00, Typ 10, Typ 11)', ha='center', fontsize=15, fontweight='bold')
ax.text(58.5, 8, 'Ein Wort hat 33 Bit, z0 links bis z32 rechts, = 11 Oktalziffern t0 bis t10 (t0 = z0 bis z2, t10 = z30 bis z32). Ein Datensatz belegt je Wort eine Zelle (einen Sektor).', ha='center', fontsize=7.2, color='#444444')
# ---------------- Typ 00
y = 11.5
ax.text(2, y, 'Typ 00 – kat4-Text', fontsize=10.5, fontweight='bold'); ax.text(33, y, 'Datensatz = 1 Wort (4 Zeichen zu je 8 Bit; Programm = n Worte)', fontsize=8)
kopf(y + 2.8); yy = y + 5.6; wort(yy, 'Wort 1')
feld(yy, 5.2, 0, 0, RT, 'Ende\nz0'); feld(yy, 5.2, 1, 8, GE, 'Zeichen 4\nz1–z8'); feld(yy, 5.2, 9, 16, GN, 'Zeichen 3\nz9–z16'); feld(yy, 5.2, 17, 24, BL, 'Zeichen 2\nz17–z24'); feld(yy, 5.2, 25, 32, GN, 'Zeichen 1 (erstes)\nz25–z32')
ax.text(X0, yy + 6.9, 'z0 = 1: letztes Wort des Textes (Endemarke); sonst 0. Das erste Zeichen steht rechts, die weiteren folgen nach links; fehlende Zeichen bleiben links 0. Code = Ausgabeadresse der Kodetabelle ohne das werthöchste Bit.', fontsize=6.0)
streifen(yy + 8.8, ['W1', 'W2', 'W3', 'W4', 'W5', '…', 'Wn\nz0 = 1', '?', '?'], [BL] * 5 + [WS, RT, GR, GR], kopf_txt='Zellen der Spur 0, 1, 2 …')
# ---------------- Typ 10
y = 32.0
ax.text(2, y, 'Typ 10 – Eingabefolge', fontsize=10.5, fontweight='bold'); ax.text(33, y, 'Datensatz = 2 Worte (2 aufeinanderfolgende Sektoren; Länge immer gerade)', fontsize=8)
kopf(y + 2.8); yy = y + 5.6; wort(yy, 'Wort 1')
feld(yy, 5.2, 0, 32, GN, 'Datenwert: 11 Oktalziffern t0 bis t10 (Ziffern 0 bis 7), ganzes 33-Bit-Wort, z0 ist Datenbit')
yy2 = yy + 6.2; wort(yy2, 'Wort 2')
feld(yy2, 5.2, 0, 20, GR, 'nicht benutzt = 0\nt0 bis t6 (z0–z20)'); feld(yy2, 5.2, 21, 26, GE, 'Kennzeichen 1\nz21–z26 (t7, t8)', 5.8); feld(yy2, 5.2, 27, 32, GE, 'Kennzeichen 2\nz27–z32 (t9, t10)', 5.8)
ax.text(X0, yy2 + 6.9, 'Zwei Zeichen zu je 6 Bit als Eingabeadresse (Kodetabelle R 300, Tabelle 1, Spalte „Eingabe Adresse“). Keine Endemarke, Ende nur über die Länge. 16 Datensätze je Spur.', fontsize=6.0)
streifen(yy2 + 8.8, ['D1', 'K1', 'D2', 'K2', 'D3', 'K3', 'D4', 'K4', 'D5', 'K5', '…', '?'], [GN, GE] * 5 + [WS, GR], w=5.2, kopf_txt='Zellen: D = Datenwort, K = Kennzeichen')
# ---------------- Typ 11
y = 58.0
ax.text(2, y, 'Typ 11 – Maschinenworte', fontsize=10.5, fontweight='bold'); ax.text(33, y, 'Datensatz = 1 Wort (11 Oktalziffern; Programm = n Worte, keine Endemarke)', fontsize=8)
kopf(y + 2.8); yy = y + 5.6; wort(yy, 'Wort 1')
feld(yy, 5.2, 0, 32, BL, 'Datenwort: 11 Oktalziffern t0 bis t10, ganzes 33-Bit-Wort, z0 ist Datenbit')
ax.text(X0, yy + 6.9, 'Keine Endemarke: das Ende ergibt sich allein aus der Länge im Verzeichniseintrag. Ein Wort je Sektor ab Zelle 0 der Anfangsspur, 32 Worte je Spur.', fontsize=6.0)
streifen(yy + 8.8, ['W1', 'W2', 'W3', 'W4', 'W5', '…', 'Wn', '?', '?'], [BL] * 7 + [GR, GR], kopf_txt='Zellen der Spur 0, 1, 2 …')
ax.text(58.5, 80.5, '„?“ = Inhalt undefiniert. Typ 01 ist reserviert. Das Verzeichnis (Abschnitt 4.1) trägt den Typ in Wort 3, z1 bis z2. Zahlen oktal.', ha='center', fontsize=6.2, color='#444444')
fig.savefig('../ZT-Trommelaufbau_3.png', dpi=200)
print('ZT-Trommelaufbau_3.png geschrieben')
