#!/usr/bin/env python3
"""zil_texte.py -- erzeugt die Textwoerter (kat4 MIT Umschaltzeichen) fuer die Ausschriften von zil.asm (Projekt ZT-Loader, ZIL).

Hintergrund: Die Ausschriften laufen ueber das Projektmakro KAT4AUSGABE_G (macro_zt_loader.macro). Die Anweisung kat4 fuegt keine Umschaltzeichen ein;
die Zeichencodes samt Um. GB (057) und Um. KB (0117) werden deshalb hier erzeugt: Jeder Text wird vom Assembler mit dtm uebersetzt (dtm setzt die Umschaltzeichen),
aus dem Listing (.dmp) werden die Ausgabeadressen gelesen, kat4-Zeichen = Ausgabeadresse / 010 (oktal, wie in kat4ausgabe_g.asm), 4 Zeichen je Wort,
z0 (040000000000) am letzten Wort. Der Text beginnt immer in KB (so liest ihn KAT4AUSGABE_G): ein fuehrendes Um. KB von dtm entfaellt, ein fuehrendes Um. GB bleibt.
Aufruf (aus dem Projektstamm):  python3 -I Assembler/Projekt_ZT_LOADER/Unterprojekt_ZIL_Initialloader/zil/gen/zil_texte.py
Ausgabe: der dw-Block fuer zil.asm (zwischen den Marken ';#TEXTE-START' und ';#TEXTE-ENDE'), auf STDOUT. Die Texte stehen unten in TEXTE.
"""
import os, re, subprocess, sys, tempfile

PROJEKT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *(['..'] * 5)))
ASSEMBLER = os.path.join(PROJEKT, 'Assembler')
UM_GB, UM_KB, Z0 = 0o57, 0o117, 0o40000000000

# (Marke, Text) in der Reihenfolge der Ausschriften
TEXTE = [
    ('t_repgef', 'Repository gefunden'),
    ('t_frage', 'Zusatztrommel loeschen [J/N]'),
    ('t_pende', 'Programmende'),
    ('t_lband', 'Lochband mit ZTD in Leser 1 einlegen'),
    ('t_lszu', 'lochstreifen zu lang'),
    ('t_geladen', 'ZTD geladen mit Programm-ID 1'),
    ('t_keinrep', 'Kein Repository gefunden'),
    ('t_uprepo', 'UP Repository pruefen'),
]


def zeichen_aus_dtm(texte):
    """Uebersetzt jeden Text mit dtm und liefert je Text die Liste der kat4-Zeichen (mit Umschaltzeichen von dtm)."""
    with tempfile.TemporaryDirectory(dir=ASSEMBLER) as tmp:
        with open(os.path.join(tmp, 't.asm'), 'w', encoding='utf8') as f:
            f.write('                start\n')
            for t in texte:
                f.write('                dtm     %s\n' % t)
            f.write('                020     0\n                end\n')
        subprocess.run(['./c82ass.sh', '-p', os.path.basename(tmp), '-s', 't.asm', '--no-color'], cwd=ASSEMBLER, check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(os.path.join(tmp, 't.dmp'), encoding='utf8') as f:
            zeilen = f.read().split('\n')
    ergebnis = []
    for z in zeilen:
        m = re.match(r'^(?:[0-7]{4}:)?\s*0[01] ([0-7]{4}) 030\s+(.*)$', z.rstrip())
        if not m:
            continue
        code = int(m.group(1), 8) >> 3
        if 'dtm' in m.group(2):
            ergebnis.append([])
        if ergebnis:
            ergebnis[-1].append(code)
    assert len(ergebnis) == len(texte), (len(ergebnis), len(texte))
    return ergebnis


def worte(zeichen):
    """Packt Zeichen zu kat4-Woertern (4 je Wort, erstes Zeichen rechts, z0 am letzten Wort)."""
    if zeichen and zeichen[0] == UM_KB:        # Der Text beginnt in KB, Um. KB am Anfang ist ueberfluessig
        zeichen = zeichen[1:]
    ws = []
    for i in range(0, len(zeichen), 4):
        w = 0
        for k, c in enumerate(zeichen[i:i + 4]):
            w |= c << (8 * k)
        ws.append(w)
    ws[-1] |= Z0
    return ws, zeichen


def endzustand(zeichen):
    """Zustand des Geraets nach dem Text (0 = KB, 1 = GB), Start KB."""
    z = 0
    for c in zeichen:
        if c == UM_GB:
            z = 1
        elif c == UM_KB:
            z = 0
    return z


def main():
    alle = zeichen_aus_dtm([t for _, t in TEXTE])
    print(';#TEXTE-START   (erzeugt von gen/zil_texte.py, nicht von Hand aendern; Zeichen je Wort 4, erstes rechts, z0 = 040000000000 am letzten Wort)')
    print('                begin                        ; ein Block (Festlegung 027): der Optimierer darf die dw-Zeilen der Texte nicht verlegen')
    for (marke, text), z in zip(TEXTE, alle):
        ws, z = worte(z)
        for i, w in enumerate(ws):
            lab = (marke + ':').ljust(16) if i == 0 else ' ' * 16
            kom = '"%s" (Ende %s)' % (text, 'GB' if endzustand(z) else 'KB') if i == 0 else 'Fortsetzung'
            print('%sdw      %012o       ; %s' % (lab, w, kom))
    print('                bend                         ; Ende des Textblocks')
    print(';#TEXTE-ENDE')
    print('; Endzustaende:', {m: ('GB' if endzustand(worte(z)[1]) else 'KB') for (m, _), z in zip(TEXTE, alle)}, file=sys.stderr)


if __name__ == '__main__':
    main()
