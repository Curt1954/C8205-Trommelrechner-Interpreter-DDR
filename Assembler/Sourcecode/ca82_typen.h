// ca82_typen.h - Version 1.00-030 (siehe ca82_version.h)
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
} lineElements;

typedef struct {
    char macroName[MACRO_PARAMETER_LAENGE];
    char macro[16];
    int macroParameterAnzahl;
    char macroParameters[MACRO_PARAMETER_ANZAHL][MACRO_PARAMETER_LAENGE]; 
    int macroLineCount;
    lineElements *macroParsedLines;  
    int ausQuelltext;                // 1 = im Quelltext definiert, 0 = aus der Makrodatei
    char defDatei[1024];             // Makrodatei, in der das Makro definiert ist (leer: Quelltext)
    int defZeile;                    // Zeile der MACRO-Anweisung in defDatei (0 = unbekannt)
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
        (*lineCount)++; \
    } while (0)

#define MELDE_WARNUNG2(format, ...) \
    do { \
        snprintf(fehlertext, sizeof(fehlertext), ";%s*** Warnung%s: " format, _gelb, _normal, __VA_ARGS__); \
        STRKOPIE((*result)[*lineCount].sp1, fehlertext); \
        STRKOPIE((*result)[*lineCount].sp2, ""); \
        STRKOPIE((*result)[*lineCount].sp3, ""); \
        STRKOPIE((*result)[*lineCount].sp4, ""); \
        (*lineCount)++; \
    } while (0)



#endif
