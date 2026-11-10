#!/usr/bin/env python3
"""typ10ein_gen.py -- erzeugt typ10ein.asm und den Leser-1-Streifen Test-virtuelleGeraete/Leser1/typ10ein.txt fuer den Test des Projektmakros TYP10EINGABE
(ZT-Repository_Aufgabenstellung.md 7a). Die Sollwerte (Wort 1, Wort 2, KBGB je Eingabe) kommen aus einem unabhaengigen Python-Modell der Regeln von 7a.
Die Lochbilder werden wie bei hschl aus Tabelle 1 der Kodetabellen gelesen (Spalte Ausgabe-Adresse). Aufruf vom Projektstamm oder durch Assembler/asm_und_test.sh."""
import os, sys, importlib.util
HIER = os.path.dirname(os.path.abspath(__file__))
STAMM = os.path.abspath(os.path.join(HIER, *(['..'] * 5)))
spec = importlib.util.spec_from_file_location('streifen_hschl', os.path.join(STAMM, 'Assembler', 'Projekt_ZT_LOADER', 'Unterprojekt_Allgemein', 'hschl', 'gen', 'streifen.py'))
st = importlib.util.module_from_spec(spec); spec.loader.exec_module(st)

# Eingabeadressen der benutzten Zeichen (Kodetabelle R 300)
EA = {str(i): i for i in range(10)}
EA.update({'+': 0o20, '.': 0o33, ':': 0o15, 'WRZL': 0o32, '_': 0o12, 'a': 0o21, 'GB': 0o37, 'KB': 0o57})
# die Eingaben (Folge der Zeichen), Beschreibung
EINGABEN = [
    ('+ 0 7 7 1 2 3 4 5 6 7 0 1 2 :', '12 Ziffern: die letzten 11 bleiben (Beispiel 1 aus 7a)'),
    ('+ 0 1 2 3 :', 'Vornullen (Beispiel 2 aus 7a)'),
    ('2 .', 'nur ein Kennzeichen (Beispiel 3 aus 7a)'),
    ('WRZL _ .', 'Punkt sofort: nichts gelesen, alles 0; WRZL und Leertaste werden uebergangen'),
    ('_ 1 WRZL 2 8 9 + 3 a _ 4 5 .', 'Uebergehen von Leertaste, WRZL, Buchstabe, 8, 9 und + im Ziffernteil'),
    ('GB 3 4 .', 'Um. GB wird nachgefuehrt, Kennzeichen 3 und 4, keine Ziffern'),
    ('5 6 7 KB 1 :', 'Um. KB wird nachgefuehrt, Ziffern 7 und 1'),
    ('0 0 7 7 7 7 7 7 7 7 7 7 7 :', '11 Ziffern 7: Wort 1 mit gesetztem Bit z0'),
    ('+ .', 'ein Kennzeichen +, Eingabeadresse 20'),
]

def modell(folge):
    """Python-Modell der Regeln 7a: liefert (wort1, wort2, kbgb-Aenderung oder None)."""
    kz, ziff, kb = [], [], None
    for z in folge.split():
        if z in ('.', ':'):
            break
        if z == 'GB': kb = 1; continue
        if z == 'KB': kb = 0; continue
        if z in [str(i) for i in range(10)] + ['+']:
            if len(kz) < 2: kz.append(EA[z])
            elif z in '01234567' and z != '+': ziff.append(int(z))
    kz += [0] * (2 - len(kz))
    w1 = 0
    for d in ziff[-11:]: w1 = (w1 << 3) | d
    return w1, (kz[0] << 6) | kz[1], kb

