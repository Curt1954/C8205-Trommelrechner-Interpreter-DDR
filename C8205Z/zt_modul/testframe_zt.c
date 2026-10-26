/* testframe_zt.c — Testrahmen des Zusatztrommelmoduls zt_modul (C 8205Z).
 * Version: 0.01-001
 * Teile: 1 Tabellen, 2 Referenzwerte und Statistik des Zeitmodells (ohne Zustand), 3 Datenübertragung mit
 * Ersatz-HT (virtuelle Zeit), 4 Persistenz, 5 Echtzeit und Abbruch, 6 Kopplung an die echte Haupttrommel (trommel.c).
 * Läuft in einem Arbeitsordner (Dateien zt_test_*.txt, ht_test.txt); Aufruf: make test-zt. Rückgabe 0 = alles bestanden. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <unistd.h>
#include "zt_modul.h"
#include "trommel.h"

static int fehler = 0, pruefungen = 0;
#define PRUEFE(bed, ...) do { pruefungen++; if (!(bed)) { fehler++; printf("FEHLER Zeile %d: ", __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)

static uint64_t ersatz_ht[4096];
static unsigned ersatz_sektor = 0;
static uint64_t e_lesen(unsigned a) { return ersatz_ht[a & 07777]; }
static int e_schreiben(unsigned a, uint64_t w) { ersatz_ht[a & 07777] = w; return 0; }
static unsigned e_sektor(void) { return ersatz_sektor; }
static const zt_ht_t ERSATZ = { e_lesen, e_schreiben, e_sektor };

static double ms(long long ns) { return (double)ns / 1e6; }
static double nanos_jetzt(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }

static const char *PF[ZT_ANZAHL] = { "zt_test_1.txt", "zt_test_2.txt", "zt_test_3.txt", "zt_test_4.txt" };

static void teil1_tabellen(void)
{
    unsigned char s1[32] = {0}, s2[32] = {0};
    for (int k = 0; k < 4; k++)
        for (int i = 0; i < 8; i++)
            PRUEFE(ZT_ZT_PERM[4 * i + k] == ZT_HT_PERM[8 * k + i], "ZT[%d] != HT[%d]", 4 * i + k, 8 * k + i);
    for (int i = 0; i < 32; i++) { s1[ZT_HT_PERM[i]]++; s2[ZT_ZT_PERM[i]]++; }
    for (int i = 0; i < 32; i++) PRUEFE(s1[i] == 1 && s2[i] == 1, "keine Permutation bei %d", i);
}

static void teil2_modell(void)
{
    /* Referenzwerte (Spezifikation Abschnitt 7): pz (ms), t0 (ms), Eingabe 461/661, Ausgabe 401/601 in ms */
    static const double R[5][4] = { {0, 0, 83.200, 82.500}, {0.3, 0, 83.200, 82.800}, {5.0, 1.0, 83.864, 82.750},
                                    {12.34, 2.5, 81.532, 82.965}, {19.9, 3.3, 81.564, 82.850} };
    static const int folge[5][4] = { {0,1,2,3}, {0,1,2,3}, {2,3,0,1}, {1,2,3,0}, {2,3,0,1} };
    zt_plan_t plan;
    for (int r = 0; r < 5; r++) {
        long long pz = (long long)(R[r][0] * 1e6 + 0.5), t0 = (long long)(R[r][1] * 1e6 + 0.5);
        long long e = zt_modell_dauer(pz, t0, ZT_UMSCHALT_NS, ZT_RICHTUNG_EINGABE, &plan);
        long long a = zt_modell_dauer(pz, t0, ZT_UMSCHALT_NS, ZT_RICHTUNG_AUSGABE, NULL);
        PRUEFE(llabs(e - (long long)(R[r][2] * 1e6 + 0.5)) <= 500, "Zeile %d Eingabe %.3f, erwartet %.3f", r, ms(e), R[r][2]);
        PRUEFE(llabs(a - (long long)(R[r][3] * 1e6 + 0.5)) <= 500, "Zeile %d Ausgabe %.3f, erwartet %.3f", r, ms(a), R[r][3]);
        zt_modell_dauer(pz, t0, ZT_UMSCHALT_NS, ZT_RICHTUNG_EINGABE, &plan);
        for (int n = 0; n < 4; n++) PRUEFE(plan.folge[n] == folge[r][n], "Zeile %d Blockfolge[%d] = %d", r, n, plan.folge[n]);
    }
    /* Statistik über 64 x 64 Phasen: Eingabe 80,9 / 82,8 / 84,7 ms, Ausgabe 82,5 / 83,8 / 85,6 ms */
    for (int rich = 0; rich < 2; rich++) {
        long long mn = 1LL << 60, mx = 0; double sum = 0;
        for (int i = 0; i < 64; i++)
            for (int j = 0; j < 64; j++) {
                long long d = zt_modell_dauer(i * 20000000LL / 64, j * 3328000LL / 64, ZT_UMSCHALT_NS, rich, NULL);
                if (d < mn) mn = d;
                if (d > mx) mx = d;
                sum += (double)d;
            }
        {
            double mi = sum / 4096.0 / 1e6;
            double soll[2][3] = { {80.9, 82.8, 84.7}, {82.5, 83.8, 85.6} };
            PRUEFE(ms(mn) > soll[rich][0] - 0.05 && ms(mn) < soll[rich][0] + 0.05, "Richtung %d min %.3f", rich, ms(mn));
            PRUEFE(mi > soll[rich][1] - 0.05 && mi < soll[rich][1] + 0.05, "Richtung %d Mittel %.3f", rich, mi);
            PRUEFE(ms(mx) > soll[rich][2] - 0.05 && ms(mx) < soll[rich][2] + 0.05, "Richtung %d max %.3f", rich, ms(mx));
            printf("  Modell %s: min %.3f  Mittel %.3f  max %.3f ms\n", rich ? "Ausgabe" : "Eingabe", ms(mn), mi, ms(mx));
        }
    }
    /* Umschaltzeit: 0 ms -> 77,1 ms, 0,3..2,5 ms -> 84,6 ms, 3 ms und mehr -> 92,0 ms (Eingabe, Maximum) */
    {
        static const long long U[3] = { 0, 300000, 5000000 };
        static const double S[3] = { 77.1, 84.6, 92.0 };
        for (int q = 0; q < 3; q++) {
            long long mx = 0;
            for (int i = 0; i < 32; i++) for (int j = 0; j < 32; j++) {
                long long d = zt_modell_dauer(i * 20000000LL / 32, j * 3328000LL / 32, U[q], ZT_RICHTUNG_EINGABE, NULL);
                if (d > mx) mx = d;
            }
            PRUEFE(ms(mx) > S[q] - 0.1 && ms(mx) < S[q] + 0.1, "u=%lld: max %.3f, erwartet %.1f", U[q], ms(mx), S[q]);
        }
    }
}

