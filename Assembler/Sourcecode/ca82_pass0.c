// ca82_pass0.c - Pass 0: Aufloesung der Makros
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
//
// Ablauf von pass0():
//   1. pass0PruefeMakrodefinitionen: Makrodatei laden, Makros im Quelltext sammeln, jede Definition pruefen
//      (Name vorhanden, MEND vorhanden); bei Fehlern Abbruch mit Rueckgabecode 16.
//   1a. Hat der Quelltext Zeilen mit $ ($IF, $REPT, $SET ...), wertet quelltextDirektivenAuswerten sie vorab aus (Doku 4.1).
//   2. Wiederholt: pass0EinDurchlauf ersetzt alle Makroaufrufe durch den Makrotext. Enthaelt das Ergebnis
//      wieder Makroaufrufe (verschachtelte Makros), beginnt pass0 den naechsten Durchlauf mit dem Ergebnis.
//   3. Bei Fehlern in der Aufloesung: Listing, Fehlerzeilen auf STDERR, Abbruch.
#include "ca82_intern.h"
#include "ca82_berichte.h"

// ---------------------------------------------------

// Prueft Makrodefinitionen auf fehlendes MEND/MACROENDE und fehlenden Namen.
// Rueckgabe: Anzahl der Fehler (Zaehler wird mit der Anzahl der Fehler aus dem Quelltext vorbelegt).
static int pass0PruefeMakroEnden(int fehlerVorher) {
    int in_macro = 0;
    int macro_errors = fehlerVorher;
    char old_mname[256]="";

    for (int i = 0; i < macroCount; i++) {
        for (int j = 0; j < macros[i].macroLineCount; j++) {
            // Prüfe, ob eine neue MACRO-Deklaration beginnt
            if (  (strcmp(old_mname,"" ) == 0 ) || strcmp(macros[i].macroName,old_mname ) != 0 ) {
                STRKOPIE(old_mname, macros[i].macroName);
                // Falls ein vorheriges MACRO nicht geschlossen wurde, FEHLER MELDEN!
                if (in_macro) {
                    PRINT_FEHLER("%s", "MACRO ohne MEND oder MACROENDE.");
                    macro_errors++;
                }

                // Prüfe, ob das MACRO in `.sp1` einen Namen hat
                if (strlen(macros[i].macroName) == 0) {
                    PRINT_FEHLER("%s", "MACRO ohne Namen.");
                    macro_errors++;
                }

                in_macro = 1; // Ein neues Makro wurde geöffnet
            }

            // Prüfe auf gültiges Makro-Ende
            if (in_macro &&
                (strcmp(macros[i].macroParsedLines[j].sp2, "MEND") == 0 ||
                strcmp(macros[i].macroParsedLines[j].sp2, "MACROENDE") == 0 ||
                strcmp(macros[i].macroParsedLines[j].sp2, "macroende") == 0)) {
                in_macro = 0; // Makro korrekt geschlossen
            }

        }

        // Falls das letzte Makro nicht geschlossen wurde, FEHLER MELDEN!
        if (in_macro) {
            PRINT_FEHLER("Fehlendes MEND in MACRO %s .",old_mname);
            macro_errors++;
            in_macro = 0;
        }
    }
    return macro_errors;
}

// Laedt die Makrodatei, sammelt die Makros aus dem Quelltext und bricht bei fehlerhaften Definitionen ab.
static void pass0PruefeMakrodefinitionen(void) {
    erzeugeMacroArray(makroDateiName());              // 1. c82ass.makros (niedrigste Rangfolge)
    int quelltext_errors = ladeMakroLokalSchalter();  // 1a. ;#MAKROLOKAL=1 (Makro-Variablen standardmaessig lokal, ab 1.02-001)
    quelltext_errors += ladeMakroUmordnenSchalter(); // 1b. ;#MAKROUMORDNEN=YES/NO (Makro-Umordnung im Optimierer, ab 1.03-007)
    quelltext_errors += ladeObjBefehle();            // 1c. ;#PRECOMMAND= und ;#POSTCOMMAND= (Befehlsworte im .obj, ab 1.03-009)
    quelltext_errors += ladeProjektMakrodateien();    // 2. ;#MACRODATEI1= bis 9= (ersetzen gleichnamige Makros aus c82ass.makros)
    quelltext_errors += makroSpecFehler();            // 2a. Fehler in $SPEC-Zeilen der Makrodateien (ab 1.03-002, Doku 4.32)
    quelltext_errors += sammleQuelltextMakros();      // 3. Makrodefinitionen im Quelltext (hoechste Rangfolge)
    int macro_errors = pass0PruefeMakroEnden(quelltext_errors);

    // Fehler-Ausgabe
    if (macro_errors > 0) {
        is_error = 1;
        PRINT_FEHLER("%d fehlerhafte Makrodefinition(en) (Makrodatei oder Quelltext).\n", macro_errors);
        if (macro_errors > quelltext_errors) {
            printAllMacros();    // Auflistung nur, wenn die Makrodatei Fehler enthält (wie bisher)
        }
        exit(RC_FEHLER);
    }
}

