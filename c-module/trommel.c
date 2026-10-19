/* trommel.c — Implementierung, s. trommel.h für Architektur-Kommentar.
 * Plattformabhängiges (Threads, Uhr, Schlafen) steckt in plattform.h (Linux und Windows). */
#ifdef __MINGW32__
#define __USE_MINGW_ANSI_STDIO 1     /* %llo/%llu wie unter Linux */
#endif
#include "trommel.h"
#include "bahnsperre.h"
#include "unterbrechung.h"
#include "plattform.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

/* Dateiformat = Interpreter-Trommeldatei: "aaaa: ttttttttttt\n" (LF!) */
#define LINE_LEN     18u    /* 4 + 1 (':') + 1 (' ') + 11 + 1 ('\n') */
#define WORT_OFFSET   6u    /* Offset des t-Teils innerhalb der Zeile */
#define ADR_ANZAHL 4096u
#define ADR_MAX    07777u
#define WORT_MASKE 0x1FFFFFFFFULL   /* 33 Bit */
#define TICK_NS    104000ULL        /* 1 Wortzeit = 104 µs (Hardware.md) */
#define WARTE_SLICE_MS 50u          /* Aufrufer prüft alle 50 ms auf Abbruch */

/* Entscheidung des Projektinhabers (13.10.2026): "Schlitz ist Schlitz" — ist eine Sektornummer
 * aktuell, dann für die ganzen 104 µs; trifft in dieser Zeitspanne eine Anforderung ein, wird sie bedient. */
#ifndef TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ
#define TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ 1
#endif

/* Vollständige physische Zugriffsreihenfolge (logische Sektornummern in
 * physischer Reihenfolge), s. Hardware.md / Magnettrommel.md. */
static const unsigned int PERM[32] = {
    000,015,032,007,024,001,016,033,
    010,025,002,017,034,011,026,003,
    020,035,012,027,004,021,036,013,
    030,005,022,037,014,031,006,023
};

volatile unsigned int trommel_aktuelle_sektornummer;

static FILE *drum_datei = NULL;
static pf_thread_t drum_thread;
static int drum_thread_gestartet = 0;
static volatile int drum_laeuft = 0;

/* Ein Mutex schützt Auftrag, Statistik und Datei; der zweite serialisiert die Aufrufer.
 * Beide werden beim ersten Einschalten angelegt und bleiben für die Prozesslebensdauer bestehen. */
static pf_mutex_t mtx, anf_mtx;
static pf_cond_t cv_fertig;
static int pf_bereit = 0;

static unsigned long long drum_t0_ns;       /* Zeitpunkt von Tick 0 (Einschalten) */
static unsigned int drum_start_index = 0;   /* PERM-Index bei Tick 0 */
static unsigned long long letzter_tick = 0; /* zuletzt verarbeiteter Tick */
static volatile int abbruch_flag = 0;       /* trommel_warten_abbrechen() */
static pf_flag_t req_wartet;                /* Hintergrundprozess soll aktiv auf den nächsten Tick warten (Windows) */

static struct {
    int aktiv, fertig, schreiben, ergebnis;
    unsigned int adresse;
    uint64_t wert;                 /* Schreibwert bzw. gelesener Wert */
    unsigned long long ab_tick;    /* frühester Tick, an dem der Zugriff erfolgen darf */
    unsigned long long ausgefuehrt_tick;
} req;

static trommel_statistik_t stat_;

static unsigned long long jetzt_ns(void)
{
    return pf_zeit_ns();
}

static unsigned long long tick_von(unsigned long long ns)
{
    return (ns - drum_t0_ns) / TICK_NS;
}

unsigned int trommel_sektor(unsigned int adresse)
{
    return adresse & 0x1Fu;       /* z19-z23, 5 Bit, s. Hardware.md */
}

unsigned int trommel_bahn(unsigned int adresse)
{
    return adresse >> 5;          /* z12-z18, 7 Bit, s. Hardware.md */
}

/* ---- Dateizugriff (Aufrufer hält mtx) --------------------------------- */
static int lese_zelle(unsigned int adresse, uint64_t *wert)
{
    char puf[12];
    long offset = (long)adresse * LINE_LEN + WORT_OFFSET;
    if (!drum_datei || adresse > ADR_MAX) return -1;
    if (fseek(drum_datei, offset, SEEK_SET) != 0 || fread(puf, 1, 11, drum_datei) != 11) {
        fprintf(stderr, "trommel_lesen: Lesefehler bei Adresse %04o\n", adresse);
        return -1;
    }
    puf[11] = '\0';
    *wert = strtoull(puf, NULL, 8) & WORT_MASKE;
    return 0;
}