def main():
    tab = st.lochbilder()
    erste = {}
    for nr, ea, aus, name in tab:
        erste.setdefault(ea, aus); erste[ea] = min(erste[ea], aus)
    zeilen = []
    for folge, _ in EINGABEN:
        for z in folge.split():
            zeilen.append(st.zeile(erste[EA[z]]))
    zeilen.append('10101010')   # Abschluss: Zeile mit ungerader Lochzahl (Bandende, Handbuch 5.6)
    os.makedirs(st.AUS, exist_ok=True)
    st.streifen(zeilen, 'typ10ein.txt')
    n = len(EINGABEN)
    kbgb = 0
    soll = []
    for folge, _ in EINGABEN:
        w1, w2, kb = modell(folge)
        if kb is not None: kbgb = kb
        soll.append((w1, w2, kbgb))
    A = []
    A.append('; typ10ein.asm - ERZEUGT von gen/typ10ein_gen.py (nicht von Hand aendern). Test des Projektmakros TYP10EINGABE (ZT-Repository_Aufgabenstellung 7a): liest %d Typ-10-Eingaben vom Lochbandleser 1 (K1).' % n)
    A.append('; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (die Tabelle legt equ100 selbst).')
    A.append('; Ablauf: KBGB := 0, K1 anwaehlen; je Eingabe R1 := Adresse des 2-Zellen-Bereichs, UP eingabe aufrufen, KBGB danach in die Zelle kb+i merken; am Ende R1 pruefen (dif1), Halt.')
    A.append('; Der Streifen (Test-virtuelleGeraete/Leser1/typ10ein.txt) enthaelt die Eingaben nacheinander, danach eine Zeile mit ungerader Lochzahl.')
    A.append(';#MACRODATEI1=../../macro_zt_loader.macro')
    A.append(';#DOK-0001 typ10ein: Projektmakro TYP10EINGABE: %d Eingaben vom Leser 1, Wort 1 und Wort 2 je Eingabe, KBGB nach jeder Eingabe, R1 unveraendert' % n)
    A.append(';#SPEI-0001 0001-0034')
    A.append(';#PROT STUFE=2')
    A.append('; --leser1 Test-virtuelleGeraete/Leser1/typ10ein.txt')
    A.append('')
    A.append('r1:             abs     07773                ; Register 1: Adresse des Bereichs (Adressfeld)')
    A.append('kbgb:           abs     07775                ; globale KB/GB-Zelle des Projekts (0 = KB, 1 = GB)')
    A.append('')
    A.append('                start                        ; Zaehlung beginnt bei 0000')
    A.append('                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm')
    A.append('erg:            db      %d                  ; Zellen 0001 bis %04o: Ergebnisbereiche, je Eingabe 2 Zellen (Wort 1, Wort 2)' % (2 * n, 2 * n))
    A.append('kb:             db      %d                   ; Zellen %04o bis %04o: KBGB nach jeder Eingabe' % (n, 2 * n + 1, 3 * n))
    A.append('dif1:           db      1                    ; Zelle %04o: R1 - Soll nach dem letzten Aufruf (0, wenn R1 unveraendert)' % (3 * n + 1))
    A.append('')
    A.append('haupt:          241     kbgb                 ; KBGB := 0 (Anfangszustand KB), AC := 0')
    A.append('                ANWAHL  K1                   ; Lochbandleser 1 anwaehlen (Kanal K1)')
    for i in range(n):
        A.append('                211     a%d                   ; AC := Adresse des Bereichs der Eingabe %d' % (i, i + 1))
        A.append('                240     r1                   ; R1 := Bereich')
        A.append('                025     eingabe              ; UP eingabe: Eingabe %d lesen' % (i + 1))
        A.append('                211     kbgb                 ; AC := KBGB nach der Eingabe')
        A.append('                240     kb+%d                 ; Zelle kb+%d := KBGB' % (i, i))
    A.append('                211     r1                   ; AC := R1')
    A.append('                220     a%d                   ; minus Soll (Bereich der letzten Eingabe): 0, wenn R1 unveraendert' % (n - 1))
    A.append('                240     dif1                 ; dif1 := Abweichung')
    A.append('                020     0                    ; Halt (normales Ende)')
    for i in range(n):
        A.append('a%d:             da      erg+%d                ; Adresse des Bereichs der Eingabe %d (Adressfeld)' % (i, 2 * i, i + 1))
    A.append('')
    A.append('; ---- UP eingabe: Projektmakro TYP10EINGABE. R1 = Bereich (2 Zellen), KBGB global')
    A.append('eingabe:        TYP10EINGABE                 ; Unterprogramm (Makro)')
    A.append('schluss:        end')
    A.append('')
    A.append('; Sollwerte aus dem unabhaengigen Python-Modell (gen/typ10ein_gen.py) der Regeln von 7a; Beispiele 1 bis 3 aus 7a von Hand: (1) 71234567012 / 00000002000, (2) 00000000123 / 00000002000, (3) 0 / 00000000200.')
    for i, (folge, text) in enumerate(EINGABEN):
        A.append('; Eingabe %d: %s  (%s)' % (i + 1, folge, text))
    A.append(';#PRUEFE-START')
    A.append('; US=1')
    for i, (w1, w2, k) in enumerate(soll):
        A.append('; %04o: %011o   # Eingabe %d Wort 1' % (1 + 2 * i, w1, i + 1))
        A.append('; %04o: %011o   # Eingabe %d Wort 2' % (2 + 2 * i, w2, i + 1))
    for i, (w1, w2, k) in enumerate(soll):
        A.append('; %04o: %011o   # KBGB nach Eingabe %d' % (2 * n + 1 + i, k, i + 1))
    A.append('; %04o: %011o   # dif1: R1 unveraendert' % (3 * n + 1, 0))
    A.append('; 7775: %011o   # KBGB am Ende' % soll[-1][2])
    A.append(';#PRUEFE-ENDE')
    open(os.path.join(HIER, '..', 'typ10ein.asm'), 'w', encoding='utf-8', newline='\n').write('\n'.join(A) + '\n')

main()