static void teil3_daten(void)
{
    zt_stat_t st;
    int rc;
    const char *p[ZT_ANZAHL];
    for (int k = 0; k < 4; k++) { remove(PF[k]); p[k] = PF[k]; }
    PRUEFE(zt_einschalten(p, 7) == ZT_OK, "Einschalten");
    zt_ht_ankoppeln(&ERSATZ);
    zt_phasen_fest(1, 5000000, 1000000);
    for (unsigned a = 0; a < 4096; a++) ersatz_ht[a] = ((uint64_t)a * 0123457ULL + 1) & 077777777777ULL;

    PRUEFE(zt_ausgabe(05540, 0140, &st) == ZT_KEINE_ANWAHL, "Ausgabe ohne Anwahl");
    PRUEFE(zt_eingabe(05540, 0140, &st) == ZT_KEINE_ANWAHL, "Eingabe ohne Anwahl");
    PRUEFE(zt_anwahl(0) == ZT_FEHLER && zt_anwahl(5) == ZT_FEHLER, "falsche Anwahl");
    PRUEFE(zt_gewaehlt() == 0, "noch keine Anwahl");

    PRUEFE(zt_anwahl(2) == ZT_OK && zt_gewaehlt() == 2, "Anwahl 2");
    /* HT-Spur 0140 -> ZT2, Spur 0100 (zzz0 = 04000: Spur = 04000 >> 5 = 0100) */
    rc = zt_ausgabe(04000, 0140 * 1, &st);
    PRUEFE(rc == ZT_OK, "Ausgabe rc=%d", rc);
    PRUEFE(zt_semaphore_frei(), "Semaphore nach Ausgabe");
    PRUEFE(zt_letzte_adresse(2) >= 0 && (zt_letzte_adresse(2) >> 5) == 0100, "letzte Adresse ZT2 nach Ausgabe: %d", zt_letzte_adresse(2));
    PRUEFE(zt_letzte_adresse(1) == -1 && zt_letzte_adresse(3) == -1 && zt_letzte_adresse(0) == -1 && zt_letzte_adresse(5) == -1, "andere ZT ohne letzte Adresse");
    {
        unsigned spur_ht = (0140 >> 5) & 0x7F, spur_zt = (04000 >> 5) & 0x7F;
        int gleich = 1, andere = 1;
        for (unsigned i = 0; i < 32; i++) if (zt_lesen(2, (spur_zt << 5) | i) != ersatz_ht[(spur_ht << 5) | i]) gleich = 0;
        PRUEFE(gleich, "ZT2 Spur %o = HT Spur %o", spur_zt, spur_ht);
        for (unsigned a = 0; a < 4096; a++) if ((a >> 5) != spur_zt && zt_lesen(2, a) != 0) andere = 0;
        PRUEFE(andere, "andere Spuren der ZT2 unveraendert");
        for (int k = 1; k <= 4; k++) if (k != 2) for (unsigned a = 0; a < 4096; a++) if (zt_lesen(k, a) != 0) andere = 0;
        PRUEFE(andere, "ZT1, ZT3, ZT4 unveraendert");
    }
    PRUEFE(st.dauer_ns > 80000000ULL && st.dauer_ns < 86000000ULL, "Dauer %.3f ms", (double)st.dauer_ns / 1e6);
    PRUEFE(st.ticks_ht == st.dauer_ns / 104000ULL, "ticks_ht");

    /* Eingabe zurück in andere HT-Spur, Hin- und Rückweg reproduziert die Daten */
    for (unsigned i = 0; i < 32; i++) ersatz_ht[(011 << 5) | i] = 0;
    rc = zt_eingabe(04000, (011 << 5), &st);
    PRUEFE(rc == ZT_OK, "Eingabe rc=%d", rc);
    {
        int gleich = 1;
        for (unsigned i = 0; i < 32; i++) if (ersatz_ht[(011 << 5) | i] != ersatz_ht[(((0140 >> 5) & 0x7F) << 5) | i]) gleich = 0;
        PRUEFE(gleich, "HT Spur 011 = Ausgangsspur");
        PRUEFE(ersatz_ht[(012 << 5)] == (((uint64_t)(012 << 5) * 0123457ULL + 1) & 077777777777ULL), "Nachbarspur unveraendert");
    }
    PRUEFE(zt_semaphore_frei(), "Semaphore nach Eingabe");
    PRUEFE(zt_letzte_adresse(2) >= 0 && (zt_letzte_adresse(2) >> 5) == 0100, "letzte Adresse ZT2 nach Eingabe: %d", zt_letzte_adresse(2));

    /* ZT3 getrennt: Anwahl wechselt die Trommel */
    zt_anwahl(3);
    PRUEFE(zt_ausgabe(0, (020 << 5), &st) == ZT_OK, "Ausgabe ZT3");
    PRUEFE(zt_lesen(3, 5) == ersatz_ht[(020 << 5) | 5] && zt_lesen(2, 5) == 0, "ZT3 getrennt von ZT2");

    /* Sektor i auf Sektor i: HT-Sektor 013 -> ZT-Sektor 013 */
    PRUEFE(zt_lesen(3, 013) == ersatz_ht[(020 << 5) | 013], "Sektor 013");

    /* alle Phasen: je 8 Lagen Hin- und Rueckweg ohne Datenverlust, Semaphore frei */
    for (int q = 0; q < 8; q++) {
        int ok = 1;
        zt_phasen_fest(1, q * 2500000LL + 123456, (q * 450000LL) % 3328000LL);
        zt_anwahl(4);
        for (unsigned i = 0; i < 32; i++) ersatz_ht[(030 << 5) | i] = 01000000000ULL + q * 100 + i;
        if (zt_ausgabe(0, (030 << 5), &st) != ZT_OK) ok = 0;
        for (unsigned i = 0; i < 32; i++) ersatz_ht[(031 << 5) | i] = 0;
        if (zt_eingabe(0, (031 << 5), &st) != ZT_OK) ok = 0;
        for (unsigned i = 0; i < 32; i++) if (ersatz_ht[(031 << 5) | i] != 01000000000ULL + q * 100 + i) ok = 0;
        PRUEFE(ok && zt_semaphore_frei(), "Phasenlage %d", q);
    }
    zt_phasen_fest(0, 0, 0);
    ersatz_sektor = 015;                    /* HT-Position 1 */
    PRUEFE(zt_ausgabe(0, 0, &st) == ZT_OK && st.dauer_ns > 70000000ULL && st.dauer_ns < 90000000ULL, "gemessene Phase");
}

