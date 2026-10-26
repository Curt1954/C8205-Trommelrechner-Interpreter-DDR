/* zt_modul.c — Zusatztrommeln des C 8205Z (Schnittstelle und Beschreibung: zt_modul.h).
 * Version: 0.01-003
 *
 * Aufbau: Der Aufrufer ist der Initiator (er füllt die Puffer), ein Hintergrundprozess (Thread) ist der Empfänger
 * (er leert sie). Zwei Puffer zu je 8 Worten, je ein Semaphor: Der Initiator setzt ihn vor dem Füllen, der Empfänger
 * gibt ihn nach dem Schreiben frei. Block n benutzt Puffer n mod 2. Die Zeitpunkte aller Blöcke stehen vor dem Beginn
 * des Befehls fest (Plan aus zt_modell_dauer); im Modus ECHT warten beide Seiten bis zu diesen Zeitpunkten.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "plattform.h"
#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif

#ifndef ZT_OHNE_TROMMEL
#include "trommel.h"      /* Vorgabe-Kopplung an die Haupttrommel; mit -DZT_OHNE_TROMMEL entfaellt sie (Erweiterungsmodul fuer GRAFIK) */
#endif
#include "zt_modul.h"

const unsigned char ZT_HT_PERM[32] = { 000,015,032,007,024,001,016,033, 010,025,002,017,034,011,026,003,
                                       020,035,012,027,004,021,036,013, 030,005,022,037,014,031,006,023 };
const unsigned char ZT_ZT_PERM[32] = { 000,010,020,030,015,025,035,005, 032,002,012,022,007,017,027,037,
                                       024,034,004,014,001,011,021,031, 016,026,036,006,033,003,013,023 };

#define HT_W   ((long long)ZT_HT_POS_NS)
#define HT_U   (32LL * HT_W)                    /* 3,328 ms */
#define ZT_S   ((long long)ZT_SEKTORZEIT_NS)
#define ZT_U   (32LL * ZT_S)                    /* 20 ms */
#define ZT_BLOCKZEIT (29LL * ZT_S)              /* 7 * 4 + 1 Positionen = 18,125 ms */
#define WORT_MASKE ((1ULL << 33) - 1ULL)

/* ================= Zeitmodell (reine Rechnung) ================= */

static long long llmax(long long a, long long b) { return a > b ? a : b; }
static long long ceil_div(long long a, long long b)
{
    long long q = a / b;
    if (a % b != 0 && ((a > 0) == (b > 0))) q++;
    return q;
}
static long long mod_pos(long long a, long long m) { long long r = a % m; return r < 0 ? r + m : r; }

/* Zeit ab t bis zum nächsten Beginn der HT-Position pos */
static long long ht_warte(long long t, int pos)
{
    long long ph = mod_pos(t - (long long)pos * HT_W, HT_U);
    return ph == 0 ? 0 : HT_U - ph;
}

/* HT-Gruppenbefehl auf Block j ab t: Warten auf Position 8j, dann 8 Worte; liefert das Ende */
static long long ht_block(long long t, int j, long long *beginn)
{
    t += ht_warte(t, 8 * j);
    *beginn = t;
    return t + 8 * HT_W;
}

/* ZT-Block k ab t: beginnt an der ersten ZT-Position p = k (mod 4); Dauer 18,125 ms */
static void zt_block(long long t, int k, long long phase, long long *start, long long *ende)
{
    long long ts = t - phase;
    long long n = ceil_div(ts, ZT_S);
    while (mod_pos(n, 4) != k) n++;
    ts = n * ZT_S;
    *start = ts + phase;
    *ende  = ts + ZT_BLOCKZEIT + phase;
}

/* Blockfolge: beginnt mit dem Block, dessen ZT-Position zuerst an den Kopf kommt, dann zyklisch */
static void blockfolge(long long t, long long phase_zt, int folge[4])
{
    int pos = (int)mod_pos(ceil_div(t - phase_zt, ZT_S), 32);
    for (int i = 0; i < 4; i++) folge[i] = (pos + i) % 4;
}

