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
    // Listing, .dmp und .test zeigen den Namen (.LD), .mqo und .obj den Code (OPSYM, O-21)
    const char *opAnzeige = opsymAnzeigeName(&lineAsmAufgeloest[i]);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, opAnzeige != NULL ? opAnzeige : lineAsmAufgeloest[i].sp2);
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

// ---- Schalter --ABSPR: absolut adressierte Lochstreifendatei (.kep) fuer das Kleine Eingabeprogramm (KEP) ----
// Statt des Objektcodes K1K2 wird ein binaer im R300-Code codierter Lochstreifen geschrieben: je Lochungszeile
// 8 Ziffern 0/1 (Spurfolge w v u p 8 4 2 1), Zeichen nur 0 1 : . (Lage KB, Paritaet ungerade).
//   Leitbefehl:  <Adresse>240:   (Adresse = start bzw. neuer Wert einer 20-Zeile, ohne Vornullen)
//   Das Pragma LEITADRESSE gilt zuerst: ersetzt es 01 durch 00, ist K1=00 (Rest unveraendert, keine Addition);
//   ersetzt es 01 durch 02..09, werden diese Zeilen nicht umgesetzt (nicht ausgegeben, Warnung).
//   K1=00: Rest der Zeile ohne Leerzeichen unveraendert;  K1=01: (Adressstellen + Basis), dann 3 Oktalziffern Op;
//   K1=20: Basis := Wert, dazu neuer Leitbefehl;  K1=21 (Hauptleitadresse) und das Endezeichen entfallen.
// Jede Oktalziffer wird durch ihre 3 Bits ersetzt; Wort mit '.', Leitbefehl mit ':' abgeschlossen.
int absprAktiv = 0;                     // 1 = Aufruf mit --ABSPR
static unsigned long absprBasis = 0;    // aktueller Wert oo..oo (Leit-/Ladeadresse)
int absprAnzahl0209 = 0;                // Zeilen mit K1=02..09 (nicht umgesetzt, nur gezaehlt)
int absprAnzahl01 = 0;                  // Zeilen, die nach Anwendung des Pragmas LEITADRESSE noch K1=01 haben

static void absprZeichen(FILE *f, char z) {
    static const char *const kb0 = "00010000", *const kb1 = "00000001", *const dp = "00001101", *const pkt = "00111011";
    fprintf(f, "%s\n", z == '0' ? kb0 : z == '1' ? kb1 : z == ':' ? dp : pkt);
}

// Gibt eine Oktalzahl (Ziffernfolge) als Bitfolge aus; fuehrende Nullbits entfallen (mindestens eine 0 bleibt).
static void absprOktal(FILE *f, const char *ziffern, int vornullenBehalten, char abschluss) {
    int begonnen = vornullenBehalten;
    for (const char *c = ziffern; *c; c++) {
        for (int b = 2; b >= 0; b--) {
            char bit = (((*c - '0') >> b) & 1) ? '1' : '0';
            if (bit == '1') begonnen = 1;
            if (begonnen) absprZeichen(f, bit);
        }
    }
    if (!begonnen) absprZeichen(f, '0');
    absprZeichen(f, abschluss);
}

#define ABSPR_BAHN_MAX 64
unsigned long absprBahnAdresse[ABSPR_BAHN_MAX];   // Woerter, die auf die Zellen 0002 bis 0037 (das KEP selbst) geladen werden; 0000 und 0001 sind die Sprungzellen (wie beim Minimalprogramm) und warnen nicht
static unsigned long absprAdr = 0;                // Adresse, auf die das naechste Wort geladen wird
int absprBahnAnzahl = 0;

static void absprLeitbefehl(FILE *f, unsigned long adresse) {
    char text[32];
    absprAdr = adresse;
    snprintf(text, sizeof(text), "%lo240", adresse);   // oktale Adresse ohne Vornullen, dann Operationscode 240
    absprOktal(f, text, 0, ':');
}

// Erster Leitbefehl; wird von pass3 vor der ersten Zeile aufgerufen.
void absprStart(FILE *f) {
    absprBasis = startAdresse;
    absprLeitbefehl(f, absprBasis);
}

static void absprWortGezaehlt(void) {            // ein Wort wird auf absprAdr geladen
    if (absprAdr >= 2 && absprAdr <= 037) {      // Warnung folgt in meldeErfolg
        if (absprBahnAnzahl < ABSPR_BAHN_MAX) absprBahnAdresse[absprBahnAnzahl] = absprAdr;
        absprBahnAnzahl++;
    }
    absprAdr++;
}

