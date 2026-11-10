#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
erzeuge_pult_toene.py - erzeugt die synthetischen Klangdateien fuer die Pult-Tasten des C 8205 (nur Modus GRAFIK):

  einrast_ein.wav    Typ 2, Einrasten:  dumpfer Anschlag, dann Rastklick der Klinke und Federnachklang
                     (Selektoren SP, BS, LS, Selektor SW und die Kanaltasten K0 bis K3)
  einrast_aus.wav    Typ 2, Loesen:     leichter Klick der Klinke, dann Tick der Taste am oberen Anschlag, kein Anschlag
  radio_wechsel.wav  Typ 1, Wechsel:    Einrasten der neuen Taste, Gleiten der Sperrleiste und der Tick der
                     ausgeloesten alten Taste; ein Klang fuer beide Richtungen (H-R und T-SW)

Die Impulstaste (Typ 3) kommt nicht von hier, sondern aus einer Aufnahme (schneide_klick.py).

Die Klaenge sind errechnet, nicht aufgenommen, und noch nicht angehoert (Stand 27.10.2026). Das Klangbild der
Impulstaste (Aufnahme keyboard-klick-tasten.mp3: hell, Energie 2,5 bis 5 kHz, Schwerpunkt um 3,9 kHz, nach etwa 9 ms
auf 10 % abgeklungen) ist der Massstab fuer die hellen Klick-Anteile. Alle Zahlen stehen oben als Konstanten und
lassen sich nach dem Anhoeren aendern.

Bausteine (je Ereignis): KLICK = Rauschen im Band plus gedaempfte Sinus-Schwingungen (Metall auf Metall);
ANSCHLAG = tiefe gedaempfte Schwingung plus tiefpassgefiltertes Rauschen (Taste setzt auf);
PING = lange gedaempfte Teiltoene (Feder, Gehaeuse); RATSCH = kurzes Bandrauschen (Sperrleiste gleitet).

