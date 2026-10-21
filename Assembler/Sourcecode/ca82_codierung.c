// ca82_codierung.c - Codierung: Operationscodes, Text (dt/dz), Umschluesselung
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"


char* getOperationCode(char *operation) {
    static char octalCodeString[4]; 
    // Oktale Operationscodes bestehen aus genau drei Oktalziffern (0-7); z. B. 999 ist ungueltig
    if (strlen(operation) == 3 &&
        operation[0] >= '0' && operation[0] <= '7' &&
        operation[1] >= '0' && operation[1] <= '7' &&
        operation[2] >= '0' && operation[2] <= '7') {
        strncpy(octalCodeString, operation, 3);
        octalCodeString[3] = '\0'; 
        return octalCodeString;
    }

    // Rückgabe für ungültigen Code
    return "XXX";
}


void formatLabel(char **label) {
    if (*label == NULL) {
        fprintf(stderr, "%sFehler: Ungültiger Label-Zeiger%s\n", _violett, _normal);
        exit(RC_FEHLER);
    }

    char temp[35] = {0};
    const char *start = *label;
    while (*start == ' ') start++;
    const char *end = *label + strlen(*label) - 1;
    while (end > start && *end == ' ') end--;

    size_t trimmedLength = end - start + 1;
    strncpy(temp, start, trimmedLength);

    for (size_t i = trimmedLength; i < 34; i++) {
        temp[i] = ' ';
    }
    temp[34] = '\0';

    free(*label);
    *label = malloc(35 * sizeof(char));
    if (*label == NULL) exit(RC_FEHLER);
    strkopiere(*label, 35, temp);
}


char *formatOperand(const char *op) {
    // Speicher für das neue Format reservieren
    char *formatted = malloc(9 * sizeof(char)); // 8 Zeichen + Nullterminator

    // Leerzeichen entfernen (Trimmen)
    const char *start = op;
    while (isspace((unsigned char)*start)) start++; // Führende Leerzeichen entfernen
    const char *end = start + strlen(start) - 1;
    while (end > start && isspace((unsigned char)*end)) end--; // Nachfolgende Leerzeichen entfernen

    size_t length = end - start + 1;
    // Zeichen kopieren und auffüllen
    if (length > 0) {
        strncpy(formatted, start, length);
    }
    for (size_t i = length; i < 8; i++) {
        formatted[i] = ' '; // Mit Leerzeichen auffüllen
    }
    formatted[8] = '\0'; // Nullterminator setzen
    return formatted;
}



#define OUT_SIZE 50 
TableRow outUmschluesselungsTable[OUT_SIZE] = {
    {0010, 60, 49},
    {0020, 34, 50},
    {0230, 0, 51},
    {0040, 91, 52},
    {0250, 62, 53},
    {0260, 39, 54},
    {0070, 0, 55},
    {0100, 126, 56},
    {0310, 93, 57},
    {0200, 35, 48},
    {01740, 42, 37},
    {01550, 9, 9},
    {01300, 81, 113},
    {01660, 87, 119},
    {0450, 69, 101},
    {01110, 82, 114},
    {01630, 84, 116},
    {01710, 90, 122},
    {01440, 85, 117},
    {0510, 73, 105},
    {01060, 79, 111},
    {01270, 80, 112},
    {0150, 40, 58},
    {0400, 61, 43},
    {0610, 65, 97},
    {01420, 83, 115},
    {0640, 68, 100},
    {0460, 70, 102},
    {0670, 71, 103},
    {0700, 72, 104},
    {01210, 74, 106},
    {01220, 75, 107},
    {01030, 76, 108},
    {01600, 59, 96},
    {01410, 41, 47},
    {02720, 10, 10},
    {01500, 89, 121},
    {01470, 88, 120},
    {0430, 67, 99},
    {01650, 86, 118},
    {0620, 66, 98},
    {01050, 78, 110},
    {01240, 77, 109},
    {01530, 63, 44},
    {0730, 33, 46},
    {01000, 465, 45},   // Zeile 48: Tabelle 1: Gbuch = 465 (Dreieck), Klbuch = 45 (Minus)
    {0320, 32, 32}
};
//    {0320, 32, 32}

