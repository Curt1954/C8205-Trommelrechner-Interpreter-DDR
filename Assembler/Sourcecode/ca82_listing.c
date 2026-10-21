// ca82_listing.c - Formatierte Ausgabe des Listings (STDOUT und .dmp)
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"


void printFormattedAsmListing(lineElements lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p) {
    int maxWidth1 = 0, maxWidth2 = 0, maxWidth3 = 0;


    // Berechnung der maximalen Spaltenbreite für sp1, sp2, sp3
    for (int i = 0; i < lineCountAsmAufgeloest_p; i++) {
        char *trimmed = lineAsmAufgeloest_p[i].sp1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Entfernt Leerzeichen & Tabs

        // **Überspringe Kommentarzeilen**
        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*' || *trimmed == '&' || *trimmed == '\0') {
            continue; // Springt zur nächsten Zeile
        }

        // Berechnung der maximalen Breite
        int len1 = strlen(trimmed);
        if (len1 > maxWidth1) maxWidth1 = len1;

        int len2 = strlen(lineAsmAufgeloest_p[i].sp2);
        int len3 = strlen(lineAsmAufgeloest_p[i].sp3);

        if (len2 > maxWidth2) maxWidth2 = len2;
        if (len3 > maxWidth3) maxWidth3 = len3;
    }

    if (maxWidth1 < 16) maxWidth1 = 16;
    if (maxWidth2 < 10) maxWidth2 = 10;
    if (maxWidth3 < 20) maxWidth3 = 20;

    char formatString[256];
    snprintf(formatString, sizeof(formatString), "%%-%ds %%-%ds %%-%ds %%s\n", maxWidth1, maxWidth2, maxWidth3);

    for (int i = 0; i < lineCountAsmAufgeloest_p; i++) {
        char *trimmed = lineAsmAufgeloest_p[i].sp1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen

        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*' || *trimmed == '&' ) {
            // Direkte Ausgabe ohne feste Spaltenbreite
            printf("%s %s %s %s\n",
                lineAsmAufgeloest_p[i].sp1,
                lineAsmAufgeloest_p[i].sp2,
                lineAsmAufgeloest_p[i].sp3,
                lineAsmAufgeloest_p[i].sp4);
        } else {
            // Formatierte Ausgabe mit dynamischer Spaltenbreite
            printf(formatString,
                lineAsmAufgeloest_p[i].sp1,
                lineAsmAufgeloest_p[i].sp2,
                lineAsmAufgeloest_p[i].sp3,
                lineAsmAufgeloest_p[i].sp4);
        }
    }
}


// Entfernt ANSI-Farbcodes (ESC [ <Ziffern und ;> m) aus text (in place).
static void entferneFarbcodes(char *text) {
    char *r = text, *w = text;
    while (*r) {
        if (*r == '\033' && r[1] == '[') {
            const char *q = r + 2;
            while ((*q >= '0' && *q <= '9') || *q == ';') q++;
            if (*q == 'm') { r = (char *)q + 1; continue; }
        }
        *w++ = *r++;
    }
    *w = '\0';
}

// Ersetzt in der Adress-/Kennzeichenspalte des Listings (sp0, z. B. "0007: 01 2006 241" oder "      01 2006 241")
// das Kennzeichen 01 durch den Wert des Pragmas LEITADRESSE (Standard 01 = keine Aenderung).
// Die Ersetzung erfolgt an Ort und Stelle (zwei Zeichen durch zwei Zeichen), die Spaltenbreite bleibt gleich.
static void ersetzeKennzeichen01(char *sp0) {
    if (leitadresseKennzeichen == 1) return;
    char *p = sp0;
    while (*p == ' ') p++;
    char *q = p;
    while (*q >= '0' && *q <= '7') q++;
    if (q > p && *q == ':') {          // Adressspalte "<oktalzahl>:" ueberspringen
        p = q + 1;
        while (*p == ' ') p++;
    }
    if (p[0] == '0' && p[1] == '1' && (p[2] == ' ' || p[2] == '\0')) {
        p[0] = (char)('0' + leitadresseKennzeichen / 10);
        p[1] = (char)('0' + leitadresseKennzeichen % 10);
    }
}

