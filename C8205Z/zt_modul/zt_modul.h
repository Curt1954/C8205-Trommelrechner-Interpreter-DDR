/* zt_modul.h — Zusatztrommeln (ZT1 bis ZT4) des C 8205Z als eigenständiges C-Modul.
 *
 * Version: 0.01-003   (Build zzz steigt bei jeder Änderung dieser Datei und von zt_modul.c um 1)
 * Spezifikation: Zusatztrommel_Zeitmodell.md (Projekt C8205Z, Abschnitt 6 und 7).
 *
 * Aufgabe: vier Zusatztrommeln zu je 4096 Worten (33 Bit), zwei Puffer zu je 8 Worten mit je einem Zugriffs-
 * semaphor, ein Hintergrundprozess (Empfänger) und das Zeitmodell. Ein E/A-Befehl überträgt immer eine ganze Spur
 * (32 Worte, 4 Blöcke zu 8 Worten); der Aufrufer blockiert bis zum Ende des Befehls.
 *
 *   5k00 030        zt_anwahl(k)                  k = 1..4
 *   zzz0 bbbb 601   zt_ausgabe(zzz0, bbbb, &s)    HT-Spur bbbb -> gewählte ZT, Spur (zzz0 >> 5) & 0x7F
 *   zzz0 bbbb 661   zt_eingabe(zzz0, bbbb, &s)    gewählte ZT, Spur zzz0 -> HT-Spur bbbb
 * (Der Adreßtransport 032 entfällt.) Der Sektor der Quelle kommt auf den gleichen Sektor des Ziels; die Blockfolge
 * betrifft nur die Zeit.
 *
 * Zeit: zwei Betriebsarten (zt_zeitmodus):
 *   ZT_ZEIT_VIRTUELL (Vorgabe)  es wird nicht geschlafen; s->dauer_ns liefert die Dauer nach dem Zeitmodell.
 *   ZT_ZEIT_ECHT                die Seiten warten bis zu den Zeitpunkten des Modells (Monotonic-Uhr): der Aufruf dauert
 *                               rund 81 bis 86 ms, wie der Befehl der Maschine.
 * zt_modell_dauer() rechnet das Modell ohne Datei, ohne Thread und ohne Uhr (Ganzzahl-Nanosekunden); es ist die
 * C-Fassung von spur_ein/spur_aus aus zt_zeitmodell.py.
 *
 * Die Haupttrommel wird über zt_ht_t angekoppelt; Vorgabe sind die Direktzugriffe von trommel.h (trommel_lesen,
 * trommel_schreiben, trommel_aktueller_sektor). Dann muß trommel.c mit eingebunden sein.
 * Mit -DZT_OHNE_TROMMEL entfaellt die Vorgabe (trommel.c wird nicht gebraucht); dann ist zt_ht_ankoppeln VOR zt_einschalten Pflicht.
 * Nur EIN Befehl gleichzeitig (ein zweiter Aufrufer erhält ZT_FEHLER). Windows-Zweig wie plattform.h: nicht übersetzt.
 */
#ifndef ZT_MODUL_H
#define ZT_MODUL_H

#include <stdint.h>
#include "c8205_api.h"

#define ZT_ANZAHL        4
#define ZT_SPUREN        128
#define ZT_SEKTOREN      32
#define ZT_SEKTORZEIT_NS 625000      /* eine ZT-Position (ZT-Umlauf 20 ms) */
#define ZT_HT_POS_NS     104000      /* eine HT-Position (HT-Umlauf 3,328 ms) */
#define ZT_BLOCK         8           /* Worte je Block */
#define ZT_PUFFER        2
#define ZT_UMSCHALT_NS   300000      /* u, Vorgabe 0,3 ms, einstellbar */

/* Rückgabewerte */
#define ZT_OK             0
#define ZT_KEINE_ANWAHL   1          /* der Aufrufer löst den Halt mit Flag A aus */
#define ZT_ABGEBROCHEN    2
#define ZT_FEHLER         3          /* Datei, Modul aus, falsches k, zweiter Aufrufer */

#define ZT_RICHTUNG_EINGABE 0        /* 661: ZT -> HT (Initiator ZT, Empfänger HT) */
#define ZT_RICHTUNG_AUSGABE 1        /* 601: HT -> ZT (Initiator HT, Empfänger ZT) */

#define ZT_ZEIT_VIRTUELL 0
#define ZT_ZEIT_ECHT     1

/* Permutationen: Position 0..31 -> logischer Sektor (oktal); ZT_PERM[4i+k] == HT_PERM[8k+i] */
extern C8205_API const unsigned char ZT_HT_PERM[32];
extern C8205_API const unsigned char ZT_ZT_PERM[32];

