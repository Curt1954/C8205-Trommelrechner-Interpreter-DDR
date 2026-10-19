/* bahnsperre.c — s. bahnsperre.h für Architektur-Kommentar. */
#include "bahnsperre.h"
#include <stdio.h>
#include <string.h>
#include <errno.h>
#ifdef _WIN32
#include <windows.h>
#endif

volatile unsigned int bahnsperre_schalter = 0;

void bahnsperre_setzen(int ein_aus, int s0040, int s0100, int s0200,
                        int s0400, int s1000)
{
    unsigned int m = 0;
    if (ein_aus) m |= (1u << BAHNSPERRE_BIT_0001);
    if (s0040)   m |= (1u << BAHNSPERRE_BIT_0040);
    if (s0100)   m |= (1u << BAHNSPERRE_BIT_0100);
    if (s0200)   m |= (1u << BAHNSPERRE_BIT_0200);
    if (s0400)   m |= (1u << BAHNSPERRE_BIT_0400);
    if (s1000)   m |= (1u << BAHNSPERRE_BIT_1000);
    bahnsperre_schalter = m;
}

int bahnsperre_hauptschalter_ein(void)
{
    return (bahnsperre_schalter & (1u << BAHNSPERRE_BIT_0001)) != 0;
}

int bahnsperre_spur_gesperrt(unsigned int bahn)
{
    unsigned int zusatzschalter_bits;

    if (!bahnsperre_hauptschalter_ein())
        return BAHNSPERRE_OFFEN;      /* AUS -> alle Spuren offen */

    /* Bits BAHNSPERRE_BIT_0040 .. BAHNSPERRE_BIT_1000 (Positionen 1-5)
     * direkt auf Bahn-Nr.-Bits 0-4 abbilden (40₈->Bit0 ... 1000₈->Bit4),
     * s. Hardware.md, Original-Tabelle 1. */
    zusatzschalter_bits = (bahnsperre_schalter >> 1) & 0x1Fu;

    /* Gesperrt <=> Bahn-Nr. ist Bit-Teilmenge der eingeschalteten
     * Zusatzschalter (leere Teilmenge, bahn=0, ist immer enthalten). */
    return ((bahn & ~zusatzschalter_bits) == 0)
               ? BAHNSPERRE_GESPERRT : BAHNSPERRE_OFFEN;
}


/* ---- Schalterdatei neben der Trommel (Entwurf 86/87) ------------------------------------------------------------ */

static FILE *oeffne_utf8(const char *pfad, const char *modus)
{
#ifdef _WIN32
    wchar_t wp[1024], wm[8];
    unsigned int i;
    if (MultiByteToWideChar(CP_UTF8, 0, pfad, -1, wp, 1024) == 0) { errno = EINVAL; return NULL; }
    for (i = 0; modus[i] && i < 7; i++) wm[i] = (wchar_t)modus[i];
    wm[i] = 0;
    return _wfopen(wp, wm);
#else
    return fopen(pfad, modus);
#endif
}

int bahnsperre_dateiname(const char *trommelpfad, char *ziel, unsigned int groesse)
{
    size_t n = strlen(trommelpfad), basis = n, i;
    /* Endung nur im letzten Pfadteil abschneiden */
    for (i = n; i > 0; i--) {
        char z = trommelpfad[i - 1];
        if (z == '/' || z == '\\') break;
        if (z == '.') { if (i - 1 > 0 && trommelpfad[i - 2] != '/' && trommelpfad[i - 2] != '\\') basis = i - 1; break; }
    }
    if (basis + 6 > groesse) return -1;      /* ".basp" + Endnull */
    memcpy(ziel, trommelpfad, basis);
    memcpy(ziel + basis, ".basp", 6);
    return 0;
}

static void melde(char *meldung, unsigned int groesse, const char *fmt, const char *a, const char *b)
{
    if (meldung && groesse) snprintf(meldung, groesse, fmt, a, b);
}

