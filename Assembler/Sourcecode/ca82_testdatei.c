// ca82_testdatei.c - Erzeugung der .test-Datei
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"


// ----------------------

// Erzeugt die .test-Datei direkt aus den strukturierten Listing-Zeilen
// (denselben Daten, aus denen auch die .dmp-Datei erzeugt wird - siehe
// printFormattedAsmListingX). Jede Zeile hat sp0 = "<adresse>: <K1> [<K2>] [<Wert>]",
// sp1 = Label, sp2 = Mnemonic, sp3 = Operand, sp4 = Kommentar.
// Es werden nur Zeilen mit K1 (Spalte 2) == "00" oder "01" berücksichtigt.
// Aus sp0 (Spalten 1,3,4) werden alle Ziffern eingesammelt und linksbündig
// mit Nullen auf 11 Stellen aufgefüllt. Alles ab Spalte 6 (Mnemonic, Operand,
// Kommentar) wird - falls vorhanden - als "# ..."-Kommentar angehängt.
extern char inputFileName[1024];   // wird weiter unten definiert

// Testmarken, die im Quelltext als Kommentarzeile (";" + optionaler Leerraum + Marke ...) stehen duerfen und
// in den Abschnitt "Trommeldatei:" der .test-Datei gehoeren. Marken mit '-' am Ende (#DOK-, #SPEI-, #SPUR-)
// werden als Praefix erkannt (#DOK-0001 ...), alle anderen muessen als ganzes Wort stehen (Ende, Leerraum
// oder '=' dahinter). Bewusst NICHT enthalten: --pruefe-... (gehoert in den Abschnitt "Pruefungen:"),
// #INTERRUPT (muss ZWISCHEN zwei Befehlszeilen stehen, nicht im Vorspann) und das Pragma ";#; LEITADRESSE ...".
// #STARTE ersetzt die Tastenfolge: Ist es im Vorspann, erzeugt der Assembler keinen Abschnitt "Tastenfolge:".
static int istTestVorspannText(const char *t) {
    static const char *marken[] = {
        "#DOK-", "#SPEI-", "#SPUR-", "#PROT", "#AC", "#BZ", "#STARTE", "#TROMMEL",
        "--leser1", "--leser2", "--stanzer1", "--sw-ausgabe", "--k0"
    };
    for (size_t m = 0; m < sizeof(marken) / sizeof(marken[0]); m++) {
        size_t n = strlen(marken[m]);
        if (strncmp(t, marken[m], n) != 0) continue;
        if (marken[m][n - 1] == '-') return 1;
        char c = t[n];
        if (c == '\0' || c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '=') return 1;
    }
    return 0;
}

