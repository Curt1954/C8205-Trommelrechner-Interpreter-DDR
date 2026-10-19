/* testframe_tonmisch.c - Pruefungen des Tonmischers (tonmisch.c) ohne Python und ohne Audiogeraet.
 * Linux:  make test-ton     (baut mit der statischen Bibliothek libtonmisch.a und -static)
 * Ausgabe: je Pruefung eine Zeile; am Ende "TONMISCH BESTANDEN" und Rueckgabe 0, sonst Rueckgabe 1. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include "tonmisch.h"

static int fehler = 0, gesamt = 0;
#define PRUEFE(bed, text) do { gesamt++; if (!(bed)) { fehler++; printf("FEHLER  %s (Zeile %d)\n", text, __LINE__); } else printf("ok      %s\n", text); } while (0)

static int kl(tm_t *t, int n, int wert)
{
    int16_t *d = (int16_t *)malloc((size_t)n * sizeof(int16_t));
    int i, id;
    for (i = 0; i < n; i++) d[i] = (int16_t)wert;
    id = tm_klang(t, d, (size_t)n);
    free(d);
    return id;
}

static double jetzt(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + ts.tv_nsec * 1e-9; }
static void warte_ms(int ms) { struct timespec ts = { ms / 1000, (long)(ms % 1000) * 1000000L }; nanosleep(&ts, NULL); }

int main(void)
{
    tm_t *t;
    int16_t b[TM_BLOCK];
    int i, k, k2;

    /* --- Stille, Einzelklang, Ueberlappung, Begrenzung --- */
    t = tm_neu();
    PRUEFE(t != NULL, "tm_neu");
    tm_block(t, b);
    for (i = 0; i < TM_BLOCK && b[i] == 0; i++) ;
    PRUEFE(i == TM_BLOCK, "Ruhe ergibt Stille");

    k = kl(t, 1000, 500);
    PRUEFE(k == 0, "erste Klangnummer 0");
    PRUEFE(tm_einzel(t, TM_KANAL_SCHREIBWERK, k, 1.0, NULL) == TM_OK, "Einzelklang angenommen");
    tm_block(t, b);
    PRUEFE(b[0] == 500 && b[440] == 500 && tm_klingt(t) == 1, "Block 1: 441 Samples, Klang laeuft weiter");
    tm_block(t, b);
    PRUEFE(b[0] == 500 && b[440] == 500 && tm_klingt(t) == 1, "Block 2: Klang laeuft weiter");
    tm_block(t, b);
    PRUEFE(b[0] == 500 && b[117] == 500 && b[118] == 0 && tm_klingt(t) == 0, "Block 3: Klang endet nach 1000 Samples, danach Stille");
    tm_block(t, b);
    PRUEFE(b[0] == 0 && tm_klingt(t) == 0, "danach Stille");

    k = kl(t, 441, 20000); k2 = kl(t, 441, 20000);
    tm_einzel(t, TM_KANAL_LESER, k, 1.0, NULL); tm_einzel(t, TM_KANAL_STANZER, k2, 1.0, NULL);
    tm_block(t, b);
    PRUEFE(b[0] == 32767 && b[440] == 32767, "Summe wird auf +32767 begrenzt");
    k = kl(t, 441, -20000); k2 = kl(t, 441, -20000);
    tm_einzel(t, TM_KANAL_LESER, k, 1.0, NULL); tm_einzel(t, TM_KANAL_STANZER, k2, 1.0, NULL);
    tm_block(t, b);
    PRUEFE(b[0] == -32768, "Summe wird auf -32768 begrenzt");

    /* --- Pegel (Abschneiden zur Null wie int() in Python) --- */
    k = kl(t, 441, 1001);
    tm_einzel(t, TM_KANAL_SCHREIBWERK, k, 0.5, NULL);
    tm_block(t, b);
    PRUEFE(b[0] == 500, "Pegel 0,5 schneidet zur Null ab (1001 -> 500)");
    k = kl(t, 441, -1001);
    tm_einzel(t, TM_KANAL_SCHREIBWERK, k, 0.5, NULL);
    tm_block(t, b);
    PRUEFE(b[0] == -500, "Pegel 0,5 schneidet zur Null ab (-1001 -> -500)");
    k = kl(t, 441, 1000);
    tm_einzel(t, TM_KANAL_SCHREIBWERK, k, 0.0, NULL);
    tm_block(t, b);
    PRUEFE(b[0] == 0 && tm_klingt(t) == 0, "Pegel 0 ist stumm, Klang laeuft trotzdem ab");

    /* --- Schleife mit Pegel, ohne Neustart --- */
    {
        int16_t d[10]; int id;
        for (i = 0; i < 10; i++) d[i] = (int16_t)(i + 1);
        id = tm_klang(t, d, 10);
        tm_dauer_an(t, TM_KANAL_RECHNER, "g", id, 1.0);
        tm_block(t, b);
        PRUEFE(b[0] == 1 && b[9] == 10 && b[10] == 1 && b[440] == (int16_t)(440 % 10 + 1), "Schleife wiederholt sich im Block");
        tm_block(t, b);
        PRUEFE(b[0] == (int16_t)((441 % 10) + 1), "Schleife laeuft ueber die Blockgrenze ohne Neustart weiter");
        tm_dauer_pegel(t, "g", 0.0);
        tm_block(t, b);
        PRUEFE(b[0] == 0 && b[300] == 0 && tm_klingt(t) == 1, "Pegel 0: Schleife stumm, laeuft aber weiter");
        tm_dauer_pegel(t, "g", 1.0);
        tm_block(t, b);
        PRUEFE(b[0] != 0, "Pegel 1: wieder hoerbar");
        tm_dauer_aus(t, "g");
        PRUEFE(tm_klingt(t) == 0 && tm_klingt_schluessel(t, "g") == 0, "dauer_aus entfernt die Schleife");
    }

    /* --- Schluessel: ersetzen, abbrechen --- */
    k = kl(t, 44100, 7);
    tm_dauer_an(t, TM_KANAL_RECHNER, "a", k, 1.0);
    tm_dauer_an(t, TM_KANAL_RECHNER, "a", k, 1.0);
    PRUEFE(tm_klingt_schluessel(t, "a") == 1, "zweite Schleife mit demselben Schluessel ersetzt die erste");
    tm_einzel(t, TM_KANAL_RECHNER, k, 1.0, "fade");
    PRUEFE(tm_klingt_schluessel(t, "fade") == 1 && tm_klingt(t) == 2, "Einzelklang mit Schluessel");
    tm_dauer_aus(t, "fade");
    PRUEFE(tm_klingt_schluessel(t, "fade") == 0 && tm_klingt_schluessel(t, "a") == 1, "Einzelklang ueber den Schluessel abgebrochen");
    tm_alles_aus(t);
    PRUEFE(tm_klingt(t) == 0, "alles_aus");

    /* --- Tore --- */
    k = kl(t, 44100, 5);
    tm_einzel(t, TM_KANAL_LESER, k, 1.0, NULL);
    tm_dauer_an(t, TM_KANAL_STANZER, "m", k, 1.0);
    tm_einzel(t, TM_KANAL_RECHNER, k, 1.0, NULL);
    tm_tor(t, TM_KANAL_LESER, 0);
    PRUEFE(tm_klingt(t) == 2, "Tor zu verwirft Klaenge des Kanals");
    tm_einzel(t, TM_KANAL_LESER, k, 1.0, NULL);
    PRUEFE(tm_klingt(t) == 2, "Tor zu: neue Einzelklaenge werden nicht angenommen");
    tm_tor(t, TM_KANAL_STANZER, 0);
    tm_dauer_an(t, TM_KANAL_STANZER, "m", k, 1.0);
    PRUEFE(tm_klingt(t) == 1, "Tor zu: auch Schleifen werden verworfen und nicht angenommen");
    tm_tor(t, TM_KANAL_LESER, 1);
    tm_einzel(t, TM_KANAL_LESER, k, 1.0, NULL);
    PRUEFE(tm_klingt(t) == 2, "Tor wieder offen");
    tm_alles_aus(t);
    PRUEFE(tm_einzel(t, 9, k, 1.0, NULL) == TM_FEHLER && tm_einzel(t, 0, 999, 1.0, NULL) == TM_FEHLER, "falscher Kanal und falscher Klang werden abgewiesen");

    /* --- Stimmen voll --- */
    k = kl(t, 44100, 1);
    for (i = 0; i < 200; i++) if (tm_einzel(t, TM_KANAL_RECHNER, k, 1.0, NULL) == TM_VOLL) break;
    PRUEFE(i < 200 && tm_klingt(t) == 128, "128 Stimmen, danach TM_VOLL");
    tm_alles_aus(t);
    tm_frei(t);

    /* --- Speichersenke, von Hand --- */
    t = tm_neu();
    k = kl(t, 441, 1234);
    tm_senke_speicher(t);
    tm_einzel(t, TM_KANAL_RECHNER, k, 1.0, NULL);
    PRUEFE(tm_schritt(t, 3) == TM_OK && tm_bloecke(t) == 3, "tm_schritt erzeugt drei Bloecke");
    {
        uint8_t *m = (uint8_t *)malloc(3 * TM_BLOCK_BYTE);
        size_t n = tm_speicher_kopie(t, m, 3 * TM_BLOCK_BYTE);
        PRUEFE(n == 3 * TM_BLOCK_BYTE && tm_speicher_laenge(t) == n, "882 Byte je Block");
        PRUEFE(m[0] == (1234 & 0xFF) && m[1] == (1234 >> 8) && m[2 * 440] == (1234 & 0xFF), "little endian, Klang im ersten Block");
        PRUEFE(m[TM_BLOCK_BYTE] == 0 && m[2 * TM_BLOCK_BYTE] == 0, "danach Stille");
        free(m);
    }
    PRUEFE(tm_senke_speicher(t) == TM_FEHLER, "zweite Senke abgewiesen");
    tm_frei(t);

    /* --- Strom im Takt der Uhr (Speichersenke, Thread) --- */
    t = tm_neu();
    tm_senke_speicher(t);
    {
        double t0 = jetzt();
        unsigned long n1;
        PRUEFE(tm_starten(t) == TM_OK, "tm_starten");
        PRUEFE(tm_starten(t) == TM_FEHLER, "zweites tm_starten abgewiesen");
        warte_ms(1000);
        tm_schliessen(t);
        n1 = tm_bloecke(t);
        printf("        %lu Bloecke in %.3f s (Soll: 100 + %d Vorlauf)\n", n1, jetzt() - t0, TM_VORLAUF);
        PRUEFE(n1 >= 100 && n1 <= 100 + TM_VORLAUF + 2, "1 s Lauf = 100 Bloecke plus hoechstens Vorlauf (20 ms), nie weiter voraus");
        PRUEFE(tm_schritt(t, 1) == TM_FEHLER, "nach tm_schliessen kein Schritt mehr");
    }
    tm_frei(t);

    /* --- Vorlauf einstellbar (G4-004) --- */
    t = tm_neu();
    tm_senke_speicher(t);
    PRUEFE(tm_vorlauf(t, 0) == TM_FEHLER && tm_vorlauf(t, TM_VORLAUF_MAX + 1) == TM_FEHLER, "Vorlauf ausserhalb 1 bis 3 abgewiesen");
    PRUEFE(tm_vorlauf(t, 1) == TM_OK, "Vorlauf 1 Block einstellbar");
    tm_starten(t);
    PRUEFE(tm_vorlauf(t, 2) == TM_FEHLER, "Vorlauf nach dem Start nicht mehr aenderbar");
    warte_ms(500);
    tm_schliessen(t);
    { unsigned long n = tm_bloecke(t); printf("        %lu Bloecke in 0,5 s bei Vorlauf 1\n", n); PRUEFE(n >= 50 && n <= 53, "Vorlauf 1: 50 bis 53 Bloecke in 0,5 s"); }
    tm_frei(t);

    /* --- tm_warte_takt --- */
    t = tm_neu();
    tm_senke_speicher(t);
    tm_starten(t);
    {
        unsigned long z = tm_bloecke(t), n;
        double t0 = jetzt();
        n = tm_warte_takt(t, z, 500);
        PRUEFE(n != z && jetzt() - t0 < 0.1, "tm_warte_takt: kehrt mit dem naechsten Block zurueck (nach etwa 10 ms, nicht erst nach der Frist)");
        t0 = jetzt();
        n = tm_warte_takt(t, tm_bloecke(t) + 1000UL, 500);
        PRUEFE(n != 0 && jetzt() - t0 < 0.1, "tm_warte_takt: weicht die Zahl schon ab, kehrt es sofort zurueck");
    }
    tm_schliessen(t);
    PRUEFE(tm_warte_takt(t, tm_bloecke(t), 2000) == tm_bloecke(t), "nach tm_schliessen wartet tm_warte_takt nicht");
    tm_frei(t);

    /* --- Prozess-Senke: cat in eine Datei (Trockenlauf) --- */
    {
        char *argv[] = { "sh", "-c", "cat > /tmp/tonmisch_trocken.raw", NULL };
        long groesse = -1;
        FILE *f;
        t = tm_neu();
        k = kl(t, 44100, 3000);
        PRUEFE(tm_senke_prozess(t, argv) == TM_OK, "Prozess-Senke gestartet (sh -c cat)");
        tm_dauer_an(t, TM_KANAL_RECHNER, "g", k, 0.8);
        tm_starten(t);
        warte_ms(600);
        tm_schliessen(t);
        tm_frei(t);
        f = fopen("/tmp/tonmisch_trocken.raw", "rb");
        if (f) { fseek(f, 0, SEEK_END); groesse = ftell(f); fclose(f); }
        printf("        %ld Byte Audio nach 0,6 s\n", groesse);
        PRUEFE(groesse >= TM_BLOCK_BYTE * 58 && groesse <= TM_BLOCK_BYTE * 66 && groesse % TM_BLOCK_BYTE == 0, "etwa 0,6 s Audio, ganze Bloecke, an den Prozess geliefert");
        remove("/tmp/tonmisch_trocken.raw");
    }

    /* --- Prozess-Senke fehlt / bricht weg --- */
    {
        char *nix[] = { "gibt-es-nicht-tonmisch", NULL };
        char *wegg[] = { "true", NULL };
        char text[200] = "";
        int a = 0;
        double t0;
        t = tm_neu();
        PRUEFE(tm_senke_prozess(t, nix) == TM_FEHLER, "nicht vorhandenes Abspielprogramm: Fehler beim Oeffnen");
        tm_frei(t);
        t = tm_neu();
        tm_senke_prozess(t, wegg);
        tm_starten(t);
        t0 = jetzt();
        for (i = 0; i < 100 && !a; i++) { tm_warte_takt(t, tm_bloecke(t), 20); a = tm_ausfall(t, text, sizeof text); }
        printf("        Ausfall nach %.0f ms: %s\n", (jetzt() - t0) * 1000, text);
        PRUEFE(a == 1 && strstr(text, "true") != NULL, "Abspielprogramm bricht weg: Ausfall mit Text");
        tm_schliessen(t);
        tm_frei(t);
    }

    /* --- Datei-Senke --- */
    {
        long groesse = -1; FILE *f;
        t = tm_neu();
        PRUEFE(tm_senke_datei(t, "/tmp/tonmisch_datei.raw") == TM_OK, "Datei-Senke");
        tm_schritt(t, 5);
        tm_frei(t);
        f = fopen("/tmp/tonmisch_datei.raw", "rb");
        if (f) { fseek(f, 0, SEEK_END); groesse = ftell(f); fclose(f); }
        PRUEFE(groesse == 5 * TM_BLOCK_BYTE, "Datei-Senke: 5 Bloecke = 4410 Byte");
        remove("/tmp/tonmisch_datei.raw");
    }

    printf("----\n%d Pruefungen, %d Fehler\n", gesamt, fehler);
    if (fehler) return 1;
    printf("TONMISCH BESTANDEN\n");
    return 0;
}