static void teil4_persistenz(void)
{
    const char *p[ZT_ANZAHL];
    zt_stat_t st;
    uint64_t vorher[32];
    for (int k = 0; k < 4; k++) p[k] = PF[k];
    for (unsigned i = 0; i < 32; i++) vorher[i] = zt_lesen(2, (0100 << 5) | i);
    zt_ausschalten();
    PRUEFE(zt_anwahl(1) == ZT_FEHLER, "nach Ausschalten keine Anwahl");
    PRUEFE(zt_einschalten(p, -1) == ZT_OK, "Wiedereinschalten");
    zt_ht_ankoppeln(&ERSATZ);
    {
        int gleich = 1;
        for (unsigned i = 0; i < 32; i++) if (zt_lesen(2, (0100 << 5) | i) != vorher[i]) gleich = 0;
        PRUEFE(gleich, "ZT2 nach Neustart unveraendert");
    }
    PRUEFE(zt_gewaehlt() == 0, "Anwahl nach Neustart aufgehoben");
    zt_anwahl(2);
    for (unsigned i = 0; i < 32; i++) ersatz_ht[(050 << 5) | i] = 0;
    PRUEFE(zt_eingabe(04000, (050 << 5), &st) == ZT_OK, "Eingabe nach Neustart");
    {
        int gleich = 1;
        for (unsigned i = 0; i < 32; i++) if (ersatz_ht[(050 << 5) | i] != vorher[i]) gleich = 0;
        PRUEFE(gleich, "Daten aus der Datei");
    }
    zt_leeren();
    PRUEFE(zt_lesen(2, (0100 << 5)) == 0 && zt_gewaehlt() == 0, "zt_leeren");
}

