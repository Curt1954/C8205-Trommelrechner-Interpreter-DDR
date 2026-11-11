# -*- coding: utf-8 -*-
"""
grafik_zt.py - Zusatztrommeln des C 8205Z im Modus GRAFIK (Schalter --C8205Z): Anbindung des C-Moduls zt_modul (Projekt C8205Z) ueber das
Erweiterungsmodul c8205_ztmodul. Gleiche Schnittstelle wie c8205_zt.Zusatztrommeln (anwahl, ausgabe, eingabe, leeren, schliessen), die der
Interpreter in a005/a028 benutzt (m.zt); der Python-Interpreter (TEST) rechnet dagegen weiter mit Zeit 0 (c8205_zt.py).
Aenderungen (G5-001 neu mit c8205_grafik.py G4-013; G5-002: ansicht() fuer den HW-Check)

Zeit (Zeitmodell der Zusatztrommeln, Zusatztrommel_Zeitmodell.md): ein Befehl 601/661 dauert rund 81 bis 86 ms.
  --trommelzeit alt   Haupttrommel nach der Wanduhr: das C-Modul wartet in Echtzeit (Modus ECHT, Phasen aus Uhr und aktuellem Sektor);
                      der Aufruf blockiert so lange wie der Befehl der Maschine.
  --trommelzeit echt / schnell   virtuelle Zeit der Haupttrommel (grafik_trommel.vt, Wortzeit 104 us): das C-Modul rechnet nur (Modus
                      VIRTUELL, Phasen aus vt), die Dauer wird als Ticks auf vt aufgeschlagen; bei 'echt' schlaeft _pace() sie ab.
Die Haupttrommel wird ueber ihre Direktzugriffe (c8205_trommel.lesen/schreiben, ohne Koinzidenz) angekoppelt; die Zeit rechnet das Modul.
Strg+C / X im Fenster: abbrechen() beendet einen laufenden Befehl (GrafikAbbruch).
"""
VERSION_ZT = 'G5-003'      # Kennung dieses Moduls (G5-003); frueher in der Kopfzeile

import os
import random
import sys

import c8205_interp as I
from grafik_trommel import GrafikAbbruch

_HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # Projektordner
MODULVERZ = os.path.join(_HIER, 'C8205Z', 'zt_modul', 'python')
ZT_ANZAHL = 4
HT_POS_NS = 104000
ZT_SEKTOR_NS = 625000
ZT_UMLAUF_NS = 32 * ZT_SEKTOR_NS


def lade_modul():
    """Importiert c8205_ztmodul. Nicht ladbar: KonfigFehler mit Bauanleitung."""
    if MODULVERZ not in sys.path:
        sys.path.insert(0, MODULVERZ)
    try:
        import c8205_ztmodul
    except ImportError as e:
        raise I.KonfigFehler(
            'das C-Modul "c8205_ztmodul" (Zusatztrommeln) ist nicht ladbar: ' + str(e) + '\n'
            '  Bauen: im Ordner C8205Z/zt_modul/python  "python3 setup.py build_ext --inplace" '
            '(Windows: "python setup.py build_ext --inplace"; braucht einen C-Compiler und die Python-Entwicklungsdateien).')
    return c8205_ztmodul


