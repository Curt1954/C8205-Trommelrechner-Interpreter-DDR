// ca82_typen.h - Version 1.03-007 (siehe ca82_version.h)
#ifndef CA82_TYPEN_H
#define CA82_TYPEN_H

#include "ca82_standards.h"

extern char fehlertext[4096];

// Maximale Laenge einer Quelltextzeile in Bytes (interne Puffer: MACRO_PARAMETER_LAENGE = 256 inkl. Endezeichen)
#define MAX_QUELLZEILE 255

#define MACRO_PARAMETER_ANZAHL 32
#define MACRO_PARAMETER_LAENGE 256

#define PROGRAMMZEILEN 8192
// Quelltext einschliesslich Makroexpansion darf hoechstens ZEILEN_GRENZE Zeilen haben; der Rest der Felder
// bleibt fuer Literalzeilen und Fehlermarken der spaeteren Paesse frei.
#define ZEILEN_RESERVE 2048
#define ZEILEN_GRENZE (PROGRAMMZEILEN - ZEILEN_RESERVE)
#define MACRODEFINITIONEN 4096

typedef struct {
    char label[LABEL_SIZE];
    int lineNumber;
} MacroLabel;

typedef char elementType[MACRO_PARAMETER_LAENGE];
typedef struct {
    elementType sp1;
    elementType sp2;
    elementType sp3;
    elementType sp4;
    int srcLine;         // Zeilennummer in der .asm-Quelle (0 = unbekannt); fuer Fehlerorte auf STDERR
    char opname[16];     // ursprünglicher markierter Name (.LD) nach Ersetzung durch den Code in sp2 (leer: kein Name); nur fuer Listing, .dmp, .test
    int verlegt;         // Marke des Optimierers (ab c82ass 1.01-030, Doku 5.4): 0 = Zeile des Programmierers, 1 = equ100 * eines verschobenen Blocks (jetzt equ <Adresse>),
                         // 2 = ebenso fuer equ40 *, 3 = Literal, das der Optimierer bei FILL in die Luecke eines verschobenen Blocks gesetzt hat,
                         // 4 = begin-Zeile, deren Bloecke nicht unter 07600 passen (Pass 2 meldet den Fehler); nur in lineAsmAufgeloestTemp gueltig
    int makroInst;       // Herkunft aus einem Makro (ab c82ass 1.03-007, Doku 5.6): 0 = keine; sonst Nummer der Makroaufloesung (Aufrufnummer) des
                         // AEUSSERSTEN Aufrufs eines Makros mit $SPEC TYP=M (bei geschachtelten TYP=M-Aufrufen tragen auch die Zeilen des inneren
                         // Aufrufs die Nummer des aeusseren). Die Zeile gehoert dann zum Unterprogramm-Rumpf dieses Aufrufs; ein Block ist ein
                         // zusammenhaengender Lauf gleicher Nummer, den der Optimierer als Ganzes hinter end verlegen darf.
} lineElements;

typedef struct {
    char macroName[MACRO_PARAMETER_LAENGE];
    char macro[16];
    int macroParameterAnzahl;        // Zahl der festen Parameter (bei variabel: Mindestzahl)
    int variabel;                    // 1 = "MACRO n+": beliebig viele weitere Parameter (bis MACRO_PARAMETER_ANZAHL), Zugriff mit $P(i)
    char macroParameters[MACRO_PARAMETER_ANZAHL][MACRO_PARAMETER_LAENGE];   // bei benannt = 1 die Parameternamen (Doku 4.26)
    int benannt;                     // 0 = Parameter nur mit Nummern, 1 = Namen hinter MACRO (Doku 4.26), -1 = Namen oder Rumpf fehlerhaft: der Aufruf entfaellt ohne Folgefehler
    int schluesselAnzahl;            // Zahl der Schluesselwortparameter name=vorgabe hinter MACRO (Doku 4.30, ab c82ass 1.01-025); 0 = Aufruf rein positional
    char schluessel[MACRO_PARAMETER_ANZAHL];   // 1 = der Name Nummer k+1 ist ein Schluesselwortparameter (nur bei benannt = 1)
    char vorgabe[MACRO_PARAMETER_ANZAHL][MACRO_PARAMETER_LAENGE];   // Vorgabe des Schluesselwortparameters Nummer k+1 (leer erlaubt)
    int macroLineCount;
    lineElements *macroParsedLines;  
    int ausQuelltext;                // 1 = im Quelltext definiert, 0 = aus der Makrodatei
    int herkunft;                    // 0 = c82ass.makros, 1 = Quelltext, 2 = projektspezifische Makrodatei (;#MACRODATEIn=)
    char defDatei[1024];             // Makrodatei, in der das Makro definiert ist (leer: Quelltext)
    int defZeile;                    // Zeile der MACRO-Anweisung in defDatei bzw. im Quelltext (0 = unbekannt)
    int aufrufe;                     // Anzahl der Aufrufe in diesem Lauf (fuer --makros)
    int hatSpec;                     // 1 = das Makro hat eine Spezifikationszeile $SPEC (ab c82ass 1.03-002, Doku 4.32)
    int specTyp;                     // TYP der Spezifikationszeile: 0 = Macro (Vorgabe), 1 = Aufruf, 2 = LoadMakro, 3 = Eingebettet (ab 1.03-004)
    char specClass[32];              // CLASS der Spezifikationszeile (Grossbuchstaben, Ziffern, _); leer = keine Klasse
    int specAktion;                  // ACTION der Spezifikationszeile: 0 = None (Vorgabe), 1 = Load (Wirkung noch nicht festgelegt)
} macroDefinitionen;