static void *abbrecher(void *arg) { (void)arg; usleep(25000); zt_abbrechen(); return NULL; }

static void teil5_echtzeit(void)
{
    zt_stat_t st;
    double t0, t1;
    pthread_t th;
    zt_phasen_fest(1, 5000000, 1000000);
    zt_zeitmodus(ZT_ZEIT_ECHT);
    zt_anwahl(1);
    for (unsigned i = 0; i < 32; i++) ersatz_ht[(060 << 5) | i] = 0123 + i;
    t0 = nanos_jetzt();
    PRUEFE(zt_ausgabe(0, (060 << 5), &st) == ZT_OK, "Ausgabe echt");
    t1 = nanos_jetzt();
    printf("  Echtzeit Ausgabe: gemessen %.2f ms, Modell %.2f ms\n", (t1 - t0) / 1e6, (double)st.dauer_ns / 1e6);
    PRUEFE((t1 - t0) / 1e6 > (double)st.dauer_ns / 1e6 - 1.0 && (t1 - t0) / 1e6 < (double)st.dauer_ns / 1e6 + 15.0, "Echtzeitdauer");
    t0 = nanos_jetzt();
    for (unsigned i = 0; i < 32; i++) ersatz_ht[(061 << 5) | i] = 0;
    PRUEFE(zt_eingabe(0, (061 << 5), &st) == ZT_OK, "Eingabe echt");
    t1 = nanos_jetzt();
    printf("  Echtzeit Eingabe: gemessen %.2f ms, Modell %.2f ms\n", (t1 - t0) / 1e6, (double)st.dauer_ns / 1e6);
    PRUEFE((t1 - t0) / 1e6 > (double)st.dauer_ns / 1e6 - 1.0 && (t1 - t0) / 1e6 < (double)st.dauer_ns / 1e6 + 15.0, "Echtzeitdauer Eingabe");
    {
        int gleich = 1;
        for (unsigned i = 0; i < 32; i++) if (ersatz_ht[(061 << 5) | i] != 0123 + i) gleich = 0;
        PRUEFE(gleich, "Daten nach Echtzeit-Hin- und Rueckweg");
    }
    /* Abbruch mitten im Befehl */
    pthread_create(&th, NULL, abbrecher, NULL);
    t0 = nanos_jetzt();
    PRUEFE(zt_ausgabe(0, (062 << 5), &st) == ZT_ABGEBROCHEN, "Abbruch");
    t1 = nanos_jetzt();
    pthread_join(th, NULL);
    PRUEFE((t1 - t0) / 1e6 < 60.0, "Abbruch rechtzeitig (%.1f ms)", (t1 - t0) / 1e6);
    PRUEFE(zt_semaphore_frei(), "Semaphore nach Abbruch frei");
    PRUEFE(zt_ausgabe(0, (062 << 5), &st) == ZT_OK, "Befehl nach Abbruch");
    zt_zeitmodus(ZT_ZEIT_VIRTUELL);
    zt_phasen_fest(0, 0, 0);
}

