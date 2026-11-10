#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
schneide_klick.py - schneidet aus einer Aufnahme mit vielen Tastenklicks den besten Einzelklick heraus
und erzeugt daraus die Klangdateien fuer die Impulstaste (Typ 3) des Pults.

Ausgabe (44100 Hz, 16 bit, mono, wie die uebrigen Dateien in ton/):
  impuls_druck.wav   der Klick beim Niederdrücken (Spitze auf --spitze normiert)
  impuls_los.wav     abgeleitet: derselbe Klick 1,2-fach schneller (hoeher, kuerzer) und 9 dB leiser,
                     als Loslass-Tick (E+/E-, M+/M-); er ist nicht aufgenommen, sondern errechnet.

Verfahren (wie bei den Schreibwerk-Zeichen in ton/SW_Ton_Beschreibung.md): Einsaetze ueber die 1-ms-Huellkurve
suchen (Schwelle: das Groessere aus 5 % des Maximums und dem 5-fachen Median), nur Klicks mit mindestens
0,35 s Ruhe davor und danach behalten, davon unter der besseren Haelfte (Signal-Rausch-Abstand) den mit dem typischsten Spektralschwerpunkt
waehlen (Ausklang nach 60 ms unter 15 % der Spitze, keine Uebersteuerung). Ausschnitt von 6 ms vor bis 54 ms nach der Spitze,
Einblendung 2 ms, Ausblendung 6 ms.

Aufruf:  python3 schneide_klick.py QUELLE [--ziel ORDNER] [--spitze 0.35] [--anzahl 1]
  QUELLE  .mp3 (braucht ffmpeg im Suchpfad) oder .wav (beliebiger Takt, 16 bit; wird nicht umgetaktet,
          deshalb am besten 44100 Hz mono)
  --anzahl N   N beste Klicks als impuls_druck_01.wav ... (zum Auswaehlen nach Gehoer); Vorgabe 1