#define INITIAL_SIZE 10   // Starte mit 10 Makros
#define GROWTH_FACTOR 2   // Verdopple die Groesse bei Bedarf

#define MELDE_FEHLER(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Fehler%s: " format, _violett, _normal, __VA_ARGS__); \
        STRKOPIE(result[*lineCount].sp1, fehlertext); \
        STRKOPIE(result[*lineCount].sp2, ""); \
        STRKOPIE(result[*lineCount].sp3, ""); \
        STRKOPIE(result[*lineCount].sp4, ""); \
        result[*lineCount].srcLine = 0; \
        result[*lineCount].makroInst = 0; \
        (*lineCount)++; \
    } while (0)

#define MELDE_WARNUNG(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Warnung%s: " format, _gelb, _normal, __VA_ARGS__); \
        STRKOPIE(result[*lineCount].sp1, fehlertext); \
        STRKOPIE(result[*lineCount].sp2, ""); \
        STRKOPIE(result[*lineCount].sp3, ""); \
        STRKOPIE(result[*lineCount].sp4, ""); \
        result[*lineCount].srcLine = 0; \
        result[*lineCount].makroInst = 0; \
        (*lineCount)++; \
    } while (0)

#define REALLOC_RESULT \
    do { \
        lineElements *temp = (lineElements *)realloc(result, (*lineCount + 1) * sizeof(lineElements)); \
        if (!temp) { \
            fprintf(stderr, "Speicherfehler bei Realloc!\n"); \
            exit(RC_FEHLER); \
        } \
        result = temp; \
    } while (0)

#define REALLOC_ERGEBNIS \
    lineElements *temp = (lineElements *)realloc(*ergebnis, (*lineCount + 1) * sizeof(lineElements)); \
    if (!temp) { \
        free(*ergebnis); \
        fprintf(stderr, "Speicherfehler!\n"); \
        exit(RC_FEHLER); \
    } \
    *ergebnis = temp;

//Pointer-Varianten
#define REALLOC_RESULT2 \
    do { \
        lineElements *temp = (lineElements *)realloc(*result, (*lineCount + 1) * sizeof(lineElements)); \
        if (!temp) { \
            free(*result); \
            return -1; /* Gebe einen Fehlercode zurück, statt NULL wei die übergeordnete Funktion es so will*/ \
        } \
        *result = temp; \
    } while (0)

#define MELDE_FEHLER2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Fehler%s: " format, _violett, _normal, __VA_ARGS__); \
        STRKOPIE((*result)[*lineCount].sp1, fehlertext); \
        STRKOPIE((*result)[*lineCount].sp2, ""); \
        STRKOPIE((*result)[*lineCount].sp3, ""); \
        STRKOPIE((*result)[*lineCount].sp4, ""); \
        (*result)[*lineCount].makroInst = 0; \
        (*lineCount)++; \
    } while (0)

#define MELDE_WARNUNG2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Warnung%s: " format, _gelb, _normal, __VA_ARGS__); \
        STRKOPIE((*result)[*lineCount].sp1, fehlertext); \
        STRKOPIE((*result)[*lineCount].sp2, ""); \
        STRKOPIE((*result)[*lineCount].sp3, ""); \
        STRKOPIE((*result)[*lineCount].sp4, ""); \
        (*result)[*lineCount].makroInst = 0; \
        (*lineCount)++; \
    } while (0)



#endif