// ---------------------------------------------------

// Kommentarzeile ";+++ <Aufruf>" (mit --makros zusaetzlich die Herkunft in sp4) fuer einen Makroaufruf.
// Eigene Funktion, damit die grossen Puffer nicht im Stapelrahmen der (rekursiven) Aufloesung liegen.
static void __attribute__((noinline)) pass0AufrufKommentar(const lineElements *z, const char *operationscode, int srcLine, lineElements *ziel) {
    char macroAufrufLine[1024];
    snprintf(macroAufrufLine, sizeof(macroAufrufLine), "%-20.240s %-20.240s %-20.240s %-20.240s", z->sp1, z->sp2, z->sp3, z->sp4);
    ziel->srcLine = srcLine;
    STRKOPIE(ziel->sp1, ";+++ ");
    STRANHANG(ziel->sp1, macroAufrufLine);
    STRKOPIE(ziel->sp2, "");
    STRKOPIE(ziel->sp3, "");
    STRKOPIE(ziel->sp4, "");
    if (makrolisteAktiv) {
        // --makros: Herkunft je Aufruf in sp4 (sonst bleibt die Zeile unveraendert); Pass 3 gibt sie als Kommentarzeile im Listing aus
        char herkunft[1200];
        if (makroHerkunftFuerAufruf(operationscode, herkunft, sizeof(herkunft))) {
            char text[1500];
            snprintf(text, sizeof(text), ";+++ Makro %s aus %s, aufgerufen in Quelltextzeile %s", operationscode, herkunft, qOrt(srcLine));
            STRKOPIE(ziel->sp4, text);
        }
    }
}

// Tiefe der Aufloesung (0 = Aufruf im Quelltext) und Quelltextzeile des aeussersten Aufrufs: alle Zeilen einer Expansion,
// auch die der verschachtelten Aufrufe, tragen den Ort des aeussersten Aufrufs.
static int pass0Tiefe = 0;
int pass0AeussereZeile = 0;   // auch von ca82_makros.c benutzt ($NOTE, $DUMP)

// Loest die Zeile z auf, wenn sie ein Makroaufruf ist: Ergebnis (malloc, *anzahl Zeilen) ist die Kommentarzeile ";+++ <Aufruf>"
// gefolgt vom aufgeloesten Makrotext; verschachtelte Aufrufe sind dabei schon an Ort und Stelle aufgeloest (loeseMacroAuf ruft
// diese Funktion fuer jede Zeile des Makrorumpfs). Rueckgabe NULL, wenn z kein Makroaufruf ist.
static lineElements *pass0AufrufAufloesen(const lineElements *z, int *anzahl) {
    *anzahl = 0;
    if ( beginntMitSemikolon(z->sp1) == 1 ) return NULL;
    if (z->sp1[0] == '\0' && z->sp2[0] == '\0' && z->sp3[0] == '\0' && z->sp4[0] == '\0') return NULL;

    char operationscode[128] = "";
    char aktuelleParameterZeile[1024] = "";
    char label[256];

    STRKOPIE(label, z->sp1);
    STRKOPIE(aktuelleParameterZeile, z->sp3);
    STRKOPIE(operationscode, z->sp2);

    if (pass0Tiefe == 0) pass0AeussereZeile = z->srcLine;
    pass0Tiefe++;
    int lineCount = 0;
    lineElements *ergebnis = loeseMacroAuf(macros, &macroCount, operationscode, aktuelleParameterZeile, &lineCount, label );
    pass0Tiefe--;
    if (ergebnis == NULL) return NULL;

    if (lineCountAsmAufgeloest + lineCount + 1 >= ZEILEN_GRENZE) {
        meldeZuVieleZeilen(pass0AeussereZeile);
        exit(RC_FEHLER);
    }
    lineElements *aus = (lineElements *)malloc(((size_t)lineCount + 1) * sizeof(lineElements));
    if (!aus) { fprintf(stderr, "Speicherzuweisung fehlgeschlagen!\n"); exit(RC_FEHLER); }
    pass0AufrufKommentar(z, operationscode, pass0AeussereZeile, &aus[0]);
    aus[0].makroInst = makroLetzteInstanz;   // die Kommentarzeile ";+++ Aufruf" gehoert zum Rumpf (0, wenn das Makro kein TYP=M mit $SPEC ist)
    for (int i = 0; i < lineCount; i++) {
        memcpy(&aus[i + 1], &ergebnis[i], sizeof(lineElements));
        aus[i + 1].srcLine = pass0AeussereZeile;   // Ort = Makroaufruf (der aeusserste)
    }
    free(ergebnis);
    *anzahl = lineCount + 1;
    return aus;
}

