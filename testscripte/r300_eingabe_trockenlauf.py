# -*- coding: utf-8 -*-
"""
r300_eingabe_trockenlauf.py - TROCKENLAUF des GRAFIK-Wegs fuer das Eingabeprogramm r300_eingabe (RE-001), OHNE Tkinter.
NICHT das echte Fenster, NICHT --HWCHECK. Prueft: Netz, Taste SW, G, R am Pult (PultSteuerung), dann die getippten Zeichen durch die Logikschicht des
SW-Fensters (SwEingabe/SwAnzeige, wie grafik_sw_pult_test.py) in den echten Rechner-Thread mit der Trommel trommel_r300_eingabe.txt.
Gegen die Sollfolge: K0-Zeichen, die der Rechner bekommt; Text am Schreibwerk; Spur im Speicher ab 3000; Zeichen ohne R300-Code bleiben wirkungslos.
Aufruf: python3 -I testscripte/r300_eingabe_trockenlauf.py   (Rueckgabewert 0 = alles OK)
"""
import os
import shutil
import sys
import tempfile
import threading
import time

HIER = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HIER)
sys.path.insert(0, PROJ); sys.path.insert(0, os.path.join(PROJ, 'grafik-interpreter-module'))
sys.path.insert(0, HIER)
import c8205_interp as I            # noqa: E402
import c8205_grafik as G            # noqa: E402
import r300_eingabe_erzeugen as E   # noqa: E402
from grafik_trommel import GrafikTrommel     # noqa: E402
from grafik_pult import PultSteuerung, BETRIEB    # noqa: E402
from grafik_sw import SwAnzeige, SwEingabe        # noqa: E402

PULT = os.path.join(PROJ, 'pult')
ERG = []


def pruefe(ok, text):
    ERG.append(ok)
    print(('OK       ' if ok else 'FEHLER   ') + text)