long long zt_modell_dauer(long long phase_zt, long long phase_ht, long long u, int richtung, zt_plan_t *plan)
{
    zt_plan_t lokal;
    zt_plan_t *p = plan ? plan : &lokal;
    long long t = phase_ht, frei[2] = {0, 0}, ende = 0, hb, s, e;
    memset(p, 0, sizeof *p);
    blockfolge(t, phase_zt, p->folge);

    if (richtung == ZT_RICHTUNG_EINGABE) {         /* ZT -> Puffer -> HT */
        long long ht_frei = 0, he;
        for (int n = 0; n < 4; n++) {
            int pb = n % 2, b = p->folge[n];
            t = llmax(t, frei[pb]);                          /* Puffer muß leer sein */
            zt_block(t, b, phase_zt, &s, &e);
            he = ht_block(llmax(e, ht_frei), b, &hb);
            ht_frei = he; frei[pb] = he; ende = he;
            p->init_wait[n] = s - t; p->init_ende[n] = e; p->emp_ende[n] = he;
            t = e + u;
        }
    } else {                                       /* HT -> Puffer -> ZT */
        long long zt_frei = 0, ht_t = t, he;
        for (int n = 0; n < 4; n++) {
            int pb = n % 2, b = p->folge[n];
            ht_t = llmax(ht_t, frei[pb]);
            he = ht_block(ht_t, b, &hb);
            zt_block(llmax(he, zt_frei), b, phase_zt, &s, &e);
            zt_frei = e + u; frei[pb] = e; ende = e;
            p->init_wait[n] = hb - ht_t; p->init_ende[n] = he; p->emp_ende[n] = e;
            ht_t = he;
        }
    }
    p->dauer = ende - phase_ht;
    return p->dauer;
}

/* ================= Zustand ================= */

typedef struct {
    int       aktiv;
    unsigned  gen;
    int       richtung, sel;
    unsigned  spur_zt, spur_ht;
    zt_plan_t plan;
    long long basis_abs;          /* absolute Zeit (ns), die der Modellzeit tau0 entspricht */
    long long tau0;
    int       n_fertig;
} befehl_t;

static int            an = 0, pf_bereit = 0, thr_gestartet = 0;
static volatile int   stop_flag = 0;
static int            abbruch = 0, belegt = 0, emp_arbeitet = 0;
static int            modus = ZT_ZEIT_VIRTUELL;
static long long      umschalt = ZT_UMSCHALT_NS;
static int            fest_an = 0;
static long long      fest_pz = 0, fest_ph = 0;
static int            gewaehlt = 0;
static volatile int   letzte_adr[ZT_ANZAHL] = { -1, -1, -1, -1 };   /* zuletzt bearbeitete ZT-Adresse (Spur*32+Sektor), -1 = keine */
static zt_ht_t        ht_vorgabe, ht;
static char           dateipfad[ZT_ANZAHL][1024];
static uint64_t       mem[ZT_ANZAHL][4096];
static int            schmutzig[ZT_ANZAHL];
static long long      zt_t0_ns;
static int            zt_idx0;
static uint64_t       puffer[ZT_PUFFER][ZT_BLOCK];
static int            sem[ZT_PUFFER], voll[ZT_PUFFER];      /* sem: 0 FREI, 1 BESETZT */
static befehl_t       cmd;
static pf_mutex_t     mtx;
static pf_cond_t      cv;
static pf_thread_t    thr;

static void schlafe_bis(long long ziel_abs)
{
    while ((long long)pf_zeit_ns() < ziel_abs) pf_schlafe_bis((uint64_t)ziel_abs, 0);
}

static int ht_vorgabe_gesetzt = 0;
static void vorgabe_ht(void)
{
    if (ht_vorgabe_gesetzt) return;
#ifndef ZT_OHNE_TROMMEL
    ht_vorgabe.lesen = trommel_lesen;
    ht_vorgabe.schreiben = trommel_schreiben;
    ht_vorgabe.aktueller_sektor = trommel_aktueller_sektor;
#endif
    ht_vorgabe_gesetzt = 1;
}

/* ================= Dateien ================= */

static int datei_laden(int k)
{
    FILE *f = fopen(dateipfad[k], "r");
    char zeile[128];
    memset(mem[k], 0, sizeof mem[k]);
    if (!f) return 1;                                   /* fehlt: leer, wird beim Sichern angelegt */
    while (fgets(zeile, sizeof zeile, f)) {
        unsigned a; unsigned long long w;
        if (sscanf(zeile, "%o: %llo", &a, &w) == 2 && a < 4096) mem[k][a] = w & WORT_MASKE;
    }
    fclose(f);
    return 0;
}

