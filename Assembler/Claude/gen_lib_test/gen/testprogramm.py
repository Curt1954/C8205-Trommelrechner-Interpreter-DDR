#!/usr/bin/env python3
"""testprogramm.py -- gemeinsamer Aufbau der Pruefprogramme der Bibliothek c82gen (gen_lib_test und gen_lib_test_archiv).

Das Programm prueft jede Idiom-Gruppe der Bibliothek im Interpreter; die Sollwerte kommen aus dem Python-Modell hier,
nicht aus einem Lauf:
  1. Schieben:      schiebe_links (zyklisch) und schiebe_rechts fuer n = 1 bis 32, je nach schiebespur W-Transport auf 7640 (026) oder Nullspur im Programm (612/616)
  2. Unterprogramme: inner (zwei Ausgaenge) wird von outer zweimal und von haupt einmal gerufen (Rueckkehrzelle am UP-Ende, Festlegung 010)
  3. Kurzidiome:    setze, kopiere, erhoehe, subtrahiere, wenn_* (Sprung und kein Sprung)
  4. Felder:        feld_schreiben, feld_lesen
  5. Ausgabe:       text, zahl_ausgeben (4 Oktalziffern), ziffer_ausgeben -> Schreibwerk-Datei
  6. Eingabe:       eingabetafel, eingabe_init, zeichen_lesen ueber K0: Zeichen 2 (Wert), J (Standardwert), A (Sprung)
Aufruf des Aufbaus: bauen(archiv, basis, schiebespur) liefert (P, pruefe, name); basis = Ladeadresse im Test (Archivfall 040 modulo 0100: zweite Eingabetafel);
schiebespur = None (Vorgabe: Normalmodus w7640, Archivmodus nullspur), 'w7640' oder 'nullspur'.
"""
import os
import sys

hier = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(hier, '..', '..', 'gen_lib'))
from c82gen import Prog, AE   # noqa: E402

M33 = (1 << 33) - 1


def rotl(w, n):
    return ((w << n) | (w >> (33 - n))) & M33