def main():
    soll_gr = E.soll_liste()
    tmp = tempfile.mkdtemp()
    alt = os.getcwd()
    os.chdir(tmp)
    try:
        pfad = os.path.join(tmp, 'trommel.txt')
        shutil.copy(os.path.join(PROJ, 'Trommel', 'trommel_r300_eingabe.txt'), pfad)
        tr = GrafikTrommel(pfad)
        r = G.Rechner(G.lade_graph(os.path.join(PROJ, 'markdown-dateien')), tr, pult_modus=True)
        s = PultSteuerung(PULT, r, hochlauf_s=0.01, auslauf_s=0.01, tastenzeit_s=0.0)
        anzeige = SwAnzeige()
        # S3-04: das Fenster zeigt jedes angenommene Zeichen selbst (echo); der Rechner gibt nur die Meldung aus (U-3)
        sw = SwEingabe(r.m.k0, r.m, echo=anzeige.schreibe, abstand=0.1)
        r.sw.hoere(anzeige.schreibe)
        vom_rechner = []
        r.sw.hoere(vom_rechner.append)
        geliefert = []
        orig = r.m.k0.annehmen

        def spion(q, tok, **kw):
            ok = orig(q, tok, **kw)
            if ok and q == 'SW':
                geliefert.append(tok)
            return ok
        r.m.k0.annehmen = spion
        stop = threading.Event()

        def lauf():
            try:
                while not stop.is_set():
                    r.leerlauf()
                    r.lauf_wenn_gewuenscht()
                    time.sleep(0.002)
            except G.GrafikAbbruch:
                pass
        s.bei_betrieb = lambda: (r.taste('H'), threading.Thread(target=lauf, daemon=True).start())
        s.netz_klick(0.0)
        s.tick(1.0)
        pruefe(s.netz == BETRIEB, 'Netz ein, Hochlauf beendet')
        pruefe(bool(s.klick('SW', 1.0)), 'Taste SW wirkt')
        pruefe(bool(s.klick('G', 1.1)) and bool(s.klick('R', 1.2)), 'G und R wirken')

        def warte(bed, sek=5.0):
            t0 = time.time()
            while time.time() - t0 < sek:
                sw.liefern()
                if bed():
                    return True
                time.sleep(0.003)
            return False

        keysym_zu_zeichen = {v: k for k, v in E.KEYSYM.items()}
        fehl_halt = 0
        ergebnisse = []
        for zn, n in E.folge() + E.NICHT_R300:
            if not warte(lambda: sw.erwartet() and not r.m.k0._q['SW'], 10.0):     # erwartet() bleibt wahr, bis der Rechner das Token holt: Vorrat leer abwarten
                fehl_halt += 1
                print('   kein Eingabe-Halt vor', repr(zn))
                break
            e = sw.tippen(zn)
            ergebnisse.append((zn, e))
            warte(lambda: sw.zweite is None, 2.0)      # zweite Eingabe gesendet oder blockiert
        pruefe(fehl_halt == 0, 'vor jedem Zeichen stand der Rechner im Eingabe-Halt')
        warte(lambda: sw.erwartet() and not r.m.k0._q['SW'], 10.0)
        time.sleep(0.3)
        soll_tokens = [t for t, _n, _c, _w in soll_gr]
        pruefe(geliefert == soll_tokens, f'K0-Zeichen des Rechners = Sollfolge ({len(soll_tokens)} Token)'
               + ('' if geliefert == soll_tokens else f'\n   ist  {geliefert}\n   soll {soll_tokens}'))
        verworfen = [zn for zn, e in ergebnisse if zn in dict(E.NICHT_R300) and e == 'verworfen']
        pruefe(len(verworfen) == len(E.NICHT_R300), f'Zeichen ohne R300-Code verworfen: {"".join(verworfen)}')
        vorlage = SwAnzeige()          # das Fenster setzt den Tabulator in Leerzeichen um: Sollbild durch dieselbe Anzeigelogik
        for c in E.MELDUNG + '\n' + ''.join('\n' if z == '\r' else z for z, _n in E.folge()):
            vorlage.schreibe(c)
        erwartet = vorlage.text()
        pruefe(''.join(vom_rechner) == E.MELDUNG + '\n', 'Ausgabe des Rechners = nur die Meldung (kein Echo des Programms, U-3)'
               + ('' if ''.join(vom_rechner) == E.MELDUNG + '\n' else f'\n   ist {"".join(vom_rechner)!r}'))
        pruefe(anzeige.text() == erwartet, 'Text im Fenster = Meldung + Anzeige jedes angenommenen Zeichens (S3-04)'
               + ('' if anzeige.text() == erwartet else f'\n   ist  {anzeige.text()!r}\n   soll {erwartet!r}'))
        stop.set()
        r.abbrechen()
        time.sleep(0.2)
        tr.schliessen()
        mem = {}
        with open(pfad, encoding='utf-8') as f:
            for z in f:
                mem[int(z[:4], 8)] = z[6:17]
        abw = [(f'{E.SPUR + i:04o}', E.wort_oktal(w), mem.get(E.SPUR + i)) for i, (_t, _n, _c, w) in enumerate(soll_gr)
               if mem.get(E.SPUR + i) != E.wort_oktal(w)]
        pruefe(not abw, f'Spur im Speicher ab 3000 ({len(soll_gr)} Worte) = Sollfolge' + ('' if not abw else f' Abweichungen: {abw[:5]}'))
        pruefe(mem.get(E.SPUR + len(soll_gr)) == '00000000000', 'hinter der Spur kein weiteres Wort (die verworfenen Zeichen kamen nicht an)')
    finally:
        os.chdir(alt)
        shutil.rmtree(tmp, ignore_errors=True)
    print(f'\nERGEBNIS (TROCKENLAUF, ohne Tkinter, nicht das echte Fenster, nicht --HWCHECK): {sum(ERG)} OK, {len(ERG) - sum(ERG)} FEHLER')
    return 0 if all(ERG) else 1


if __name__ == '__main__':
    sys.exit(main())