static int stellung_gueltig(const char *s)
{
    int i;
    for (i = 0; i < 6; i++) if (s[i] != '0' && s[i] != '1') return 0;
    return 1;
}

static void stellung_uebernehmen(const char *s)
{
    bahnsperre_setzen(s[0] == '1', s[1] == '1', s[2] == '1', s[3] == '1', s[4] == '1', s[5] == '1');
}

int bahnsperre_hochfahren(const char *trommelpfad, const char *basp, char *stellung, char *meldung, unsigned int meldung_groesse)
{
    char datei[1100];
    char text[8];
    FILE *f;

    if (meldung && meldung_groesse) meldung[0] = 0;
    if (!trommelpfad || bahnsperre_dateiname(trommelpfad, datei, sizeof datei) != 0) {
        melde(meldung, meldung_groesse, "Bahnsperre: Pfad der Schalterdatei zu lang oder fehlt%s%s", "", "");
        return -1;
    }

    if (basp) {                                                   /* 1. --BASP angegeben: uebernehmen und schreiben */
        if (strlen(basp) != 6 || !stellung_gueltig(basp)) {
            melde(meldung, meldung_groesse, "Bahnsperre: ungueltige Stellung '%s' (erwartet: genau sechs Ziffern 0/1)%s", basp, "");
            return -1;
        }
        memcpy(text, basp, 6); text[6] = 0;
        f = oeffne_utf8(datei, "wb");
        if (!f || fwrite(text, 1, 6, f) != 6 || fputc('\n', f) == EOF) {
            if (f) fclose(f);
            melde(meldung, meldung_groesse, "Bahnsperre: Schalterdatei nicht zu schreiben: %s (%s)", datei, strerror(errno));
            return -1;
        }
        if (fclose(f) != 0) {
            melde(meldung, meldung_groesse, "Bahnsperre: Schalterdatei nicht zu schreiben: %s (%s)", datei, strerror(errno));
            return -1;
        }
        stellung_uebernehmen(text);
        if (stellung) memcpy(stellung, text, 7);
        return 0;
    }

    f = oeffne_utf8(datei, "rb");                                 /* 2. --BASP fehlt: aus der Datei */
    if (!f) {
        if (errno != ENOENT) {
            melde(meldung, meldung_groesse, "Bahnsperre: Schalterdatei nicht lesbar: %s (%s)", datei, strerror(errno));
            return -1;
        }
        memcpy(text, "000000", 7);                                /* 3. Datei fehlt: mit 000000 anlegen */
        f = oeffne_utf8(datei, "wb");
        if (!f || fwrite(text, 1, 6, f) != 6 || fputc('\n', f) == EOF) {
            if (f) fclose(f);
            melde(meldung, meldung_groesse, "Bahnsperre: Schalterdatei nicht anzulegen: %s (%s)", datei, strerror(errno));
            return -1;
        }
        if (fclose(f) != 0) {
            melde(meldung, meldung_groesse, "Bahnsperre: Schalterdatei nicht anzulegen: %s (%s)", datei, strerror(errno));
            return -1;
        }
        stellung_uebernehmen(text);
        if (stellung) memcpy(stellung, text, 7);
        return 0;
    }
    {
        char puffer[16];
        size_t n = fread(puffer, 1, sizeof puffer, f);
        int lesefehler = ferror(f);
        fclose(f);
        if (lesefehler) {
            melde(meldung, meldung_groesse, "Bahnsperre: Schalterdatei nicht lesbar: %s (%s)", datei, strerror(errno));
            return -1;
        }
        if (n != 7 || puffer[6] != '\n' || !stellung_gueltig(puffer)) {
            melde(meldung, meldung_groesse,
                  "Bahnsperre: Schalterdatei formal fehlerhaft (erwartet eine Zeile mit sechs Zeichen 0/1 und LF): %s%s", datei, "");
            return -1;
        }
        memcpy(text, puffer, 6); text[6] = 0;
        stellung_uebernehmen(text);
        if (stellung) memcpy(stellung, text, 7);
    }
    return 0;
}
