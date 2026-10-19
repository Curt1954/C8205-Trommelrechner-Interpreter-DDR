/* testframe_koinzidenz.c — Testrahmen fuer den Auftragskanal des Trommel-Moduls (Koinzidenz im Modul).
 * Uebersetzen: make test.   Prueft: Dateiformat, Koinzidenz/Wartezeit, 33-Bit-Maskierung, Bahnsperre, Abbruch, Fehlerfaelle, Takt. */
#ifdef __MINGW32__
#define __USE_MINGW_ANSI_STDIO 1
#endif
#ifndef _WIN32
#define _GNU_SOURCE
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include "trommel.h"
#include "bahnsperre.h"
#include "unterbrechung.h"

static int fehler = 0;
#define PRUEFE(bed, ...) do { if (!(bed)) { fehler++; printf("  FEHLER: "); printf(__VA_ARGS__); printf("\n"); } } while (0)

#ifdef _WIN32
#include <windows.h>
static unsigned long long jetzt_ns(void)
{
    LARGE_INTEGER c, f; QueryPerformanceCounter(&c); QueryPerformanceFrequency(&f);
    return (unsigned long long)c.QuadPart / (unsigned long long)f.QuadPart * 1000000000ULL
         + (unsigned long long)c.QuadPart % (unsigned long long)f.QuadPart * 1000000000ULL / (unsigned long long)f.QuadPart;
}
#else
static unsigned long long jetzt_ns(void)
{
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return (unsigned long long)ts.tv_sec * 1000000000ULL + (unsigned long long)ts.tv_nsec;
}
#endif

static uint64_t muster(unsigned a) { return ((uint64_t)a * 0123u + 045u) & 0x1FFFFFFFFULL; }

static void anlegen(const char *pfad)
{
    FILE *f = fopen(pfad, "wb"); unsigned a;
    for (a = 0; a < 4096; a++) fprintf(f, "%04o: %011llo\n", a, (unsigned long long)muster(a));
    fclose(f);
}

static void zeile_lesen(const char *pfad, unsigned a, char out[19])
{
    FILE *f = fopen(pfad, "rb"); fseek(f, (long)a * 18, SEEK_SET); if (fread(out, 1, 18, f) != 18) out[0] = 0; out[18] = 0; fclose(f);
}