static int schreibe_zelle(unsigned int adresse, uint64_t wert)
{
    long offset = (long)adresse * LINE_LEN + WORT_OFFSET;
    if (!drum_datei || adresse > ADR_MAX) return TROMMEL_FEHLER;
    if (bahnsperre_spur_gesperrt(trommel_bahn(adresse)) == BAHNSPERRE_GESPERRT)
        return TROMMEL_SCHREIBEN_GESPERRT;
    if (fseek(drum_datei, offset, SEEK_SET) != 0) return TROMMEL_FEHLER;
    /* auf 33 Bit begrenzt: mehr als 11 Oktalziffern würden Doppelpunkt/Zeilenende der Folgezeile überschreiben */
    fprintf(drum_datei, "%011llo", (unsigned long long)(wert & WORT_MASKE));
    fflush(drum_datei);
    return TROMMEL_OK;
}

/* Ausführung des anstehenden Auftrags (Aufrufer hält mtx) */
static void auftrag_ausfuehren(unsigned long long tick)
{
    if (req.schreiben) {
        req.ergebnis = schreibe_zelle(req.adresse, req.wert);
    } else {
        uint64_t w = 0;
        req.ergebnis = (lese_zelle(req.adresse, &w) == 0) ? TROMMEL_OK : TROMMEL_FEHLER;
        req.wert = w;
    }
    req.fertig = 1;
    req.ausgefuehrt_tick = tick;
    stat_.zugriffe++;
    pf_cond_broadcast(&cv_fertig);
}

/* ---- Hintergrundprozess: die drehende Trommel -------------------------- */
PF_THREAD_FUNC(drum_hintergrundprozess)
{
    (void)arg;
    pf_timerslack_minimieren();
    for (;;) {
        unsigned long long soll_ns = drum_t0_ns + (letzter_tick + 1ULL) * TICK_NS;
        unsigned long long bis, jetzt;
        pf_schlafe_bis(soll_ns, pf_flag_lese(&req_wartet));

        pf_mutex_lock(&mtx);
        if (!drum_laeuft) { pf_mutex_unlock(&mtx); break; }
        jetzt = jetzt_ns();
        bis = tick_von(jetzt);
        stat_.aufwachen++;
        if (jetzt > soll_ns) {
            unsigned long long v = jetzt - soll_ns;
            stat_.verspaetung_summe_ns += v;
            if (v > stat_.verspaetung_max_ns) stat_.verspaetung_max_ns = v;
        }
        /* verspätet aufgewacht: übersprungene Ticks der Reihe nach nachholen, damit kein Sektor ausgelassen wird */
        while (letzter_tick < bis) {
            unsigned int s;
            letzter_tick++;
            s = PERM[(drum_start_index + letzter_tick) % 32u];
            trommel_aktuelle_sektornummer = s;
            stat_.ticks = letzter_tick;
            if (letzter_tick < bis) stat_.nachgeholte_ticks++;
            if (req.aktiv && !req.fertig && letzter_tick >= req.ab_tick &&
                trommel_sektor(req.adresse) == s)
                auftrag_ausfuehren(letzter_tick);
        }
        pf_mutex_unlock(&mtx);
    }
    PF_THREAD_ENDE;
}

/* ---- Ein-/Ausschalten ---------------------------------------------------- */
static int datei_pruefen(FILE *f)
{
    char z[LINE_LEN + 1];
    long groesse;
    unsigned int a;
    if (fseek(f, 0, SEEK_END) != 0) return -1;
    groesse = ftell(f);
    if (groesse != (long)(ADR_ANZAHL * LINE_LEN)) {
        fprintf(stderr, "trommel_einschalten: Dateigroesse %ld, erwartet %u (4096 Zeilen zu %u Byte, LF, Format \"aaaa: ttttttttttt\"; "
                        "unter Windows keine CRLF-Zeilenenden)\n",
                groesse, ADR_ANZAHL * LINE_LEN, LINE_LEN);
        return -1;
    }
    for (a = 0; a <= ADR_MAX; a += ADR_MAX) {          /* erste und letzte Zeile */
        unsigned int i;
        fseek(f, (long)a * LINE_LEN, SEEK_SET);
        if (fread(z, 1, LINE_LEN, f) != LINE_LEN) return -1;
        for (i = 0; i < LINE_LEN; i++) {
            int ok = (i < 4 || (i >= WORT_OFFSET && i < WORT_OFFSET + 11)) ? (z[i] >= '0' && z[i] <= '7')
                   : (i == 4) ? (z[i] == ':') : (i == 5) ? (z[i] == ' ') : (z[i] == '\n');
            if (!ok) {
                fprintf(stderr, "trommel_einschalten: Zeile %04o hat nicht das Format \"aaaa: ttttttttttt\\n\"\n", a);
                return -1;
            }
        }
    }
    return 0;
}