def bauen(archiv, basis=None, schiebespur=None):
    name = ('gen_lib_test_archiv' + ('040' if basis else '')) if archiv else 'gen_lib_test'
    P = Prog('Pruefprogramm der Bibliothek c82gen (%s)' % (('Archivmodus' + (', Ladeadresse %04o' % basis if basis else '')) if archiv else 'Normalmodus'), grenze=0o2000, archiv=archiv, schiebespur=schiebespur)
    if archiv:
        P.kopf = ['Archivmodus (Zelle 0000 = Sprung, nur dbn, benannte Konstanten, zwei Eingabetafeln); der Test laeuft ab Zelle 0000.']
    P.pragma('#DOK-0001 Pruefprogramm c82gen: Schieben, UP, Kurzidiome, Felder, Ausgabe, Eingabetafel (%s)' % ('Archivmodus' if archiv else 'Normalmodus'))
    P.pragma('--sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/%s.txt' % name)
    P.pragma('--k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/gen_lib_test.txt')
    P.pragma('--pruefe-sw-ausgabe Test-Ergebnisvergleiche/gen_lib_test-sw-ausgabe.txt')
    P.pragma('#TASTENFOLGE H SW=1 G R')           # Buchstaben ueber K0 nur mit gedrueckter Taste SW
    soll = {}

    # ---- Daten (Tafel zuerst angelegt, damit die Ausrichtung im Layout frueh steht) ------------------
    P.eingabetafel('tk', {2: 2, 0o21: 'ja'}, standard=0o77, namen={2: '2', 0o21: 'A'})

    # ---- 1. Schieben ---------------------------------------------------------------------------------
    PN = 0o57012345671 - (1 << 33)          # 33-Bit-Muster mit gesetztem Vorzeichenbit (negativ)
    PR = 0o07123456701                      # positives Muster fuer Rechtsverschiebung
    if archiv:
        P.lab('haupt')                      # Ziel des Sprungs in Zelle 0000 (nur Archivmodus)
    P.var('pn', PN, 'Muster mit Vorzeichenbit')
    P.var('pr', PR, 'Muster positiv')
    for n in range(1, 33):
        P.laden('pn')
        P.schiebe_links(n)
        P.speichere('l%d' % n)
        P.arbeit('l%d' % n, 'Ergebnis links %d' % n)
        soll['l%d' % n] = rotl(PN & M33, n)
    for n in range(1, 33):
        P.laden('pr')
        P.schiebe_rechts(n)
        P.speichere('r%d' % n)
        P.arbeit('r%d' % n, 'Ergebnis rechts %d' % n)
        soll['r%d' % n] = PR >> n

    # ---- 2. Unterprogramme ----------------------------------------------------------------------------
    P.nullen('px')
    P.aufruf('outer')
    P.setze('px', 7)
    P.aufruf('inner')
    P.kopiere('ri', 'rd')
    for v in ('px', 'ri', 'ra', 'rb', 'rs', 'rd'):
        P.arbeit(v, 'Zelle ' + v)
    soll.update({'ra': 100, 'rb': 6, 'rs': 106, 'rd': 8, 'ri': 8})

    # ---- 3. Kurzidiome ----------------------------------------------------------------------------------
    P.setze('x', 5)
    P.setze('y', 7)
    P.setze('neg', -3)
    P.nullen('cnt')
    for _ in range(3):
        P.erhoehe('cnt', '#1')
    P.laden('y')
    P.subtrahiere('x')
    P.speichere('dif')
    P.kopiere('dif', 'dif2')
    for v in ('x', 'y', 'neg', 'cnt', 'dif', 'dif2'):
        P.arbeit(v, 'Zelle ' + v)
    soll.update({'cnt': 3, 'dif': 2, 'dif2': 2, 'neg': (-3) & M33})

    def zweig(r, wenn, *args, erwartet):
        t, w = P.neu('t'), P.neu('w')
        wenn(*args, t)
        P.nullen(r)                         # kein Sprung
        P.sprung(w)
        P.lab(t)
        P.setze(r, 1)                       # Sprung
        P.lab(w)
        P.arbeit(r, 'Sprungergebnis ' + r)
        soll[r] = erwartet
    zweig('c1', P.wenn_kleiner_gleich, 'x', 'y', erwartet=1)        # 5 <= 7
    zweig('c2', P.wenn_groesser_gleich, 'x', 'y', erwartet=0)       # 5 >= 7: nein
    zweig('c3', P.wenn_gleich, 'x', 'y', erwartet=0)                # 5 = 7: nein
    zweig('c4', P.wenn_gleich, 'y', 7, erwartet=1)                  # 7 = Konstante 7
    zweig('c5', P.wenn_negativ, 'neg', erwartet=1)
    zweig('c6', P.wenn_nichtnegativ, 'neg', erwartet=0)
    zweig('c7', P.wenn_nichtnegativ, 'x', erwartet=1)

    # ---- 4. Felder ----------------------------------------------------------------------------------------
    P.feld('fe', [11, 22, 33, 44], 'Feld')
    P.setze('ix', 2 * AE)
    P.setze('wv', 0o123)
    P.feld_schreiben('fe', 'ix', 'wv')
    P.feld_lesen('fe', 'ix')
    P.speichere('fr')
    for v in ('ix', 'wv', 'fr'):
        P.arbeit(v, 'Zelle ' + v)
    soll.update({'fe+0': 11, 'fe+1': 22, 'fe+2': 0o123, 'fe+3': 44, 'fr': 0o123})

    # ---- 5. Ausgabe -------------------------------------------------------------------------------------
    P.text('Test')
    P.setze('zahl', 0o1234)
    P.zahl_ausgeben('zahl', 4)
    P.zeichen('$wrzl')
    P.setze('d5', 5)
    P.ziffer_ausgeben('d5')
    P.zeichen('$wrzl')
    P.arbeit('zahl', 'auszugebende Zahl')
    P.arbeit('d5', 'auszugebende Ziffer')

    # ---- 6. Eingabe ---------------------------------------------------------------------------------------
    P.anwahl(0)
    P.eingabe_init('tk')
    P.zeichen_lesen('tk')
    P.speichere('z1')
    P.zeichen_lesen('tk')
    P.speichere('z2')
    P.zeichen_lesen('tk')                    # 'A': Tafelzelle 000 ja
    P.setze('z3', 0o777)                     # wird uebersprungen
    P.lab('ja')
    P.setze('z3', 1)
    P.diag(1)
    P.halt()
    for v in ('z1', 'z2', 'z3'):
        P.arbeit(v, 'Eingabeergebnis ' + v)
    soll.update({'z1': 2, 'z2': 0o77, 'z3': 1})

    # ---- Unterprogramme (hinter dem Hauptprogramm) -------------------------------------------------------
    with P.unterprogramm('inner', 'px = 0: ri := 100, sonst ri := px + 1'):
        P.wenn_gleich('px', 0, 'in_null')
        P.laden('px')
        P.addiere('#1')
        P.speichere('ri')
        P.up_ende('inner', 'Ausgang px <> 0')
        P.lab('in_null')
        P.setze('ri', 100)
    with P.unterprogramm('outer', 'inner zweimal rufen: px = 0 und px = 5'):
        P.nullen('px')
        P.aufruf('inner')
        P.kopiere('ri', 'ra')
        P.setze('px', 5)
        P.aufruf('inner')
        P.kopiere('ri', 'rb')
        P.laden('ra')
        P.addiere('rb')
        P.speichere('rs')
    return P, soll, name
