#!/bin/bash
# c8205_grafik.sh - Startscript fuer den Modus GRAFIK (Stufe 1: Kern und Trommel, OHNE Fenster, OHNE Ton).
# Aufruf (aus jedem Ordner):  ./c8205_grafik.sh [Schalter ...]
#
# Alle Schalter gehen unveraendert an c8205_grafik.py; Hilfe: ./c8205_grafik.sh -h
# Der Rueckgabewert ist der von c8205_grafik.py (0 = normal, 8 = Abbruch mit Strg+C, 16 = Start nicht moeglich).
#
# In Stufe 1 gibt es noch kein Pult-Fenster. Die Pult-Tasten kommen von der Kommandozeile:
#   ./c8205_grafik.sh --entwickler-tasten "H"                 nur Halt, Rechner steht
#   ./c8205_grafik.sh --entwickler-tasten "H G R"             Grundstellung, Start; laeuft, bis das Programm haelt
#                                                             oder auf Eingabe wartet (dann Strg+C)
#   ./c8205_grafik.sh --entwickler-k0 DATEI --entwickler-tasten "..."   K0-Zeichen (eines je Zeile) vorab eingeben
# Ausgabe: Zustand am Ende des Laufs (BZ, AC, AR, Flags), Schreibwerk-Text, Trommelstatistik.
#
# ACHTUNG: Die Trommeldatei (virtuelle_Geraete/Trommel/trommel.txt) ist der Speicher des Rechners. Programme veraendern sie.
#          Wer die Ausgangsbelegung behalten will, sichert die Datei vorher oder startet mit  --trommel EIGENE_KOPIE.txt
#          (neben der Trommeldatei liegt die Schalterdatei der Bahnsperren, z. B. trommel.basp; oder --BASP 000000).
#
# Linux; getestet nur unter Linux.

cd "$(dirname "$0")" || exit 16

export PYTHONWARNINGS=ignore::ResourceWarning   # harmlose Warnungen aus dem unveraenderten c8205_interp.py (Stufe 5 raeumt auf)
export PYTHONDONTWRITEBYTECODE=1                # keine __pycache__-Ordner im Projekt

if ! command -v python3 >/dev/null 2>&1; then
    echo "FEHLER: python3 nicht gefunden." >&2
    exit 16
fi

if ! ls c-module/python/c8205_trommel*.so >/dev/null 2>&1; then
    echo "FEHLER: das C-Modul c8205_trommel (echte Trommel) fehlt in c-module/python/." >&2
    echo "  Bauen:  cd c-module/python && python3 setup.py build_ext --inplace   (braucht gcc und die Python-Entwicklungsdateien)" >&2
    exit 16
fi

exec python3 c8205_grafik.py "$@"