int trommel_einschalten_start(const char *dateipfad, int start_index)
{
    if (drum_laeuft) { fprintf(stderr, "trommel_einschalten: Trommel laeuft bereits\n"); return -1; }
    if (!pf_bereit) {
        pf_zeit_start();
        pf_mutex_init(&mtx);
        pf_mutex_init(&anf_mtx);
        pf_cond_init(&cv_fertig);
        pf_bereit = 1;
    }
#ifdef _WIN32
    {   /* Pfad ist UTF-8 (Projektordner enthalten Umlaute); fopen versteht unter Windows nur die ANSI-Codepage */
        wchar_t wpfad[1024];
        if (MultiByteToWideChar(CP_UTF8, 0, dateipfad, -1, wpfad, 1024) == 0) {
            fprintf(stderr, "trommel_einschalten: Pfad nicht umwandelbar oder zu lang\n");
            return -1;
        }
        drum_datei = _wfopen(wpfad, L"r+b");
    }
#else
    drum_datei = fopen(dateipfad, "r+b");
#endif
    if (!drum_datei) {
        perror("trommel_einschalten: fopen");
        return -1;
    }
    if (datei_pruefen(drum_datei) != 0) {
        fclose(drum_datei);
        drum_datei = NULL;
        return -1;
    }
    /* "nach dem Einschalten ist dieser Wert zufaellig" (Autor-Vorgabe) */
    if (start_index < 0) {
        srand((unsigned)time(NULL));
        drum_start_index = (unsigned)(rand() % 32);
    } else {
        drum_start_index = (unsigned)start_index % 32u;
    }

    memset(&req, 0, sizeof req);
    memset(&stat_, 0, sizeof stat_);
    abbruch_flag = 0;
    pf_flag_setze(&req_wartet, 0);
    letzter_tick = 0;
    trommel_aktuelle_sektornummer = PERM[drum_start_index];
    drum_t0_ns = jetzt_ns();

    drum_laeuft = 1;
    if (pf_thread_start(&drum_thread, drum_hintergrundprozess, NULL) != 0) {
        fprintf(stderr, "trommel_einschalten: Hintergrundprozess konnte nicht gestartet werden\n");
        fclose(drum_datei);
        drum_datei = NULL;
        drum_laeuft = 0;
        return -1;
    }
    drum_thread_gestartet = 1;
    return 0;
}

int trommel_einschalten(const char *dateipfad)
{
    return trommel_einschalten_start(dateipfad, -1);
}

void trommel_ausschalten(void)
{
    if (!drum_thread_gestartet) return;
    pf_mutex_lock(&mtx);
    drum_laeuft = 0;
    if (req.aktiv && !req.fertig) {       /* wartenden Aufrufer freigeben */
        req.fertig = 1;
        req.ergebnis = TROMMEL_ABGEBROCHEN;
        pf_cond_broadcast(&cv_fertig);
    }
    pf_mutex_unlock(&mtx);
    pf_wecken();
    pf_thread_join(&drum_thread);
    drum_thread_gestartet = 0;
    pf_mutex_lock(&mtx);
    if (drum_datei) {
        fclose(drum_datei);
        drum_datei = NULL;
    }
    pf_mutex_unlock(&mtx);
}