// Prüfen, ob die Zeichen der Text-Definition in der Tabelle vorhanden sind.
int isValueInTable(const char *operand, TableRow outUmschluesselungsTable_p[], int size, int *missingPos) {
    for (size_t i = 0; i < strlen(operand); i++) {
        unsigned char asciiValue = (unsigned char)operand[i]; // ASCII-Wert des Zeichens

        int found = 0; // Flag, ob das Zeichen gefunden wurde

        for (int j = 0; j < size; j++) {
            if (outUmschluesselungsTable_p[j].spalte2 == asciiValue || outUmschluesselungsTable_p[j].spalte3 == asciiValue) {
                found = 1; // Zeichen gefunden
                break;
            }
        }

        if (!found) {
            *missingPos = (int)i; // Speichere die Position des fehlenden Zeichens
            return 0; // Fehler: Zeichen nicht gefunden
        }
    }

    return 1; // Alle Zeichen gültig
}


void copyAndIncrementLineElementsX(int i, char *buffer) {
    pruefeZeilenfeld(lineCountAsmAufgeloestX);
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, buffer);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, lineAsmAufgeloest[i].sp1);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, lineAsmAufgeloest[i].sp2);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, lineAsmAufgeloest[i].sp3);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, lineAsmAufgeloest[i].sp4);
    
    lineCountAsmAufgeloestX++; 
}

void copyAndIncrementLineElementsSpOnly(int i, char *buffer) {
    (void)i;
    pruefeZeilenfeld(lineCountAsmAufgeloestX);
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, buffer);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, "; ");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");
    
    lineCountAsmAufgeloestX++; 
}


// Schreibt eine Zeile in die Objektdatei (.obj).
//  - Die Adreßspalte entfaellt: "0007: 01 0006 241" wird zu "01 0006 241"; bei Zeilen, die schon bisher keine
//    Adresse hatten ("      20 0000 0100"), entfallen die fuehrenden Leerzeichen.
//  - Das Kennzeichen 01 wird durch den Wert des Pragmas LEITADRESSE ersetzt (Standard 01).
// Die Puffer fuer .dmp und .test behalten die Adresse; sie werden von dieser Funktion nicht veraendert.
// Das Listing (STDOUT und .dmp) erhaelt das Kennzeichen xx in schreibeListingX (ersetzeKennzeichen01).
int objWortAnzahl = 0;   // Anzahl der in die .obj geschriebenen Worte (fuer die Warnung bei leerem Programm)
void schreibeObjZeile(FILE *objFile, const char *zeile) {
    const char *p = zeile;
    objWortAnzahl++;
    while (*p == ' ') p++;

    // Adreßspalte "<oktalzahl>:" samt folgenden Leerzeichen ueberspringen
    const char *q = p;
    while (*q >= '0' && *q <= '7') q++;
    if (q > p && *q == ':') {
        p = q + 1;
        while (*p == ' ') p++;
    }

    if (p[0] == '0' && p[1] == '1' && (p[2] == ' ' || p[2] == '\0')) {
        fprintf(objFile, "%02d%s.\n", leitadresseKennzeichen, p + 2);
    } else {
        fprintf(objFile, "%s.\n", p);
    }
}