static void absprZeile(FILE *f, const char *p) {
    char kz[3] = "00";
    char rest[128];
    size_t n = 0;
    if (p[0] >= '0' && p[0] <= '9' && p[1] >= '0' && p[1] <= '9' && (p[2] == ' ' || p[2] == '\0')) {
        kz[0] = p[0]; kz[1] = p[1];
        p += 2;
    }   // sonst (Nullwort "0"): wie K1=00
    for (; *p && n < sizeof(rest) - 1; p++) if (*p != ' ') rest[n++] = *p;
    rest[n] = '\0';
    if (strcmp(kz, "01") == 0 && leitadresseKennzeichen >= 2 && leitadresseKennzeichen <= 9) {
        absprAnzahl0209++;                             // K1=02..09 (Pragma LEITADRESSE): wird nicht umgesetzt
        return;
    }
    if (strcmp(kz, "21") == 0) return;                 // Hauptleitadresse: entfaellt
    if (strcmp(kz, "20") == 0) {
        absprBasis = strtoul(rest, NULL, 8);
        absprLeitbefehl(f, absprBasis);
    } else if (strcmp(kz, "01") == 0 && leitadresseKennzeichen == 1) {   // Pragma LEITADRESSE hat Vorrang: nur noch echte 01
        absprAnzahl01++;
        absprWortGezaehlt();
        unsigned long z = strtoul(rest, NULL, 8);       // aaaa ooo
        char text[32];
        snprintf(text, sizeof(text), "%lo%03lo", (z >> 9) + absprBasis, z & 0777UL);
        absprOktal(f, text, 0, '.');
    } else {
        absprWortGezaehlt();
        absprOktal(f, rest, 1, '.');                    // 00: unveraendert, auch Vornullen
    }
}

// Objektdatei binaer: Jedes Zeichen der Objektzeile wird als ein R300-Lochbild (Spurfolge w v u p 8 4 2 1, 1 = gelocht,
// ungerade Lochzahl) in einer Zeile aus acht Ziffern 0/1 ausgegeben (Kodetabelle 1, Klbuch; Anfangslage Klbuch, es ist
// keine Umschaltung noetig). Die Objektzeilen haben kein Zeilenende: die Wortmarke "." trennt die Woerter.
void schreibeLochbild(FILE *f, char zeichen) {
    static const unsigned char ziffer[10] = { 020, 001, 002, 023, 004, 025, 026, 007, 010, 031 };
    int lb;
    if (zeichen >= '0' && zeichen <= '9') lb = ziffer[zeichen - '0'];
    else if (zeichen == '.') lb = 073;
    else if (zeichen == '/') lb = 0141;
    else return;                       // andere Zeichen kommen in einer Objektzeile nicht vor
    for (int b = 7; b >= 0; b--) fputc(((lb >> b) & 1) ? '1' : '0', f);
    fputc('\n', f);
}

void schreibeLochbilder(FILE *f, const char *text) {
    for (; *text; text++) schreibeLochbild(f, *text);
}

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

    if (absprAktiv) { absprZeile(objFile, p); return; }

    // Objektzeile ohne Leerzeichen (danach binaer codiert): ein Zwischenraum (ZR) wuerde beim Lesen durch die Eingabe mit Kennzeichen das gerade
    // gelesene Wort verwerfen. Die Zeile wird deshalb ohne alle Leerzeichen und Tabulatoren ausgegeben.
    char kompakt[256];
    size_t n = 0;
    if (p[0] == '0' && p[1] == '1' && (p[2] == ' ' || p[2] == '\0')) {
        snprintf(kompakt, sizeof(kompakt), "%02d", leitadresseKennzeichen);
        n = strlen(kompakt);
        p += 2;
    }
    for (; *p && n < sizeof(kompakt) - 1; p++) {
        if (*p != ' ' && *p != '\t') kompakt[n++] = *p;
    }
    kompakt[n] = '\0';
    schreibeLochbilder(objFile, kompakt);
    schreibeLochbilder(objFile, ".");     // kein Zeilenende: SatzMarke/WRZL wuerde das Minimalprogramm v6 als zusaetzliches Wort 0 speichern
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
        char schl[64];
        snprintf(schl, sizeof(schl), "dt Operand unzulässig, Position %i", missingChar);
        if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("dt Operand enthält unzulässige Zeichen an Position: %i.", missingChar);
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
// kat4 (Doku 3.3.14): komprimierter Text, 4 Ausgabezeichen je Maschinenwort.
// Je Zeichen wird die Ausgabeadresse der Kodetabelle ohne das abschliessende x (3 Oktalziffern = 9 Bit)
// ohne das werthoechste Bit (8 Bit) abgelegt; das erste Zeichen steht rechts (Bit 0 bis 7), das zweite
// links daneben usw. Fehlende Zeichen des letzten Wortes bleiben 0. Das letzte Wort traegt z0 = 1
// (Bit 32 = 040000000000, linkes Bit des 33-Bit-Wortes). Umschaltzeichen werden nicht eingefuegt.
// Liefert Anfang und Laenge des Textes ohne umschliessende \-Zeichen (der Operand bleibt unveraendert).
static const char *kat4Text(const char *operand, size_t *laenge) {
    const char *t = operand;
    size_t n;
    if (t[0] == '\\') t++;
    n = strlen(t);
    if (n > 0 && t[n - 1] == '\\') n--;
    *laenge = n;
    return t;
}

