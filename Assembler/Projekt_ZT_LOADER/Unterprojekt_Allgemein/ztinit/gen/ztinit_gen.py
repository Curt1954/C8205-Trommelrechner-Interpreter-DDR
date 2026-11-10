#!/usr/bin/env python3
"""ztinit_gen.py -- erzeugt ztinit.asm (und ueber ztinit_vor/gen/ztinit_vor_gen.py die Variante ztinit_vor.asm) mit der Bibliothek c82gen (0.01-005).

Test des Unterprogramms ztinit (Makro ZTINIT aus macro_zt_loader.macro; ZT-Repository_Aufgabenstellung 6a), nur mit --C8205Z lauffaehig:
  1. Vorbelegung: Der Spurpuffer spuf00 (Zellen 0, 1, 5, 17, 18, 23 und 31 dezimal mit 0111, 0222, 0777, 0444, 0666, 0555 und 0333 belegt) wird mit zt_schreibe auf sieben
     ZT-Spuren ausgegeben: ZT3 Spur 127, ZT3 Spur 63, ZT2 Spur 64 (ab hier ist zzz0 negativ), ZT1 Spur 0, ZT0 Spur 1, ZT0 Spur 127, ZT0 Spur 0.
  2. R1 := Adresse spuf00, 025 ztinit.
  3. Ausgabe von spuf00 (jetzt Spur 0) auf ZT0 Spur 2 OHNE neue Anwahl (601 von Hand gebildet): gelingt nur, wenn ZT 0 am Ende angewaehlt ist. Halt.
Variante vor=True (ztinit_vor): Halt nach der Vorbelegung, ohne ztinit; beweist, dass die vorbelegten ZT-Zellen vorher ungleich 0 sind.
Die Sollwerte kommen aus dem Python-Modell unten, nicht aus einem Lauf.
Aufruf (vom Projektstamm): python3 -I Assembler/Projekt_ZT_LOADER/Unterprojekt_Allgemein/ztinit/gen/ztinit_gen.py"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
STAMM = os.path.abspath(os.path.join(HIER, '..', '..', '..', '..'))              # .../Assembler
sys.path.insert(0, os.path.join(STAMM, 'Claude', 'gen_lib'))
from c82gen import Prog

MAKRODATEI = os.path.join(STAMM, 'Projekt_ZT_LOADER', 'macro_zt_loader.macro')
VORBELEGT = [(3, 127), (3, 63), (2, 64), (1, 0), (0, 1), (0, 127), (0, 0)]      # (Zusatztrommel, Spur) mit dem Muster belegt
MUSTER = {0: 0o111, 1: 0o222, 5: 0o777, 17: 0o444, 18: 0o666, 23: 0o555, 31: 0o333}   # Zelle (dezimal) -> Wert in spuf00 vor ztinit
SPUR0 = {0: 0o52525252525, 16: 1, 19: 0o40}                                      # Spur 0 von ZT 0 nach ztinit (Zellen 17, 18 und der Rest = 0); Zelle 19 = 32 dezimal = 040 (seit 09.11.2026, kat5-Verzeichnis Spuren 1 bis 32; vorher 060)


def bauen(vor):
    """Liefert (P, pruefe, ztpruefe, name)."""
    name = 'ztinit_vor' if vor else 'ztinit'
    P = Prog(name, grenze=0o7600)
    P.pragma('#MACRODATEI1=../../macro_zt_loader.macro')
    P.pragma('#DOK-0001 ' + ('ztinit_vor: nur die Vorbelegung der Zusatztrommeln, ztinit wird nicht aufgerufen' if vor
                             else 'ztinit: alle vier ZT loeschen, Spur 0 von ZT 0 anlegen, ZT 0 am Ende angewaehlt'))
    P.pragma('#SPEI-0001 0001-0001')
    P.pragma('#PROT STUFE=2')
    P.pragma('#ZTROMMEL=LEER')
    P.absolut('r1', 0o7773, 'Register 1: Adresse von SPUF-00 fuer ztinit')
    for d, sp in VORBELEGT:
        P.zt_schreibe('#%d' % d, '#%d' % sp, 'spuf00', 'ZT%d Spur %d mit spuf00 belegen' % (d, sp))
    if not vor:
        P.laden(P.adresse_von('spuf00'), 'AC := Adresse SPUF-00')
        P.speichere('r1', 'R1 := Adresse SPUF-00')
        P.aufruf('ztinit', 'UP ztinit: alle ZT loeschen, Spur 0 anlegen, ZT 0 angewaehlt')
        P.laden(P.adresse_von('spuf00'), 'AC := Adresse SPUF-00 (jetzt Spur 0)')
        P.addiere('#01000000601', 'plus Spurfeld zzz0 = 0100 (Spur 2) und Operationscode 601')
        P.speichere('nach', 'Ausgabebefehl auf die naechste Zelle')
        P.lab('nach')
        P.op('db', 1, 'Laufzeit: Ausgabe auf ZT0 Spur 2 OHNE neue Anwahl')
    P.halt()
    if not vor:
        P.lab('ztinit')
        P.makro('ZTINIT', makrodatei=MAKRODATEI, k='Unterprogramm ztinit (Makro aus macro_zt_loader.macro)')
    P.ausrichten(32, 0, 'SPUF-00 auf die Spurgrenze')
    P.feld('spuf00', [MUSTER.get(i, 0) for i in range(32)], 'spuf00')
    # ---- Python-Modell der Sollwerte ----------------------------------------------------------------
    zt = {}                                       # (Trommel, ZT-Adresse) -> Wert; nicht genannte Zellen sind 0 (#ZTROMMEL=LEER)
    for d, sp in VORBELEGT:
        for c, v in MUSTER.items():
            zt[(d, sp * 32 + c)] = v
    soll = []                                     # Pruefzeilen (Trommel, Adresse, Wert, Kommentar)
    nie = [(1, 0o40), (3, 0), (0, 0o140) if not vor else (0, 0o100)]            # nie beschriebene Zellen: bleiben 0
    if vor:
        for d, sp in VORBELEGT:
            for c, v in MUSTER.items():
                soll.append((d, sp * 32 + c, v, 'vorbelegt'))
        pruefe = {}
    else:
        zt = {}                                   # nach ztinit sind alle Zellen 0 ausser Spur 0 von ZT 0 ...
        for c in range(32):
            zt[(0, c)] = SPUR0.get(c, 0)
            zt[(0, 0o100 + c)] = SPUR0.get(c, 0)  # ... und der Kopie auf ZT0 Spur 2 (Ausgabe ohne neue Anwahl)
        for c in range(32):
            soll.append((0, c, zt[(0, c)], 'ZT0 Spur 0'))
        for d, sp in VORBELEGT:
            if (d, sp) != (0, 0):
                for c in sorted(MUSTER):
                    soll.append((d, sp * 32 + c, 0, 'geloescht'))
        for c in range(32):
            soll.append((0, 0o100 + c, zt[(0, 0o100 + c)], 'ZT0 Spur 2 = Kopie von Spur 0 (ZT 0 angewaehlt)'))
        pruefe = {('spuf00' if c == 0 else 'spuf00+%d' % c): SPUR0.get(c, 0) for c in range(32)}
    for d, a in nie:
        soll.append((d, a, 0, 'nie beschrieben'))
    return P, pruefe, soll, name


def schreibe(vor):
    P, pruefe, soll, name = bauen(vor)
    pfad = os.path.join(HIER, '..', '..', name, name + '.asm')
    pfad = os.path.abspath(pfad)
    P.schreibe(pfad, pruefe=pruefe, ztpruefe=soll, gen_name='gen/%s_gen.py' % name)


if __name__ == '__main__':
    schreibe(False)
