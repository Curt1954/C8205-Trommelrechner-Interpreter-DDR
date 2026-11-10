# -*- coding: utf-8 -*-
"""
C 8205Z - Zusatztrommeln fuer den Interpreter (Python-Fassung, versuchsweise Anbindung).

Version: 0.01-005
(Versionierung: Build zzz erhoeht sich bei jeder Aenderung dieser Datei um 1.)

Zweck: Stellt vier Zusatztrommeln (ZT0 bis ZT3 laut Befehlsadresse, intern k = 1..4, Dateien zt1.txt .. zt4.txt) bereit, die c8205_interp.py nur mit dem Aufrufschalter --C8205Z benutzt.
Ohne den Schalter wird dieses Modul nicht geladen; die Befehle 5k00 030, 601 und 661 verhalten sich dann wie bisher
(Anwahl a2 < 4: Stub, 601/661: Leer-Operation mit Loeschen).

Befehle (Wort = 11 Oktalziffern 'zzzz bbbb BAZ'; die oberen vier Ziffern sind bei allen uebrigen Befehlen ohne Bedeutung):
  5k00 030    Anwahl der Zusatztrommel (k = 1..4: 5100 = ZT0, 5200 = ZT1, 5300 = ZT2, 5400 = ZT3); gilt bis zur naechsten Anwahl.
              Der Interpreter ruft anwahl(k) mit k = 1..4 auf; ZT0 liegt in zt1.txt, ZT3 in zt4.txt (Stand 30.10.2026).
  zzz0 bbbb 601   Ausgabe: HT-Spur bbbb -> gewaehlte ZT, Spur zzz0
  zzz0 bbbb 661   Eingabe: gewaehlte ZT, Spur zzz0 -> HT-Spur bbbb
Adresse: wie die Ausgabe-Adresse des R-300-Kodes; wirksam ist nur die Spur, spur = (adresse >> 5) & 0x7F, die letzte
Oktalziffer und der Sektorteil sind ohne Bedeutung. Ein Befehl uebertraegt immer eine ganze Spur (32 Worte); der
Sektor i der Quelle kommt auf den Sektor i des Ziels (die ZT hat dieselbe logische Nummerierung wie die HT).
Der Adresstransport 032 entfaellt (Entscheidung des Inhabers).

Zeit: Der Interpreter rechnet alle Zeiten = 0; die Zeitrechnung des Moduls (Zusatztrommel_Zeitmodell.md) ist hier
noch nicht angebunden. Die Schnittstelle entspricht in den Namen der Spezifikation (zt_anwahl, zt_ausgabe, zt_eingabe),
damit das spaetere C-Modul an derselben Stelle eingehaengt werden kann.
"""
import os

ZT_ANZAHL = 4
ZT_SPUREN = 128
ZT_SEKTOREN = 32
ZT_OK = 0
ZT_KEINE_ANWAHL = 1
ZT_FEHLER = 3


def zt_spur(adresse):
    """Spur einer ZT-Adresse (zzz0, 12 Bit): die oberen sieben Bit."""
    return (adresse >> 5) & 0x7F


class Zusatztrommeln:
    def __init__(self, verzeichnis, trommel_klasse, leere_datei):
        """verzeichnis: Ordner der vier Dateien zt1.txt .. zt4.txt (Format wie Trommel/trommel.txt; fehlende Dateien
        werden leer angelegt). trommel_klasse: Klasse mit rd/wr/setze_inhalt/schliessen (Trommel des Interpreters).
        leere_datei: Funktion, die eine leere Trommeldatei anlegt."""
        self.verzeichnis = verzeichnis
        self.gewaehlt = 0
        self.zt = {}
        os.makedirs(verzeichnis, exist_ok=True)
        for k in range(1, ZT_ANZAHL + 1):
            pfad = os.path.join(verzeichnis, f'zt{k}.txt')
            if not os.path.isfile(pfad):
                leere_datei(pfad)
            self.zt[k] = trommel_klasse(pfad)

    def pfad(self, k):
        return os.path.join(self.verzeichnis, f'zt{k}.txt')

    def anwahl(self, k):
        """5k00 030, k = 1..4."""
        if k not in self.zt:
            return ZT_FEHLER
        self.gewaehlt = k
        return ZT_OK

    def ausgabe(self, zt_adresse, ht_adresse, ht):
        """601: HT-Spur -> gewaehlte ZT. ht: Objekt mit rd(adr) und wr(adr, wert) (Machine)."""
        if self.gewaehlt == 0:
            return ZT_KEINE_ANWAHL
        z = self.zt[self.gewaehlt]
        s_zt, s_ht = zt_spur(zt_adresse), zt_spur(ht_adresse)
        for i in range(ZT_SEKTOREN):
            z.wr((s_zt << 5) | i, ht.rd((s_ht << 5) | i))
        return ZT_OK

    def eingabe(self, zt_adresse, ht_adresse, ht):
        """661: gewaehlte ZT -> HT-Spur."""
        if self.gewaehlt == 0:
            return ZT_KEINE_ANWAHL
        z = self.zt[self.gewaehlt]
        s_zt, s_ht = zt_spur(zt_adresse), zt_spur(ht_adresse)
        for i in range(ZT_SEKTOREN):
            ht.wr((s_ht << 5) | i, z.rd((s_zt << 5) | i))
        return ZT_OK

    def zelle(self, o, adresse):
        """Inhalt der Zelle adresse (0000 bis 7777) der Zusatztrommel o = 0..3 (ZT0 = zt1.txt); fuer die ZT-Zellen-Pruefung."""
        return self.zt[o + 1].rd(adresse)

    def leeren(self):
        """Alle vier Zusatztrommeln leeren (bei #ZTROMMEL=LEER) und die Anwahl aufheben."""
        for z in self.zt.values():
            z.setze_inhalt({})
        self.gewaehlt = 0

    def schliessen(self):
        for z in self.zt.values():
            z.schliessen()