// Auflösen des dt Befehls
int zFlagErz = 0; // Zustandsflag
int textPC = 0;   // Trommeladresse des naechsten von erzeugenText ausgegebenen Wortes
void erzeugenText(char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int no_kbgb ,int iii) {
    int ersteAusgabe = 1; // Flag, um die erste Ausgabe zu erkennen
    char *zeichenfolge = operand;
    int missingChar;
    char buffer[32];

    // Entferne die umschließenden \-Zeichen
    if (zeichenfolge[0] == '\\') zeichenfolge++;
    if (zeichenfolge[0] != '\0' && zeichenfolge[strlen(zeichenfolge) - 1] == '\\') zeichenfolge[strlen(zeichenfolge) - 1] = '\0';   // leerer Operand: kein Zugriff vor dem Puffer

    if (isValueInTable(zeichenfolge, outUmschluesselungsTable, OUT_SIZE, &missingChar) == 0) {
        is_error3 = 1;
        printHell = 1;
        PRINT_FEHLER("dt Operand enthält unzulässige Zeichen an Position: %i.", missingChar);
        return;
    }

    // Jedes Wort (auch ein Umschalt-Praefix 0570/1170) belegt genau eine
    // Trommeladresse, beginnend bei textPC. Die Adresse wird pro Zeile in
    // .adr/.adrValid gemerkt, damit erzeugeTestDatei sie verwenden kann.
    void ausgabeWort(const char *wort) {
        schreibeObjZeile(machineCodeFile, wort);
        pruefeZeilenfeld(lineCountAsmAufgeloestX);
        lineElementsX *z = &lineAsmAufgeloestX[lineCountAsmAufgeloestX];
        if (ersteAusgabe == 1) {
            fprintf(hilfsFile, "%s\n", line);
            STRKOPIE(z->sp0, wort);
            STRKOPIE(z->sp1, lineAsmAufgeloest[iii].sp1);
            STRKOPIE(z->sp2, lineAsmAufgeloest[iii].sp2);
            STRKOPIE(z->sp3, lineAsmAufgeloest[iii].sp3);
            STRKOPIE(z->sp4, lineAsmAufgeloest[iii].sp4);
            ersteAusgabe = 0;
        } else {
            fprintf(hilfsFile, "%s\n", "; ");
            STRKOPIE(z->sp0, wort);
            STRKOPIE(z->sp1, "; ");
            STRKOPIE(z->sp2, "");
            STRKOPIE(z->sp3, "");
            STRKOPIE(z->sp4, "");
        }
        z->adr = textPC++;
        z->adrValid = 1;
        lineCountAsmAufgeloestX++;
    }

    // Zeichenweise Verarbeitung
    for (size_t i = 0; i < strlen(zeichenfolge); i++) {
        int asciiWert = (int) zeichenfolge[i];
        int spalte = 0;       // 2 oder 3: in welcher Tabellenspalte gefunden
        int code = 0;         // Oktalcode aus Spalte 1
        for (size_t j = 0; j < OUT_SIZE; j++) {
            if (outUmschluesselungsTable[j].spalte2 == (unsigned int)asciiWert) { spalte = 2; code = outUmschluesselungsTable[j].spalte1; break; }
        }
        if (!spalte) {
            for (size_t j = 0; j < OUT_SIZE; j++) {
                if (outUmschluesselungsTable[j].spalte3 == (unsigned int)asciiWert) { spalte = 3; code = outUmschluesselungsTable[j].spalte1; break; }
            }
        }
        if (!spalte) continue;

        int steuer = (asciiWert == 32) || (asciiWert == 9) || (asciiWert == 10);
        int zustandPasst = (spalte == 2) ? (zFlagErz == 1) : (zFlagErz == 0);
        int direkt = steuer || ((zustandPasst || (no_kbgb == 1)) && !((no_kbgb == 2) && (i == 0)));

        if (!direkt) {
            if (no_kbgb != 1) {
                snprintf(buffer, sizeof(buffer), "      00 %04o 030", (spalte == 2) ? 0570 : 01170);
                ausgabeWort(buffer);
            }
            zFlagErz = (spalte == 2) ? 1 : 0;
        }
        snprintf(buffer, sizeof(buffer), "      00 %04o 030", code);
        ausgabeWort(buffer);
    }
}

// ---------

int zFlag = 0; // Unterscheidung 2. Spalte -- 3. Spalte
int zaehleText(char operand[], int no_kbgb) {
    int zaehler = 0; 
    char *zeichenfolge = operand;

    if (zeichenfolge[0] == '\\') zeichenfolge++;
    if (zeichenfolge[0] != '\0' && zeichenfolge[strlen(zeichenfolge) - 1] == '\\') zeichenfolge[strlen(zeichenfolge) - 1] = '\0';   // leerer Operand: kein Zugriff vor dem Puffer

    for (size_t i = 0; i < strlen(zeichenfolge); i++) {
        char zeichen = zeichenfolge[i];
        int asciiWert = (int)zeichen;

        // Suche in der zweiten Spalte der Tabelle
        int gefunden = 0;
        for (size_t j = 0; j < OUT_SIZE; j++) {
            if (outUmschluesselungsTable[j].spalte2 == (unsigned int)asciiWert) {
                // Treffer in der zweiten Spalte   
                if (  ( 
                        (asciiWert == 32) || (asciiWert == 9) || (asciiWert == 10) 
                        )
                        || 
                        ((
                        (zFlag == 1) || (no_kbgb == 1)  //|| ((no_kbgb == 0) && (j == 0 ))
                        ) 
                        && 
                        ! ( (no_kbgb == 2) && (i == 0 ) ) 
                        ) 
                    ) {
                    zaehler++; // Ein fprintf
                } else {
                    if ( no_kbgb != 1) {
                       zaehler++; // Zwei fprintfs
                    }
                    zaehler++; 
                    zFlag = 1; 
                }
                gefunden = 1;
                break;
            }
        }

        if (!gefunden) {
            // Suche in der dritten Spalte der Tabelle
            for (size_t j = 0; j < OUT_SIZE; j++) {
                if (outUmschluesselungsTable[j].spalte3 == (unsigned int)asciiWert) {
                    // Treffer in der dritten Spalte
                    if (  ( 
                            (asciiWert == 32) || (asciiWert == 9) || (asciiWert == 10) 
                          )
                          || 
                          ((
                            (zFlag == 0) || (no_kbgb == 1) //|| ((no_kbgb == 0) && (j == 0 ))
                          ) 
                          && 
                          ! ( (no_kbgb == 2) && (i == 0 ) )
                          )  
                       ) {
                        zaehler++;
                    } else {
                        if ( no_kbgb != 1) {
                            zaehler++; // Zwei fprintfs
                        }
                        zaehler++; 
                        zFlag = 0; 
                    }
                    gefunden = 1;
                    break;
                }
            }
        }
    }

    return zaehler; 
}