Nur Standardbibliothek (und ffmpeg fuer .mp3).
"""
import argparse
import array
import math
import os
import subprocess
import sys
import wave

RATE = 44100
HIER = os.path.dirname(os.path.abspath(__file__))


def lade(pfad):
    """Liefert die Abtastwerte als array('h'), mono 44100 Hz."""
    if pfad.lower().endswith('.wav'):
        with wave.open(pfad, 'rb') as w:
            if w.getsampwidth() != 2:
                raise ValueError('erwartet 16 bit')
            roh = array.array('h')
            roh.frombytes(w.readframes(w.getnframes()))
            if w.getnchannels() == 2:
                roh = array.array('h', ((roh[i] + roh[i + 1]) // 2 for i in range(0, len(roh) - 1, 2)))
            if w.getframerate() != RATE:
                print(f'Hinweis: Takt {w.getframerate()} Hz statt {RATE} Hz, Ausgabe wird entsprechend '
                      f'zu hoch oder zu tief klingen.', file=sys.stderr)
            return roh
    erg = subprocess.run(['ffmpeg', '-v', 'error', '-i', pfad, '-ac', '1', '-ar', str(RATE),
                          '-f', 's16le', '-'], capture_output=True, check=True)
    roh = array.array('h')
    roh.frombytes(erg.stdout)
    if sys.byteorder == 'big':
        roh.byteswap()
    return roh


def schreibe(pfad, werte):
    roh = array.array('h', (max(-32768, min(32767, int(round(v * 32767)))) for v in werte))
    if sys.byteorder == 'big':
        roh.byteswap()
    with wave.open(pfad, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(roh.tobytes())


def ms(x):
    return int(round(RATE * x / 1000.0))


def huellkurve(x):
    """RMS je 1 ms."""
    n = ms(1)
    return [math.sqrt(sum(v * v for v in x[i:i + n]) / n) / 32768.0 for i in range(0, len(x) - n, n)]


def finde_klicks(x):
    env = huellkurve(x)
    med = sorted(env)[len(env) // 2]
    schwelle = max(0.05 * max(env), 5 * med)
    einsaetze, i = [], 0
    while i < len(env):
        if env[i] > schwelle:
            einsaetze.append(i * ms(1))
            i += 80
        else:
            i += 1
    iso = []
    for k, o in enumerate(einsaetze):
        vor = (o - einsaetze[k - 1]) / RATE if k > 0 else 99.0
        nach = (einsaetze[k + 1] - o) / RATE if k < len(einsaetze) - 1 else 99.0
        if vor > 0.35 and nach > 0.35:
            iso.append(o)
    return einsaetze, iso


def bewerte(x, o):
    """Liefert (Spitzenindex, Spitze 0..1, Signal-Rausch-Abstand, Ausklangverhaeltnis) oder None."""
    a, b = o, min(len(x), o + ms(15))
    pk = max(range(a, b), key=lambda i: abs(x[i]))
    spitze = abs(x[pk]) / 32768.0
    if pk - ms(70) < 0 or pk + ms(260) > len(x):
        return None
    vor = x[pk - ms(70):pk - ms(15)]
    rausch = math.sqrt(sum(v * v for v in vor) / len(vor)) / 32768.0 or 1e-6
    ausklang = max(abs(v) for v in x[pk + ms(60):pk + ms(250)]) / 32768.0 / spitze
    return pk, spitze, spitze / rausch, ausklang


def schwerpunkt(x, pk, laenge_ms=30.0):
    """Spektralschwerpunkt in Hz der ersten 30 ms ab 3 ms vor der Spitze (einfache DFT, grob, 200-Hz-Raster)."""
    seg = [v / 32768.0 for v in x[pk - ms(3):pk - ms(3) + ms(laenge_ms)]]
    m = len(seg)
    fen = [seg[i] * (0.5 - 0.5 * math.cos(2 * math.pi * i / (m - 1))) for i in range(m)]
    s0 = s1 = 0.0
    for f in range(200, 12001, 200):
        w = 2 * math.pi * f / RATE
        re = sum(fen[i] * math.cos(w * i) for i in range(m))
        im = sum(fen[i] * math.sin(w * i) for i in range(m))
        a = math.hypot(re, im)
        s0 += a
        s1 += a * f
    return s1 / s0 if s0 else 0.0


def ausschnitt(x, pk, vor_ms=6.0, nach_ms=54.0, ein_ms=2.0, aus_ms=6.0):
    seg = [v / 32768.0 for v in x[pk - ms(vor_ms):pk + ms(nach_ms)]]
    n, ne, na = len(seg), ms(ein_ms), ms(aus_ms)
    for i in range(ne):
        seg[i] *= i / ne
    for i in range(na):
        seg[n - 1 - i] *= i / na
    return seg


def normiere(seg, spitze):
    m = max(abs(v) for v in seg) or 1.0
    return [v * spitze / m for v in seg]


def beschleunige(seg, faktor):
    """Lineare Neuabtastung: faktor > 1 = hoeher und kuerzer."""
    n = int(len(seg) / faktor)
    aus = []
    for i in range(n):
        p = i * faktor
        k = int(p)
        f = p - k
        aus.append(seg[k] * (1 - f) + seg[min(k + 1, len(seg) - 1)] * f)
    return aus


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('quelle')
    ap.add_argument('--ziel', default=HIER)
    ap.add_argument('--spitze', type=float, default=0.35)
    ap.add_argument('--anzahl', type=int, default=1)
    a = ap.parse_args()
    x = lade(a.quelle)
    einsaetze, iso = finde_klicks(x)
    print(f'{len(x) / RATE:.1f} s, {len(einsaetze)} Einsaetze, davon {len(iso)} isoliert')
    gut = []
    for o in iso:
        r = bewerte(x, o)
        if r and r[1] < 0.9 and r[3] < 0.15:
            gut.append(r)
    if not gut:
        sys.exit('kein brauchbarer Einzelklick gefunden')
    # Auswahl: unter der besseren Haelfte nach Signal-Rausch-Abstand den Klick nehmen, dessen Spektralschwerpunkt
    # dem Median aller brauchbaren Klicks am naechsten liegt (das "typischste" Klangbild, nicht der Ausreisser)
    zentren = [schwerpunkt(x, r[0]) for r in gut]
    med = sorted(zentren)[len(zentren) // 2]
    rang = sorted(range(len(gut)), key=lambda k: -gut[k][2])[:max(a.anzahl, (len(gut) + 1) // 2)]
    rang.sort(key=lambda k: abs(zentren[k] - med))
    gut = [gut[k] for k in rang]
    print(f'{len(zentren)} brauchbare Klicks, Median des Spektralschwerpunkts {med:.0f} Hz')
    os.makedirs(a.ziel, exist_ok=True)
    for k, (pk, spitze, snr, aus) in enumerate(gut[:a.anzahl], 1):
        name = 'impuls_druck.wav' if a.anzahl == 1 else f'impuls_druck_{k:02d}.wav'
        seg = normiere(ausschnitt(x, pk), a.spitze)
        schreibe(os.path.join(a.ziel, name), seg)
        print(f'{name}: bei {pk / RATE:.2f} s, Spitze {spitze:.3f}, S/N {snr:.0f}, Ausklang {aus:.2f}')
        if k == 1:
            los = beschleunige(ausschnitt(x, pk, 6.0, 54.0, 1.5, 6.0), 1.2)
            los = normiere(los, a.spitze * 10 ** (-9 / 20))
            schreibe(os.path.join(a.ziel, 'impuls_los.wav'), los)
            print('impuls_los.wav: abgeleitet (1,2-fach schneller, 9 dB leiser)')


if __name__ == '__main__':
    main()