// Schreibt das formatierte Listing nach f. Mit ohneFarben = 1 (Datei .dmp) werden die ANSI-Farbcodes
// vorher aus den Feldern entfernt und die Spaltenbreiten aus dem Text ohne Farbcodes berechnet;
// frueher standen in der .dmp bei Fehlerlaeufen Escape-Sequenzen (z. B. um die Marke EE).
static void schreibeListingX(FILE *f, int ohneFarben, lineElementsX lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p) {
    char b0[sizeof(lineAsmAufgeloest_p[0].sp0)];
    char b1[sizeof(lineAsmAufgeloest_p[0].sp1)];
    char b2[sizeof(lineAsmAufgeloest_p[0].sp2)];
    char b3[sizeof(lineAsmAufgeloest_p[0].sp3)];
    char b4[sizeof(lineAsmAufgeloest_p[0].sp4)];
    const char *s0, *s1, *s2, *s3, *s4;

#define HOLE_FELDER(idx) \
    do { \
        s0 = lineAsmAufgeloest_p[idx].sp0; s1 = lineAsmAufgeloest_p[idx].sp1; s2 = lineAsmAufgeloest_p[idx].sp2; \
        s3 = lineAsmAufgeloest_p[idx].sp3; s4 = lineAsmAufgeloest_p[idx].sp4; \
        if (ohneFarben) { \
            snprintf(b0, sizeof(b0), "%s", s0); entferneFarbcodes(b0); s0 = b0; \
            snprintf(b1, sizeof(b1), "%s", s1); entferneFarbcodes(b1); s1 = b1; \
            snprintf(b2, sizeof(b2), "%s", s2); entferneFarbcodes(b2); s2 = b2; \
            snprintf(b3, sizeof(b3), "%s", s3); entferneFarbcodes(b3); s3 = b3; \
            snprintf(b4, sizeof(b4), "%s", s4); entferneFarbcodes(b4); s4 = b4; \
        } \
        if (leitadresseKennzeichen != 1) { \
            if (s0 != b0) snprintf(b0, sizeof(b0), "%s", s0); \
            ersetzeKennzeichen01(b0); s0 = b0; \
        } \
    } while (0)

    int maxWidth1 = 0, maxWidth2 = 0, maxWidth3 = 0;

    // **1. Schritt: Maximale Breiten für sp1, sp2, sp3 berechnen**
    for (int i = 0; i < lineCountAsmAufgeloest_p; i++) {
        HOLE_FELDER(i);
        // Prüfen, ob sp1 ignoriert werden soll
        const char *trimmed = s1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen

        if (*trimmed != ';' && *trimmed != '#' && *trimmed != '$'  && *trimmed != '*' && *trimmed != '&') { // Zeilen mit `$` ausschließen
            int len1 = strlen(s1);
            if (len1 > maxWidth1) maxWidth1 = len1;
        }

        int len2 = strlen(s2);
        int len3 = strlen(s3);

        if (len2 > maxWidth2) maxWidth2 = len2;
        if (len3 > maxWidth3) maxWidth3 = len3;
    }

    char formatString[256];
    snprintf(formatString, sizeof(formatString), "%%-20s %%-%ds %%-%ds %%-%ds %%s\n", maxWidth1, maxWidth2, maxWidth3);

    for (int i = 0; i < lineCountAsmAufgeloest_p; i++) {
        HOLE_FELDER(i);
        const char *trimmed = s1;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen

        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*' || *trimmed == '&') {
            // Direkte Ausgabe ohne feste Spaltenbreite
            fprintf(f, "%-20s %s %s %s %s\n", s0, s1, s2, s3, s4);
        } else {
            // Formatierte Ausgabe mit dynamischer Spaltenbreite
            fprintf(f, formatString, s0, s1, s2, s3, s4);
        }
    }
#undef HOLE_FELDER
}

void printFormattedAsmListingX(lineElementsX lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p, FILE *dmpFile) {
    schreibeListingX(stdout, 0, lineAsmAufgeloest_p, lineCountAsmAufgeloest_p);       // Bildschirm: mit Farben
    if (dmpFile) {
        schreibeListingX(dmpFile, 1, lineAsmAufgeloest_p, lineCountAsmAufgeloest_p);  // .dmp: ohne Farbcodes
    }
}