class GrafikZT:
    """Zusatztrommeln ueber das C-Modul (Nummer im Modul k = 1..4; Anzeige und Befehl 5k00 030: 5100 = ZT0 .. 5400 = ZT3, d = k - 1). trommel: die GrafikTrommel (Haupttrommel, Zeitmodell, Direktzugriffe)."""

    def __init__(self, verzeichnis, trommel, start_index=None, modul=None):
        self.Z = modul or lade_modul()
        self.trommel = trommel
        self.verzeichnis = verzeichnis
        self.eingeschaltet = False
        self.befehle = 0
        self.zeit_summe_ns = 0
        self.letzte_dauer_ns = 0
        self.idx0 = random.randrange(32) if start_index is None else start_index % 32      # ZT-Position beim Einschalten
        try:
            os.makedirs(verzeichnis, exist_ok=True)
        except OSError as e:
            raise I.KonfigFehler(f'Zusatztrommeln (--C8205Z): Ordner {verzeichnis!r} nicht anlegbar: {e}')
        pfade = [os.path.join(verzeichnis, f'zt{k}.txt') for k in range(1, ZT_ANZAHL + 1)]
        T = trommel.T
        try:
            self.Z.einschalten(pfade, self.idx0, T.lesen, T.schreiben, T.aktueller_sektor)
        except self.Z.ZtFehler as e:
            raise I.KonfigFehler(f'Zusatztrommeln (--C8205Z) nicht einschaltbar: {e}')
        self.eingeschaltet = True

    # --- Schnittstelle des Interpreters (a028: Anwahl, a005: 601/661) -------------------------------------------------
    def anwahl(self, k):
        """5k00 030 (5100 = ZT0 .. 5400 = ZT3): Zusatztrommel d (0..3) anwaehlen; der Interpreter ruft mit k = d + 1 (1..4) auf."""
        if self.Z.anwahl(k) != self.Z.ZT_OK:
            raise I.KonfigFehler(f'Zusatztrommel {k} nicht anwaehlbar')

    def ausgabe(self, zzz0, bbbb, m=None):
        """601: HT-Spur bbbb -> gewaehlte ZT, Spur zzz0. Rueckgabe 0 oder ZT_KEINE_ANWAHL (1)."""
        return self._befehl(self.Z.ausgabe, zzz0, bbbb)

    def eingabe(self, zzz0, bbbb, m=None):
        """661: gewaehlte ZT, Spur zzz0 -> HT-Spur bbbb."""
        return self._befehl(self.Z.eingabe, zzz0, bbbb)

    def _befehl(self, funk, zzz0, bbbb):
        tr, Z = self.trommel, self.Z
        virtuell = getattr(tr, 'zeitmodell', 'alt') != 'alt'
        if virtuell:
            Z.zeitmodus(0)
            ph = (tr.vt & 31) * HT_POS_NS                                    # HT-Position des Befehlsbeginns
            pz = (-self.idx0 * ZT_SEKTOR_NS - tr.vt * HT_POS_NS + ph) % ZT_UMLAUF_NS   # Beginn der ZT-Position 0 in Modellzeit
            Z.phasen_fest(1, pz, ph)
        else:
            Z.zeitmodus(1)
            Z.phasen_fest(0, 0, 0)                                           # Phasen aus Uhr und aktuellem Sektor
        rc, dauer_ns, ticks, _wz = funk(zzz0 & 0xFFF, bbbb & 0xFFF)
        if rc == Z.ZT_KEINE_ANWAHL:
            return rc
        if rc == Z.ZT_ABGEBROCHEN:
            raise GrafikAbbruch('Zusatztrommel-Befehl abgebrochen')
        if rc != Z.ZT_OK:
            raise I.KonfigFehler('Zusatztrommel-Befehl fehlgeschlagen (Datei nicht beschreibbar oder Modul aus)')
        self.befehle += 1
        self.zeit_summe_ns += dauer_ns
        self.letzte_dauer_ns = dauer_ns
        if virtuell:
            tr.vt += ticks
            tr._pace()
        return rc

    def leeren(self):
        """Alle vier Zusatztrommeln leeren und die Anwahl aufheben (wie c8205_zt.Zusatztrommeln.leeren)."""
        if self.eingeschaltet:
            self.Z.leeren()

    # --- Steuerung ------------------------------------------------------------------------------------------------
    def abbrechen(self):
        """Aus einem anderen Thread: beendet einen laufenden Befehl (er wirft GrafikAbbruch)."""
        if self.eingeschaltet:
            self.Z.abbrechen()

    # --- Anzeige (HW-Check, nur lesend, ohne Zeit) -----------------------------------------------------------------
    def ansicht(self):
        """Fuer den HW-Check: (gewaehlt, adressen, inhalt). gewaehlt 0..4 (0 = keine Anwahl); adressen = je ZT die zuletzt bearbeitete
        Adresse (Spur*32+Sektor, laeuft waehrend eines Befehls mit) oder None; inhalt = das Wort an der Adresse der gewaehlten ZT
        (33 Bit) oder None. Es zeigt immer nur die gewaehlte ZT einen Inhalt (es ist immer nur eine aktiv)."""
        if not self.eingeschaltet:
            return 0, [None] * ZT_ANZAHL, None
        Z = self.Z
        adressen = []
        for k in range(1, ZT_ANZAHL + 1):
            a = Z.letzte_adresse(k)
            adressen.append(a if a >= 0 else None)
        g = Z.gewaehlt()
        inhalt = None
        if 1 <= g <= ZT_ANZAHL and adressen[g - 1] is not None:
            inhalt = Z.lesen(g, adressen[g - 1]) & ((1 << 33) - 1)
        return g, adressen, inhalt

    def statistik(self):
        return dict(zt_befehle=self.befehle, zt_zeit_summe_ms=round(self.zeit_summe_ns / 1e6, 3),
                    zt_letzte_dauer_ms=round(self.letzte_dauer_ns / 1e6, 3), zt_gewaehlt=self.Z.gewaehlt() if self.eingeschaltet else 0)

    def schliessen(self):
        if self.eingeschaltet:
            self.eingeschaltet = False
            try:
                self.Z.ausschalten()
            except Exception:
                pass