// Gemeinsamer Helfer fuer kat4 und kat5: schreibt ein Maschinenwort in die Objektdatei, die Hilfsdatei und
// das Listing. Das erste Wort traegt die Quellzeile, jedes weitere Wort steht in einer Folgezeile. Die
// Adresse (textPC, vom Aufrufer gesetzt) wird je Wort um 1 weitergezaehlt.
static void katAusgabeWort(FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii, const char *wort, int *ersteAusgabe) {
    schreibeObjZeile(machineCodeFile, wort);
    pruefeZeilenfeld(lineCountAsmAufgeloestX);
    lineElementsX *z = &lineAsmAufgeloestX[lineCountAsmAufgeloestX];
    if (*ersteAusgabe == 1) {
        fprintf(hilfsFile, "%s\n", line);
        STRKOPIE(z->sp0, wort);
        STRKOPIE(z->sp1, lineAsmAufgeloest[iii].sp1);
        STRKOPIE(z->sp2, lineAsmAufgeloest[iii].sp2);
        STRKOPIE(z->sp3, lineAsmAufgeloest[iii].sp3);
        STRKOPIE(z->sp4, lineAsmAufgeloest[iii].sp4);
        *ersteAusgabe = 0;
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

int zaehleKat4(const char operand[]) {
    size_t n;
    kat4Text(operand, &n);
    return (int)((n + 3) / 4);
}

void erzeugenKat4(const char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii) {
    size_t n;
    const char *text = kat4Text(operand, &n);
    char zeichenfolge[1024];
    int missingChar;
    int ersteAusgabe = 1;

    if (n >= sizeof(zeichenfolge)) n = sizeof(zeichenfolge) - 1;
    memcpy(zeichenfolge, text, n);
    zeichenfolge[n] = '\0';

    if (isValueInTable(zeichenfolge, outUmschluesselungsTable, OUT_SIZE, &missingChar) == 0) {
        is_error3 = 1;
        printHell = 1;
        char schl[64];
        snprintf(schl, sizeof(schl), "kat4 Operand unzulässig, Position %i", missingChar);
        if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("kat4 Operand enthält unzulässige Zeichen an Position: %i.", missingChar);
        return;
    }

    size_t woerter = (n + 3) / 4;
    for (size_t w = 0; w < woerter; w++) {
        unsigned long long wert = 0;
        for (size_t k = 0; k < 4 && w * 4 + k < n; k++) {
            int asciiWert = (unsigned char)zeichenfolge[w * 4 + k];
            unsigned int code = 0;
            int gefunden = 0;
            for (size_t j = 0; j < OUT_SIZE && !gefunden; j++) {
                if (outUmschluesselungsTable[j].spalte2 == (unsigned int)asciiWert) { code = outUmschluesselungsTable[j].spalte1; gefunden = 1; }
            }
            for (size_t j = 0; j < OUT_SIZE && !gefunden; j++) {
                if (outUmschluesselungsTable[j].spalte3 == (unsigned int)asciiWert) { code = outUmschluesselungsTable[j].spalte1; gefunden = 1; }
            }
            wert |= (unsigned long long)(((code >> 3) & 0377)) << (8 * k);
        }
        if (w + 1 == woerter) wert |= 040000000000ULL;    // z0 = 1 am letzten Wort
        char buffer[40];
        snprintf(buffer, sizeof(buffer), "      00 %011llo", wert);
        katAusgabeWort(machineCodeFile, hilfsFile, line, iii, buffer, &ersteAusgabe);
    }
}

// ---------
// kat5 (Doku 3.3.15, neues Format ab c82ass 1.03-001): komprimierter Text in genau einem Maschinenwort, 1 bis 5 Zeichen, je Zeichen ein
// 6-Bit-Code (Tabelle der Doku, in Sortierreihenfolge numeriert, unabhaengig von der Ausgabeadresse der Kodetabelle). Das Wort ist
// linksbuendig: das erste Zeichen steht in z3 bis z8 (Bit 29 bis 24), das fuenfte in z27 bis z32 (Bit 5 bis 0); z0 bis z2 bleiben 0, ein
// Endekennzeichen gibt es nicht. Fehlende Zeichen rechts bleiben Code 00 (Fuellung). Mehr als 5 Zeichen und ein leerer Operand sind ein
// Fehler. Umschaltzeichen werden nicht eingefuegt. Vorrat: a bis z, 0 bis 9, Leerzeichen, . , - : + = und die Marken $wrzl, $inkb, $ingb
// (ohne Beachtung der Gross-/Kleinschreibung, je Marke ein Zeichen).

#define KAT5_MAXZEICHEN 5
#define KAT5_WRZL 053
#define KAT5_INKB 054
#define KAT5_INGB 055

// Erkennt an Stelle i des Textes eine Marke. Liefert die Laenge der Marke und setzt *code, sonst 0.
static size_t kat5Marke(const char *t, size_t n, size_t i, int *code) {
    static const struct { const char *name; int code; } marken[] = {
        { "$wrzl", KAT5_WRZL }, { "$inkb", KAT5_INKB }, { "$ingb", KAT5_INGB }
    };
    for (size_t m = 0; m < sizeof(marken) / sizeof(marken[0]); m++) {
        size_t l = strlen(marken[m].name);
        size_t k = 0;
        if (i + l > n) continue;
        while (k < l && tolower((unsigned char)t[i + k]) == marken[m].name[k]) k++;
        if (k == l) { *code = marken[m].code; return l; }
    }
    return 0;
}

// Code eines einzelnen Zeichens ohne Marken; -1, wenn das Zeichen nicht zum Vorrat gehoert.
static int kat5Zeichencode(unsigned char c) {
    if (c >= 'a' && c <= 'z') return 021 + (int)(c - 'a');    // a bis z: 021 bis 052
    if (c >= '0' && c <= '9') return 07 + (int)(c - '0');     // 0 bis 9: 07 bis 020
    switch (c) {
        case ' ': return 01;
        case ',': return 02;
        case '-': return 03;
        case '.': return 04;
        case '+':
        case '=': return 05;
        case ':': return 06;
        default:  return -1;
    }
}

// Zerlegt den Text in Zeichen. Eine Marke zaehlt als ein Zeichen, ein unzulaessiges Zeichen (auch ein $ ohne
// gueltigen Markennamen) zaehlt ebenfalls als eines. codes darf NULL sein; sonst muss er n Plaetze haben
// (unzulaessige Zeichen erhalten dort den Code 0). *fehlerPos erhaelt die Position (0-basiert wie bei kat4)
// des ersten unzulaessigen Zeichens, sonst -1; *fehlerDollar ist 1, wenn dieses Zeichen ein $ ohne gueltigen
// Markennamen ist.
static size_t kat5Zerlegen(const char *t, size_t n, int *codes, int *fehlerPos, int *fehlerDollar) {
    size_t anzahl = 0;
    size_t i = 0;
    *fehlerPos = -1;
    *fehlerDollar = 0;
    while (i < n) {
        int code = 0;
        size_t laenge = 1;
        if (t[i] == '$') {
            laenge = kat5Marke(t, n, i, &code);
            if (laenge == 0) {
                laenge = 1;
                code = 0;
                if (*fehlerPos < 0) { *fehlerPos = (int)i; *fehlerDollar = 1; }
            }
        } else {
            code = kat5Zeichencode((unsigned char)t[i]);
            if (code < 0) {
                code = 0;
                if (*fehlerPos < 0) *fehlerPos = (int)i;
            }
        }
        if (codes) codes[anzahl] = code;
        anzahl++;
        i += laenge;
    }
    return anzahl;
}

// kat5 belegt immer genau eine Zelle (Doku 3.3.15), unabhaengig vom Text; Fehler im Text meldet erzeugenKat5 in Pass 3.
int zaehleKat5(const char operand[]) {
    (void)operand;
    return 1;
}

void erzeugenKat5(const char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii) {
    size_t n;
    const char *text = kat4Text(operand, &n);
    int codes[1024];
    int fehlerPos, fehlerDollar;
    int ersteAusgabe = 1;

    if (n >= sizeof(codes) / sizeof(codes[0])) n = sizeof(codes) / sizeof(codes[0]) - 1;

    if (n == 0) {
        is_error3 = 1;
        printHell = 1;
        if (fehlerZaehleUndPruefe("kat5 ohne Text")) PRINT_FEHLER("%s", "kat5 ohne Text: der Operand ist leer.");
        return;
    }

    size_t zeichen = kat5Zerlegen(text, n, codes, &fehlerPos, &fehlerDollar);
    if (fehlerPos >= 0) {
        is_error3 = 1;
        printHell = 1;
        char schl[64];
        if (fehlerDollar) {
            snprintf(schl, sizeof(schl), "kat5 $ ohne Markenname, Position %i", fehlerPos);
            if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("kat5 Operand enthält $ ohne gültigen Markennamen ($wrzl, $inkb, $ingb) an Position: %i.", fehlerPos);
        } else {
            snprintf(schl, sizeof(schl), "kat5 Operand unzulässig, Position %i", fehlerPos);
            if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("kat5 Operand enthält unzulässige Zeichen an Position: %i.", fehlerPos);
        }
        return;
    }
    if (zeichen > KAT5_MAXZEICHEN) {
        is_error3 = 1;
        printHell = 1;
        char schl[64];
        snprintf(schl, sizeof(schl), "kat5 Operand zu lang, %i Zeichen", (int)zeichen);
        if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("kat5 Operand hat %i Zeichen, erlaubt sind höchstens %i (ein Wort); längere Texte stehen in mehreren kat5-Zeilen oder in kat6.", (int)zeichen, KAT5_MAXZEICHEN);
        return;
    }

    // Warnung bei Zustandsunstimmigkeit KB/GB (Doku 3.3.15): Der Zustand wird nur innerhalb des Operanden
    // gefuehrt, ist am Textanfang unbekannt, $inkb setzt KB, $ingb setzt GB.
    {
        int zustand = -1;   // -1 unbekannt, 0 KB, 1 GB
        size_t i = 0;
        while (i < n) {
            int code = 0;
            size_t laenge = 1;
            char text_w[160];
            if (text[i] == '$') {
                laenge = kat5Marke(text, n, i, &code);
                if (code == KAT5_INKB) zustand = 0;
                if (code == KAT5_INGB) zustand = 1;
            } else {
                char c = text[i];
                if (zustand == 1 && (isdigit((unsigned char)c) || c == '.' || c == ',' || c == '-' || c == ':' || c == '+')) {
                    snprintf(text_w, sizeof(text_w), "kat5: Zeichen '%c' an Position %i erscheint im Zustand GB (nach $ingb) als anderes Zeichen.", c, (int)i);
                    meldeWarnungOrt(lineAsmAufgeloest[iii].srcLine, text_w);
                } else if (zustand == 0 && c == '=') {
                    snprintf(text_w, sizeof(text_w), "kat5: Zeichen '=' an Position %i erscheint im Zustand KB (nach $inkb) als '+'.", (int)i);
                    meldeWarnungOrt(lineAsmAufgeloest[iii].srcLine, text_w);
                }
            }
            i += laenge;
        }
    }

    unsigned long long wert = 0;
    for (size_t k = 0; k < zeichen; k++) {
        wert |= (unsigned long long)codes[k] << (6 * (KAT5_MAXZEICHEN - 1 - k));   // erstes Zeichen links (Bit 29 bis 24)
    }
    char buffer[40];
    snprintf(buffer, sizeof(buffer), "      00 %011llo", wert);
    katAusgabeWort(machineCodeFile, hilfsFile, line, iii, buffer, &ersteAusgabe);
}

// ---------
// kat6 (Doku 3.3.18): komprimierter Text, 5 Zeichen je Maschinenwort, je Zeichen der 6-Bit-Eingabecode der
// Kodetabelle (Bits v u 8 4 2 1, Spalte "Eingabe Adresse"). Das erste Zeichen steht rechts (Bit 0 bis 5), das
// zweite links daneben usw., das fuenfte in Bit 24 bis 29; Bit 31 (z1) bleibt 0. Der Code 00 ist die Ziffer 0,
// deshalb gibt es keine Fuellung: In jedem Wort steht unmittelbar links vom letzten Zeichen ein Stoppbit 1
// (voll: Bit 30 = z2; bei m Zeichen im letzten Wort: Bit 6*m). Das letzte Wort traegt zusaetzlich z0 = 1
// (Bit 32 = 040000000000). Umschaltzeichen werden nicht eingefuegt. Vorrat: a bis z, 0 bis 9, Leerzeichen,
// . , - : + = / % ` und die Marken $wrzl (032), $inkb (057), $ingb (037) (ohne Beachtung der Gross-/Klein-
// schreibung, je Marke ein Zeichen). + und = haben denselben Code 020.

#define KAT6_WRZL 032
#define KAT6_INKB 057
#define KAT6_INGB 037

// Erkennt an Stelle i des Textes eine Marke. Liefert die Laenge der Marke und setzt *code, sonst 0.
static size_t kat6Marke(const char *t, size_t n, size_t i, int *code) {
    static const struct { const char *name; int code; } marken[] = {
        { "$wrzl", KAT6_WRZL }, { "$inkb", KAT6_INKB }, { "$ingb", KAT6_INGB }
    };
    for (size_t m = 0; m < sizeof(marken) / sizeof(marken[0]); m++) {
        size_t l = strlen(marken[m].name);
        size_t k = 0;
        if (i + l > n) continue;
        while (k < l && tolower((unsigned char)t[i + k]) == marken[m].name[k]) k++;
        if (k == l) { *code = marken[m].code; return l; }
    }
    return 0;
}

// Code eines einzelnen Zeichens ohne Marken; -1, wenn das Zeichen nicht zum Vorrat gehoert.
static int kat6Zeichencode(unsigned char c) {
    if (c >= '0' && c <= '7') return (int)(c - '0');          // 0 bis 7: 00 bis 07
    if (c == '8') return 010;
    if (c == '9') return 011;
    if (c >= 'a' && c <= 'i') return 021 + (int)(c - 'a');     // a bis i: 021 bis 031
    if (c >= 'j' && c <= 'r') return 041 + (int)(c - 'j');     // j bis r: 041 bis 051
    if (c >= 's' && c <= 'z') return 062 + (int)(c - 's');     // s bis z: 062 bis 071
    switch (c) {
        case ' ': return 012;
        case ':': return 015;
        case '+':
        case '=': return 020;
        case '.': return 033;
        case '-': return 040;
        case '`': return 060;
        case '/': return 061;
        case ',': return 073;
        case '%': return 074;
        default:  return -1;
    }
}

// Zerlegt den Text in Zeichen (wie kat5Zerlegen): Marke = ein Zeichen, unzulaessiges Zeichen (auch $ ohne
// gueltigen Markennamen) = ein Zeichen, damit Pass 2 und Pass 3 gleich zaehlen. codes darf NULL sein.
static size_t kat6Zerlegen(const char *t, size_t n, int *codes, int *fehlerPos, int *fehlerDollar) {
    size_t anzahl = 0;
    size_t i = 0;
    *fehlerPos = -1;
    *fehlerDollar = 0;
    while (i < n) {
        int code = 0;
        size_t laenge = 1;
        if (t[i] == '$') {
            laenge = kat6Marke(t, n, i, &code);
            if (laenge == 0) {
                laenge = 1;
                code = 0;
                if (*fehlerPos < 0) { *fehlerPos = (int)i; *fehlerDollar = 1; }
            }
        } else {
            code = kat6Zeichencode((unsigned char)t[i]);
            if (code < 0) {
                code = 0;
                if (*fehlerPos < 0) *fehlerPos = (int)i;
            }
        }
        if (codes) codes[anzahl] = code;
        anzahl++;
        i += laenge;
    }
    return anzahl;
}

int zaehleKat6(const char operand[]) {
    size_t n;
    int fehlerPos, fehlerDollar;
    const char *text = kat4Text(operand, &n);   // gleiche Behandlung der \-Zeichen wie bei kat4 und kat5
    return (int)((kat6Zerlegen(text, n, NULL, &fehlerPos, &fehlerDollar) + 4) / 5);
}

void erzeugenKat6(const char operand[], FILE *machineCodeFile, FILE *hilfsFile, const char *line, int iii) {
    size_t n;
    const char *text = kat4Text(operand, &n);
    int codes[1024];
    int fehlerPos, fehlerDollar;
    int ersteAusgabe = 1;

    if (n >= sizeof(codes) / sizeof(codes[0])) n = sizeof(codes) / sizeof(codes[0]) - 1;

    if (n == 0) {
        is_error3 = 1;
        printHell = 1;
        if (fehlerZaehleUndPruefe("kat6 ohne Text")) PRINT_FEHLER("%s", "kat6 ohne Text: der Operand ist leer.");
        return;
    }

    size_t zeichen = kat6Zerlegen(text, n, codes, &fehlerPos, &fehlerDollar);
    if (fehlerPos >= 0) {
        is_error3 = 1;
        printHell = 1;
        char schl[64];
        if (fehlerDollar) {
            snprintf(schl, sizeof(schl), "kat6 $ ohne Markenname, Position %i", fehlerPos);
            if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("kat6 Operand enthält $ ohne gültigen Markennamen ($wrzl, $inkb, $ingb) an Position: %i.", fehlerPos);
        } else {
            snprintf(schl, sizeof(schl), "kat6 Operand unzulässig, Position %i", fehlerPos);
            if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER("kat6 Operand enthält unzulässige Zeichen an Position: %i.", fehlerPos);
        }
        return;
    }

    // Warnung bei Zustandsunstimmigkeit KB/GB (Doku 3.3.18): Der Zustand wird nur innerhalb des Operanden
    // gefuehrt, ist am Textanfang unbekannt, $inkb setzt KB, $ingb setzt GB. Im Zustand GB zeigen Ziffern,
    // . , - : + / % und der Akzent ein anderes Zeichen, im Zustand KB zeigt = ein +.
    {
        int zustand = -1;   // -1 unbekannt, 0 KB, 1 GB
        size_t i = 0;
        while (i < n) {
            int code = 0;
            size_t laenge = 1;
            char text_w[160];
            if (text[i] == '$') {
                laenge = kat6Marke(text, n, i, &code);
                if (code == KAT6_INKB) zustand = 0;
                if (code == KAT6_INGB) zustand = 1;
            } else {
                char c = text[i];
                if (zustand == 1 && (isdigit((unsigned char)c) || c == '.' || c == ',' || c == '-' || c == ':' || c == '+'
                                     || c == '/' || c == '%' || c == '`')) {
                    snprintf(text_w, sizeof(text_w), "kat6: Zeichen '%c' an Position %i erscheint im Zustand GB (nach $ingb) als anderes Zeichen.", c, (int)i);
                    meldeWarnungOrt(lineAsmAufgeloest[iii].srcLine, text_w);
                } else if (zustand == 0 && c == '=') {
                    snprintf(text_w, sizeof(text_w), "kat6: Zeichen '=' an Position %i erscheint im Zustand KB (nach $inkb) als '+'.", (int)i);
                    meldeWarnungOrt(lineAsmAufgeloest[iii].srcLine, text_w);
                }
            }
            i += laenge;
        }
    }

    size_t woerter = (zeichen + 4) / 5;
    for (size_t w = 0; w < woerter; w++) {
        unsigned long long wert = 0;
        size_t m = 0;                                        // Zahl der Zeichen in diesem Wort (1 bis 5)
        for (size_t k = 0; k < 5 && w * 5 + k < zeichen; k++) {
            wert |= (unsigned long long)codes[w * 5 + k] << (6 * k);
            m++;
        }
        wert |= 1ULL << (6 * m);                             // Stoppbit links vom letzten Zeichen (bei m = 5: Bit 30 = z2)
        if (w + 1 == woerter) wert |= 040000000000ULL;       // z0 = 1 am letzten Wort
        char buffer[40];
        snprintf(buffer, sizeof(buffer), "      00 %011llo", wert);
        katAusgabeWort(machineCodeFile, hilfsFile, line, iii, buffer, &ersteAusgabe);
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
    char schl[256];
    snprintf(schl, sizeof(schl), "dz Operand %s nicht gültig", operand);
    if (fehlerZaehleUndPruefe(schl)) PRINT_FEHLER ("dz Operand %s nicht gültig.", operand);
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
