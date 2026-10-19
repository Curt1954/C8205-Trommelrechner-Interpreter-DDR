#!/usr/bin/env python3
"""r300_eingabe_log_auswerten.py (RLA-002) - wertet das Debug-Log des GRAFIK-Laufs r300_eingabe aus.

Aufruf (aus dem Projektordner):
    python3 testscripte/r300_eingabe_log_auswerten.py [LOG [TROMMEL_NACH_LAUF [BERICHT]]]
Vorgabe: r300_eingabe_debug.log, r300_eingabe_trommel_nach_lauf.txt, Bericht auf dem Bildschirm (und in BERICHT, wenn angegeben).
Rueckgabewert 0 = nichts Auffaelliges, 1 = mindestens ein Befund. Der Gravis (Tottaste der deutschen Tastatur) steht als [BEKANNT] und zaehlt nicht (RLA-002).

Was geprueft wird (je Tipp der Klickspur Tests/r300_eingabe_klickspur.txt):
  1. Kam im SW-Fenster die Taste an, die die Wiedergabe erzeugt hat?      (sonst: Wiedergabe-Artefakt, nicht Fehler des SW)
  2. Wurde ein vorgemerktes Zeichen (nach einem Umschaltzeichen) dem Rechner wirklich geliefert?
  3. Stimmt die Tokenfolge am Rechner mit der Spur auf der Trommel ueberein (Spurwort = Ausgabewort des Tokens)?
  4. Stimmt die Anzeige im Fenster (Echo des Fensters, S3-04; das Programm gibt kein Echo aus) mit den Tokens ueberein?
  5. Wurden ae oe ue ss Paragraph verworfen (sie haben keinen R300-Code)?
  6. Lag der Fokus bei jedem Tipp im SW-Text?
Die Sollfolge Tests/r300_eingabe_soll.txt gilt fuer eine Wiedergabe, die jede Taste so erzeugt, wie sie ein Mensch tippt; weicht die
tatsaechliche Folge ab, nennt der Bericht die Abweichung und ordnet sie einem der Punkte 1 oder 2 zu.
"""
import ast
import os
import re
import sys

LOG = sys.argv[1] if len(sys.argv) > 1 else 'r300_eingabe_debug.log'
TROMMEL = sys.argv[2] if len(sys.argv) > 2 else 'r300_eingabe_trommel_nach_lauf.txt'
BERICHT = sys.argv[3] if len(sys.argv) > 3 else None
HIER = os.path.dirname(os.path.abspath(__file__))
PROJEKT = os.path.dirname(HIER)
VERWORFEN_ERWARTET = {'adiaeresis', 'odiaeresis', 'udiaeresis', 'ssharp', 'section'}

zeilen_aus = []


def ausgabe(text=''):
    zeilen_aus.append(text)
    print(text)


def lies_log(pfad):
    with open(pfad, encoding='utf-8') as f:
        return f.read().splitlines()


def lies_soll():
    soll = []
    with open(os.path.join(PROJEKT, 'Tests', 'r300_eingabe_soll.txt'), encoding='utf-8') as f:
        for z in f:
            if z.startswith('#') or not z.strip():
                continue
            m = re.match(r"^\s*(\d+)\s+(\d+)\s+(.+?)\s{2,}(\d\d)\s+(\d{11})\s+(.*?)\s*$", z)
            if m:
                soll.append(m.groups())
    return soll


def lies_trommel(pfad):
    tr = {}
    with open(pfad, encoding='utf-8') as f:
        for z in f:
            m = re.match(r"^([0-7]{4}):\s*(\d{11})", z)
            if m:
                tr[int(m.group(1), 8)] = m.group(2)
    return tr


def _zeit(zeile):
    m = re.match(r"\s*(\d+\.\d+)", zeile)
    return float(m.group(1)) if m else None