typedef struct {
    char *symbol; 
    int octalValue; 
} dzZeichen;

dzZeichen dzTable[] = {
    {"$wrzl",  02720},
    {"$sm",    02720},
    {"$inkb",  01170},
    {"$ingb",   0570},
    {"$irrz",  03770},
    {"$irrs",   0160},
    {"$trans", 01770},
    {"$bm",    03520},
    {"$vorl",     00},
    {"$irrb",   0760},
    {"$tab",   01550},
    {"$zr",     0320},
    {"$wr",    01120},
    {"%",      01740},
    {":",       0150},
    {"+",       0400},
    {"`",      01600},
    {"/",      01410},
    {",",      01530},
    {".",       0730},
    {"-",      01000}
};

// Anzahl der Einträge in der Tabelle
const int dzCount = sizeof(dzTable) / sizeof(dzTable[0]);

void dzAuswertung(char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii) {
    char buffer[32];

    for (int i = 0; i < dzCount; i++) {
        // Prüfe, ob der Operand in der ersten Spalte der Tabelle enthalten ist
        if (strcmp(operand, dzTable[i].symbol) == 0) {
            // Zweite Spalte ausgeben
            snprintf(buffer, sizeof(buffer), "      00 %04o 030", dzTable[i].octalValue);
            schreibeObjZeile(machineCodeFile, buffer);

            fprintf(hilfsFile, "%s\n", line);
            copyAndIncrementLineElementsX(iii, buffer);
            // Adresse fuer die .test-Datei merken (wie bei dt/dto/dtm): die
            // dz-Zeile traegt in sp0 keine Adresse. textPC wird vom Aufrufer gesetzt.
            lineAsmAufgeloestX[lineCountAsmAufgeloestX - 1].adr = textPC;
            lineAsmAufgeloestX[lineCountAsmAufgeloestX - 1].adrValid = 1;
            return; // Funktion beenden, da der Eintrag gefunden wurde
        }
    }
    is_error3=1;
    printHell = 1;
    PRINT_FEHLER ("dz Operand %s nicht gültig.", operand);
}

int zaehleBackslashes(const char *templine) {
    int count = 0;
    for (size_t i = 0; i < strlen(templine); i++) {
        if (templine[i] == '\\') {
            count++;
        }
    }
    return count; 
}

// replaceSubstring sucht in line nach dem Substring operand und ersetzt ihn durch den Octal-Wert von dwValue
void replaceSubstring(char *line, size_t lineSize, const char *operand, unsigned int dwValue) {
    char tempLine[1024]; 
    char *pos = strstr(line, operand); 

    if (pos) {
        size_t pre = (size_t)(pos - line);
        if (pre >= sizeof(tempLine)) pre = sizeof(tempLine) - 1;
        memcpy(tempLine, line, pre);
        tempLine[pre] = '\0'; 
        size_t l0 = strnlen(tempLine, sizeof(tempLine));
        snprintf(tempLine + l0, sizeof(tempLine) - l0, "%05o", dwValue);
        STRANHANG(tempLine, pos + strlen(operand));
        strkopiere(line, lineSize, tempLine);
    }
}
