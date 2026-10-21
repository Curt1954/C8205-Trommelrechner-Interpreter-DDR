// ca82_makros.h - Version 1.00-026 (siehe ca82_version.h)
#ifndef CA82_MAKROS_H
#define CA82_MAKROS_H

#include "ca82_typen.h"

// ---- Daten des Makromoduls ----
extern macroDefinitionen *macros;
extern int macroCount;
extern int macroCapacity;
extern char recursiv_macro[128];

// ---- Vom Makromodul angebotene Funktionen ----
void erzeugeMacroArray(const char *macroFileName);
lineElements *loeseMacroAuf(macroDefinitionen *macros_p, int *macroCount_p, char *aktuellerOpCode,
                            char *aktuelleParameterZeile, int *lineCount, char *label);
void macroSprung1Aufloesen(lineElements **ergebnis, int *lineCount, char *mna);
int macroIfAufloesen(lineElements *ergebnis, int *imIf, int *inBedingung);
void printAllMacros(void);
int sammleQuelltextMakros(void);          // Makrodefinitionen im Quelltext; Rueckgabe: Anzahl Fehler
int beginntMitSemikolon(const char *line);
int makroDateiSetzen(const char *pfad);   // Option -m; 0 = ok, -1 = Pfad zu lang
const char *makroDateiName(void);

// Zaehler der aufgeloesten Makros (Begrenzung seed_max)
extern int seed_value;
extern int seed_max;

// ---- Vom Makromodul benoetigte Daten und Funktionen des Hauptprogramms (ca82ass.c) ----
extern lineElements linesAsm[PROGRAMMZEILEN];
extern int lineCountAsm;
extern int is_error;
extern int is_error0;

void copyLineElements(lineElements *output, lineElements *ergebnis, int i);
void processLine(char *line, lineElements linesAsm_p[], int *lineCount);
void verarbeiteZeile_wdhl_adr_e(char *tempLine);
int verarbeiteZeile_wdhl(char *tempLine, char *loe, char *resu, char *opcode, char *anzahl, char *adresse);

#endif