static int datei_sichern(int k)
{
    FILE *f = fopen(dateipfad[k], "w");
    if (!f) return -1;
    for (unsigned a = 0; a < 4096; a++) fprintf(f, "%04o: %011llo\n", a, (unsigned long long)mem[k][a]);
    if (fclose(f) != 0) return -1;
    schmutzig[k] = 0;
    return 0;
}

/* ================= Empfänger (Hintergrundprozess) ================= */

static void empfaenger_arbeit(int richtung, int sel, unsigned spur_zt, unsigned spur_ht, int p, int b)
{
    for (int i = 0; i < ZT_BLOCK; i++) {
        unsigned sektor = ZT_ZT_PERM[4 * i + b];         /* ZT-Position 4i+b = HT-Position 8b+i */
        if (richtung == ZT_RICHTUNG_EINGABE) ht.schreiben((spur_ht << 5) | sektor, puffer[p][i]);
        else { mem[sel][(spur_zt << 5) | sektor] = puffer[p][i]; letzte_adr[sel] = (int)((spur_zt << 5) | sektor); }
    }
}

PF_THREAD_FUNC(empfaenger)
{
    (void)arg;
    pf_mutex_lock(&mtx);
    while (!stop_flag) {
        int n, p;
        if (abbruch || !cmd.aktiv || cmd.n_fertig >= 4 || !voll[(n = cmd.n_fertig) % 2]) {
            pf_cond_wait_ms(&cv, &mtx, 20);
            continue;
        }
        p = n % 2;
        {
            unsigned gen = cmd.gen;
            int b = cmd.plan.folge[n], richtung = cmd.richtung, sel = cmd.sel;
            unsigned szt = cmd.spur_zt, sht = cmd.spur_ht;
            long long ziel = cmd.basis_abs + (cmd.plan.emp_ende[n] - cmd.tau0);
            int echt = (modus == ZT_ZEIT_ECHT);
            emp_arbeitet = 1;
            pf_mutex_unlock(&mtx);
            if (echt) schlafe_bis(ziel);
            if (!abbruch) empfaenger_arbeit(richtung, sel, szt, sht, p, b);
            pf_mutex_lock(&mtx);
            emp_arbeitet = 0;
            if (gen == cmd.gen && !abbruch) {
                voll[p] = 0; sem[p] = 0; cmd.n_fertig++;
            }
            pf_cond_broadcast(&cv);
        }
    }
    pf_mutex_unlock(&mtx);
    PF_THREAD_ENDE;
}

/* ================= Schnittstelle ================= */

int zt_einschalten(const char *pfad[ZT_ANZAHL], int start_index)
{
    if (an) return ZT_FEHLER;
    if (!pf_bereit) { pf_zeit_start(); pf_mutex_init(&mtx); pf_cond_init(&cv); pf_bereit = 1; }
    for (int k = 0; k < ZT_ANZAHL; k++) {
        if (!pfad || !pfad[k] || strlen(pfad[k]) >= sizeof dateipfad[k]) return ZT_FEHLER;
        strcpy(dateipfad[k], pfad[k]);
        datei_laden(k);
        schmutzig[k] = 0;
        if (datei_sichern(k) != 0) return ZT_FEHLER;      /* legt fehlende Dateien an, prüft Schreibrecht */
    }
    zt_t0_ns = (long long)pf_zeit_ns();
    zt_idx0 = start_index >= 0 ? start_index % 32 : (int)((zt_t0_ns / 1000) % 32);
    memset(&cmd, 0, sizeof cmd);
    memset(sem, 0, sizeof sem); memset(voll, 0, sizeof voll);
    gewaehlt = 0; abbruch = 0; belegt = 0; emp_arbeitet = 0; stop_flag = 0;
    for (int k = 0; k < ZT_ANZAHL; k++) letzte_adr[k] = -1;
    vorgabe_ht();
    if (!ht.lesen) ht = ht_vorgabe;
    if (!ht.lesen || !ht.schreiben || !ht.aktueller_sektor) return ZT_FEHLER;   /* ohne Vorgabe: zt_ht_ankoppeln vor dem Einschalten */
    if (pf_thread_start(&thr, empfaenger, NULL) != 0) return ZT_FEHLER;
    thr_gestartet = 1;
    an = 1;
    return ZT_OK;
}

