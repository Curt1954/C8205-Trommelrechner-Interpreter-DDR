/* tonmisch.h - Tonmischer fuer den Modus GRAFIK (Stufe 4, GRAFIK_Beschreibung Abschnitt 6 (alt: Dok. 10) S4-01 bis S4-03, S4-12).
 *
 * Aufbau: 44,1 kHz, mono, 16 bit, Bloecke zu 10 ms (441 Samples).  Ein Strom laeuft vom Start bis zum Ende dauernd (bei Ruhe
 * Stille).  Einzelklaenge werden in den naechsten Block eingemischt und ueberlappen (Summe, auf 16 bit begrenzt); Dauergeraeusche
 * sind Schleifen mit Pegel 0 bis 1.  Je Tonkanal (Rechner, Schreibwerk, Leser, Stanzer) gibt es ein Tor: geschlossen = stumm,
 * Einzelklaenge und Schleifen des Kanals werden verworfen, neue nicht angenommen.
 *
 * Der Mischer ist eine Instanz (tm_t); mehrere Instanzen sind unabhaengig.  Alle Funktionen ausser tm_frei() sind aus beliebigen
 * Threads aufrufbar (ein Mutex je Instanz).  Der Mischer ruft nie in Python zurueck: Zeitgeber der Zustandsautomaten laufen ueber
 * tm_warte_takt() in einem Python-Thread, der Ausfall wird mit tm_ausfall() abgefragt.
 *
 * Senken (vor tm_starten waehlen, genau eine):
 *   tm_senke_prozess  Abspielprogramm mit Roh-Audio (s16le, 44100 Hz, mono) ueber eine Roehre an dessen Standardeingabe
 *                     (Linux: posix_spawnp; Windows: nicht moeglich, dort tm_senke_winmm)
 *   tm_senke_winmm    Windows: waveOut (winmm), ein Ring aus vier Puffern zu 10 ms.  NICHT uebersetzt, NICHT getestet.
 *   tm_senke_datei    schreibt die Bloecke in eine Datei (Trockenlauf)
 *   tm_senke_speicher sammelt die Bloecke im Speicher (Pruefungen; hoechstens TM_SPEICHER_MAX Byte)
 *   keine             der Strom wird erzeugt und verworfen
 * Ohne tm_starten (kein Thread) erzeugt tm_schritt() Bloecke von Hand: fuer Pruefungen ohne Echtzeit.
 *
 * STAND: Linux gebaut und mit Testrahmen geprueft (testframe_tonmisch.c, -static).  Der Windows-Zweig ist nach der Win32-Dokumentation
 * geschrieben und nicht uebersetzt.  Ton am Geraet nicht geprueft.
 */
#ifndef TONMISCH_H
#define TONMISCH_H

#include <stddef.h>
#include <stdint.h>
#include "c8205_api.h"

#define TM_RATE        44100
#define TM_BLOCK       441                 /* Samples je Block = 10 ms */
#define TM_BLOCK_BYTE  (TM_BLOCK * 2)
#define TM_VORLAUF     2                   /* Voreinstellung: der Erzeuger liegt hoechstens 2 Bloecke (20 ms) vor der Wiedergabe (G4-004; vorher 3) */
#define TM_VORLAUF_MAX 3                   /* hoechstens 3 Bloecke (30 ms); Ring aus 4 Bloecken */
#define TM_RING        4
#define TM_SCHLUESSEL  32                  /* Laenge eines Schluessels einschliesslich Endenull */
#define TM_SPEICHER_MAX (64u * 1024u * 1024u)

#define TM_KANAL_RECHNER     0
#define TM_KANAL_SCHREIBWERK 1
#define TM_KANAL_LESER       2
#define TM_KANAL_STANZER     3
#define TM_KANAELE           4

#define TM_OK        0
#define TM_FEHLER   (-1)                   /* falscher Aufruf (Kanal, Klang, Zustand) oder kein Speicher */
#define TM_VOLL     (-2)                   /* keine freie Stimme (Klang wurde verworfen) */
#define TM_AUSFALL  (-3)                   /* die Senke ist ausgefallen */

typedef struct tonmisch tm_t;

C8205_API tm_t *tm_neu(void);
C8205_API void  tm_frei(tm_t *t);                                      /* schliesst und gibt frei */

/* Klang uebergeben (Kopie, mono, 16 bit, little endian im Rechner) -> Klangnummer >= 0 oder TM_FEHLER */
C8205_API int   tm_klang(tm_t *t, const int16_t *daten, size_t anzahl);

/* Senke waehlen (vor tm_starten bzw. tm_schritt; hoechstens eine) */
C8205_API int   tm_senke_prozess(tm_t *t, char *const argv[]);          /* argv: NULL-beendet, argv[0] wird im Suchpfad gesucht */
C8205_API int   tm_senke_winmm(tm_t *t);                                /* nur Windows, sonst TM_FEHLER */
C8205_API int   tm_senke_datei(tm_t *t, const char *pfad);
C8205_API int   tm_senke_speicher(tm_t *t);
C8205_API size_t tm_speicher_laenge(tm_t *t);                           /* bisher gesammelte Byte */
C8205_API size_t tm_speicher_kopie(tm_t *t, uint8_t *ziel, size_t kapazitaet);   /* kopiert vom Anfang, Rueckgabe: Zahl der Byte */

/* Strom */
C8205_API int   tm_vorlauf(tm_t *t, int bloecke);                       /* Vorlauf einstellen (1 bis TM_VORLAUF_MAX), vor tm_starten */
C8205_API int   tm_starten(tm_t *t);                                    /* Thread: erzeugt dauernd Bloecke im Takt der Uhr */
C8205_API int   tm_schritt(tm_t *t, int bloecke);                       /* ohne Thread: erzeugt und sendet Bloecke sofort */
C8205_API void  tm_block(tm_t *t, int16_t *ziel);                       /* mischt einen Block (441 Samples), ohne Senke (Pruefungen) */
C8205_API void  tm_schliessen(tm_t *t);                                 /* Thread beenden, Senke schliessen, alle Stimmen verwerfen */

/* Ereignisse.  schluessel: Zeichenkette bis TM_SCHLUESSEL-1 Zeichen oder NULL/"" (kein Schluessel) */
C8205_API int   tm_einzel(tm_t *t, int kanal, int klang, double pegel, const char *schluessel);
C8205_API int   tm_dauer_an(tm_t *t, int kanal, const char *schluessel, int klang, double pegel);
C8205_API void  tm_dauer_pegel(tm_t *t, const char *schluessel, double pegel);
C8205_API void  tm_dauer_aus(tm_t *t, const char *schluessel);          /* entfernt alle Stimmen mit diesem Schluessel */
C8205_API void  tm_tor(tm_t *t, int kanal, int offen);
C8205_API void  tm_alles_aus(tm_t *t);                                  /* alle Stimmen sofort weg, Tore bleiben */
C8205_API int   tm_klingt(tm_t *t);
C8205_API int   tm_klingt_schluessel(tm_t *t, const char *schluessel);

/* Takt und Ausfall */
C8205_API unsigned long tm_bloecke(tm_t *t);                            /* bisher gesendete Bloecke */
/* wartet bis zu `ms` Millisekunden, bis die Blockzahl von `zuletzt` abweicht (oder Ausfall/Ende); Rueckgabe: Blockzahl */
C8205_API unsigned long tm_warte_takt(tm_t *t, unsigned long zuletzt, unsigned ms);
C8205_API int   tm_ausfall(tm_t *t, char *text, size_t kapazitaet);     /* 1 = ausgefallen (Text), 0 = laeuft */

#endif
