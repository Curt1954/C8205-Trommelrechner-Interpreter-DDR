#!/usr/bin/env python3
"""zt_zeitmodell.py -- Zeitmodell der Zusatztrommeln (ZT) des C 8205Z gegen die Haupttrommel (HT).

Aufruf:  python3 -I zt/zt_zeitmodell.py [--luecke MS] [--simple]
  --luecke MS  Zeit zwischen Blockende und Ausgabe des naechsten E/A-Befehls (Vorgabe 0,3 ms)
Annahmen (Stand 25.10.2026, Inhaber): HT 32 Positionen zu 104 us; ZT 32 Sektoren zu 625 us (20 ms/Umlauf);
Block = 8 Worte; HT-Block = 8 physisch aufeinanderfolgende Positionen ab 0/8/16/24 (Gruppenbefehl);
ZT-Block k = ZT-Positionen p = k (mod 4), 8 Worte im Abstand 4 Sektoren (2,5 ms); zwei alternierende Puffer.
START='fliegend': Block beginnt an der ersten Position p = k (mod 4); ORDNUNG='zuerst': beginnt mit dem Block, der zuerst kommt, dann zyklisch.
--luecke = Umschaltzeit zwischen Blockende und Beginn des naechsten Blocks.
Die ZT laeuft unsynchron zur HT (Phase zufaellig); es wird ueber alle Phasen gemittelt/maximiert.
"""
import sys
HT_W = 0.104            # ms je HT-Position
HT_U = 32 * HT_W        # 3,328 ms
ZT_S = 0.625            # ms je ZT-Sektor
ZT_U = 32 * ZT_S        # 20 ms
G = 4                   # ZT-Abstand der Worte eines Blocks (Sektoren)

HT = "00 15 32 07 24 01 16 33 10 25 02 17 34 11 26 03 20 35 12 27 04 21 36 13 30 05 22 37 14 31 06 23".split()
ZT = "00 10 20 30 15 25 35 05 32 02 12 22 07 17 27 37 24 34 04 14 01 11 21 31 16 26 36 06 33 03 13 23".split()

def pruefe_folgen():
    """ZT[k::4] ergibt die vier HT-Achtergruppen (Block k = HT-Positionen 8k..8k+7)."""
    for k in range(4):
        assert ZT[k::4] == HT[8*k:8*k+8], k
    assert sorted(HT) == sorted(ZT) == sorted("%02o" % i for i in range(32))
    return True

def warte(t, takt, pos):
    """Zeit ab t bis zum naechsten Beginn der Position pos (Takt je Position, 32 Positionen)."""
    u = 32 * takt
    ph = (t - pos * takt) % u
    return 0.0 if ph < 1e-9 else u - ph

def ht_block(t, j):
    """HT-Gruppenbefehl auf Block j ab Zeit t -> Ende (Warten auf Position 8j, dann 8 Worte)."""
    t += warte(t, HT_W, 8 * j)          # HT-Phase absolut: Position 0 bei t=0
    return t + 8 * HT_W

START = 'fliegend'   # 'fliegend': Block beginnt an der ersten ZT-Position p = k (mod 4) nach t (Puffer nimmt Worte in beliebiger Reihenfolge)
                     # 'fest': Block beginnt erst an ZT-Position k (konservativ, bis 20 ms Anlauf)