void zt_ausschalten(void)
{
    if (!an) return;
    pf_mutex_lock(&mtx);
    stop_flag = 1; abbruch = 1;
    pf_cond_broadcast(&cv);
    pf_mutex_unlock(&mtx);
    if (thr_gestartet) { pf_thread_join(&thr); thr_gestartet = 0; }
    for (int k = 0; k < ZT_ANZAHL; k++) if (schmutzig[k]) datei_sichern(k);
    an = 0;
    gewaehlt = 0;
}

int zt_anwahl(int k)
{
    if (!an || k < 1 || k > ZT_ANZAHL) return ZT_FEHLER;
    gewaehlt = k;
    return ZT_OK;
}

int zt_gewaehlt(void) { return gewaehlt; }

void zt_ht_ankoppeln(const zt_ht_t *h)
{
    vorgabe_ht();
    ht = h ? *h : ht_vorgabe;
}

void zt_zeitmodus(int m) { modus = (m == ZT_ZEIT_ECHT) ? ZT_ZEIT_ECHT : ZT_ZEIT_VIRTUELL; }
void zt_umschaltzeit(long long ns) { umschalt = ns < 0 ? 0 : ns; }
void zt_phasen_fest(int a, long long pz, long long ph) { fest_an = a; fest_pz = pz; fest_ph = ph; }

void zt_abbrechen(void)
{
    if (!pf_bereit) return;
    pf_mutex_lock(&mtx);
    if (belegt) abbruch = 1;                 /* wirkt nur auf den laufenden Befehl */
    pf_cond_broadcast(&cv);
    pf_mutex_unlock(&mtx);
}

/* Phasen des Befehlsbeginns: Modellzeit tau0 = Lage in der HT-Umdrehung; phase_zt = Beginn der ZT-Position 0 */
static void phasen_messen(long long jetzt, long long *pz, long long *ph)
{
    if (fest_an) { *pz = fest_pz; *ph = fest_ph; return; }
    {
        unsigned sektor = ht.aktueller_sektor() & 037u;
        int pos = 0;
        for (int i = 0; i < 32; i++) if (ZT_HT_PERM[i] == sektor) pos = i;
        *ph = (long long)pos * HT_W;
        *pz = mod_pos(zt_t0_ns - (long long)zt_idx0 * ZT_S - jetzt + *ph, ZT_U);
    }
}

