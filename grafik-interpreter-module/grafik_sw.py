# -*- coding: utf-8 -*-
"""
grafik_sw.py - Logik des SW-Fensters im Modus GRAFIK (Stufe 3), ohne Tkinter.
Version: G4-008

Zwei Teile:
  SwAnzeige  - Darstellung der Schreibwerk-Ausgabe mit Schreibposition (Spalte 0 bis 130), Tabulatorstopp alle 12 Spalten,
               rechtem Anschlag (Ueberdruck auf Position 130, kein Zeilenumbruch), WR/WRZL (Position 0).
               GRAFIK_Beschreibung §6 (alt: Dok. 03 Abschnitt 5 Nr. 17), GRAFIK_Beschreibung §3.1 (alt: Dok. 01 Abschnitt 1.6).
  SwEingabe  - Abbildung der getippten Computertastatur-Zeichen auf K0-Zeichen (R300-Code, Tabelle 1), Zeichenlage KB/GB,
               selbstaendiges Umschaltzeichen, zwei Eingaben im Abstand von etwa 0,1 s, Blockade ohne aktiven 011, Anzeige jedes
               angenommenen Zeichens (GRAFIK_Beschreibung §4.5, §5.7 (alt: Dok. 01 Abschnitt 1.7), GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-04, S3-11, S3-13).

Festlegung des Projektinhabers (18.10.2026): Benannte Zeichen, die nicht visualisierbar sind (ZV, BM, Irrung Zeichen, Irrung Satz,
Transport, die Zeichen ≈ ≋ △ - in sw_zeichen() als <Name> geliefert), werden im SW-Fenster NUR AUSGEFUEHRT: keine Anzeige. Da keines von
ihnen eine Wirkung auf das Fenster hat, bewegt es auch die Schreibposition nicht (Auslegung, bitte bestaetigen).
Ausgefuehrt und dargestellt werden: sichtbare Zeichen, Leerzeichen (ZR), TAB, WRZL; WR (kommt als <WR>) wird ausgefuehrt: Position 0.

Standardannahmen dieser Datei (zur Abnahme, in der GRAFIK_Beschreibung nicht ausdruecklich festgelegt):
  (a) Eine Zeichenfolge der Senke gilt nur dann als benanntes Zeichen, wenn der GANZE uebergebene Text die Form <Name> hat
      (sw_zeichen() liefert je Aufruf genau ein Zeichen); einzelne '<' und '>' sind gewoehnliche Zeichen.
  (b) WR (Wagenruecklauf) setzt die Position auf 0, ohne Zeilenvorschub; folgende Zeichen ueberdrucken die Zeile.
      WRZL beginnt eine neue Zeile (Position 0). Ein TAB fuellt nur fehlende Spalten mit Leerzeichen, loescht nichts.
  (c) ENTFALLEN (18.10.2026): Vormerkung und Verfall. Kein Warten, kein Programmende als Regel (GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-13, S3-18).
  (d) Tippen ohne aktiven 011 (Rechner wartet jetzt nicht auf SW) ist blockiert: keine Eingabe, keine Anzeige, nichts vorgemerkt.
  (e) Getippt waehrend die zweite Eingabe eines vorigen Zeichens noch aussteht (unter 0,1 s): still verworfen (S3-14 offen).

Regel des Projektinhabers (18.10.2026, G3-004): Fuer die Eingabe am SW zaehlt NUR die Zeichenlage des SW selbst, nie die des Rechners
(Machine.zeichenlage). Die Umschalttasten der Computertastatur werden nicht gesondert ausgewertet: das Fenster erkennt am getippten Zeichen,
welche Lage es braucht. Der BENUTZER tippt frei, mit oder ohne Umschalttaste; weitere Festlegungen gibt es nicht, den Rest erledigt das Fenster.
Der Vorzustand des SW ist nach dem Einschalten UNBESTIMMT (SwEingabe.lage = None). Fuer das ERSTE Zeichen mit bestimmter Lage geht deshalb
IMMER das Umschaltzeichen zum Rechner (Umschaltzeichen, dann Zeichen: 'A' -> Um. GB, A, das SW steht auf GB; 'a' -> Um. KB, a, das SW steht
auf KB). Bei den folgenden Zeichen entscheidet das vorhergehende Zeichen: gleiche Lage -> nur das Zeichen, andere Lage -> Umschaltzeichen
und Zeichen. Zeichen mit gleichem Code in beiden Lagen (ZR, TAB, WRZL) gehen allein und aendern die Lage nicht (G3-008, Antwort 18.10.2026).
"""
import threading
import time

