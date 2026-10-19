/* trommel.h — eigenständiges Modul, das die Magnettrommel (Speicher)
 * simuliert: Hintergrundprozess (Thread) für die virtuelle Drehung,
 * externe Sektornummer-Variable, Auftragskanal mit Koinzidenzprüfung
 * sowie direkte Lese-/Schreibfunktionen für Vorbelegung und Tests.
 *
 * ERWEITERUNG (13.10.2026): Koinzidenz ist jetzt Teil des Moduls.
 * - Der Hintergrundprozess merkt sich die AKTUELLE Zelle (= Sektornummer;
 *   die Bahnwahl kostet keine Zeit) und schaltet sie alle 104 µs weiter
 *   (PERM-Reihenfolge, s. Hardware.md / Magnettrommel.md).
 * - Der Knotengraph stellt Anforderungen über trommel_lesen_warten() bzw.
 *   trommel_schreiben_warten(). Der Aufruf blockiert; der Hintergrundprozess
 *   führt die Anforderung erst aus, wenn die Sektornummer der Adresse die
 *   aktuelle ist, und meldet die Wartezeit in Wortzeiten (Ticks) zurück.
 * - "Schlitz ist Schlitz" (Entscheidung des Projektinhabers, 13.10.2026): Ist eine Sektornummer
 *   aktuell, dann für die ganzen 104 µs (digital). Trifft in dieser Zeitspanne eine Anforderung
 *   für diesen Sektor ein, wird sie sofort bedient (Wartezeit 0). Trifft sie später ein, wartet
 *   sie, bis der Sektor wieder aktuell ist (1..31 Ticks). Das Makro
 *   TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ=0 würde stattdessen erst den nächsten Tickbeginn zulassen.
 * - Der Takt wird aus der Monotonic-Uhr abgeleitet (absolute Zeitpunkte),
 *   daher driftet er nicht, und ein verspätet aufwachender Thread holt
 *   übersprungene Ticks nach, statt Sektoren auszulassen.
 * - Plattformen: Linux (pthread, clock_nanosleep) und Windows (Win32, plattform.h). Der Windows-Zweig
 *   ist geschrieben, aber NICHT übersetzt und NICHT getestet.
 *
 * ECHT vs. ICH-C (s. Trommelrechner-Virtualisierung.md, in Arbeit):
 * - Datei: 4096 Zeilen "aaaa: ttttttttttt\n" (18 Byte, LF), aaaa = logische
 *   12-Bit-Adresse (4 Oktalziffern), t = 11 Oktalziffern Zellinhalt.
 *   Das ist das Format der Interpreter-Trommeldatei
 *   (virtuelle_Geraete/Trommel/trommel.txt, TROMMEL_ZEILE_LAENGE = 18).
 *   (Vorher: "oooo wwwwwwwwwww", 17 Byte — inkompatibel zum Interpreter.)
 * - Die Bahnsperrenschalter (bahnsperre.h) werden im Schreibpfad geprüft,
 *   der Zugriff verbraucht aber auch bei Sperre seine Wartezeit
 *   (Befehlsablauf bleibt unbeeinflusst, s. bahnsperre.h).
 */
#ifndef TROMMEL_H
#define TROMMEL_H

#include <stdint.h>
#include "c8205_api.h"

/* Aktuelle Sektornummer (logisch, 0-37 oktal), wechselt alle 104 µs.
 * Nur zum Beobachten (Pult, Statistik); die Koinzidenz entscheidet das Modul. */
extern C8205_API volatile unsigned int trommel_aktuelle_sektornummer;

/* Rückgabewerte */
#define TROMMEL_OK                 0
#define TROMMEL_SCHREIBEN_OK       0
#define TROMMEL_SCHREIBEN_GESPERRT 1  /* Bahnsperrenschalter aktiv, s. bahnsperre.h */
#define TROMMEL_ABGEBROCHEN        2  /* Strg+C (abbruch_angefordert) oder trommel_warten_abbrechen() */
#define TROMMEL_FEHLER             3  /* Trommel aus, Adresse > 07777, Dateifehler */