int main(void)
{
    const char *pfad = "trommel_test.txt";
    unsigned a, w, s, hist[33];
    uint64_t v;
    unsigned long long t0, t1;
    trommel_statistik_t st;
    unsigned long long st0 = 0;
    int rc;

    anlegen(pfad);
    printf("[1] Einschalten, Dateiformat\n");
    { /* falsches Format (17 Byte je Zeile, altes C-Format) muss abgelehnt werden */
        FILE *f = fopen("trommel_alt.txt", "wb"); for (a = 0; a < 4096; a++) fprintf(f, "%04o %011llo\n", a, 0ULL); fclose(f);
        PRUEFE(trommel_einschalten_start("trommel_alt.txt", 0) != 0, "Datei im alten 17-Byte-Format wurde akzeptiert");
        remove("trommel_alt.txt");
    }
    PRUEFE(trommel_einschalten_start(pfad, 0) == 0, "Einschalten fehlgeschlagen");
    PRUEFE(trommel_aktueller_sektor() <= 037, "Sektor ausserhalb 0..37");
    trommel_statistik_lesen(&st); t0 = jetzt_ns(); st0 = st.ticks;

    printf("[2] Lesen mit Koinzidenz: alle 32 Sektoren, Wartezeit 0..31\n");
    memset(hist, 0, sizeof hist);
    for (s = 0; s < 32; s++) {
        a = (3u << 5) | s;
        rc = trommel_lesen_warten(a, &v, &w);
        PRUEFE(rc == TROMMEL_OK, "Lesen %04o rc=%d", a, rc);
        PRUEFE(v == muster(a), "Wert %04o: %011llo statt %011llo", a, (unsigned long long)v, (unsigned long long)muster(a));
        PRUEFE(w <= 31, "Wartezeit %u ausserhalb 0..31", w);
        if (w <= 32) hist[w]++;
    }
    printf("  Wartezeiten (Ticks:Anzahl):"); for (w = 0; w <= 32; w++) if (hist[w]) printf(" %u:%u", w, hist[w]); printf("\n");

    printf("[3] Zeitverhalten der Zugriffsfolgen (je 300 Zugriffe)\n");
    {
        unsigned schritt[3] = { 0, 1, 015 }; const char *name[3] = { "gleiche Adresse", "logisch naechste (+1)", "physisch benachbart (+15 oktal)" };
        unsigned k, n, summe, gleich, soll[3] = { 0, 5, 1 };
        for (k = 0; k < 3; k++) {
            unsigned sek = 0; summe = 0; gleich = 0;
            for (n = 0; n < 300; n++) {
                a = (5u << 5) | sek;
                rc = trommel_lesen_warten(a, &v, &w);
                PRUEFE(rc == TROMMEL_OK && w <= 31, "Folge %u rc=%d w=%u", k, rc, w);
                summe += w; if (w == soll[k]) gleich++;
                sek = (sek + schritt[k]) & 037;
            }
            printf("  %-34s mittlere Wartezeit %.2f Ticks (Soll laut Doku %u), %u von 300 genau so\n", name[k], summe / 300.0, soll[k], gleich);
        }
    }

    printf("[3b] Zeitschlitz: ist die Sektornummer aktuell, wird sofort bedient (Wartezeit 0)\n");
    {
        unsigned n, sofort = 0, gesamt = 300, sektor_jetzt;
        for (n = 0; n < gesamt; n++) {
            sektor_jetzt = trommel_aktueller_sektor();
            rc = trommel_lesen_warten((6u << 5) | sektor_jetzt, &v, &w);
            PRUEFE(rc == TROMMEL_OK && w <= 31, "Schlitz-Test rc=%d w=%u", rc, w);
            if (w == 0) sofort++;
            { unsigned long long t = jetzt_ns(); while (jetzt_ns() - t < 150000ULL) ; }   /* den Schlitz ueberspringen */
        }
        printf("  %u von %u Zugriffen auf den gerade aktuellen Sektor wurden sofort bedient\n", sofort, gesamt);
        PRUEFE(sofort * 100 >= gesamt * 85, "nur %u von %u im aktuellen Schlitz bedient", sofort, gesamt);
    }

    printf("[4] Schreiben, Ruecklesen, 33-Bit-Maskierung, Zeilen unversehrt\n");
    {
        char vor[19], nach[19], folge_vor[19], folge_nach[19]; unsigned adr = 01234;
        zeile_lesen(pfad, adr + 1, folge_vor);
        rc = trommel_schreiben_warten(adr, 077777777777777ULL, &w);     /* absichtlich mehr als 33 Bit */
        PRUEFE(rc == TROMMEL_OK, "Schreiben rc=%d", rc);
        PRUEFE(trommel_lesen(adr) == 0x1FFFFFFFFULL, "Ruecklesen: %011llo", (unsigned long long)trommel_lesen(adr));
        zeile_lesen(pfad, adr, nach); zeile_lesen(pfad, adr + 1, folge_nach);
        PRUEFE(strcmp(nach, "1234: 77777777777\n") == 0, "Zeile 1234 ist \"%s\"", nach);
        PRUEFE(strcmp(folge_vor, folge_nach) == 0, "Folgezeile wurde veraendert");
        (void)vor;
        rc = trommel_schreiben_warten(adr, 0123456701234ULL & 0x1FFFFFFFFULL, &w);
        PRUEFE(rc == TROMMEL_OK && trommel_lesen(adr) == (0123456701234ULL & 0x1FFFFFFFFULL), "zweites Schreiben/Lesen");
    }

    printf("[5] Bahnsperre im Schreibpfad (Hauptschalter EIN: Bahn 0 gesperrt)\n");
    {
        char vor[19], nach[19];
        bahnsperre_setzen(1, 0, 0, 0, 0, 0);
        zeile_lesen(pfad, 005, vor);
        rc = trommel_schreiben_warten(005, 1, &w);                       /* Bahn 0 */
        zeile_lesen(pfad, 005, nach);
        PRUEFE(rc == TROMMEL_SCHREIBEN_GESPERRT, "Bahn 0: rc=%d", rc);
        PRUEFE(strcmp(vor, nach) == 0, "gesperrte Zelle wurde veraendert");
        PRUEFE(w <= 31, "gesperrter Zugriff meldet keine gueltige Wartezeit (%u)", w);
        rc = trommel_schreiben_warten(045, 1, &w);                       /* Bahn 1 */
        PRUEFE(rc == TROMMEL_OK && trommel_lesen(045) == 1, "Bahn 1 offen: rc=%d", rc);
        bahnsperre_setzen(0, 0, 0, 0, 0, 0);
    }

    printf("[6] Abbruch\n");
    abbruch_angefordert = 1;
    rc = trommel_lesen_warten(0100, &v, &w);
    PRUEFE(rc == TROMMEL_ABGEBROCHEN, "Strg+C-Flag: rc=%d", rc);
    abbruch_angefordert = 0;
    trommel_warten_abbrechen();
    rc = trommel_lesen_warten(0100, &v, &w);
    PRUEFE(rc == TROMMEL_ABGEBROCHEN, "trommel_warten_abbrechen: rc=%d", rc);
    rc = trommel_lesen_warten(0100, &v, &w);
    PRUEFE(rc == TROMMEL_OK, "Abbruch-Flag wurde nicht verbraucht: rc=%d", rc);

    printf("[7] Fehlerfaelle\n");
    PRUEFE(trommel_lesen_warten(010000, &v, &w) == TROMMEL_FEHLER, "Adresse 10000 akzeptiert");
    PRUEFE(trommel_schreiben_warten(010000, 1, &w) == TROMMEL_FEHLER, "Schreiben 10000 akzeptiert");

    printf("[8] Takt und Hintergrundprozess\n");
    trommel_statistik_lesen(&st);
    t1 = jetzt_ns();            /* nach dem Lesen: die Statistik stammt aus der Uhr, t1 liegt knapp danach */
    {
        double soll_ticks = (t1 - t0) / 104000.0, ist = (double)(st.ticks - st0);
        printf("  Laufzeit %.1f ms, verstrichene Ticks laut Modul %.0f (Soll aus Uhr %.0f)\n", (t1 - t0) / 1e6, ist, soll_ticks);
        PRUEFE(ist - soll_ticks <= 20 && soll_ticks - ist <= 20, "Tickzahl weicht von der Uhr ab (%.0f gegen %.0f)", ist, soll_ticks);
        printf("  Aufwachvorgaenge %llu, davon nachgeholte Ticks %llu\n", st.aufwachen, st.nachgeholte_ticks);
        printf("  Aufwach-Verspaetung: mittel %.1f us, max %.1f us (Tick = 104 us)\n",
               st.aufwachen ? st.verspaetung_summe_ns / 1000.0 / st.aufwachen : 0.0, st.verspaetung_max_ns / 1000.0);
        printf("  Zugriffe %llu, mittlere Wartezeit %.2f Ticks = %.0f us\n", st.zugriffe,
               st.zugriffe ? (double)st.wartezeit_summe_ticks / st.zugriffe : 0.0,
               st.zugriffe ? (double)st.wartezeit_summe_ticks / st.zugriffe * 104.0 : 0.0);
    }

    trommel_ausschalten();
    PRUEFE(trommel_lesen_warten(0, &v, &w) == TROMMEL_FEHLER, "Zugriff nach dem Ausschalten");
    remove(pfad);
    printf("\n%s (%d Fehler)\n", fehler ? "FEHLGESCHLAGEN" : "ALLE PRUEFUNGEN BESTANDEN", fehler);
    return fehler ? 1 : 0;
}