static int ausfuehren(int richtung, unsigned zzz0, unsigned bbbb, zt_stat_t *s)
{
    int sel, ergebnis = ZT_OK, echt;
    long long pz, ph, jetzt;
    zt_plan_t plan;

    if (s) memset(s, 0, sizeof *s);
    if (!an) return ZT_FEHLER;
    pf_mutex_lock(&mtx);
    if (belegt) { pf_mutex_unlock(&mtx); return ZT_FEHLER; }
    if (gewaehlt == 0) { pf_mutex_unlock(&mtx); return ZT_KEINE_ANWAHL; }
    belegt = 1; abbruch = 0;
    sel = gewaehlt - 1;
    echt = (modus == ZT_ZEIT_ECHT);
    jetzt = (long long)pf_zeit_ns();
    phasen_messen(jetzt, &pz, &ph);
    zt_modell_dauer(pz, ph, umschalt, richtung, &plan);
    memset(sem, 0, sizeof sem); memset(voll, 0, sizeof voll);
    cmd.gen++;
    cmd.aktiv = 1; cmd.richtung = richtung; cmd.sel = sel;
    cmd.spur_zt = (zzz0 >> 5) & 0x7Fu; cmd.spur_ht = (bbbb >> 5) & 0x7Fu;
    cmd.plan = plan; cmd.basis_abs = jetzt; cmd.tau0 = ph; cmd.n_fertig = 0;
    pf_cond_broadcast(&cv);
    pf_mutex_unlock(&mtx);

    for (int n = 0; n < 4 && ergebnis == ZT_OK; n++) {        /* Initiator */
        int p = n % 2, b = plan.folge[n];
        pf_mutex_lock(&mtx);
        while (sem[p] != 0 && !abbruch) pf_cond_wait_ms(&cv, &mtx, 20);
        if (abbruch) { pf_mutex_unlock(&mtx); ergebnis = ZT_ABGEBROCHEN; break; }
        sem[p] = 1;
        pf_mutex_unlock(&mtx);
        for (int i = 0; i < ZT_BLOCK; i++) {
            unsigned sektor = ZT_HT_PERM[8 * b + i];           /* HT-Position 8b+i = ZT-Position 4i+b */
            puffer[p][i] = (richtung == ZT_RICHTUNG_EINGABE)
                ? mem[sel][(cmd.spur_zt << 5) | sektor]
                : (ht.lesen((cmd.spur_ht << 5) | sektor) & WORT_MASKE);
            if (richtung == ZT_RICHTUNG_EINGABE) letzte_adr[sel] = (int)((cmd.spur_zt << 5) | sektor);
        }
        if (echt) schlafe_bis(jetzt + (plan.init_ende[n] - ph));
        pf_mutex_lock(&mtx);
        if (abbruch) { pf_mutex_unlock(&mtx); ergebnis = ZT_ABGEBROCHEN; break; }
        voll[p] = 1;
        pf_cond_broadcast(&cv);
        pf_mutex_unlock(&mtx);
    }

    pf_mutex_lock(&mtx);
    if (ergebnis == ZT_OK) {
        while (cmd.n_fertig < 4 && !abbruch) pf_cond_wait_ms(&cv, &mtx, 20);
        if (cmd.n_fertig < 4) ergebnis = ZT_ABGEBROCHEN;
    }
    if (ergebnis != ZT_OK) {                                   /* Aufräumen: Empfänger abwarten, Semaphore frei */
        abbruch = 1;
        cmd.gen++;
        while (emp_arbeitet) pf_cond_wait_ms(&cv, &mtx, 20);
        memset(sem, 0, sizeof sem); memset(voll, 0, sizeof voll);
    }
    cmd.aktiv = 0;
    belegt = 0; abbruch = 0;
    pf_cond_broadcast(&cv);
    pf_mutex_unlock(&mtx);

    if (ergebnis == ZT_OK && richtung == ZT_RICHTUNG_AUSGABE) {
        schmutzig[sel] = 1;
        if (datei_sichern(sel) != 0) ergebnis = ZT_FEHLER;
    }
    if (ergebnis == ZT_OK && s) {
        s->dauer_ns = (unsigned long long)plan.dauer;
        s->ticks_ht = (unsigned long long)(plan.dauer / HT_W);
        for (int n = 0; n < 4; n++) s->wartezeit_block[n] = (unsigned)(plan.init_wait[n] / 1000);
    }
    return ergebnis;
}

int zt_eingabe(unsigned int zzz0, unsigned int bbbb, zt_stat_t *s) { return ausfuehren(ZT_RICHTUNG_EINGABE, zzz0, bbbb, s); }
int zt_ausgabe(unsigned int zzz0, unsigned int bbbb, zt_stat_t *s) { return ausfuehren(ZT_RICHTUNG_AUSGABE, zzz0, bbbb, s); }

/* ================= Direktzugriffe ================= */

uint64_t zt_lesen(int k, unsigned adr)
{
    if (!an || k < 1 || k > ZT_ANZAHL || adr > 07777u) return 0;
    return mem[k - 1][adr];
}

int zt_schreiben(int k, unsigned adr, uint64_t wert)
{
    if (!an || k < 1 || k > ZT_ANZAHL || adr > 07777u) return ZT_FEHLER;
    mem[k - 1][adr] = wert & WORT_MASKE;
    schmutzig[k - 1] = 1;
    return ZT_OK;
}

int zt_letzte_adresse(int k)
{
    if (!an || k < 1 || k > ZT_ANZAHL) return -1;
    return letzte_adr[k - 1];
}

void zt_leeren(void)
{
    if (!an) return;
    for (int k = 0; k < ZT_ANZAHL; k++) letzte_adr[k] = -1;
    for (int k = 0; k < ZT_ANZAHL; k++) { memset(mem[k], 0, sizeof mem[k]); datei_sichern(k); }
    gewaehlt = 0;
}

int zt_semaphore_frei(void)
{
    int ok;
    if (!pf_bereit) return 1;
    pf_mutex_lock(&mtx);
    ok = !sem[0] && !sem[1] && !voll[0] && !voll[1];
    pf_mutex_unlock(&mtx);
    return ok;
}
