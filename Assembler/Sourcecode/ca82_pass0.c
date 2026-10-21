// ca82_pass0.c - Pass 0: Aufloesung der Makros
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
//
// Ablauf von pass0():
//   1. pass0PruefeMakrodefinitionen: Makrodatei laden, Makros im Quelltext sammeln, jede Definition pruefen
//      (Name vorhanden, MEND vorhanden); bei Fehlern Abbruch mit Rueckgabecode 16.
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
            PRINT_FEHLER("Fehlerndes MEND in MACRO %s .",old_mname);
            macro_errors++;
            in_macro = 0;
        }
    }
    return macro_errors;
}

// Laedt die Makrodatei, sammelt die Makros aus dem Quelltext und bricht bei fehlerhaften Definitionen ab.
static void pass0PruefeMakrodefinitionen(void) {
    erzeugeMacroArray(makroDateiName());

    int quelltext_errors = sammleQuelltextMakros();   // Makrodefinitionen im Quelltext
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
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest++].sp1 , "");
        return;
    }

    char operationscode[128] = "";
    char aktuelleParameterZeile[1024] = "";
    char label[256];

    STRKOPIE(label,linesAsm[asmZeilenNr].sp1);
    STRKOPIE(aktuelleParameterZeile, linesAsm[asmZeilenNr].sp3);
    STRKOPIE(operationscode,linesAsm[asmZeilenNr].sp2);

    int lineCount=0;
    lineElements *ergebnis = loeseMacroAuf(macros, &macroCount, operationscode, aktuelleParameterZeile, &lineCount, label );

    if (ergebnis != NULL) {

        if (lineCountAsmAufgeloest + lineCount + 1 >= ZEILEN_GRENZE) {
            meldeZuVieleZeilen(linesAsm[asmZeilenNr].srcLine);
            exit(RC_FEHLER);
        }
        seed_value++;  //Anzahl der aufgelösten Macros
        if ( seed_value > seed_max ) {
            PRINT_FEHLER("Mehr als %i Macros können nicht verarbeitet werden.",seed_value);
            exit(RC_FEHLER);
        }
        // Statt Macroaufruf den aufgelösten Macro übernehmen
        char macroAufrufLine[1024];
        snprintf(macroAufrufLine, sizeof(macroAufrufLine), "%-20.240s %-20.240s %-20.240s %-20.240s", linesAsm[asmZeilenNr].sp1,
                        linesAsm[asmZeilenNr].sp2, linesAsm[asmZeilenNr].sp3, linesAsm[asmZeilenNr].sp4);

        lineAsmAufgeloest[lineCountAsmAufgeloest].srcLine = linesAsm[asmZeilenNr].srcLine;
        STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, ";+++ ");
        STRANHANG(lineAsmAufgeloest[lineCountAsmAufgeloest++].sp1, macroAufrufLine);

        // ergebnis enthält den aufgelösten macro mit lineCount Zeilen
        macroSprung1Aufloesen(&ergebnis, &lineCount, operationscode);

        for (int i = 0; i < lineCount; i++) {
            memcpy(&lineAsmAufgeloest[lineCountAsmAufgeloest], &ergebnis[i], sizeof(lineElements));
            lineAsmAufgeloest[lineCountAsmAufgeloest].srcLine = linesAsm[asmZeilenNr].srcLine;   // Ort = Makroaufruf
            if (xrefAktiv) xrefMerkeMakroOperand(linesAsm[asmZeilenNr].srcLine, ergebnis[i].sp3);
            lineCountAsmAufgeloest++;
        }

    } else {
        // Assemblerzeile direkt übernehmen
        lineAsmAufgeloest[lineCountAsmAufgeloest++] = linesAsm[asmZeilenNr];
    }

    free(ergebnis);
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
        strncpy(trimmedSp2, lineAsmAufgeloest[j].sp1, MACRO_PARAMETER_LAENGE - 1);
        trimmedSp2[MACRO_PARAMETER_LAENGE - 1] = '\0';
        if (  ((trimmedSp2[0] == ';') || (trimmedSp2[0] == '#') || (trimmedSp2[0] == '$')  || (trimmedSp2[0] == '&') || (strstr(trimmedSp2, "***") != NULL) ) ) {
            continue;
        }
        strncpy(trimmedSp2, lineAsmAufgeloest[j].sp2, MACRO_PARAMETER_LAENGE - 1);
        trimmedSp2[MACRO_PARAMETER_LAENGE - 1] = '\0';
        trimWhitespace(trimmedSp2);  // Entferne unnötige Leerzeichen

        // Falls `trimmedSp2` leer ist oder mit einer Ziffer beginnt, überspringe die Zeile
        if (strlen(trimmedSp2) == 0 || isdigit(trimmedSp2[0])) {
            continue;
        }

        for (int i = 0; i < macroCount; i++) {
            // Bereinige `macroName`, falls es mit `:` endet
            char macroNameCleaned[MACRO_PARAMETER_LAENGE];
            strncpy(macroNameCleaned, macros[i].macroName, MACRO_PARAMETER_LAENGE - 1);
            macroNameCleaned[MACRO_PARAMETER_LAENGE - 1] = '\0';

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

    pass0PruefeMakrodefinitionen();

    // Durchlaeufe, bis kein Makroaufruf mehr uebrig ist
    for (;;) {
        pass0EinDurchlauf();
        if (!pass0EnthaeltMakroaufruf()) break;
        // Ergebnis ist Eingabe des naechsten Durchlaufs
        memcpy(linesAsm, lineAsmAufgeloest, sizeof(lineElements) * PROGRAMMZEILEN);
        lineCountAsm = lineCountAsmAufgeloest;
        lineCountAsmAufgeloest = 0;
    }

    if ( is_error0 != 0) {
       printFormattedAsmListing(lineAsmAufgeloest, lineCountAsmAufgeloest);
       PFend();
       meldeListingFehlerAufStderr(lineAsmAufgeloest, lineCountAsmAufgeloest);
       PRINT_WARNUNG("%s","Compilierung endete mit FEHLERn.\n");
       exit(RC_FEHLER);
    }
}
