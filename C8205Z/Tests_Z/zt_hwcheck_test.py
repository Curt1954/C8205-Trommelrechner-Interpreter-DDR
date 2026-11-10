# -*- coding: utf-8 -*-
"""zt_hwcheck_test.py - prueft die Anzeige der Zusatztrommeln im HW-Check (--HWCHECK --C8205Z) ohne Fenster (mit Tk-Attrappe).
Aufruf (von ueberall): python3 C8205Z/Tests_Z/zt_hwcheck_test.py   Voraussetzung: Erweiterungsmodul c8205_ztmodul gebaut (mit --force, siehe zt_grafik_tests.sh). Immer mit python3 starten (keine Shebang-Zeile).
Rueckgabe 0 = alles ok. Der Test benutzt eine Attrappe der Haupttrommel (Woerterbuch) und einen Wegwerf-Ordner fuer zt1..zt4.
"""
import os, sys, tempfile
HIER = os.path.dirname(os.path.abspath(__file__))
STAMM = os.path.dirname(os.path.dirname(HIER))
sys.path.insert(0, STAMM)
sys.path.insert(0, os.path.join(STAMM, 'grafik-interpreter-module'))
sys.path.insert(0, os.path.join(STAMM, 'C8205Z', 'zt_modul', 'python'))
import grafik_zt, grafik_hwcheck as H

fehler = 0
def pruefe(bed, text):
    global fehler
    if not bed:
        fehler += 1
        print('FEHLER:', text)

class T:                                   # Attrappe der Haupttrommel (Direktzugriffe)
    def __init__(self): self.m = {}
    def lesen(self, a): return self.m.get(a, 0)
    def schreiben(self, a, w): self.m[a] = w & ((1 << 33) - 1); return 0
    def aktueller_sektor(self): return 0
class Trommel:
    zeitmodell = 'schnell'; vt = 0
    def __init__(self): self.T = T()
    def _pace(self): pass

class Label:                               # Attrappe von tkinter.Label
    def __init__(self, win, **kw): self.o = dict(kw)
    def grid(self, **kw): pass
    def configure(self, **kw): self.o.update(kw)
class Toplevel:
    def __init__(self, root): pass
    def title(self, t): pass
    def resizable(self, a, b): pass
    def protocol(self, n, f): pass
    def geometry(self, g): pass
class TK:
    Label = Label; Toplevel = staticmethod(Toplevel)

class Maschine:                            # nur, was der HW-Check liest
    AR = 0; BZ = 0; adr = 0; OR = 0; AC = 0; haltuhr = None
    def __init__(self, tr, zt): self.trommel = tr; self.zt = zt

with tempfile.TemporaryDirectory() as d:
    tr = Trommel()
    for i in range(32): tr.T.m[(0o11 << 5) | i] = 0o1234567 + i          # HT-Spur 011
    zt = grafik_zt.GrafikZT(d, tr, start_index=0)
    try:
        g, adr, inh = zt.ansicht()
        pruefe(g == 0 and adr == [None] * 4 and inh is None, 'Anfangszustand: keine Anwahl, keine Adresse')
        z4, inhalt = H.zt_zeilen(zt)
        pruefe([z[1] for z in z4] == ['--- --'] * 4 and not any(z[2] for z in z4), 'Anfang: vier Zeilen ohne Punkt')
        pruefe(inhalt[1] == '---- ---- ---', 'Anfang: Inhaltsfeld leer')
        zt.anwahl(3)
        zt.ausgabe(0o4000, 0o11 << 5)                                     # HT-Spur 011 -> ZT3 Spur 0100
        g, adr, inh = zt.ansicht()
        pruefe(g == 3, 'Modul-ZT 3 (= ZT2 in der Anzeige) angewaehlt')
        pruefe(adr[2] is not None and (adr[2] >> 5) == 0o100, 'ZT3: Spur 100 in der Adresse (%r)' % (adr,))
        pruefe(adr[0] is None and adr[1] is None and adr[3] is None, 'andere ZT ohne Adresse')
        pruefe(inh == zt.Z.lesen(3, adr[2]) and inh is not None and inh >= 0o1234567, 'Inhalt = Wort an der Adresse der ZT3')
        z4, inhalt = H.zt_zeilen(zt)
        pruefe([z[2] for z in z4] == [False, False, True, False], 'Punkt nur hinter ZT3')
        pruefe(z4[2][0] == 'ZT2' and z4[0][0] == 'ZT0' and z4[3][0] == 'ZT3', 'Anzeige: Zeilen heissen ZT0..ZT3')
        pruefe(z4[2][1].startswith('100 '), 'Adresszeile ZT2 beginnt mit Spur 100: %r' % (z4[2][1],))
        pruefe(inhalt[0].startswith('<<ZT2>>') and inhalt[1] != '---- ---- ---', 'ein Inhaltsfeld fuer die angewaehlte ZT')
        zt.anwahl(1)
        g, adr, inh = zt.ansicht()
        pruefe(g == 1 and inh is None, 'ZT1 angewaehlt, noch ohne Adresse: kein Inhalt (Punkt wandert, ZT3 behaelt ihre Adresse)')
        pruefe(adr[2] is not None, 'ZT3 behaelt ihre letzte Adresse')
        # Fenster mit Attrappe: sechs plus fuenf Zeilen, Punkt als Text
        m = Maschine(tr, zt)
        w = H.HwCheckFenster(None, m, tk=TK)
        pruefe(len(w._zt_namen) == 5 and w._zt_punkte[0].o.get('text') == '\u25cf', 'Fenster: Punkt hinter ZT1')
        zt.anwahl(3); w.aktualisieren()
        pruefe(w._zt_punkte[0].o.get('text') == '' and w._zt_punkte[2].o.get('text') == '\u25cf', 'Fenster: Punkt wandert zu ZT3')
        pruefe(w._zt_werte[4].o.get('text') != '---- ---- ---', 'Fenster: Inhaltsfeld gefuellt')
        w2 = H.HwCheckFenster(None, Maschine(tr, None), tk=TK)
        pruefe(w2.zt is None and not hasattr(w2, '_zt_namen'), 'ohne --C8205Z: keine Zusatzzeilen')
        pruefe(len(H.hwcheck_zeilen(m)) == 6, 'die sechs bisherigen Zeilen bleiben')
    finally:
        zt.schliessen()
print('zt_hwcheck_test:', 'ok' if fehler == 0 else f'{fehler} FEHLER')
sys.exit(1 if fehler else 0)