Aufruf:  python3 erzeuge_pult_toene.py [--ziel ORDNER] [--spitze 0.35] [--seed 8205]
Format wie die uebrigen Dateien in ton/: 44100 Hz, 16 bit, mono. Nur Standardbibliothek.
Gleicher Startwert (--seed) ergibt bitgleiche Dateien.
"""
import argparse
import array
import math
import os
import random
import sys
import wave

RATE = 44100
HIER = os.path.dirname(os.path.abspath(__file__))

# ---- Stellschrauben (Zeiten in ms, Frequenzen in Hz, Pegel relativ, 1.0 = Bezug) -----------------------------
EIN_ANSCHLAG_HZ, EIN_ANSCHLAG_TAU_MS, EIN_ANSCHLAG_PEGEL = 150.0, 12.0, 0.35
EIN_KLICK_BAND, EIN_KLICK_TAU_MS = (2200.0, 5500.0), 2.2             # erster Klick: Taste bekommt Kontakt
EIN_KLICK_TEILTOENE = ((2900.0, 4.0, 0.6), (3800.0, 3.0, 0.4), (5200.0, 2.0, 0.25))
EIN_RAST_ABSTAND_MS, EIN_RAST_PEGEL = 13.0, 0.8                       # zweiter Klick: Klinke rastet ein
EIN_RAST_BAND, EIN_RAST_TEILTOENE = (1500.0, 4000.0), ((2200.0, 5.0, 0.7), (3100.0, 4.0, 0.4))
EIN_PING = ((3300.0, 14.0, 0.08), (4700.0, 10.0, 0.05), (6100.0, 7.0, 0.03))
EIN_LAENGE_MS = 130.0

AUS_KLICK_PEGEL = 0.7                                                 # Klinke gibt frei (hell, leicht)
AUS_KLICK_BAND, AUS_KLICK_TEILTOENE = (1800.0, 4200.0), ((2800.0, 3.0, 0.6), (3700.0, 2.2, 0.3))
AUS_TICK_ABSTAND_MS, AUS_TICK_PEGEL = 21.0, 0.5                       # Taste schlaegt oben an
AUS_TICK_BAND, AUS_TICK_TEILTOENE = (2200.0, 4600.0), ((3300.0, 2.5, 0.6),)
AUS_PING = ((3500.0, 10.0, 0.06), (4700.0, 7.0, 0.04))
AUS_LAENGE_MS = 95.0

RADIO_RATSCH_ABSTAND_MS, RADIO_RATSCH_DAUER_MS, RADIO_RATSCH_PEGEL = 8.0, 11.0, 0.35
RADIO_RATSCH_BAND = (1200.0, 3200.0)
RADIO_RAST_ABSTAND_MS = 15.0                                          # Einrasten der neuen Taste
RADIO_TICK_ABSTAND_MS, RADIO_TICK_PEGEL = 25.0, 0.45                  # alte Taste springt heraus
RADIO_LAENGE_MS = 140.0

AUSBLENDUNG_MS = 8.0
OBERGRENZE_HZ = 8500.0      # alle synthetischen Klaenge werden darueber abgeschnitten (die Aufnahme hat dort nichts)


# ---- Grundbausteine --------------------------------------------------------------------------------------------
def n(ms):
    return int(round(RATE * ms / 1000.0))


def tiefpass(x, fg, stufen=2):
    a = 1.0 - math.exp(-2.0 * math.pi * fg / RATE)
    for _ in range(stufen):
        y, aus = 0.0, []
        for v in x:
            y += a * (v - y)
            aus.append(y)
        x = aus
    return x


def hochpass(x, fg, stufen=2):
    for _ in range(stufen):
        tp = tiefpass(x, fg, 1)
        x = [v - t for v, t in zip(x, tp)]
    return x


def band(x, lo, hi):
    return tiefpass(hochpass(x, lo), hi)


def rauschen(rng, dauer_ms):
    return [rng.uniform(-1.0, 1.0) for _ in range(n(dauer_ms))]


def huell(x, tau_ms, anstieg_ms=0.4):
    ta, ts = n(anstieg_ms), tau_ms / 1000.0
    return [v * math.exp(-(i / RATE) / ts) * (min(1.0, i / ta) if ta else 1.0) for i, v in enumerate(x)]


def teilton(f, tau_ms, dauer_ms, phase=0.0):
    ts = tau_ms / 1000.0
    return [math.exp(-(i / RATE) / ts) * math.sin(2.0 * math.pi * f * i / RATE + phase) for i in range(n(dauer_ms))]


def schiebe_addiere(ziel, quelle, start_ms, pegel=1.0):
    s = n(start_ms)
    if s + len(quelle) > len(ziel):
        ziel.extend([0.0] * (s + len(quelle) - len(ziel)))
    for i, v in enumerate(quelle):
        ziel[s + i] += v * pegel


def spitzenwert(x):
    return max(abs(v) for v in x) or 1.0


def normiert(x, pegel=1.0):
    m = spitzenwert(x)
    return [v * pegel / m for v in x]


# ---- Ereignisse ------------------------------------------------------------------------------------------------
def klick(rng, band_hz, tau_ms, teiltoene):
    """Metallischer Klick; auf Spitze 1 normiert."""
    dauer = 6.0 * max([tau_ms] + [t for _, t, _ in teiltoene])
    r = huell(band(rauschen(rng, dauer), *band_hz), tau_ms)
    r = normiert(r)
    for f, tau, g in teiltoene:
        t = teilton(f, tau, dauer, rng.uniform(0, 2 * math.pi))
        for i in range(min(len(r), len(t))):
            r[i] += g * t[i]
    return normiert(r)


def anschlag(rng, f, tau_ms):
    dauer = 6.0 * tau_ms
    tief = teilton(f, tau_ms, dauer)
    rau = normiert(huell(tiefpass(rauschen(rng, dauer), 700.0), tau_ms * 0.5))
    return normiert([a + 0.6 * b for a, b in zip(tief, rau)])


def ping(teiltoene, rng):
    dauer = 5.0 * max(t for _, t, _ in teiltoene)
    aus = [0.0] * n(dauer)
    for f, tau, g in teiltoene:
        for i, v in enumerate(teilton(f, tau, dauer, rng.uniform(0, 2 * math.pi))):
            if i < len(aus):
                aus[i] += g * v
    return aus


def ratsch(rng, dauer_ms, band_hz):
    r = normiert(band(rauschen(rng, dauer_ms), *band_hz))
    na, nz = n(dauer_ms * 0.25), n(dauer_ms * 0.5)
    ende = len(r)
    for i in range(ende):
        f = min(1.0, i / na) if na else 1.0
        if i > ende - nz:
            f *= (ende - i) / nz
        r[i] *= f
    return r


# ---- die drei Klaenge ------------------------------------------------------------------------------------------
def einrast_ein(rng):
    x = [0.0] * n(EIN_LAENGE_MS)
    schiebe_addiere(x, anschlag(rng, EIN_ANSCHLAG_HZ, EIN_ANSCHLAG_TAU_MS), 0.0, EIN_ANSCHLAG_PEGEL)
    schiebe_addiere(x, klick(rng, EIN_KLICK_BAND, EIN_KLICK_TAU_MS, EIN_KLICK_TEILTOENE), 0.0, 1.0)
    schiebe_addiere(x, klick(rng, EIN_RAST_BAND, EIN_KLICK_TAU_MS * 1.3, EIN_RAST_TEILTOENE),
                    EIN_RAST_ABSTAND_MS, EIN_RAST_PEGEL)
    schiebe_addiere(x, ping(EIN_PING, rng), EIN_RAST_ABSTAND_MS, 1.0)
    return x[:n(EIN_LAENGE_MS)]


def einrast_aus(rng):
    x = [0.0] * n(AUS_LAENGE_MS)
    schiebe_addiere(x, klick(rng, AUS_KLICK_BAND, 1.8, AUS_KLICK_TEILTOENE), 0.0, AUS_KLICK_PEGEL)
    schiebe_addiere(x, klick(rng, AUS_TICK_BAND, 1.6, AUS_TICK_TEILTOENE), AUS_TICK_ABSTAND_MS, AUS_TICK_PEGEL)
    schiebe_addiere(x, ping(AUS_PING, rng), AUS_TICK_ABSTAND_MS, 1.0)
    return x[:n(AUS_LAENGE_MS)]


def radio_wechsel(rng):
    x = [0.0] * n(RADIO_LAENGE_MS)
    schiebe_addiere(x, anschlag(rng, EIN_ANSCHLAG_HZ * 1.1, EIN_ANSCHLAG_TAU_MS * 0.8), 0.0, EIN_ANSCHLAG_PEGEL)
    schiebe_addiere(x, klick(rng, EIN_KLICK_BAND, EIN_KLICK_TAU_MS, EIN_KLICK_TEILTOENE), 0.0, 1.0)
    schiebe_addiere(x, ratsch(rng, RADIO_RATSCH_DAUER_MS, RADIO_RATSCH_BAND), RADIO_RATSCH_ABSTAND_MS,
                    RADIO_RATSCH_PEGEL)
    schiebe_addiere(x, klick(rng, EIN_RAST_BAND, EIN_KLICK_TAU_MS * 1.3, EIN_RAST_TEILTOENE),
                    RADIO_RAST_ABSTAND_MS, EIN_RAST_PEGEL)
    schiebe_addiere(x, klick(rng, AUS_TICK_BAND, 1.6, AUS_TICK_TEILTOENE), RADIO_TICK_ABSTAND_MS, RADIO_TICK_PEGEL)
    schiebe_addiere(x, ping(AUS_PING, rng), RADIO_TICK_ABSTAND_MS, 1.0)
    return x[:n(RADIO_LAENGE_MS)]


def schreibe(pfad, werte, spitze):
    x = normiert(tiefpass(werte, OBERGRENZE_HZ, 2), spitze)
    na = n(AUSBLENDUNG_MS)
    for i in range(min(na, len(x))):
        x[len(x) - 1 - i] *= i / na
    roh = array.array('h', (max(-32768, min(32767, int(round(v * 32767)))) for v in x))
    if sys.byteorder == 'big':
        roh.byteswap()
    with wave.open(pfad, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(roh.tobytes())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ziel', default=HIER)
    ap.add_argument('--spitze', type=float, default=0.35)
    ap.add_argument('--seed', type=int, default=8205)
    a = ap.parse_args()
    os.makedirs(a.ziel, exist_ok=True)
    # Pegelverhaeltnis: alle drei gleiche Spitze (einrast_aus war 0,8: gegen das Grundgeraeusch zu leise, 27.10.2026)
    for name, fn, rel in (('einrast_ein.wav', einrast_ein, 1.0), ('einrast_aus.wav', einrast_aus, 1.0),
                          ('radio_wechsel.wav', radio_wechsel, 1.0)):
        rng = random.Random(a.seed)
        schreibe(os.path.join(a.ziel, name), fn(rng), a.spitze * rel)
        print('geschrieben:', os.path.join(a.ziel, name))


if __name__ == '__main__':
    main()
