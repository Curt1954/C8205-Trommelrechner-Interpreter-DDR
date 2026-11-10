#!/usr/bin/env python3
"""streifen.py -- erzeugt die Teststreifen (Leser 1) fuer das Projektmakro HSCHL (Unterprojekt Allgemein, Tests hschl*, zil*).

Jede Zeile eines Streifens hat 8 Ziffern 0/1 in der Reihenfolge der Lochspuren w v u p 8 4 2 1 (Bitwert 200 100 040 020 010 4 2 1 der Ausgabeadresse,
Kodetabellen 1.3). Die Lochbilder werden aus der Spalte "Ausgabe-Adresse" der Tabelle 1 in markdown-dateien/C8205-Interpreter-Kodetabellen.md gelesen
(unabhaengig vom Makro). Die Streifentexte (Typ-10-Eingaben, seit 01.11.2026) stehen in hschl_variante.py (streifentexte()); Streifen im Ordner Test-virtuelleGeraete/Leser1/:
  hschl.txt        17 Eingaben (Beispiele 1 bis 3 aus 7a, uebergangene Zeichen, Um. GB, Um. KB, 8/9 als Kennzeichen, 11 Siebenen, 9 weitere) und /      -> 34 Worte (16 Eingaben + 1)
  hschl_voll.txt   16 Eingaben und /                                                                                                         -> 32 Worte, eine Spur
  hschl_rand.txt   16 Eingaben, 17. Eingabe von / abgebrochen                                                                                 -> 32 Worte, die 17. wird verworfen
  hschl_ziffer.txt 3 Eingaben mit 8 und 9 (als Kennzeichen und im Ziffernteil), kein Fehler                                                  -> 6 Worte
  hschl_leer.txt   nur /                                                                                                                     -> keine Eingabe, nichts wird geschrieben
  hschl_zulang.txt 2048 Eingaben = 4096 Sektoren                                                                                             -> Fehler zu lang
  hschl_zil.txt    3 Eingaben (ZTD-Platzhalterstreifen fuer den Prototyp zil)                                                                 -> 6 Worte
Aufruf (vom Projektstamm): python3 -I Assembler/Projekt_ZT_LOADER/Unterprojekt_Allgemein/hschl/gen/streifen.py
"""
import os, re, sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
from hschl_variante import streifentexte, EA

STAMM = os.path.abspath(os.path.join(HIER, *(['..'] * 5)))
KT = os.path.join(STAMM, 'markdown-dateien', 'C8205-Interpreter-Kodetabellen.md')
AUS = os.path.join(STAMM, 'Test-virtuelleGeraete', 'Leser1')


def lochbilder():
    """Liefert [(nr, eingabeadresse, ausgabeadresse als Zahl, name)] fuer alle Zeilen der Tabelle 1."""
    text = open(KT, encoding='utf-8').read()
    a = text.index('### 1.4 Die Tabelle')
    erg = []
    for z in text[a:].splitlines():
        m = re.match(r'\|\s*(\d+)\s*\|(.*)\|\s*$', z)
        if not m:
            continue
        c = [x.strip() for x in z.strip().strip('|').split('|')]
        if len(c) < 11 or not c[0].isdigit():
            continue
        erg.append((int(c[0]), int(c[6], 8), int(c[8][:3], 8), c[1]))
    return erg


def zeile(aus):
    return format(aus, '08b')


def streifen(zeilen, name):
    """Schreibt einen Streifen (Zeilen mit 8 Ziffern 0/1) nach Test-virtuelleGeraete/Leser1/<name> (auch vom Generator typ10ein_gen.py benutzt)."""
    with open(os.path.join(AUS, name), 'w', encoding='ascii', newline='\n') as f:
        f.write('\n'.join(zeilen) + '\n')


def main():
    os.makedirs(AUS, exist_ok=True)
    tab = lochbilder()
    assert len(tab) == 55, len(tab)
    aus_von_ea = {}
    for nr, ea, aus, name in tab:
        aus_von_ea.setdefault(ea, []).append(aus)
    for name, text in streifentexte().items():
        zeilen = []
        for c in text:
            zeilen.append(format(min(aus_von_ea[EA[c]]), '08b'))
        streifen(zeilen, name)


if __name__ == '__main__':
    main()