void erzeugeTestDatei(lineElementsX lineAsmAufgeloest_p[], int lineCountAsmAufgeloest_p, const char *testFileName) {
    FILE *testFile = fopen(testFileName, "w");
    if (!testFile) {
        PRINT_FEHLER("Testdatei %s konnte nicht angelegt werden.", testFileName);
        return;
    }

    // Kopfzeilen (s. C8205-Interpreter-Durchfuehrung_eines_Tests.md): Abschnitt "Trommeldatei:".
    // Stehen im Quelltext Vorspannzeilen (Kommentarzeilen mit #DOK-, #SPEI-, #PROT, --sw-ausgabe ...),
    // werden genau diese ohne fuehrendes ';' uebernommen. Nur wenn der Quelltext keine einzige solche
    // Zeile enthaelt, wird der Standard-Vorspann (Platzhalter) erzeugt.
    fprintf(testFile, "Trommeldatei:\n");
    int vorspannZeilen = 0;
    int startezeile = 0;       // #STARTE im Vorspann ersetzt die Tastenfolge
    FILE *quelle = fopen(inputFileName, "r");
    if (quelle) {
        char zeile[2048];
        while (fgets(zeile, sizeof(zeile), quelle)) {
            if (strchr(zeile, '\n') == NULL && !feof(quelle)) {
                // Zeile laenger als der Puffer: Rest ueberlesen, die Zeile ist keine Vorspannzeile
                int c;
                while ((c = fgetc(quelle)) != EOF && c != '\n') { }
                continue;
            }
            const char *p = zeile;
            while (*p == ' ' || *p == '\t') p++;
            if (*p != ';') continue;                 // nur Kommentarzeilen
            p++;
            while (*p == ' ' || *p == '\t') p++;
            if (!istTestVorspannText(p)) continue;
            size_t len = strlen(p);
            while (len > 0 && (p[len-1] == '\n' || p[len-1] == '\r' || p[len-1] == ' ' || p[len-1] == '\t')) len--;
            fprintf(testFile, "%.*s\n", (int)len, p);
            vorspannZeilen++;
            if (strncmp(p, "#STARTE", 7) == 0) startezeile = 1;
        }
        fclose(quelle);
    }
    if (vorspannZeilen == 0) {
        fprintf(testFile, "#DOK-0001\n");
        fprintf(testFile, "#SPEI-0001 0000-0000\n");
        fprintf(testFile, "#PROT STUFE=2\n");
    }

    for (int i = 0; i < lineCountAsmAufgeloest_p; i++) {
        const char *sp0 = lineAsmAufgeloest_p[i].sp0;

        char adresse[64] = "";
        char k1[16] = "";
        int pos = 0;
        int adrZeile = lineAsmAufgeloest_p[i].adrValid;

        if (adrZeile) {
            // dt/dto/dtm-Zeile: Adresse steht nicht in sp0, sondern in .adr
            snprintf(adresse, sizeof(adresse), "%04o", lineAsmAufgeloest_p[i].adr);
            if (sscanf(sp0, "%15s%n", k1, &pos) != 1) {
                continue;
            }
        } else if (sscanf(sp0, "%63[^:]:%15s%n", adresse, k1, &pos) != 2) {
            continue; // keine "<adresse>: <K1> ..."-Zeile (z.B. equ-Zeile, Fehlerzeile ohne Adresse)
        }

        // Nullwort: pass3 schreibt "dw 0" als "<adr>: 0" (nur "0", ohne K1/K2/Wert, s. .dmp/.obj).
        // Diese Zeile gehoert ebenfalls in die .test-Datei (als Wort 00000000000).
        int nullwort = (strcmp(k1, "0") == 0);

        if (!nullwort && strcmp(k1, "00") != 0 && strcmp(k1, "01") != 0) {
            continue; // nur Spalte 2 == 00 oder 01 (oder Nullwort "0") verwenden
        }

        // Verbleibende Ziffern aus sp0 (Spalten 3/4) einsammeln - sp0 enthält
        // ausschließlich Adresse/K1/K2/Wert, also keine Gefahr, versehentlich
        // Ziffern aus einem Label wie "l0001" mit aufzunehmen.
        char ziffern[64] = "";
        int zIdx = 0;
        for (const char *p = sp0 + pos; *p != '\0'; p++) {
            if (isdigit((unsigned char)*p)) {
                if (zIdx < (int)sizeof(ziffern) - 1) {
                    ziffern[zIdx++] = *p;
                }
            }
        }
        ziffern[zIdx] = '\0';

        if (nullwort && zIdx == 0) {
            ziffern[0] = '0';
            ziffern[1] = '\0';
            zIdx = 1;
        }

        if (zIdx == 0 || zIdx > 11) {
            continue; // keine verwertbaren Ziffern bzw. unerwartet lang -> überspringen
        }

        fprintf(testFile, "%s: ", adresse);
        for (int pad = 0; pad < 11 - zIdx; pad++) {
            fputc('0', testFile);
        }
        fprintf(testFile, "%s", ziffern);

        // Ab "Spalte 6" (Mnemonic, Operand, Kommentar) - und, sofern vorhanden,
        // auch das Label - als lesbaren Kommentar anhängen.
        char kommentar_p[600] = "";
        const char *teile[4] = { lineAsmAufgeloest_p[i].sp1, lineAsmAufgeloest_p[i].sp2,
                                  lineAsmAufgeloest_p[i].sp3, lineAsmAufgeloest_p[i].sp4 };
        for (int t = 0; t < 4; t++) {
            const char *s = teile[t];
            while (*s == ' ' || *s == '\t') s++;
            size_t len = strlen(s);
            while (len > 0 && (s[len-1] == ' ' || s[len-1] == '\t' || s[len-1] == '\n' || s[len-1] == '\r')) len--;
            if (len == 0) continue;
            if (kommentar_p[0] != '\0') strncat(kommentar_p, " ", sizeof(kommentar_p) - strlen(kommentar_p) - 1);
            strncat(kommentar_p, s, (len < sizeof(kommentar_p) - strlen(kommentar_p) - 1) ? len : sizeof(kommentar_p) - strlen(kommentar_p) - 1);
        }
        if (kommentar_p[0] != '\0' && strcmp(kommentar_p, ";") != 0) {
            fprintf(testFile, " # %s", kommentar_p);
        }
        fprintf(testFile, "\n");
    }

    // Fusszeilen (Platzhalter fuer die Tastenfolge). Mit #STARTE im Vorspann entfaellt der Abschnitt:
    // #STARTE ersetzt die Tastenfolge vollstaendig, zusaetzliche Tasten waeren ein Formfehler.
    if (!startezeile) {
        fprintf(testFile, "Tastenfolge:\n");
        fprintf(testFile, "H G R\n");
    }

    fclose(testFile);
}