// Hook fuer die Auswertung der $-Direktiven im normalen Quelltext (quelltextDirektivenAuswerten, Doku 4.1): wie pass0AufrufAufloesen,
// merkt aber fuer die Querverweisliste (xref) die Operanden der aufgeloesten Zeilen, wie pass0ZeileAufloesen es fuer einen Aufruf im
// Quelltext tut (nur beim aeussersten Aufruf; verschachtelte Aufrufe tragen ihre Zeilen in den Aufruf des Quelltexts hinein).
static lineElements *pass0QuelltextAufruf(const lineElements *z, int *anzahl) {
    int aussen = (pass0Tiefe == 0);
    lineElements *aus = pass0AufrufAufloesen(z, anzahl);
    if (aus != NULL && aussen && xrefAktiv) {
        for (int i = 1; i < *anzahl; i++) xrefMerkeMakroOperand(z->srcLine, aus[i].sp3);
    }
    return aus;
}

// Uebernimmt die Quellzeile asmZeilenNr nach lineAsmAufgeloest: unveraendert oder, wenn sie ein Makroaufruf ist,
// als Kommentarzeile ";+++ <Aufruf>" gefolgt vom aufgeloesten Makrotext.
static void pass0ZeileAufloesen(int asmZeilenNr) {
    if (lineCountAsmAufgeloest >= ZEILEN_GRENZE) {
        meldeZuVieleZeilen(linesAsm[asmZeilenNr].srcLine);
        exit(RC_FEHLER);
    }
    if ( beginntMitSemikolon(linesAsm[asmZeilenNr].sp1) == 1 ) {
        lineAsmAufgeloest[lineCountAsmAufgeloest++] = linesAsm[asmZeilenNr];
        return;
    }
    if (linesAsm[asmZeilenNr].sp1[0] == '\0' && linesAsm[asmZeilenNr].sp2[0] == '\0' &&
        linesAsm[asmZeilenNr].sp3[0] == '\0' && linesAsm[asmZeilenNr].sp4[0] == '\0')
    {
        // Leerzeile: alle Felder leeren (frueher blieben sp2 bis sp4 aus einem frueheren Durchlauf stehen und erzeugten eine Geisterzeile)
        memset(&lineAsmAufgeloest[lineCountAsmAufgeloest], 0, sizeof(lineElements));
        lineAsmAufgeloest[lineCountAsmAufgeloest].srcLine = linesAsm[asmZeilenNr].srcLine;
        lineCountAsmAufgeloest++;
        return;
    }

    int anzahl = 0;
    lineElements *aus = pass0AufrufAufloesen(&linesAsm[asmZeilenNr], &anzahl);
    if (aus == NULL) {
        // Assemblerzeile direkt übernehmen
        lineAsmAufgeloest[lineCountAsmAufgeloest++] = linesAsm[asmZeilenNr];
        return;
    }
    if (lineCountAsmAufgeloest + anzahl + 1 >= ZEILEN_GRENZE) {
        meldeZuVieleZeilen(linesAsm[asmZeilenNr].srcLine);
        exit(RC_FEHLER);
    }
    // Statt Macroaufruf den aufgelösten Macro übernehmen (Kommentarzeile ;+++ <Aufruf>, dann der Makrotext)
    for (int i = 0; i < anzahl; i++) {
        memcpy(&lineAsmAufgeloest[lineCountAsmAufgeloest], &aus[i], sizeof(lineElements));
        if (xrefAktiv && i > 0) xrefMerkeMakroOperand(linesAsm[asmZeilenNr].srcLine, aus[i].sp3);
        lineCountAsmAufgeloest++;
    }
    free(aus);
}

