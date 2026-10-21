// ca82_symbole.c - Version 1.00-026 (siehe ca82_version.h)
// Symbol-, Literal-, equ- und abs-Tabellen des Assemblers samt Suchfunktionen und Sortierung.
// Aus ca82ass.c ausgelagert. Das Eintragen von Symbolen und Literalen mit Fehlermeldung ins Listing
// (addSymbol, addLiteral) bleibt vorerst in ca82ass.c.
#include "ca82_standards.h"
#include "ca82_symbole.h"

Symbol symbolTable[MAX_SYMBOLS];
int symbolCount = 0, literalCount = 0;
Literal literalTable[MAX_LITERALS];
EquEntry equ_tabelle[EQU_ELEMENTS];
int equ_fuellstand = 0;
AbsEntry abs_tabelle[EQU_ELEMENTS];
int abs_fuellstand = 0;

int isLiteralInTable(const char *name) {
    for (int i = 0; i < literalCount; i++) {
        if (strcmp(literalTable[i].literalName, name) == 0) {
            return 1; // Literal gefunden
        }
    }
    return 0; // Literal nicht vorhanden
}

int isLiteralInTableRelativAdresse(const char *name) {
    for (int i = 0; i < literalCount; i++) {
        if (strcmp(literalTable[i].literalName, name) == 0) {
            return literalTable[i].relativAdresse;
        }
    }
    return -1; // Literal nicht vorhanden
}

const char* getLiteralNameByValue(const char *value) {
    for (int i = 0; i < literalCount; i++) {
        if (strcmp(literalTable[i].literalValue, value) == 0) {
            return literalTable[i].literalName; // Literal gefunden, Name zurückgeben
        }
    }
    return ""; // Kein passendes Literal gefunden
}

int appendToEquTable(const char *key, const char *value) {
    if ((equ_fuellstand < EQU_ELEMENTS) && (strlen(key) != 0)){
        equ_tabelle[equ_fuellstand].key = strdup(key);
        equ_tabelle[equ_fuellstand].value = strdup(value);
        equ_fuellstand++;
        return 0;
    }
    return -1; 
}

int sucheInEquTabelle(const char *suchbegriff) {
    for (int i = 0; i < equ_fuellstand; i++) {  
        if (strcmp(equ_tabelle[i].key, suchbegriff) == 0) {
            return 1;  
        }
    }
    return 0;  
}

// Zahl einer abs-Definition: fuehrende 0 = oktal, sonst dezimal (Doku 2, <oktalzahl>/<dezimalzahl>).
// Liefert 1 und den Wert, wenn der ganze String eine solche Zahl ist, sonst 0.
static int absZahlWert(const char *text, long *wert) {
    char *ende;
    if (text == NULL || *text == '\0') return 0;
    int basis = (text[0] == '0' && text[1] != '\0') ? 8 : 10;
    *wert = strtol(text, &ende, basis);
    return *ende == '\0';
}

// Gleicher Wert: numerisch, damit abs 010 und abs 8 als gleich gelten; Texte, die keine reine Zahl
// sind, werden wie bisher als Zeichenfolge verglichen.
static int absWerteGleich(const char *a, const char *b) {
    long wa, wb;
    if (absZahlWert(a, &wa) && absZahlWert(b, &wb)) return wa == wb;
    return strcmp(a, b) == 0;
}

int appendToAbsTable(const char *key, const char *value) {
    char key_copy[256];  
    strncpy(key_copy, key, sizeof(key_copy) - 1);
    key_copy[sizeof(key_copy) - 1] = '\0';  

    // Falls `key` auf ":" endet, entferne es
    size_t len = strlen(key_copy);
    if (len > 0 && key_copy[len - 1] == ':') {
        key_copy[len - 1] = '\0';
    }

    // Überprüfe, ob der modifizierte Schlüssel existiert
    for (int i = 0; i < abs_fuellstand; i++) {
        if (strcmp(abs_tabelle[i].key, key_copy) == 0) {
            if (absWerteGleich(abs_tabelle[i].value, value)) {
                return 0;  // Kein Update notwendig
            } else {
                return -1;  // Beenden ohne Änderung
            }
        }
    }

    // Falls der Schlüssel nicht existiert, füge ihn hinzu
    if (abs_fuellstand < EQU_ELEMENTS) {
        abs_tabelle[abs_fuellstand].key = strdup(key_copy);  // Verwende die bereinigte Kopie
        abs_tabelle[abs_fuellstand].value = strdup(value);
        abs_fuellstand++;
        return 0;
    }

    return -2;  // Tabelle ist voll, kein neuer Eintrag möglich
}

int sucheInAbsTabelle(const char *suchbegriff) {
    // Lokale Kopie erstellen
    char suchbegriff_copy[256];  // Speicher groß genug wählen
    strncpy(suchbegriff_copy, suchbegriff, sizeof(suchbegriff_copy) - 1);
    suchbegriff_copy[sizeof(suchbegriff_copy) - 1] = '\0'; // Null-Terminierung sicherstellen

    // Falls `suchbegriff_copy` auf `':'` endet, entfernen
    size_t len = strlen(suchbegriff_copy);
    if (len > 0 && suchbegriff_copy[len - 1] == ':') {
        suchbegriff_copy[len - 1] = '\0';
    }

    // Suche mit der modifizierten Kopie
    for (int i = 0; i < abs_fuellstand; i++) { 
        if (strcmp(abs_tabelle[i].key, suchbegriff_copy) == 0) {
            return 1;  //gefunden
        }
    }
    return 0;  
}

void swap(Symbol *a, Symbol *b) {
    Symbol temp = *a;
    *a = *b;
    *b = temp;
}

void bubbleSortBySymbol(Symbol tabelle[], int anzahl) {
    for (int i = 0; i < anzahl - 1; i++) {
        for (int j = 0; j < anzahl - i - 1; j++) {
            if (strcmp(tabelle[j].symbol, tabelle[j + 1].symbol) > 0) {
                swap(&tabelle[j], &tabelle[j + 1]);
            }
        }
    }
}

void bubbleSortByAddress(Symbol tabelle[], int anzahl) {
    for (int i = 0; i < anzahl - 1; i++) {
        for (int j = 0; j < anzahl - i - 1; j++) {
            if (tabelle[j].address > tabelle[j + 1].address) {
                swap(&tabelle[j], &tabelle[j + 1]);
            }
        }
    }
}

int getSymbolAddress(char *operand) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, operand) == 0) {
            symbolTable[i].verwendet = 1;   // Verwendung in einem Operanden (-WARN=SYM)
            return symbolTable[i].address;
        }
    }
    return -1; // Operand nicht gefunden
}

int isSymbol(char *token) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, token) == 0) {
            return 1; // Symbol
        }
    }
    return 0; // Kein Symbol
}
