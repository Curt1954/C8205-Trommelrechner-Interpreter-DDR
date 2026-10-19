#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
k0_schatten_haken.py - Messwerkzeug zu Interpreter 0.03-016 (Anwahlbefehl K0 und Schalter SW).

Baut in eine KOPIE von c8205_interp.py einen Zusatz ein. Der Zusatz schreibt bei jedem Anwahlbefehl K0 (a028) eine Zeile in die Datei, die in der
Umgebungsvariablen C8205_SCHATTEN steht, wenn die alte Regel (Flag SW, bis 0.03-015) und die neue Regel (Schalterstellung m.sw_schalter)
verschieden entscheiden wuerden. Ohne die Variable tut der Zusatz nichts. Das Verhalten des Interpreters aendert er nicht.
NUR AUF EINE KOPIE ANWENDEN, nie auf das Projekt selbst.

Aufruf:  cp -a PROJEKT PROJEKT_MESSUNG
         python3 testscripte/k0_schatten_haken.py PROJEKT_MESSUNG/c8205_interp.py
         cd PROJEKT_MESSUNG && C8205_SCHATTEN=/tmp/schatten.log python3 testscripte/grafik_gleichwertigkeit.py --alle
Die Datei entsteht erst bei der ersten Abweichung: keine Datei = keine Abweichung.
Zeile: Arbeitsordner, Prozess, sw_schalter, Flag SW, BZ, Aufruf (Tabulator getrennt).
Stand 18.10.2026 (Checkpoint 24): Bei allen 193 Programmen von --alle (und den 58 von --neue-geraete) tritt eine Abweichung nur bei
sw_zwei_ziffern.test auf (BZ=24 und BZ=109); bei compute_all_tests.sh (127 Aufrufe) keine.
"""
import sys

ALT = "            m.fl['T'], m.fl['SW'] = (0, 1) if m.sw_schalter else (1, 0)"
NEU = ("            import os as _os, sys as _sys\n"
       "            _p = _os.environ.get('C8205_SCHATTEN')\n"
       "            if _p and bool(m.sw_schalter) != bool(m.fl['SW']):\n"
       "                with open(_p, 'a') as _f:\n"
       "                    _f.write(f\"{_os.getcwd()}\\t{_os.getpid()}\\tsw_schalter={m.sw_schalter}\\tflSW={m.fl['SW']}\\tBZ={getattr(m, 'BZ', None)}\\t{' '.join(_sys.argv[-4:])}\\n\")\n"
       + ALT)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    pfad = sys.argv[1]
    with open(pfad, encoding='utf-8') as fh:
        s = fh.read()
    if 'C8205_SCHATTEN' in s:
        print('Zusatz ist schon eingebaut:', pfad)
        return 0
    if s.count(ALT) != 1:
        print('Zeile von a028 (0.03-016) nicht eindeutig gefunden; keine Aenderung:', pfad)
        return 1
    with open(pfad, 'w', encoding='utf-8') as fh:
        fh.write(s.replace(ALT, NEU))
    print('Zusatz eingebaut in', pfad)
    return 0


if __name__ == '__main__':
    sys.exit(main())