// Ein Durchlauf ueber alle Quellzeilen (linesAsm -> lineAsmAufgeloest).
static void pass0EinDurchlauf(void) {
    for (int asmZeilenNr = 0; asmZeilenNr < lineCountAsm; asmZeilenNr++) {
        pass0ZeileAufloesen(asmZeilenNr);
    }
}

// ---------------------------------------------------

// Rueckgabe 1, wenn lineAsmAufgeloest noch einen Aufruf eines bekannten Makros enthaelt (verschachtelte Makros).
static int pass0EnthaeltMakroaufruf(void) {
    for (int j = 0; j < lineCountAsmAufgeloest; j++) {
        char trimmedSp2[MACRO_PARAMETER_LAENGE];
        STRKOPIE(trimmedSp2, lineAsmAufgeloest[j].sp1);
        if (  ((trimmedSp2[0] == ';') || (trimmedSp2[0] == '#') || (trimmedSp2[0] == '$')  || (trimmedSp2[0] == '&') || (strstr(trimmedSp2, "***") != NULL) ) ) {
            continue;
        }
        STRKOPIE(trimmedSp2, lineAsmAufgeloest[j].sp2);
        trimWhitespace(trimmedSp2);  // Entferne unnötige Leerzeichen

        // Falls `trimmedSp2` leer ist oder mit einer Ziffer beginnt, überspringe die Zeile
        if (strlen(trimmedSp2) == 0 || isdigit(trimmedSp2[0])) {
            continue;
        }

        for (int i = 0; i < macroCount; i++) {
            // Bereinige `macroName`, falls es mit `:` endet
            char macroNameCleaned[MACRO_PARAMETER_LAENGE];
            STRKOPIE(macroNameCleaned, macros[i].macroName);

            size_t len = strlen(macroNameCleaned);
            if (len > 0 && macroNameCleaned[len - 1] == ':') {
                macroNameCleaned[len - 1] = '\0';
            }

            if (strcmp(trimmedSp2, macroNameCleaned) == 0) {
                return 1;
            }
        }
    }
    return 0;
}

// ---------------------------------------------------

void pass0(void) {
    printf("Verarbeite '%s', Erzeuge Macroersetzungen\n\n", makroDateiName());
    is_error0 = 0;
    makroAufrufHook = pass0AufrufAufloesen;   // verschachtelte Makroaufrufe an Ort und Stelle aufloesen (Quelltextreihenfolge)

    pass0PruefeMakrodefinitionen();

    // $IF, $REPT, $SET usw. im normalen Quelltext (nur wenn eine Zeile mit $ beginnt; sonst bleibt linesAsm unveraendert, Doku 4.1)
    makroAufrufHook = pass0QuelltextAufruf;
    quelltextDirektivenAuswerten();
    makroAufrufHook = pass0AufrufAufloesen;

    // Durchlaeufe, bis kein Makroaufruf mehr uebrig ist
    for (;;) {
        pass0EinDurchlauf();
        if (!pass0EnthaeltMakroaufruf()) break;
        // Ergebnis ist Eingabe des naechsten Durchlaufs
        memcpy(linesAsm, lineAsmAufgeloest, sizeof(lineElements) * PROGRAMMZEILEN);
        lineCountAsm = lineCountAsmAufgeloest;
        lineCountAsmAufgeloest = 0;
    }

    opsymErsetzeNamen();   // markierte Namen (.LD) durch den Operationscode ersetzen; danach sehen alle Paesse nur den Code

    if ( is_error0 != 0) {
       printFormattedAsmListing(lineAsmAufgeloest, lineCountAsmAufgeloest);
       PFend();
       meldeListingFehlerAufStderr(lineAsmAufgeloest, lineCountAsmAufgeloest);
       PRINT_WARNUNG("%s","Compilierung endete mit FEHLERn.\n");
       exit(RC_FEHLER);
    }
}
