#!/usr/bin/env python3
"""zil_variante.py -- gemeinsame Hilfe der Generatoren zil_nein_gen.py und zil_keinrepo_gen.py (Projekt ZT-Loader, ZIL).

Die Varianten sind Kopien von zil/zil.asm, die sich nur in Platzhalterwert (d_repo), Testkopf (Eingabedatei, Leser-1-Streifen, Ausgabeordner, Sollwertdatei)
und Sollwerten unterscheiden. Der Ablauf wird nur in zil/zil.asm gepflegt; die erzeugten .asm nie von Hand aendern.
Aufruf der Generatoren (vom Projektstamm): python3 -I <ordner>/gen/<name>_gen.py (asm_und_test.sh tut das selbst).
"""
import os

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = os.path.join(HIER, '..', 'zil.asm')


def ersetze(zeilen, anfang, neu):
    """Ersetzt genau die eine Zeile, die mit 'anfang' beginnt (sonst Abbruch)."""
    treffer = [i for i, z in enumerate(zeilen) if z.startswith(anfang)]
    assert len(treffer) == 1, (anfang, treffer)
    zeilen[treffer[0]] = neu
    return zeilen


def erzeuge(name, ordner, dok, d_repo, eingabe, soll_text, pruefe, kommentar, leser1=None):
    """Schreibt <ordner>/<name>.asm. eingabe = Name der Eingabedatei oder None (dann entfaellt die --k0-Zeile); leser1 = Streifen in Test-virtuelleGeraete/Leser1/ (hschl_zil.txt bleibt, wenn None; Varianten ohne Lesen des Streifens behalten die Zeile ebenfalls)."""
    with open(QUELLE, encoding='utf8') as f:
        zeilen = f.read().split('\n')
    ende = [i for i, z in enumerate(zeilen) if z.startswith('; Sollwerte von Hand hergeleitet')]
    assert len(ende) == 1
    zeilen = zeilen[:ende[0]]
    zeilen.insert(0, '; %s.asm - ERZEUGT von gen/%s_gen.py aus ../zil/zil.asm (nicht von Hand aendern). %s' % (name, name, kommentar))
    zeilen = ersetze(zeilen, ';#DOK-0001', ';#DOK-0001 ' + dok)
    if eingabe:
        zeilen = ersetze(zeilen, '; --k0 datei=', '; --k0 datei=Test-virtuelleGeraete/T-SW-Eingabe/' + eingabe)
    else:
        zeilen = [z for z in zeilen if not z.startswith('; --k0 datei=')]
    if leser1:
        zeilen = ersetze(zeilen, '; --leser1 ', '; --leser1 Test-virtuelleGeraete/Leser1/' + leser1)
    zeilen = ersetze(zeilen, '; --sw-ausgabe ', '; --sw-ausgabe Test-virtuelleGeraete/SW-Ausgabe/' + name)
    zeilen = ersetze(zeilen, '; --pruefe-sw-ausgabe ', '; --pruefe-sw-ausgabe Test-Ergebnisvergleiche/%s-sw-ausgabe.txt' % name)
    if d_repo != 1:
        zeilen = ersetze(zeilen, 'd_repo:', 'd_repo:         dw      %d                    ; Zelle 0006: Platzhalter-Ergebnis von repo (Variante: kein Repository)' % d_repo)
    import textwrap
    for z in soll_text.rstrip('\n').split('\n'):
        if len(z) > 240 and z.startswith(';'):
            teile = textwrap.wrap(z[1:].strip(), width=200)
            zeilen.append('; ' + teile[0])
            zeilen += [';     ' + x for x in teile[1:]]
        else:
            zeilen.append(z)
    zeilen += [';#PRUEFE-START'] + ['; ' + p for p in pruefe] + [';#PRUEFE-ENDE', '']
    with open(os.path.join(ordner, name + '.asm'), 'w', encoding='utf8', newline='\n') as f:
        f.write('\n'.join(zeilen))
