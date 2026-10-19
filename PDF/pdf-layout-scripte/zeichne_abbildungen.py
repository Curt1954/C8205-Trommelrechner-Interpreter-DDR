# -*- coding: utf-8 -*-
"""Zeichnet die drei Pult-Abbildungen des C 8205 neu (Vorlage: Scans der Originalunterlagen).

Aufruf:  python3 PDF/pdf-layout-scripte/zeichne_abbildungen.py [AUSGABEVERZEICHNIS]   (Vorgabe: markdown-dateien/abbildungen/)
Ergebnis: je Abbildung eine .svg (Vektor, Schrift als Pfade) und eine .png (300 dpi).
Abhaengigkeiten: matplotlib, Schrift DejaVu Sans (wie die PDF-Gestaltungsrichtlinie).
Koordinaten sind Millimeter, Ursprung links oben.
"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["svg.fonttype"] = "path"

INK = "#1F2937"        # Palette PDF.md: Tinte
MUTED = "#6B7280"      # Grau
PANEL = "#F3F4F6"      # Flaeche
GRAU_TASTE = "#D1D5DB" # Taste ohne Funktion (Linienfarbe der Palette)
TASTE_LEER = "#E5E7EB" # unbeschriftete Taste
LW = 0.8


def neue_flaeche(w, h):
    fig = plt.figure(figsize=(w / 25.4, h / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    return fig, ax


def speichern(fig, name, ziel):
    for ext in ("svg", "png"):
        fig.savefig(os.path.join(ziel, f"{name}.{ext}"), dpi=300, facecolor="white")
    plt.close(fig)


def text(ax, x, y, s, fs=7.5, ha="center", va="center", color=INK, weight="normal", style="normal", zorder=2):
    ax.text(x, y, s, fontsize=fs, ha=ha, va=va, color=color, fontweight=weight, fontstyle=style, zorder=zorder)


def linie(ax, x1, y1, x2, y2, lw=LW, color=INK, ls="-"):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls=ls, solid_capstyle="butt")


def taste(ax, x, y, w=8.2, h=8.2, main=None, oben=None, unten=None, fs=8.0, fc="white",
          gestrichelt=False, rund=1.1, grau=False):
    if grau:
        fc = GRAU_TASTE
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rund}",
                                fc=fc, ec=INK if not gestrichelt else MUTED, lw=LW,
                                ls=(0, (2.2, 1.6)) if gestrichelt else "-", zorder=3))
    if main is not None:
        text(ax, x + w / 2, y + h / 2 + 0.1, main, fs=fs, color=MUTED if (gestrichelt or grau) else INK, zorder=4)
    if oben is not None:
        text(ax, x + w / 2, y + h * 0.31, oben, fs=fs, color=MUTED if grau else INK, zorder=4)
        text(ax, x + w / 2, y + h * 0.74, unten, fs=fs - 1.3, color=MUTED, zorder=4)


# ---------------------------------------------------------------------------- Abbildung 1: Lampenfeld
def lampenfeld(ziel):
    W, H = 150, 82
    fig, ax = neue_flaeche(W, H)
    ax.add_patch(FancyBboxPatch((0.8, 0.8), W - 1.6, H - 1.6, boxstyle="round,pad=0,rounding_size=2.5",
                                fc=PANEL, ec=INK, lw=1.0))
    # obere Reihe: Zustandslampen
    namen = ["E", "A", "T", "SW", "K1", "K2", "K3", "FE", "FÜ", "BS", "US", "R", "H", "B", "N"]
    r, y1 = 3.2, 11.0
    xs = [9.0 + 8.7 * i for i in range(len(namen))]
    for n, x in zip(namen, xs):
        ax.add_patch(Circle((x, y1), r, fc="white", ec=INK, lw=0.9))
        if n != "N":
            text(ax, x, y1 + 7.6, n, fs=7.5)
    i_t, i_sw, i_b, i_n = 2, 3, 13, 14
    linie(ax, xs[i_t] + r, y1, xs[i_sw] - r, y1)              # T und SW gehoeren zu K0
    linie(ax, xs[i_b] + r, y1, xs[i_n] - r, y1)               # B und N
    linie(ax, xs[i_t], y1 + 10.4, xs[i_sw], y1 + 10.4, lw=0.6)
    text(ax, (xs[i_t] + xs[i_sw]) / 2, y1 + 13.2, "K0", fs=7.5)
    # Schluesselschalter unter N
    ky = 31.0
    linie(ax, xs[i_n], y1 + r, xs[i_n], ky - 3.6)
    text(ax, xs[i_n] + 2.0, y1 + 7.6, "N", fs=7.5, ha="left")
    ax.add_patch(Circle((xs[i_n], ky), 3.9, fc=INK, ec=INK, lw=0.9))          # Schluessel: dunkle Scheibe, helle Schluesselfahne
    linie(ax, xs[i_n] - 1.9, ky + 1.9, xs[i_n] + 1.9, ky - 1.9, lw=2.4, color="white")
    text(ax, xs[i_n], ky + 7.2, "Schlüssel-\nschalter", fs=6.6, color=MUTED)

    # untere Reihe: Befehlsregister in Triaden
    p, yd = 3.7, 40.0
    triaden = []                                   # (x0, Wertigkeit)
    x0 = 9.0
    for wert in ("1000", "100", "10", "1"):
        triaden.append((x0, wert))
        x0 += 2 * p + 5.2
    ar_ende = triaden[-1][0] + 2 * p
    x_or = ar_ende + 9.0
    for wert in ("B", "A", "Z"):
        triaden.append((x_or, wert))
        x_or += 2 * p + 5.2
    for k, (x0, wert) in enumerate(triaden):
        for j, g in enumerate(("4", "2", "1")):
            ax.add_patch(Circle((x0 + j * p, yd), 1.35, fc=INK, ec=INK, lw=0.5))
            text(ax, x0 + j * p, yd + 3.7, g, fs=6.0, color=MUTED)
        text(ax, x0 + p, yd + 7.6, wert, fs=7.0, weight="bold")
        if k not in (3, 6):                            # Trennstrich zwischen den Triaden
            xb = x0 + 2 * p + 2.6
            linie(ax, xb, yd - 2.8, xb, yd + 2.8, lw=0.9)
    xb = ar_ende + 4.5                                 # Grenze AR | OR
    linie(ax, xb, yd - 3.6, xb, yd + 3.6, lw=1.7)
    # Vergleicher V1, V2
    vx = [x_or + 3.0, x_or + 11.5]
    for j, x in enumerate(vx):
        ax.add_patch(Circle((x, yd), 1.35, fc=INK, ec=INK, lw=0.5))
        text(ax, x, yd + 3.7, str(j + 1), fs=6.6, color=MUTED)
    # Klammern und Gruppennamen
    yk = yd + 12.0
    def klammer(xa, xb_, kurz, lang):
        linie(ax, xa, yk, xb_, yk, lw=0.7)
        linie(ax, xa, yk - 1.0, xa, yk, lw=0.7)
        linie(ax, xb_, yk - 1.0, xb_, yk, lw=0.7)
        text(ax, (xa + xb_) / 2, yk + 3.6, kurz, fs=8.0, weight="bold")
        text(ax, (xa + xb_) / 2, yk + 7.4, lang, fs=7.0)
    klammer(triaden[0][0] - 1.5, ar_ende + 1.5, "AR", "Adreßregister")
    klammer(triaden[4][0] - 1.5, triaden[6][0] + 2 * p + 1.5, "OR", "Operationsregister")
    klammer(vx[0] - 1.8, vx[1] + 1.8, "V", "Vergleicher")
    text(ax, 5.0, H - 9.5,
         "B  Betriebsanzeige   ·   N  Netzstromversorgung liegt an",
         fs=6.6, ha="left", color=INK)
    text(ax, 5.0, H - 5.5,
         "Triade = drei Lampen mit den Gewichten 4 · 2 · 1 (eine Oktalziffer). "
         "Obere Reihe: Zustandslampen (Flags).",
         fs=6.3, ha="left", color=MUTED)
    speichern(fig, "C8205-Abb-Lampenfeld", ziel)


# ---------------------------------------------------------------------------- Abbildung 2: Pult-Tastatur
def pult_tastatur(ziel):
    """Tastatur des Bedienpultes. Oberer Teil nach Foto und Scan, Gruppenraender nach der Strichzeichnung
    (Tastengruppen grenzen aneinander; ST, H und R liegen ausserhalb)."""
    W, H = 176, 96
    fig, ax = neue_flaeche(W, H)
    a = 8.2          # Tastenkante
    pt = 9.8         # Tastenteilung
    g2 = (pt - a) / 2
    # --- oben links: Kanalwahl (Anordnung nach dem Foto: K0 ueber K1, K2 ueber K3)
    y_a, y_b = 5.0, 16.5
    for n, x, y in (("K0", 10, y_a), ("K1", 12.2, y_b), ("K2", 25, y_a), ("K3", 27.2, y_b)):
        taste(ax, x, y, main=n, fs=8.5)
    # --- oben rechts: einrastende Schalter, darunter je eine unbeschriftete Taste
    for n, x in (("SP", 84), ("BS", 101), ("LS", 118), ("SW", 135)):
        taste(ax, x, y_a, main=n, fs=8.5)
        taste(ax, x + 0.4, y_b, main=None, fc=TASTE_LEER)
    # --- unten: Hauptfeld (Tastenpositionen)
    y1, y2 = 40.0, 50.8
    off_l = 3.5                       # untere Reihe links nach rechts versetzt
    off_r = -3.2                      # untere Reihe rechts nach links versetzt
    xH = 8.0
    xT = xH + 3 * pt
    xB = xT + 18.4
    xIS = xB + 8 * pt + a + 5.0
    xIB = xIS + pt
    xWM, xST = xIS - 2.5, xIB - 2.2
    # --- Gruppenraender (zuerst zeichnen, damit die Zeigerlinien hinter den Tasten liegen)
    ym = y1 + a + (y2 - y1 - a) / 2           # Mitte zwischen den Tastenreihen
    yt, yb = y1 - 4.0, y2 + a + 4.0
    dash = (0, (3.0, 2.0))
    xa1, xa2 = xH + pt - g2, xH + pt + off_l - g2                        # linker Rand, Reihe 1 / 2
    xab1, xab2 = xH + 2 * pt + a + g2, xH + 2 * pt + off_l + a + g2      # Rand A | B
    xbc = (xT + off_l + a + xB + off_r) / 2                              # Rand B | C (gerade)
    xc1 = xIB + a + 1.4                                                  # rechter Rand, Reihe 1
    xc2 = (xWM + a + xST) / 2                                            # rechter Rand, Reihe 2
    ax.add_patch(Polygon([(xa1, ym), (xa1, yt), (xc1, yt), (xc1, ym), (xc2, ym), (xc2, yb),
                          (xa2, yb), (xa2, ym)], closed=True, fc="none", ec=INK, lw=0.7, ls=dash,
                         joinstyle="round"))
    ax.plot([xab1, xab1, xab2, xab2], [yt, ym, ym, yb], color=INK, lw=0.7, ls=dash)
    ax.plot([xbc, xbc], [yt, yb], color=INK, lw=0.7, ls=dash)
    # --- Zeigerlinien mit Punkt und Beschriftung (Linie, Text rechts daneben wie in der Vorlage)
    yl1 = yb + 7.0
    yl2 = yb + 15.5
    def zeiger(x, y_ende, y_text, s):
        linie(ax, x, ym, x, y_ende, lw=0.6)
        ax.add_patch(Circle((x, ym), 0.9, fc=INK, ec=INK, lw=0.4))
        text(ax, x + 1.6, y_text, s, fs=7.0, ha="left", va="center")
    zeiger(xH + off_l + 1.5 * pt + a / 2, yl2 + 2.2, yl2, "Tasten mit Rollensperre")
    zeiger(xT + off_l + a / 2, yl1 + 2.2, yl1, "Schalter mit Rollensperre")
    zeiger(xB + off_r + 4.5 * pt + a / 2, yl1 + 7.0, yl1 + 2.0, "Tasten mit Entriegelung und\nRollensperre")
    # --- Tasten
    for n, x in (("H", xH), ("E", xH + pt), ("M", xH + 2 * pt), ("T", xT)):
        taste(ax, x, y1, main=n, fs=8.5)
    for n, x in (("R", xH + off_l), ("G", xH + pt + off_l), ("Ü", xH + 2 * pt + off_l), ("SW", xT + off_l)):
        taste(ax, x, y2, main=n, fs=8.5)
    for i, n in enumerate(["B", "+", "1", "3", "5", "7", "9", "·", ":"]):
        taste(ax, xB + i * pt, y1, main=n, fs=8.5)
    for i, n in enumerate(["D", "−", "0", "2", "4", "6", "8", ",", "ZR"]):
        taste(ax, xB + i * pt + off_r, y2, main=n, fs=8.5)
    taste(ax, xIS, y1, main="IS", fs=8.0)
    taste(ax, xIB, y1, main="IB", fs=8.0)
    taste(ax, xWM, y2, main="WM", fs=8.0)
    taste(ax, xST, y2, main="ST", fs=8.0)
    text(ax, 5.0, H - 4.0,
         "Gestrichelt umrandet: Tastengruppen mit Rollensperre bzw. Entriegelung (Vorlage: „Tastatur des C 8205“).",
         fs=6.3, ha="left", color=MUTED)
    speichern(fig, "C8205-Abb-Tastatur_Bedienpult", ziel)


# ---------------------------------------------------------------------------- Abbildung 3: Schreibwerk-Tastatur
def schreibwerk_tastatur(ziel):
    """Schreibwerktastatur. Vorlagen: Zeichnung 'Tastatur des Schreibwerkes', Bedienungsanleitung Abb. 14
    (Foto) und Abb. 13 (Teileliste). Die Taste mit zwei Kreisen ist der Eingabetaster der Blockmarke BM."""
    W, H = 190, 100
    fig, ax = neue_flaeche(W, H)
    a, pt = 8.2, 9.8
    y0, y1, y2, y3, y4 = 14.0, 25.5, 37.0, 48.5, 63.0
    x0 = 16.0
    def pos(zeile_off, i):
        return x0 + zeile_off + i * pt
    # Reihe 0: Randversteller, Ziffern (oben Grossbuchstabenlage, unten Kleinbuchstabenlage), ...
    r0 = [("<", "1"), ('"', "2"), ("≈", "3"), ("[", "4"), (">", "5"), ("'", "6"), ("≋", "7"),
          ("~", "8"), ("]", "9"), ("#", "0"), ("?", ",")]
    taste(ax, pos(0, 0), y0, main="|", fs=9)
    for i, t in enumerate(r0):
        taste(ax, pos(0, i + 1), y0, oben=t[0], unten=t[1], fs=8.5)
    xk = pos(0, 12)                                                  # Taste mit zwei Kreisen: Eingabetaster Blockmarke BM
    taste(ax, xk, y0)
    for fy in (0.31, 0.71):
        ax.add_patch(Circle((xk + a / 2, y0 + a * fy), 1.2, fc="none", ec=INK, lw=0.8, zorder=4))
    taste(ax, pos(0, 13), y0, main="→", fs=9)                      # Ruecktaste
    taste(ax, pos(0, 14), y0, main="−", fs=9)                      # Tab. loeschen
    # Reihe 1
    o1 = 4.9
    for i, c in enumerate("QWERTZUIOP"):
        taste(ax, pos(o1, i), y1, main=c, fs=8.5)
    taste(ax, pos(o1, 10), y1, oben="(", unten=":", fs=8.5)
    taste(ax, pos(o1, 11), y1, oben="=", unten="+", fs=8.5)
    taste(ax, pos(o1, 12), y1, main="+", fs=9)                     # Tab. setzen
    # Reihe 2
    o2 = o1 + 5.2
    for i, c in enumerate("ASDFGHJKL"):
        taste(ax, pos(o2, i), y2, main=c, fs=8.5)
    taste(ax, pos(o2, 9), y2, oben=";", unten="`", fs=8.5)
    taste(ax, pos(o2, 10), y2, oben=")", unten="/", fs=8.5)
    taste(ax, pos(o2, 11), y2, oben="£", unten="$", fs=8.5)              # Pfundzeichen / Dollar, eingabefaehig
    # Reihe 3
    o3 = o1
    taste(ax, pos(o3, 0), y3, main="KB", fs=8.0)
    for i, c in enumerate("YXCVBNM"):
        taste(ax, pos(o3, i + 1), y3, main=c, fs=8.5)
    taste(ax, pos(o3, 8), y3, oben="*", unten="%", fs=8.5)
    taste(ax, pos(o3, 9), y3, oben="!", unten=".", fs=8.5)
    taste(ax, pos(o3, 10), y3, oben="△", unten="-", fs=8.0)
    taste(ax, pos(o3, 11), y3, main="GB", fs=8.0)
    # Reihe 4: Zeilenschaltung, Leertaste, Tabulatorausloesung
    taste(ax, pos(o2, 0), y4, w=12.4, main="↑", fs=10)
    taste(ax, pos(o2, 0) + 16.5, y4, w=88.0, main=None)
    taste(ax, pos(o2, 0) + 16.5 + 88.0 + 4.6, y4, w=12.4, main="←", fs=10)
    # hohe Taste links: Wagenruecklauf ohne Zeilenschaltung (Bedienungsanleitung Abb. 13, Nr. 71)
    ly0, ly1 = y2 - 1.0, y2 + 2 * 11.5 + a - 1.0
    ax.add_patch(FancyBboxPatch((6.0, ly0), 7.0, ly1 - ly0, boxstyle="round,pad=0,rounding_size=1.1",
                                fc="white", ec=INK, lw=LW, zorder=3))
    text(ax, 9.5, (ly0 + ly1) / 2, "→|", fs=8.5, zorder=4)
    linie(ax, 9.5, ly1, 9.5, ly1 + 3.0, lw=0.6)
    text(ax, 3.0, ly1 + 4.0, "Wagenrücklauf\nohne Zeilen-\nschaltung", fs=6.8, ha="left", va="top")
    # hohe Taste rechts: WRZL
    xw = pos(o1, 12) + 14.2
    wy0, wy1 = y1 + a / 2 + 2.2, y3 + a + 1.2          # WRZL-Taste: unter der Linie von "Tab. setzen"
    ax.add_patch(FancyBboxPatch((xw, wy0), 7.0, wy1 - wy0, boxstyle="round,pad=0,rounding_size=1.1",
                                fc="white", ec=INK, lw=LW, zorder=3))
    text(ax, xw + 3.5, (wy0 + wy1) / 2, "↵", fs=10, zorder=4)
    # Beschriftungen mit Hilfslinien
    def marke(xk_, yk_, xt, yt, s_, ha="center", va="center"):
        linie(ax, xk_, yk_, xt, yt, lw=0.6)
        text(ax, xt if ha == "center" else xt + (1.2 if ha == "left" else -1.2), yt, s_, fs=7.0, ha=ha, va=va)
    marke(pos(0, 0) + a / 2, y0, pos(0, 0) + a / 2, y0 - 4.0, "Randversteller", ha="left", va="bottom")
    marke(pos(0, 13) + a / 2, y0, pos(0, 13) + a / 2, y0 - 4.0, "Rücktaste", ha="center", va="bottom")
    xbm = pos(0, 12) + 2.0                                           # Eingabetaster BM: Beschriftung hoeher, damit sie nicht an "Rücktaste" stösst
    linie(ax, xbm, y0, xbm, y0 - 8.5, lw=0.6)
    text(ax, xbm - 1.2, y0 - 8.5, "Eingabetaster Blockmarke BM", fs=7.0, ha="right", va="center")
    marke(pos(0, 14) + a, y0 + a / 2, pos(0, 14) + a + 4.0, y0 + a / 2, "Tab. löschen", ha="left")
    marke(pos(o1, 12) + a, y1 + a / 2, xw + 7.0 + 3.0, y1 + a / 2, "Tab. setzen", ha="left")
    marke(xw + 3.5, wy1, xw + 3.5, wy1 + 4.0, "WRZL", ha="center", va="top")
    xz = pos(o2, 0) + 6.2
    marke(xz, y4 + a, xz, y4 + 15.5, "Zeilenschaltung-ZV", ha="left", va="top")
    xs_ = pos(o2, 0) + 16.5 + 44.0
    marke(xs_, y4 + a, xs_, y4 + 15.5, "Leertaste-ZWR", ha="center", va="top")
    xt_ = pos(o2, 0) + 16.5 + 88.0 + 4.6 + 6.2
    marke(xt_, y4 + a, xt_, y4 + 15.5, "Tab. Auslösung", ha="center", va="top")
    # Legende
    text(ax, 5.0, H - 5.5,
         "Tasten mit zwei Zeichen: oben Großbuchstabenlage, unten Kleinbuchstabenlage; KB / GB schalten die Lage um.",
         fs=6.3, ha="left", color=MUTED)
    speichern(fig, "C8205-Abb-Tastatur_Schreibwerk", ziel)


def finde_wurzel():
    """Projektwurzel = naechster Ordner ueber diesem Skript, der markdown-dateien/ enthaelt."""
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(d, "markdown-dateien")):
            return d
        p = os.path.dirname(d)
        if p == d:
            sys.exit("Ordner markdown-dateien/ oberhalb von %s nicht gefunden (Ausgabeverzeichnis als Argument angeben)."
                     % os.path.dirname(os.path.abspath(__file__)))
        d = p


if __name__ == "__main__":
    ziel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(finde_wurzel(), "markdown-dateien", "abbildungen")
    os.makedirs(ziel, exist_ok=True)
    lampenfeld(ziel)
    pult_tastatur(ziel)
    schreibwerk_tastatur(ziel)
    print("fertig:", ziel)
