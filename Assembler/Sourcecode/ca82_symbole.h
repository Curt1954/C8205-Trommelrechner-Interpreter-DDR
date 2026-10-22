// ca82_symbole.h - Version 1.00-030 (siehe ca82_version.h)
// Tabellen des Assemblers (Symbole, Literale, equ, abs): Typen, Daten und Suchfunktionen (ca82_symbole.c).
#ifndef CA82_SYMBOLE_H
#define CA82_SYMBOLE_H

#include "ca82_standards.h"

#define BITMASK 010000000000
#define EQU_ELEMENTS 4096

typedef struct {
    char symbol[MAX_SYMBOL_LENGTH]; 
    int address;
    unsigned int relativAdresse;
    char orig_operation[MAX_SYMBOL_LENGTH]; 
    int aufgeloestIndex;   // Index der Definitionszeile in lineAsmAufgeloest (-1 = unbekannt); fuer Fehlermarken in Pass 2
    int verwendet;   // 1 = Symbol wurde in einem Operanden/Ausdruck nachgeschlagen (fuer -WARN=SYM)
} Symbol;

typedef struct {
    char literalName[MAX_SYMBOL_LENGTH];
    char literalValue[MAX_LINE_LENGTH];
    unsigned int relativAdresse;
} Literal;

typedef struct { char *key; char *value; } EquEntry;
typedef struct { char *key; char *value; } AbsEntry;

extern Symbol symbolTable[MAX_SYMBOLS];
extern int symbolCount;
extern Literal literalTable[MAX_LITERALS];
extern int literalCount;
extern EquEntry equ_tabelle[EQU_ELEMENTS];
extern int equ_fuellstand;
extern AbsEntry abs_tabelle[EQU_ELEMENTS];
extern int abs_fuellstand;
extern char inputFileName[1024];     // Quelltext (Projektverzeichnis/Datei.asm)

int isLiteralInTable(const char *name);                  // Literalsymbol (l0001 ...) vorhanden? 1/0
int isLiteralInTableRelativAdresse(const char *name);    // relative Adresse des Literals, -1 wenn nicht vorhanden
const char* getLiteralNameByValue(const char *value);    // Name des Literals mit diesem Wert, sonst ""
int appendToEquTable(const char *key, const char *value);
int sucheInEquTabelle(const char *suchbegriff);
int appendToAbsTable(const char *key, const char *value);   // 0 = ok, -1 = anderer Wert, -2 = Tabelle voll
int sucheInAbsTabelle(const char *suchbegriff);
void bubbleSortBySymbol(Symbol tabelle[], int anzahl);
void bubbleSortByAddress(Symbol tabelle[], int anzahl);
int getSymbolAddress(char *operand);                     // Adresse des Symbols, -1 wenn unbekannt; markiert es als verwendet
int isSymbol(char *token);                               // Symbol vorhanden? 1/0

#endif