import c8205_interp as I

VERSION_SW = 'G4-008'
BREITE = 130          # rechter Anschlag
TAB_ABSTAND = 12      # Tabulatorstopp alle 12 Zeichen
_ECHO = {'WRZL': '\n', 'TAB': '\t', 'ZR': ' '}      # K0-Zeichen -> Text fuer die Anzeige der Eingabe (alle anderen Zeichen: sie selbst)


class SwAnzeige:
    """Zeilenmodell des Fensters: eine Liste von Zellen je Zeile (jede Zelle ein Zeichen oder <Name>)."""

    def __init__(self):
        self.zeilen = [[]]
        self.pos = 0
        self.geaendert = set()      # Zeilennummern (0-basiert), die neu zu zeichnen sind
        self.neu_ab = 0             # Zeilen ab hier sind neu angehaengt

    def _setze(self, zelle):
        z = self.zeilen[-1]
        i = self.pos if self.pos < BREITE else BREITE - 1      # hinter dem Anschlag: Ueberdruck auf Position 130
        while len(z) < i:
            z.append(' ')
        if i < len(z):
            z[i] = zelle
        else:
            z.append(zelle)
        if self.pos < BREITE:
            self.pos += 1
        self.geaendert.add(len(self.zeilen) - 1)

    def _tab(self):
        ziel = min(BREITE, (self.pos // TAB_ABSTAND + 1) * TAB_ABSTAND)
        z = self.zeilen[-1]
        while len(z) < ziel:
            z.append(' ')
        self.pos = ziel
        self.geaendert.add(len(self.zeilen) - 1)

    def _rueck(self):
        """Rücktaste (G4-006): löscht das Zeichen links der Schreibposition und setzt die Position um eins zurück; am Zeilenanfang keine Wirkung.
        Steht das Zeichen am Zeilenende, wird die Zelle entfernt, sonst durch ein Leerzeichen ersetzt (die Zeichen rechts davon bleiben an ihrer Stelle).
        Keine Anzeige eines Namens und kein Wert für den Rechner: reine Fensterfunktion."""
        if self.pos <= 0:
            return
        z = self.zeilen[-1]
        i = self.pos - 1
        if i < len(z):
            if i == len(z) - 1:
                del z[i]
            else:
                z[i] = ' '
        self.pos = i
        self.geaendert.add(len(self.zeilen) - 1)

    def schreibe(self, s):
        """Ein Zeichen der Schreibwerk-Ausgabe, wie sw_zeichen() es liefert: ein Zeichen, \\t, \\n, \\r oder <Name>.
        Benannte (nicht visualisierbare) Zeichen werden nur ausgefuehrt: keine Anzeige, keine Bewegung der Schreibposition;
        einzige Wirkung auf das Fenster hat <WR> (Position 0)."""
        if len(s) > 2 and s[0] == '<' and s[-1] == '>':
            if s == '<WR>':             # Wagenruecklauf kommt aus sw_zeichen() als <WR>: wird ausgefuehrt (Position 0)
                self.pos = 0
            return
        for c in s:
            if c == '\n':
                self.zeilen.append([])
                self.pos = 0
                self.geaendert.add(len(self.zeilen) - 1)
            elif c == '\r':
                self.pos = 0
            elif c == '\b':             # G4-006: Rücktaste aus dem Fenster (nie aus der Rechnerausgabe: sw_zeichen() liefert kein Zeichen 8)
                self._rueck()
            elif c == '\t':
                self._tab()
            else:
                self._setze(c)

    def zeile_text(self, n):
        return ''.join(self.zeilen[n])

    def text(self):
        return '\n'.join(self.zeile_text(n) for n in range(len(self.zeilen)))

    def hole_geaenderte(self):
        g = sorted(self.geaendert)
        self.geaendert = set()
        return g


# ---------------------------------------------------------------------------------------------------------------------
# Eingabe

_KB, _GB = 'KB', 'GB'


def _zeilen_fuer(zeichen):
    return [r for r in I.TABELLE1 if r[0] != 54 and r[6] is not None and ord(zeichen) in (r[4], r[5])]


def lage_des_zeichens(zeichen):
    """'KB' oder 'GB', wenn das Zeichen nur in dieser Lage vorkommt; None, wenn es in beiden Lagen denselben Code hat (ZR, TAB, WRZL, ...)
    oder im R300-Code nicht vorkommt."""
    if len(zeichen) != 1 or zeichen in ('\r', '\n', '\t', ' ') or ord(zeichen) < 32:
        return None
    for r in _zeilen_fuer(zeichen):
        nr, kl, gb, _, a_gb, a_kb = r[:6]
        if nr in (25, 26):
            continue
        in_kb, in_gb = (a_kb == ord(zeichen)), (a_gb == ord(zeichen))
        if in_kb and in_gb:
            return None
        if in_kb:
            return _KB
        if in_gb:
            return _GB
    return None


def abbilden(zeichen, lage):
    """Getipptes Computertastatur-Zeichen -> Liste von K0-Zeichen, die der Rechner nacheinander erhalten muss
    (ggf. zuerst das Umschaltzeichen), oder None, wenn das Zeichen im R300-Code nicht vorkommt (nicht angenommen).
    lage: aktuelle Zeichenlage des SW selbst, 'KB' oder 'GB' (SwEingabe.lage), NICHT die Lage des Rechners; None = Vorzustand unbestimmt
    (nach dem Einschalten): das Fenster kennt die Lage nicht und sendet daher bei jedem Zeichen mit bestimmter Lage zuerst das
    Umschaltzeichen (Regel des Projektinhabers 18.10.2026, G3-008). Zeichen mit gleichem Code in beiden Lagen (ZR, TAB, WRZL) gehen allein."""
    if len(zeichen) != 1:
        return None
    if zeichen == '\r' or zeichen == '\n':
        return ['WRZL']
    if zeichen == '\t':
        return ['TAB']
    if zeichen == ' ':
        return ['ZR']
    if ord(zeichen) < 32:
        return None
    if not _zeilen_fuer(zeichen) or all(r[0] in (25, 26) for r in _zeilen_fuer(zeichen)):
        return None
    need = lage_des_zeichens(zeichen)
    if need is None or lage == need:                  # lage None (erstes Zeichen nach dem Einschalten) ist ungleich need: Umschaltzeichen geht immer mit
        return [zeichen]
    return ['Um. KB' if need == _KB else 'Um. GB', zeichen]


class SwEingabe:
    """Eingabe am SW-Fenster (Entscheidung 18.10.2026, GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-04, S3-11, S3-13, S3-18; G3-005; neu G4-007: kleiner Puffer, 19.10.2026).

    PUFFER (G4-007, Wunsch des Projektinhabers 19.10.2026): Ein Zeichen, das kommt, waehrend der Rechner noch nicht wieder bei einem 011 ist
    (er verarbeitet das vorige Zeichen oder das Umschaltzeichen), geht NICHT mehr verloren, sondern wartet im Puffer (hoechstens PUFFER_MAX
    Eingaben, Reihenfolge bleibt). Der Takt des Fensters (liefern()) gibt jeweils EINE Eingabe an den naechsten aktiven 011 weiter; erst dann
    wird das Zeichen angezeigt und klingt (die Anzeige zeigt nur, was den Rechner erreicht hat). Der Puffer wird VERWORFEN, sobald der Kanal
    wechselt (Anwahl K1 bis K3, Schalter/Flag SW weg; Zaehler Machine.kanal_wechsel) und ist dort auch nicht fuellbar: ohne Kanal K0/SW ist die
    Taste weiter blockiert (S3-13). Ist der Puffer voll, geht die Taste verloren ('voll'). Eine Eingabe in der anderen Lage ist ein
    Paar (Umschaltzeichen, Zeichen); es kommt ganz oder gar nicht in den Puffer.

    Ein Zeichen in der anderen Lage kommt als ZWEI Eingaben (Umschaltzeichen, Zeichen); die zweite folgt dem echten Abstand der Tasten
    (kein fester Wert, siehe U-11 unten) und frueh genug erst, wenn der Rechner wieder bei einem 011 ist (vorher wartet sie im Puffer).

    KLANG (G4-008, OP-09, Entscheidung 21.10.2026): Der Klang kommt beim TASTENDRUCK, sobald das Zeichen im Puffer ist (Aufruf 'klick'), auch wenn der Rechner
    es noch nicht angenommen hat; die ANZEIGE kommt weiter erst bei der Annahme (Aufruf 'echo'). Je Zeichen genau ein Klang. Das Umschaltzeichen
    klingt nie; bei einem Paar klingt das Zeichen beim Druecken (nicht erst beim Loslassen). Keine Taste (Puffer voll, blockiert, nicht darstellbar) = kein Klang.

    Jedes angenommene Zeichen (kein Umschaltzeichen) wird ueber 'echo' in dieselbe Warteschlange gelegt wie die Ausgabe des Rechners
    (SwFenster.q): gleiche Schreibposition, Reihenfolge beider Quellen bleibt erhalten.
    tippen() aus dem Fenster-Thread; liefern() im Takt des Fensters.
    U-11 (GRAFIK_Beschreibung §5 (alt: Dok. 09) S3-11, Z-2; Antwort 18.10.2026): KEIN fester Abstand. Die zweite Eingabe folgt dem echten Druecken der Tasten:
    (a) tippen(zeichen, abstand=t): t = gemessene Zeit zwischen dem Druecken der Umschalttaste (Umschalt, AltGr) und der Zeichentaste;
    (b) tippen(zeichen) ohne abstand: das Zeichen geht beim Loslassen der Zeichentaste (loslassen()).
    Zeichen 'dazwischen' gibt es nicht; kommt die naechste Taste, ist eine noch ausstehende zweite Eingabe frei (nichts geht verloren).
    """

    EIN_TASTENDRUCK = False         # G4-009 (Projektinhaber 19.10.2026: 'Die Eingabe muss funktionieren'): vorgabemaessig Puffer bis PUFFER_MAX, keine Taste geht verloren.
    #                                 True (G4-008): der Puffer haelt hoechstens EINEN Tastendruck (ein Zeichen ohne Umschalter ODER
    #                                 Umschalter + Zeichen); erst wenn ein Eingabebefehl ihn abgeholt hat, ist die naechste Taste moeglich (sonst 'voll').
    #                                 False: wie G4-007, bis PUFFER_MAX Eingaben
    PUFFER_MAX = 8                  # Eingaben (Umschaltzeichen zaehlen mit); ein Zeichen in der anderen Lage braucht 2

    def __init__(self, k0, maschine, echo=None, abstand=None, zeit=time.monotonic, rueck=None, klick=None):
        self.k0 = k0
        self.klick = klick              # G4-008 (OP-09, Entscheidung 21.10.2026): Aufruf mit dem Zeichentext, SOFORT wenn das Zeichen in den Puffer kommt (Tastendruck);
        #                                 None = kein Klang (Pruefungen). 'echo' bleibt die ANZEIGE und kommt erst bei der Annahme durch den Rechner
        self.m = maschine
        self.echo = echo                # Aufruf mit dem anzuzeigenden Text (ein Zeichen); None = keine Anzeige (Pruefungen)
        self.abstand = abstand            # nur Vorgabe fuer Pruefungen; None = Abstand kommt von den echten Tasten (tippen(abstand=...) oder loslassen())
        self.zeit = zeit
        self.rueck = rueck              # Aufruf ohne Argument: Rücktaste im Anzeigefenster ausführen (G4-006); None = keine Anzeige (Prüfungen)
        self.puffer = []                # [[Token, frei_ab, zweite_haelfte], ...]; frei_ab = Zeitpunkt, ab dem die Eingabe gesendet werden darf; None = erst nach loslassen();
        #                                 zweite_haelfte = True beim Zeichen eines Paares (Umschaltzeichen, Zeichen)
        self.lage = None                # Zeichenlage des SW selbst (nach dem zuletzt GELIEFERTEN Token); nach dem Einschalten unbestimmt (None).
        #                                 Die Lage des Rechners (m.zeichenlage) spielt hier keine Rolle
        self.verworfen_zaehler = 0      # Eingaben, die der Puffer bei Kanalwechsel verworfen hat (Protokoll, Pruefungen)
        self._kanal_stand = getattr(maschine, 'kanal_wechsel', 0)
        self._lock = threading.Lock()

    # --- Kanal und Puffer --------------------------------------------------------------------------------------
    def _kanal_sw(self):
        """True, wenn K0 mit Unterkanal SW angewaehlt ist (sonst ist die Taste blockiert, S3-13)."""
        fl = getattr(self.m, 'fl', None)
        return bool(fl.get('SW')) if fl is not None else True

    def _kanal_pruefen(self):
        """Kanalwechsel seit dem Fuellen (Zaehler) oder K0/SW nicht mehr angewaehlt: Puffer verwerfen."""
        stand = getattr(self.m, 'kanal_wechsel', 0)
        if stand != self._kanal_stand or not self._kanal_sw():
            self._kanal_stand = stand
            if self.puffer:
                # Ausnahme: die zweite Haelfte eines Paares, dessen erste (Umschaltzeichen) schon beim Rechner ist, bleibt. Umschaltzeichen und
                # Zeichen sind EIN Tastendruck, der vor dem Kanalwechsel begann; ohne das Zeichen stuende das Umschaltzeichen allein da.
                bleibt = [self.puffer[0]] if self.puffer[0][2] else []
                if len(bleibt) < len(self.puffer):
                    self.verworfen_zaehler += len(self.puffer) - len(bleibt)
                    self.puffer = bleibt
                    return True
        self._kanal_stand = stand
        return False

    def ausstehend(self):
        """Anzahl der Eingaben im Puffer (noch nicht beim Rechner)."""
        with self._lock:
            return len(self.puffer)

    @property
    def zweite(self):
        """Zur Kompatibilitaet (Protokoll): die erste ausstehende Eingabe oder None."""
        return self.puffer[0] if self.puffer else None

    def _lage_vorschau(self):
        """Lage des SW nach allen Eingaben im Puffer (fuer die Abbildung des naechsten Zeichens)."""
        lage = self.lage
        for eintrag in self.puffer:
            lage = self._lage_nach(eintrag[0], lage)
        return lage

    @staticmethod
    def _lage_nach(token, lage):
        if token == 'Um. KB':
            return _KB
        if token == 'Um. GB':
            return _GB
        need = lage_des_zeichens(token)
        return need if need is not None else lage

    def _geliefert(self, token):
        """Ein dem Rechner gelieferter Token aendert die Lage des SW: ein Umschaltzeichen setzt sie, ein Zeichen mit bestimmter Lage
        ebenfalls (beim ersten Zeichen nach dem Einschalten; sonst steht das SW schon so). Ein Zeichen wird angezeigt."""
        self.lage = self._lage_nach(token, self.lage)
        if not token.startswith('Um.') and self.echo is not None:
            self.echo(_ECHO.get(token, token))

    def _senden(self, token):
        """Eine Eingabe an den Rechner: nur angenommen, wenn JETZT ein 011 aktiv ist (K0.annehmen prueft es)."""
        if self.k0.annehmen('SW', token, nur_offen=True):
            self._geliefert(token)
            return True
        return False

    def _pumpen(self):
        """Gibt die vorderste Eingabe des Puffers weiter, wenn ihre Zeit da ist und ein 011 aktiv ist (ein 011 bekommt genau eine).
        Rueckgabe: Anzahl der gelieferten Eingaben (0 oder 1 je Aufruf, weil ein 011 nur ein Zeichen annimmt)."""
        n = 0
        while self.puffer:
            tok, ab = self.puffer[0][:2]
            if ab is None or self.zeit() < ab:
                break
            if not self._senden(tok):
                break
            self.puffer.pop(0)
            n += 1
        return n

    def erwartet(self):
        """True, wenn der Rechner jetzt (Eingabe-Halt 011, K0, Stellung SW) ein Zeichen vom SW-Fenster erwartet."""
        return self.k0.offen('SW')

    def eingabe_aktiv(self):
        """Fenster soll den Fokus anfordern: ein 011 ist aktiv."""
        return self.erwartet()

    def tippen(self, zeichen, abstand=None):
        """Ein getipptes Zeichen. Rueckgabe (still, kein Ton, keine Meldung):
        'geliefert'   die Eingabe ist angenommen und angezeigt;
        'folgt'       das Umschaltzeichen ist angenommen, das Zeichen folgt mit dem echten Tastenabstand (liefern()) oder beim Loslassen (loslassen());
        'vorgemerkt'  der Rechner ist noch nicht bei einem 011: die Eingabe wartet im Puffer (Anzeige erst bei Annahme);
        'voll'        Puffer voll: die Taste geht verloren;
        'blockiert'   K0/SW nicht angewaehlt: Taste gesperrt, keine Eingabe, keine Anzeige, nichts im Puffer;
        'verworfen'   Zeichen nicht im R300-Code."""
        with self._lock:
            self._kanal_pruefen()
            if not self._kanal_sw():
                return 'blockiert'
            tok = abbilden(zeichen, self._lage_vorschau())
            if tok is None:
                return 'verworfen'
            for eintrag in self.puffer:             # keine Zeichen dazwischen: eine ausstehende zweite Eingabe ist jetzt frei
                if eintrag[1] is None:
                    eintrag[1] = 0.0
            self._pumpen()
            if (self.EIN_TASTENDRUCK and self.puffer) or len(self.puffer) + len(tok) > self.PUFFER_MAX:
                return 'voll'
            if self.klick is not None and not tok[-1].startswith('Um.'):      # G4-008: Klang beim Druecken, vor der Annahme durch den Rechner
                self.klick(_ECHO.get(tok[-1], tok[-1]))
            erste = [tok[0], 0.0, False]
            self.puffer.append(erste)
            zweite = None
            if len(tok) > 1:
                a = self.abstand if abstand is None else abstand
                zweite = [tok[1], None if a is None else self.zeit() + a, True]
                self.puffer.append(zweite)
            self._pumpen()
            if any(e is erste for e in self.puffer):
                return 'vorgemerkt'
            if zweite is not None and any(e is zweite for e in self.puffer):
                return 'folgt'
            return 'geliefert'

    def ruecktaste(self):
        """Rücktaste (G4-006, G4-007): nimmt zuerst das zuletzt vorgemerkte Zeichen aus dem Puffer zurück (mit seinem Umschaltzeichen, wenn
        das ebenfalls noch im Puffer steht); es hat den Rechner nie erreicht und war nie angezeigt. Ist nichts vorgemerkt, löscht sie in der
        Anzeige das zuletzt angezeigte Zeichen. Sie sendet nie etwas an den Rechner und erzeugt weder Ton noch Anzeige.
        Rückgabe: 'zurueckgenommen' | 'geloescht'."""
        with self._lock:
            for i in range(len(self.puffer) - 1, -1, -1):
                if not self.puffer[i][0].startswith('Um.'):
                    del self.puffer[i]
                    if i > 0 and self.puffer[i - 1][0].startswith('Um.'):
                        del self.puffer[i - 1]
                    return 'zurueckgenommen'
            if self.rueck is not None:
                self.rueck()
            return 'geloescht'

    def liefern(self):
        """Im Takt: die vorderste Eingabe des Puffers weitergeben, sobald ihr Abstand abgelaufen und ein 011 aktiv ist; bei Kanalwechsel den
        Puffer verwerfen. Rueckgabe: 'geliefert' | None (nichts geliefert)."""
        with self._lock:
            if self._kanal_pruefen():
                return 'verworfen'
            return 'geliefert' if self._pumpen() else None

    def loslassen(self):
        """Die Zeichentaste wurde losgelassen: die zweite Eingabe (Fall b) ist jetzt frei. Rueckgabe wie liefern()."""
        with self._lock:
            frei = False
            for eintrag in self.puffer:
                if eintrag[1] is None:
                    eintrag[1] = 0.0
                    frei = True
            if not frei:
                return None
            self._kanal_pruefen()
            return 'geliefert' if self._pumpen() else None