def main():
    befunde = 0
    log = lies_log(LOG)
    soll = lies_soll()
    wort_von_token = {s[2]: s[4] for s in soll}

    # Ereignisse: je Tipp die angekommene Taste, das Ergebnis und die danach an den Rechner gelieferten Tokens
    ev, cur = [], None
    for z in log:
        m = re.search(r"\] SW       tipp (\S+): Fokus auf SW-Text=(\w+).*Lage SW=(\S+)$", z)
        if m:
            cur = {'gen': m.group(1), 'fokus': m.group(2) == 'True', 'lage': m.group(3), 'taste': None, 'toks': []}
            ev.append(cur)
            continue
        if cur is None:
            continue
        m = re.search(r"SW       Taste char=(.*) keysym=(\S+) -> (\S+)$", z)
        if m:
            cur['taste'] = (ast.literal_eval(m.group(1)), m.group(2), m.group(3))
            cur['t_taste'] = _zeit(z)
            continue
        m = re.search(r"SW       zweite Eingabe beim Loslassen -> (\S+)$", z)
        if m:
            cur['t_los'] = _zeit(z)
            cur['los_erg'] = m.group(1)
            continue
        m = re.search(r"Rechner uebernimmt Token (.*) \(Quelle SW\)", z)
        if m:
            cur['toks'].append(ast.literal_eval(m.group(1)))
    tokens = [t for e in ev for t in e['toks']]
    echo = []
    for z in log:
        m = re.search(r"\] SWAUS\s+(.*)$", z)
        if m:
            echo.append(ast.literal_eval(m.group(1)))

    ausgabe('Auswertung des Laufs r300_eingabe  (RLA-002)')
    ausgabe(f'Log: {LOG}   Tipps: {len(ev)}   Tokens am Rechner: {len(tokens)}   Sollfolge: {len(soll)} Token')
    ausgabe()

    # 6 Fokus
    ohne = [i for i, e in enumerate(ev, 1) if not e['fokus']]
    ausgabe(f'[{"OK" if not ohne else "BEFUND"}] Fokus: bei {len(ev) - len(ohne)} von {len(ev)} Tipps lag der Fokus im SW-Text' + (f' (nicht bei Nr {ohne})' if ohne else ''))
    befunde += bool(ohne)

    # 1 angekommene Taste
    ab = []
    for i, e in enumerate(ev, 1):
        t = e['taste']
        if t is None:
            ab.append((i, e['gen'], 'kein Tastenereignis im SW-Fenster angekommen'))
        elif t[1] != e['gen']:
            ab.append((i, e['gen'], f"angekommen als {t[1]} (Zeichen {t[0]!r})"))
    # RLA-002: Gravis ist auf der deutschen Belegung nur als Tottaste (dead_grave) tippbar; die Wiedergabe findet keinen Tastencode.
    # Das ist ein BEKANNTER Wiedergabe-Artefakt-Befund (Dok. 09 5b, F-56) und zaehlt nicht als Befund, solange kein Handlauf etwas anderes zeigt.
    bekannt = [x for x in ab if x[1] == 'grave' and 'kein Tastenereignis' in x[2]]
    ab = [x for x in ab if x not in bekannt]
    ausgabe(f'[{"OK" if not ab else "BEFUND"}] Wiedergabe-Taste = angekommene Taste: {len(ev) - len(ab) - len(bekannt)} von {len(ev) - len(bekannt)}'
            + (f' (ohne {len(bekannt)} bekannten Artefakt-Befund)' if bekannt else ''))
    for i, g, was in ab:
        ausgabe(f'         Tipp Nr {i}: erzeugt {g}: {was}   (Wiedergabe-Artefakt; echte Tastatur im Handbetrieb pruefen)')
    for i, g, was in bekannt:
        ausgabe(f'[BEKANNT] Tipp Nr {i}: erzeugt {g}: {was}. Gravis = Tottaste dead_grave der deutschen Belegung, kein Tastencode fuer grave; '
                'Wiedergabe-Artefakt, kein Fehler des SW-Fensters, zaehlt nicht als Befund (Dok. 09 5b, 5d). Am echten Fenster kommt der Gravis als grave an (Handlauf F-56, 18.10.2026). Die Folge hat dann 1 Token weniger als die Sollfolge.')
    befunde += bool(ab)

    # 2 vorgemerkte Zeichen
    vorm = [(i, e) for i, e in enumerate(ev, 1) if e['taste'] and e['taste'][2] == 'folgt']
    verloren = [(i, e) for i, e in vorm if e['taste'][0] not in e['toks'] and _token_name(e['taste'][0]) not in e['toks']]
    ausgabe(f'[{"OK" if not verloren else "BEFUND"}] Zweite Eingabe nach einem Umschaltzeichen (Rueckgabe folgt) beim Rechner angekommen: {len(vorm) - len(verloren)} von {len(vorm)}')
    for i, e in verloren:
        hz = (e['t_los'] - e['t_taste']) if e.get('t_los') is not None and e.get('t_taste') is not None else None
        if hz is None:
            ursache = 'Haltezeit nicht im Log'
        elif hz < 0.05:
            ursache = f'Haltezeit {hz * 1000:.0f} ms = Wiedergabe-Artefakt (kein echtes Tippen; Wiedergabe ab G3-006 haelt 120 ms)'
        else:
            ursache = f'Haltezeit {hz * 1000:.0f} ms: Rechner war nicht rechtzeitig wieder bei 011 -> echter Befund fuer das Programm oder die Zeitlage'
        ausgabe(f'         Tipp Nr {i} ({e["gen"]}): Zeichen {e["taste"][0]!r} folgte dem Umschaltzeichen, Tokens danach nur {e["toks"]}  -> blockiert; {ursache}')
    befunde += bool(verloren)

    # 2b blockierte Tasten (kein 011 aktiv): bei einem korrekten Eingabeprogramm und Tippabstand nach T_TIPP darf keine R300-Taste blockiert sein
    blk = [(i, e['gen']) for i, e in enumerate(ev, 1) if e['taste'] and e['taste'][2] == 'blockiert']
    ausgabe(f'[{"OK" if not blk else "BEFUND"}] Blockierte Tasten (kein 011 aktiv): {len(blk)}' + (f'  (Tipp Nr, Taste): {blk}' if blk else ''))
    befunde += bool(blk)

    # 3 Spur
    if os.path.exists(TROMMEL):
        tr = lies_trommel(TROMMEL)
        spur = [tr.get(0o3000 + i, '') for i in range(len(tokens))]
        passt = sum(1 for t, w in zip(tokens, spur) if wort_von_token.get(t) == w)
        rest = tr.get(0o3000 + len(tokens), '?')
        ok3 = passt == len(tokens) and rest == '00000000000'
        ausgabe(f'[{"OK" if ok3 else "BEFUND"}] Spur ab 3000: {passt} von {len(tokens)} Worten passen zum gelieferten Token; Zelle nach der Spur {rest}')
        befunde += (not ok3)
    else:
        ausgabe(f'[---] Trommel {TROMMEL} nicht gefunden, Spur nicht geprueft')

    # 4 Anzeige im Fenster: jedes angenommene Zeichen (U-4; frueher Echo des Programms am Schreibwerk)
    erw = []
    namen = {'ZR': ' ', 'TAB': '\t', 'Tabulator': '\t', 'WRZL': '\n'}
    for t in tokens:
        if t.startswith('Um.') or t in ('ZV', 'BM'):
            continue
        erw.append(namen.get(t, t))
    meld = echo.index('\n') + 1 if '\n' in echo else 0
    ist = echo[meld:]
    ok4 = ist == erw
    ausgabe(f'[{"OK" if ok4 else "BEFUND"}] Anzeige im Fenster = angenommene Zeichen = Tokens am Rechner (ohne Umschaltzeichen): {len(ist)} Zeichen, erwartet {len(erw)}')
    befunde += (not ok4)

    # 5 Verworfen
    verw = [e['taste'][1] for e in ev if e['taste'] and e['taste'][2] == 'verworfen']
    ok5 = VERWORFEN_ERWARTET <= set(verw)
    ausgabe(f'[{"OK" if ok5 else "BEFUND"}] Zeichen ohne R300-Code verworfen: {sorted(set(verw))}')
    befunde += (not ok5)

    ausgabe()
    ausgabe(f'Ergebnis: {"keine Befunde" if not befunde else str(befunde) + " Befund(e)"}')
    if BERICHT:
        with open(BERICHT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(zeilen_aus) + '\n')
    return 1 if befunde else 0


def _token_name(zeichen):
    """Zeichen -> Tokenname fuer die wenigen Zeichen mit Namen (Leertaste, Tab, Eingabe)."""
    return {' ': 'ZR', '\t': 'TAB', '\r': 'WRZL', '\n': 'WRZL'}.get(zeichen, zeichen)


if __name__ == '__main__':
    sys.exit(main())