typedef struct {
    uint64_t (*lesen)(unsigned adr);               /* Vorgabe trommel_lesen */
    int      (*schreiben)(unsigned adr, uint64_t w);   /* Vorgabe trommel_schreiben */
    unsigned (*aktueller_sektor)(void);            /* Vorgabe trommel_aktueller_sektor */
} zt_ht_t;

typedef struct {
    unsigned long long dauer_ns;           /* Dauer des Befehls nach dem Modell (einschließlich Hintergrund) */
    unsigned long long ticks_ht;           /* dauer_ns in HT-Wortzeiten zu 104 us (abgerundet) */
    unsigned wartezeit_block[4];           /* Anlaufwartezeit der Initiatorseite je Block in us, in Reihenfolge des Befehls */
} zt_stat_t;

/* Ergebnis der reinen Rechnung (alle Zeiten in ns, Modellzeit: HT-Position 0 beginnt bei 0 mod 3,328 ms) */
typedef struct {
    int       folge[4];                    /* Blockreihenfolge des Befehls */
    long long init_wait[4];                /* Anlaufwartezeit der Initiatorseite */
    long long init_ende[4];                /* Ende der Initiatorseite (Puffer voll) */
    long long emp_ende[4];                 /* Ende der Empfängerseite (Puffer frei) */
    long long dauer;                       /* Ende des letzten Blocks minus phase_ht */
} zt_plan_t;

/* ---- Reine Rechnung (ohne Zustand) ---------------------------------------------------------------
 * phase_zt_ns: Beginn der ZT-Position 0 in Modellzeit (beliebiger Wert, wirksam mod 20 ms); phase_ht_ns: Modellzeit
 * des Befehlsbeginns (= Lage in der HT-Umdrehung, 0 .. 3,328 ms). Rückgabe: Dauer in ns (auch in plan->dauer). */
C8205_API long long zt_modell_dauer(long long phase_zt_ns, long long phase_ht_ns, long long umschalt_ns,
                                    int richtung, zt_plan_t *plan);

/* ---- Modul ------------------------------------------------------------------------------------- */
/* pfad[0..3] = Dateien der ZT1..ZT4 (Format wie Trommel/trommel.txt: "aaaa: ttttttttttt", 4096 Zeilen); fehlende
 * Dateien werden leer angelegt. start_index (0..31): ZT-Position beim Einschalten, < 0 zufällig. Startet den Empfänger. */
C8205_API int  zt_einschalten(const char *pfad[ZT_ANZAHL], int start_index);
C8205_API void zt_ausschalten(void);                   /* sichert geänderte ZT, stoppt den Empfänger */
C8205_API int  zt_anwahl(int k);                       /* 5k00 030, k = 1..4; gilt bis zur nächsten Anwahl */
C8205_API int  zt_gewaehlt(void);                      /* 0 = keine */
C8205_API int  zt_eingabe(unsigned int zzz0, unsigned int bbbb, zt_stat_t *s);
C8205_API int  zt_ausgabe(unsigned int zzz0, unsigned int bbbb, zt_stat_t *s);
C8205_API void zt_ht_ankoppeln(const zt_ht_t *ht);     /* NULL = Vorgabe (trommel.h) */
C8205_API void zt_abbrechen(void);                     /* weckt den wartenden Aufrufer (ZT_ABGEBROCHEN) */

C8205_API void zt_zeitmodus(int modus);                /* ZT_ZEIT_VIRTUELL | ZT_ZEIT_ECHT */
C8205_API void zt_umschaltzeit(long long ns);          /* u */
/* Feste Phasen für reproduzierbare Tests: an = 1 setzt phase_zt/phase_ht (ns) fest, an = 0 mißt sie wieder aus der Uhr
 * und aus ht->aktueller_sektor() (HT-Phase mit der Genauigkeit einer Position, 104 us). */
C8205_API void zt_phasen_fest(int an, long long phase_zt_ns, long long phase_ht_ns);

/* Direktzugriffe auf die ZT (ohne Zeit): Vorbelegung, Tests, Leeren. adr = Spur * 32 + Sektor. */
C8205_API uint64_t zt_lesen(int k, unsigned adr);
C8205_API int      zt_schreiben(int k, unsigned adr, uint64_t wert);
C8205_API int      zt_letzte_adresse(int k);           /* zuletzt bearbeitete Adresse der ZT k (Spur*32+Sektor, ohne Zeit; laeuft waehrend eines Befehls mit), -1 = keine */
C8205_API void    zt_leeren(void);                     /* alle ZT leeren, Anwahl aufheben, Dateien sichern */
C8205_API int      zt_semaphore_frei(void);            /* 1, wenn beide Puffer frei und leer sind (nach jedem Befehl) */

#endif