/* Einschalten: prüft/öffnet die Datei und startet den Hintergrundprozess.
 * Die Startlage der Trommel ist zufällig (Autor-Vorgabe).
 * dateipfad ist UTF-8 (unter Windows wird er in einen Wide-Char-Pfad umgewandelt). */
C8205_API int  trommel_einschalten(const char *dateipfad);

/* Wie trommel_einschalten, aber mit fester Startlage (PERM-Index 0..31),
 * für reproduzierbare Tests. start_index < 0 = zufällig. */
C8205_API int  trommel_einschalten_start(const char *dateipfad, int start_index);

/* Ausschalten: weckt wartende Aufrufer (TROMMEL_ABGEBROCHEN), stoppt den
 * Hintergrundprozess, schließt die Datei. */
C8205_API void trommel_ausschalten(void);

/* Aktuelle Sektornummer, exakt aus der Uhr berechnet (die Variable oben wird vom
 * Hintergrundprozess gesetzt und kann zwischen zwei Aufwachvorgängen veraltet sein). */
C8205_API unsigned int trommel_aktueller_sektor(void);

/* Sektor- bzw. Bahnanteil einer 12-Bit-Adresse (bitweise, s. Hardware.md). */
C8205_API unsigned int trommel_sektor(unsigned int adresse);
C8205_API unsigned int trommel_bahn(unsigned int adresse);

/* ---- Zugriffe des Knotengraphen (mit Koinzidenz) ----------------------
 * Blockieren, bis die Zelle unter dem Kopf ist und der Zugriff erfolgt ist.
 * wartezeit (darf NULL sein): Ticks (Wortzeiten zu 104 µs) vom Eintreffen
 * der Anforderung bis zur Ausführung, 0..31 (0 = im aktuellen Zeitschlitz bedient).
 * Nur EIN Aufrufer gleichzeitig (weitere Aufrufer warten, bis der Kanal frei ist). */
C8205_API int trommel_lesen_warten(unsigned int adresse, uint64_t *wert, unsigned int *wartezeit);
C8205_API int trommel_schreiben_warten(unsigned int adresse, uint64_t wert, unsigned int *wartezeit);

/* Bricht einen wartenden Zugriff aus einem anderen Thread ab (z. B. wenn der
 * Host Strg+C selbst behandelt); der Aufruf liefert dann TROMMEL_ABGEBROCHEN.
 * Das Flag gilt fuer den laufenden oder, wenn gerade keiner laeuft, fuer den NAECHSTEN
 * Zugriff und wird dabei verbraucht. */
C8205_API void trommel_warten_abbrechen(void);

/* ---- Direkte Zugriffe OHNE Koinzidenz -----------------------------------
 * Nur für Vorbelegung der Trommel aus der Testdatei und für Testrahmen,
 * NICHT für den Befehlsablauf. Adresse = voller 12-Bit-Wert (Bahn<<5 | Sektor).
 * trommel_lesen liefert bei Fehler 0 (Meldung auf stderr). Der Wert wird beim
 * Schreiben auf 33 Bit begrenzt. */
C8205_API uint64_t trommel_lesen(unsigned int adresse);
C8205_API int      trommel_schreiben(unsigned int adresse, uint64_t wert);

/* ---- Beobachtung --------------------------------------------------------*/
typedef struct {
    unsigned long long ticks;                 /* seit dem Einschalten verstrichene Wortzeiten (aus der Uhr) */
    unsigned long long aufwachen;             /* Anzahl Aufwachvorgänge des Hintergrundprozesses */
    unsigned long long nachgeholte_ticks;     /* Ticks, die erst nach dem Soll-Zeitpunkt bearbeitet wurden */
    unsigned long long verspaetung_summe_ns;  /* Summe der Aufwach-Verspätungen */
    unsigned long long verspaetung_max_ns;
    unsigned long long zugriffe;              /* ausgeführte Aufträge (auch gesperrte Schreibzugriffe) */
    unsigned long long wartezeit_summe_ticks; /* Summe der gemeldeten Wartezeiten */
} trommel_statistik_t;

C8205_API void trommel_statistik_lesen(trommel_statistik_t *s);

#endif