def zt_block(t, k, phase):
    """ZT-Block k ab t (ZT-Phase 'phase' ms verschoben) -> (Start, Ende). Dauer 18,125 ms (8 Worte im Abstand 4 Sektoren)."""
    ts = t - phase
    if START == 'fest':
        ts += warte(ts, ZT_S, k)
    else:
        n = int(-(-(ts - 1e-9) // ZT_S))              # naechste beginnende ZT-Position
        while n % 4 != k: n += 1
        ts = n * ZT_S
    ende = ts + (7 * G + 1) * ZT_S
    return ts + phase, ende + phase

ORDNUNG = 'zuerst'   # 'zuerst': beginnt mit dem Block, dessen ZT-Anfang zuerst kommt (dann zyklisch); 'fest': 0..3

def blockfolge(t, phase_zt):
    """Reihenfolge der vier Bloecke ab Zeit t."""
    if ORDNUNG == 'fest': return [0, 1, 2, 3]
    pos = int(-(-(t - phase_zt) // ZT_S)) % 32          # naechste ZT-Position, die beginnt
    return [(pos + i) % 4 for i in range(4)]

def spur_ein(phase_zt, phase_ht, luecke, doppelpuffer=True):
    """Eingabe 461: ZT -> Puffer -> HT. Zeit fuer 4 Bloecke."""
    t = phase_ht                         # Befehl 1 wird zum Zeitpunkt phase_ht (in HT-Zeit) ausgegeben
    ht_frei = 0.0; frei = [0.0, 0.0]; ende = 0.0
    folge = blockfolge(t, phase_zt)
    for n, b in enumerate(folge):
        pb = n % 2 if doppelpuffer else 0
        t = max(t, frei[pb])                              # Puffer muss leer sein
        s, e = zt_block(t, b, phase_zt)
        h0 = max(e, ht_frei)
        he = ht_block(h0 - 0.0, b) if True else 0
        ht_frei = he; frei[pb] = he; ende = he
        cpu = e                                           # Befehl endet mit dem ZT-Teil, HT-Schreiben im Hintergrund
        t = e + luecke                                    # naechster Befehl nach Blockende (ZT frei)
        if not doppelpuffer: t = max(t, he)
    return ende - phase_ht, cpu - phase_ht

def spur_aus(phase_zt, phase_ht, luecke, doppelpuffer=True):
    """Ausgabe 401: HT -> Puffer -> ZT. Zeit fuer 4 Bloecke."""
    t = phase_ht; zt_frei = 0.0; frei = [0.0, 0.0]; ende = 0.0; ht_t = t
    folge = blockfolge(t, phase_zt)
    for n, b in enumerate(folge):
        pb = n % 2 if doppelpuffer else 0
        ht_t = max(ht_t, frei[pb])
        he = ht_block(ht_t, b)
        s, e = zt_block(max(he, zt_frei), b, phase_zt)
        zt_frei = e + luecke; frei[pb] = e; ende = e
        ht_t = he
        cpu = he                                          # Befehl endet mit dem HT-Teil, ZT-Schreiben im Hintergrund
        if not doppelpuffer: ht_t = max(ht_t, e)
    return ende - phase_ht, cpu - phase_ht

IDX = 0   # 0 = Gesamtzeit einschliesslich Hintergrund, 1 = Zeit, die der Rechner im Befehl wartet

def statistik(f, luecke, n=64, **kw):
    w = []
    for i in range(n):
        for j in range(n):
            w.append(f(i * ZT_U / n, j * HT_U / n, luecke, **kw)[IDX])
    return min(w), sum(w) / len(w), max(w)

def einzel():
    """Einzeladresse (Lesen-Aendern-Schreiben) und synchron aktuelle Bloecke, Angaben des Inhabers."""
    lesen = ZT_U                       # ein Umlauf ZT
    aender = HT_U                      # bis 1 HT-Umlauf (3,33 ms)
    return lesen + aender + ZT_U, aender + ZT_U

if __name__ == "__main__":
    luecke = 0.3
    if "--luecke" in sys.argv: luecke = float(sys.argv[sys.argv.index("--luecke") + 1])
    print("Folgen pruefen (ZT[k::4] = HT-Achtergruppe k):", pruefe_folgen())
    print("HT-Umlauf %.3f ms, 8 Worte %.3f ms, Block bis 4*Wort-Schritt... Wartemax %.3f ms" % (HT_U, 8*HT_W, HT_U))
    print("ZT-Umlauf %.1f ms, Faktor ZT/HT = %.2f, Block (8 Worte im Abstand %d Sektoren) = %.3f ms" % (ZT_U, ZT_U/HT_U, G, (7*G+1)*ZT_S))
    print("Kette mit festem Start an Position k (konservativ): Block k+1 beginnt %.3f ms nach Beginn des Umlaufs; Spur 4 Bloecke = %.3f ms" % (ZT_S, 3*(ZT_U+ZT_S)+(7*G+1)*ZT_S))
    ei, ae = einzel()
    print("Einzeladresse: lesen+aendern+schreiben ca. %.1f ms; Block bei synchron aktuell ca. %.1f ms (Angabe Inhaber 44 / 24)" % (ei, ae))
    print("Spur, Lücke %.2f ms (min / Mittel / max in ms):" % luecke)
    for name, f in (("Eingabe 461", spur_ein), ("Ausgabe 401", spur_aus)):
        for dp in (True, False):
            print("  %s %-14s %6.1f %6.1f %6.1f" % (name, "Doppelpuffer" if dp else "ein Puffer", *statistik(f, luecke, doppelpuffer=dp)))
    print("  Angabe Inhaber: 4,2 + 4*20 = 85 ms je Spur")
    print("Luecke -> Spur (Eingabe, Doppelpuffer, Max):")
    for l in (0.0, 0.3, 1.0, 2.0, 2.5, 3.0, 5.0):
        print("  Luecke %.1f ms: %.1f ms" % (l, statistik(spur_ein, l, n=32)[2]))
