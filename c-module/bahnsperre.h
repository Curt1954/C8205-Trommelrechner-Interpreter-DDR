/* bahnsperre.h — Bahnsperrenschalter (Abb. 5, s. Hardware.md).
 *
 * ECHT: sechs Schalter, oktale Kennzeichnung 0001/0040/0100/0200/
 * 0400/1000, sperren wählbare Gruppen von Bahnen (Spurbereich
 * 0000-1740 oktal, d. h. Bahn-Nr. 0-37 oktal / 0-31 dezimal) gegen
 * Überschreiben. Schalter 0001 (EIN-AUS) wirkt unabhängig: EIN ->
 * mindestens Spur 0000 gesperrt; AUS -> alle Spuren offen. Bei EIN
 * gilt (Original-Tabelle 1, ausgewertet): Bahn B gesperrt <=> B ist
 * Bit-Teilmenge der eingeschalteten Zusatzschalter (40₈->Bit0,
 * 100₈->Bit1, 200₈->Bit2, 400₈->Bit3, 1000₈->Bit4 der Bahn-Nr.).
 * Bahnen ab Spur 2000₈ sind darüber nie sperrbar. Beeinflusst laut
 * Original-Text NICHT den Befehlsablauf — reine Schreibschutzfunktion,
 * durchgesetzt im Schreibpfad der Trommel (s. trommel.c).
 *
 * ICH-C: Die sechs Schalterstellungen kommen aus dem Aufrufschalter --BASP
 * des Interpreters (Modus GRAFIK) und werden beim Hochfahren der Trommel
 * ueber bahnsperre_hochfahren() uebernommen; diese haelt sie in einer
 * Schalterdatei neben der Trommeldatei fest (Entscheidung 16.10.2026,
 * Entwurf 86/87; ersetzt die fruehere Festlegung "es wird nie eine
 * Konfigurationsdatei geben"). bahnsperre_setzen() bleibt die
 * Schnittstelle fuer die Werteuebernahme im Speicher.
 */
#ifndef BAHNSPERRE_H
#define BAHNSPERRE_H

#include "c8205_api.h"

/* Bit-Positionen in bahnsperre_schalter — reine Aufzählungsreihenfolge,
 * KEINE Ableitung aus den oktalen Kennzeichnungen selbst. */
#define BAHNSPERRE_BIT_0001 0   /* EIN-AUS-Hauptschalter */
#define BAHNSPERRE_BIT_0040 1
#define BAHNSPERRE_BIT_0100 2
#define BAHNSPERRE_BIT_0200 3
#define BAHNSPERRE_BIT_0400 4
#define BAHNSPERRE_BIT_1000 5

/* Aktueller Zustand aller sechs Schalter als Bitmaske (Bit=1 -> EIN). */
extern C8205_API volatile unsigned int bahnsperre_schalter;

/* Einzige Schnittstelle: alle sechs Schalterstellungen direkt setzen
 * (0=AUS, 1=EIN je Parameter) — von der Oberfläche aufzurufen. */
C8205_API void bahnsperre_setzen(int ein_aus, int s0040, int s0100, int s0200,
                        int s0400, int s1000);

/* Hochfahren der Bahnsperrenschalter (Entwurf 86/87), als Erstes, vor dem ersten Trommelzugriff.
 * trommelpfad: Pfad der Trommeldatei (UTF-8). Die Schalterdatei liegt daneben: Pfad ohne Endung plus ".basp".
 * basp: NULL oder genau sechs Zeichen '0'/'1' (Reihenfolge 0001, 0040, 0100, 0200, 0400, 1000, links nach rechts).
 *  - basp angegeben: Stellung uebernehmen und IMMER in die Datei schreiben (eine Zeile, sechs Zeichen, LF).
 *  - basp NULL: Stellung aus der Datei uebernehmen; fehlt die Datei, wird sie mit 000000 angelegt und 000000 uebernommen.
 *  - Eine vorhandene, aber fehlerhafte oder nicht lesbare Datei wird NICHT ueberschrieben (Fehler);
 *    ebenso Fehler, wenn die Datei nicht angelegt oder nicht geschrieben werden kann.
 * Rueckgabe 0 = Erfolg, -1 = Fehler (Text in meldung, dann sind die Schalter unveraendert).
 * stellung (darf NULL sein, mindestens 7 Byte): die uebernommene Stellung als Text mit Endnull. */
C8205_API int bahnsperre_hochfahren(const char *trommelpfad, const char *basp,
                                    char *stellung, char *meldung, unsigned int meldung_groesse);

/* Name der Schalterdatei zu einer Trommeldatei (Pfad ohne Endung plus ".basp"); 0 = Erfolg, -1 = Puffer zu klein. */
C8205_API int bahnsperre_dateiname(const char *trommelpfad, char *ziel, unsigned int groesse);

/* Liefert 1, wenn der EIN-AUS-Hauptschalter (0001) auf EIN steht. */
C8205_API int bahnsperre_hauptschalter_ein(void);

#define BAHNSPERRE_OFFEN     0
#define BAHNSPERRE_GESPERRT  1

/* Prüft, ob eine gegebene Bahn (Bahn-Nr., 0 = Spur 0000, 1 = Spur
 * 0040, ... 127 = Spur 7700) gegen Überschreiben gesperrt ist —
 * vollständig nach Original-Tabelle 1, s. o. */
C8205_API int bahnsperre_spur_gesperrt(unsigned int bahn);

#endif