static void teil6_echte_ht(void)
{
    zt_stat_t st;
    FILE *f = fopen("ht_test.txt", "w");
    if (!f) { PRUEFE(0, "ht_test.txt"); return; }
    for (unsigned a = 0; a < 4096; a++) fprintf(f, "%04o: %011o\n", a, 0);
    fclose(f);
    PRUEFE(trommel_einschalten_start("ht_test.txt", 3) == TROMMEL_OK, "HT einschalten");
    zt_ht_ankoppeln(NULL);                               /* Vorgabe: trommel.h */
    for (unsigned i = 0; i < 32; i++) trommel_schreiben((070 << 5) | i, 0777 + i);
    zt_anwahl(4);
    PRUEFE(zt_ausgabe(0, (070 << 5), &st) == ZT_OK, "Ausgabe mit echter HT");
    PRUEFE(st.dauer_ns > 75000000ULL && st.dauer_ns < 92000000ULL, "Dauer %.3f ms", (double)st.dauer_ns / 1e6);
    PRUEFE(zt_eingabe(0, (071 << 5), &st) == ZT_OK, "Eingabe mit echter HT");
    {
        int gleich = 1;
        for (unsigned i = 0; i < 32; i++) if (trommel_lesen((071 << 5) | i) != 0777 + i) gleich = 0;
        PRUEFE(gleich, "Spur 071 der echten HT = Spur 070");
    }
    trommel_ausschalten();
    remove("ht_test.txt");
}

int main(void)
{
    printf("Test 1: Tabellen\n");              teil1_tabellen();
    printf("Test 2: Zeitmodell\n");            teil2_modell();
    printf("Test 3: Daten mit Ersatz-HT\n");   teil3_daten();
    printf("Test 4: Persistenz\n");            teil4_persistenz();
    printf("Test 5: Echtzeit und Abbruch\n");  teil5_echtzeit();
    printf("Test 6: echte Haupttrommel\n");    teil6_echte_ht();
    zt_ausschalten();
    for (int k = 0; k < 4; k++) remove(PF[k]);
    printf("%d Pruefungen, %d Fehler\n", pruefungen, fehler);
    printf(fehler ? "TEST ZT FALSCH\n" : "TEST ZT WAHR\n");
    return fehler ? 6 : 0;
}