/* ---- Auftragskanal des Knotengraphen --------------------------------------- */
static int anfordern(int schreiben, unsigned int adresse, uint64_t *wert, unsigned int *wartezeit)
{
    int rc;
    unsigned long long jetzt, ankunft;

    if (!pf_bereit) return TROMMEL_FEHLER;
    pf_mutex_lock(&anf_mtx);
    pf_mutex_lock(&mtx);
    if (!drum_laeuft || !drum_datei || adresse > ADR_MAX) {
        pf_mutex_unlock(&mtx);
        pf_mutex_unlock(&anf_mtx);
        return TROMMEL_FEHLER;
    }
    /* Ein anstehender Abbruch (Strg+C bzw. trommel_warten_abbrechen) gilt fuer diesen Zugriff, auch wenn er sofort bedient werden koennte;
     * sonst bliebe das Flag fuer einen spaeteren, unbeteiligten Zugriff stehen. */
    if (abbruch_angefordert || abbruch_flag) {
        abbruch_flag = 0;
        pf_mutex_unlock(&mtx);
        pf_mutex_unlock(&anf_mtx);
        return TROMMEL_ABGEBROCHEN;
    }
    jetzt = jetzt_ns();
    ankunft = tick_von(jetzt);
    memset(&req, 0, sizeof req);
    req.aktiv = 1;
    req.schreiben = schreiben;
    req.adresse = adresse;
    req.wert = schreiben ? *wert : 0;
    /* ab_tick: Mit TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ (Standard) zählt schon der laufende Zeitschlitz;
     * sonst erst der nächste Tickbeginn. */
    req.ab_tick = ankunft + (TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ ? 0ULL : 1ULL);
#if TROMMEL_ZUGRIFF_AUCH_IM_SCHLITZ
    if (PERM[(drum_start_index + ankunft) % 32u] == trommel_sektor(adresse))
        auftrag_ausfuehren(ankunft);               /* Zelle ist gerade aktuell: sofort bedienen (Wartezeit 0) */
#endif
    if (!req.fertig) {
        pf_flag_setze(&req_wartet, 1);             /* Hintergrundprozess soll genau auf den Tickbeginn achten */
        pf_wecken();
    }

    while (!req.fertig) {
        if (abbruch_angefordert || abbruch_flag) {
            abbruch_flag = 0;
            req.aktiv = 0;
            pf_flag_setze(&req_wartet, 0);
            pf_mutex_unlock(&mtx);
            pf_mutex_unlock(&anf_mtx);
            return TROMMEL_ABGEBROCHEN;
        }
        pf_cond_wait_ms(&cv_fertig, &mtx, WARTE_SLICE_MS);
    }
    pf_flag_setze(&req_wartet, 0);
    rc = req.ergebnis;
    if (rc != TROMMEL_ABGEBROCHEN) {
        unsigned int w = (unsigned int)(req.ausgefuehrt_tick - ankunft);
        if (wartezeit) *wartezeit = w;
        stat_.wartezeit_summe_ticks += w;
        if (!schreiben && rc == TROMMEL_OK) *wert = req.wert;
    }
    req.aktiv = 0;
    pf_mutex_unlock(&mtx);
    pf_mutex_unlock(&anf_mtx);
    return rc;
}

int trommel_lesen_warten(unsigned int adresse, uint64_t *wert, unsigned int *wartezeit)
{
    if (!wert) return TROMMEL_FEHLER;
    return anfordern(0, adresse, wert, wartezeit);
}

int trommel_schreiben_warten(unsigned int adresse, uint64_t wert, unsigned int *wartezeit)
{
    return anfordern(1, adresse, &wert, wartezeit);
}

void trommel_warten_abbrechen(void)
{
    if (!pf_bereit) { abbruch_flag = 1; return; }
    pf_mutex_lock(&mtx);
    abbruch_flag = 1;
    pf_cond_broadcast(&cv_fertig);
    pf_mutex_unlock(&mtx);
}

unsigned int trommel_aktueller_sektor(void)
{
    unsigned int s;
    if (!pf_bereit) return 0;
    pf_mutex_lock(&mtx);
    s = drum_laeuft ? PERM[(drum_start_index + tick_von(jetzt_ns())) % 32u] : 0u;
    pf_mutex_unlock(&mtx);
    return s;
}

/* ---- Direkte Zugriffe (ohne Koinzidenz) ------------------------------------- */
uint64_t trommel_lesen(unsigned int adresse)
{
    uint64_t w = 0;
    if (!pf_bereit) return 0;
    pf_mutex_lock(&mtx);
    if (lese_zelle(adresse, &w) != 0) w = 0;
    pf_mutex_unlock(&mtx);
    return w;
}

int trommel_schreiben(unsigned int adresse, uint64_t wert)
{
    int rc;
    if (!pf_bereit) return TROMMEL_FEHLER;
    pf_mutex_lock(&mtx);
    rc = schreibe_zelle(adresse, wert);
    pf_mutex_unlock(&mtx);
    return rc;
}

void trommel_statistik_lesen(trommel_statistik_t *s)
{
    if (!pf_bereit) { memset(s, 0, sizeof *s); return; }
    pf_mutex_lock(&mtx);
    *s = stat_;
    if (drum_laeuft) s->ticks = tick_von(jetzt_ns());   /* exakt aus der Uhr; stat_.ticks hinkt nach, wenn der Thread verdrängt wird */
    pf_mutex_unlock(&mtx);
}
