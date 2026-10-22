// ca82_pass3.c - Pass 3: Erzeugung von .obj, .mqo und .dmp
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"
#include "ca82_fluss.h"


extern char inputFileName[1024];   // wird weiter unten definiert

// Sucht die erste Quelltextzeile, in der `token` als ganzes Wort (ausserhalb eines Kommentars) vorkommt.
// Rueckgabe: Zeilennummer ab 1 oder 0, wenn nicht gefunden (z. B. wenn der Fehler aus einer Makroexpansion stammt).
static int findeQuellzeileFuerToken(const char *token) {
    size_t tl = strlen(token);
    if (tl == 0) return 0;
    FILE *f = fopen(inputFileName, "r");
    if (!f) return 0;
    char zeile[2048];
    int nr = 0, gefunden = 0;
    while (!gefunden && fgets(zeile, sizeof(zeile), f)) {
        nr++;
        char *kommentar_pos = strchr(zeile, ';');
        if (kommentar_pos) *kommentar_pos = '\0';
        for (char *p = zeile; (p = strstr(p, token)) != NULL; p++) {
            int vorne = (p == zeile) || !(isalnum((unsigned char)p[-1]) || p[-1] == '_');
            int hinten = !(isalnum((unsigned char)p[tl]) || p[tl] == '_');
            if (vorne && hinten) { gefunden = 1; break; }
        }
    }
    fclose(f);
    return gefunden ? nr : 0;
}

// Ist `text` ein Bezeichner (Buchstabe/_ gefolgt von Buchstaben, Ziffern, _), der kein bekanntes Symbol ist?
static int istUndefinierterBezeichner(const char *text) {
    if (!(isalpha((unsigned char)text[0]) || text[0] == '_')) return 0;
    for (const char *p = text; *p; p++) {
        if (!(isalnum((unsigned char)*p) || *p == '_')) return 0;
    }
    return !isSymbol((char *)text);
}

// Meldung im Format  <datei>:<zeile>: Fehler: <text>  auf STDERR (Zeile nur, wenn sie ermittelt werden konnte).
static void meldeFehlerMitOrt(const char *suchtoken, const char *text) {
    int zeile = findeQuellzeileFuerToken(suchtoken);
    fehlerMitOrt(zeile, text);
}

void outAdressError(const char *label, char *typ, char *text) {
    char line1[256];
    char xline[1024];
    char ortText[512];
    if (strncmp(typ, "Adresse (3)", 11) == 0 && istUndefinierterBezeichner(label)) {
        typ = "Symbol";
        text = "ist nicht definiert";
    }
    {
        const char *t = text;
        while (*t == ' ') t++;
        snprintf(ortText, sizeof(ortText), "%s '%s' %s", typ, label, t);
        meldeFehlerMitOrt(label, ortText);
    }
    snprintf(line1, sizeof(line1), "bei Operand: %s %s %s", label, typ, text);
    snprintf(xline, sizeof(xline), "%s%s%s",_weiss, line1,_normal);
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, xline);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");    
    lineCountAsmAufgeloestX++; 


}
// ----------------------

// Belegungspruefung (Pass 3): Jedes durch Befehle oder Daten (dw, da, dbn, dt, dto, dtm, dz)
// tatsaechlich beschriebene Wort der Trommel wird genau einmal belegt. Ueberschneidet sich die
// sequentielle Speicherbelegung mit einem frueher belegten Bereich (z.B. Programm laeuft in einen
// mit equ weiter hinten angelegten Datenbereich, oder ein spaeteres equ springt zurueck), ist das
// ein Fehler. `db` reserviert nur und beschreibt keine Zellen: es wird nicht geprueft.
#define BELEGUNG_ADRESSEN 010000   // 4 Oktalstellen
static int belegtVonZeile[BELEGUNG_ADRESSEN];   // 0 = frei, sonst Index in lineAsmAufgeloest + 1

static void meldeBelegungskonflikt(int adresse, int alteZeile, int neueZeile) {
    pruefeZeilenfeld(lineCountAsmAufgeloestX);
    char text[1024];
    char alt[300];
    char neu[300];
    snprintf(alt, sizeof(alt), "%.60s %.20s %.60s", lineAsmAufgeloest[alteZeile].sp1, lineAsmAufgeloest[alteZeile].sp2, lineAsmAufgeloest[alteZeile].sp3);
    snprintf(neu, sizeof(neu), "%.60s %.20s %.60s", lineAsmAufgeloest[neueZeile].sp1, lineAsmAufgeloest[neueZeile].sp2, lineAsmAufgeloest[neueZeile].sp3);
    snprintf(text, sizeof(text), ";%s*** 3 Fehler%s: Adresse %04o doppelt belegt: \"%s\" ueberschneidet sich mit \"%s\".",
             _violett, _normal, adresse, neu, alt);
    {
        int quellzeile = lineAsmAufgeloest[neueZeile].srcLine;
        char meldung[700];
        snprintf(meldung, sizeof(meldung), "Adresse %04o doppelt belegt: \"%s\" ueberschneidet sich mit \"%s\".", adresse, neu, alt);
        fehlerMitOrt(quellzeile, meldung);
    }
    lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, text);
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
    STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");
    lineCountAsmAufgeloestX++;
    is_error3 = 1;
}

// Belegt die Worte [von, bis) fuer die Zeile `zeile`; meldet pro Zeile hoechstens einen Konflikt.
static void belegeAdressen(int von, int bis, int zeile) {
    int gemeldet = 0;
    for (int a = von; a < bis; a++) {
        if (a < 0 || a >= BELEGUNG_ADRESSEN) {
            if (!gemeldet) {
                PRINT_FEHLER("Adresse %04o liegt ausserhalb der Trommel (0000-7777).", a);
                is_error3 = 1;
                gemeldet = 1;
            }
            break;
        }
        if (belegtVonZeile[a] != 0) {
            if (!gemeldet) {
                meldeBelegungskonflikt(a, belegtVonZeile[a] - 1, zeile);
                gemeldet = 1;
            }
        } else {
            belegtVonZeile[a] = zeile + 1;
        }
    }
}


// ----------------------

// Operationscodes, deren Adressteil nicht veraendert werden darf (Sonderbehandlung)
static const char *dreua[] = { "251", "271", "030", "032", "034", "036", "132", "134", "136", "031", "033", "035", "037", "131", "133", "135", "137"};
#define DREUA_SIZE (sizeof(dreua) / sizeof(dreua[0]))
static int istInDreua(const char *operationCode) {
    for (size_t k = 0; k < DREUA_SIZE; k++) {
        if (strcmp(operationCode, dreua[k]) == 0) return 1;
    }
    return 0;
}

// Trimmen eines Strings (Ergebnis in statischem Puffer, gueltig bis zum naechsten Aufruf)
static char *getTrimmed(const char *str) {
    while (*str && isspace((unsigned char)*str)) str++;
    const char *end = str + strlen(str) - 1;
    while (end > str && isspace((unsigned char)*end)) end--;
    static char trimmed[256];
    size_t len = (size_t)(end - str + 1);
    if (len >= sizeof(trimmed)) len = sizeof(trimmed) - 1;
    strncpy(trimmed, str, len);
    trimmed[len] = '\0';
    return trimmed;
}

// Zustand eines Pass-3-Laufs, der von den Einzelfunktionen gelesen und veraendert wird
typedef struct {
    FILE *obj;                 // .obj
    FILE *hilfs;               // .mqo
    int pc;                    // Befehlszaehler
    int relativ;               // relative Adresse (equ/spa)
    char formatString[256];    // Spaltenformat des Listings
} Pass3Zustand;

// start: Leitbefehl (Hauptleitadresse) in die Objektdatei
static void pass3Start(Pass3Zustand *z, int i, char *line, size_t lineGroesse) {
    char buffer[512];
    (void)lineGroesse;
    // Bei LEITADRESSE 00 (absolut codiertes Programm) wird kein Leitbefehl (Hauptleitadresse) vorangestellt.
    if ( startAdresse != 0 && leitadresseKennzeichen != 0) {
        snprintf(buffer, sizeof(buffer), "      21 0000 %04o", startAdresse);
        schreibeObjZeile(z->obj, buffer);
        copyAndIncrementLineElementsX(i,buffer);
        fprintf(z->hilfs,"%s\n", line);
    }
}

// equ, equ10, equ40, equ100: setzt den Befehlszaehler
static void pass3Equ(Pass3Zustand *z, int i, char *line, size_t lineGroesse, const char *operation, char *operand) {
    char buffer[512];
    int errorFlag = 0;
    int raAdr = 0;
    (void)errorFlag; (void)raAdr; (void)buffer;
    raAdr=z->relativ;               
    unsigned int dwValue = evaluateAddress(operand, "", &errorFlag, &raAdr, "", z->pc , &absolutadresse);
    if (errorFlag == 0) {
        z->relativ = dwValue;
        if (strcmp(operation, "equ100") == 0) {
            z->relativ = (z->relativ + 0100 - 1) & ~(0100 - 1); // Aufrunden auf nächste 0100
        } else if (strcmp(operation, "equ40") == 0) {
            z->relativ = (z->relativ + 0040 - 1) & ~(0040 - 1); // Aufrunden auf nächste 0040
        } else if (strcmp(operation, "equ10") == 0) {
            z->relativ = (z->relativ + 0010 - 1) & ~(0010 - 1); // Aufrunden auf nächste 0010
        }                
        snprintf(buffer, sizeof(buffer), "      20 0000 %04o", z->relativ);
        schreibeObjZeile(z->obj, buffer);
        replaceSubstring(line, lineGroesse, operand, z->relativ);
        fprintf(z->hilfs,"%s\n", line);
        replaceSubstring(lineAsmAufgeloest[i].sp3, sizeof(lineAsmAufgeloest[i].sp3), operand, z->relativ);
        copyAndIncrementLineElementsX(i,buffer);                    
        z->pc=z->relativ;
    } else {
        printHell = 1;
        is_error3=1;
    }
}

// spa: ersetzt die rechten beiden Oktalziffern des Befehlszaehlers
static void pass3Spa(Pass3Zustand *z, int i, char *line, size_t lineGroesse, char *operand) {
    char buffer[512];
    // Wirkt wie equ <adresse>: Die rechten beiden Oktalziffern des Befehlszaehlers werden durch den
    // Operanden ersetzt. Objektcode: Kennzeichenzeile 20 0000 <adresse>; im Listing und in der .mqo
    // steht statt des Operanden die berechnete Adresse (wie bei equ).
    long spaWert = 0;
    char spaMeldung[512];
    if ( pruefeSpaOperand(operand, &spaWert, spaMeldung, sizeof(spaMeldung)) ) {
        z->relativ = (int)spaAdresse((unsigned int)z->pc, spaWert);
        snprintf(buffer, sizeof(buffer), "      20 0000 %04o", z->relativ);
        schreibeObjZeile(z->obj, buffer);
        snprintf(lineAsmAufgeloest[i].sp3, sizeof(lineAsmAufgeloest[i].sp3), "%05o", z->relativ);
        snprintf(line, lineGroesse, z->formatString,
                lineAsmAufgeloest[i].sp1,
                lineAsmAufgeloest[i].sp2,
                lineAsmAufgeloest[i].sp3,
                lineAsmAufgeloest[i].sp4);
        line[strcspn(line, "\r")] = '\0';
        removeNewlines(line);
        fprintf(z->hilfs,"%s\n", line);
        copyAndIncrementLineElementsX(i,buffer);
        z->pc = z->relativ;
    } else {
        outAdressError(operand, "Operand", "ist ungültig (spa erwartet eine Zahl von 00 bis 77 oktal)");
        printHell = 1;
        is_error3 = 1;
    }
}

// abs: nur Pruefung des Operanden
static void pass3Abs(Pass3Zustand *z, int i, char *line, size_t lineGroesse, char *operand) {
    int errorFlag = 0;
    int raAdr = 0;
    (void)i;
    (void)line;
    (void)lineGroesse;
    raAdr=z->relativ;
    unsigned int dwValue = evaluateAddress(operand, "", &errorFlag, &raAdr, "", 0 , &absolutadresse);  // nur zweks Prüfung
    (void)dwValue; //Warnung unterdrücken
    if ( errorFlag != 0) {is_error3=1; printHell = 1; }
}

// dw: ein Datenwort
static void pass3Dw(Pass3Zustand *z, int i, char *line, size_t lineGroesse, const char *operandEin) {
    char buffer[512];
    int errorFlag = 0;
    int raAdr = 0;
    (void)errorFlag; (void)raAdr; (void)buffer;
    char operand[256];
    STRKOPIE(operand, operandEin);
    (void)lineGroesse;
    if (strspn(operand, "-0123456789") == strlen(operand) && operand[0] != '0' && !(operand[0] == '-' && operand[1] == '0') && strchr(operand + 1, '-') == NULL) {
        char octalString[MAX_LINE_LENGTH];
        if ( (operand[0] == '-') || (operand[0] == '+') ) {
            // Falls das erste Zeichen ein '-', prüfe das zweite Zeichen
            if (operand[1] == '0') {
                snprintf(octalString, sizeof(octalString), "%012lo", (unsigned long int) strtol(operand, NULL, 8));
            } else {
                snprintf(octalString, sizeof(octalString), "%ld", (unsigned long int) strtol(operand, NULL, 10));
            }
        } else {
            // Falls kein '-+', prüfe das erste Zeichen direkt
            if (operand[0] == '0') {
                snprintf(octalString, sizeof(octalString), "%012lo", (unsigned long int) strtol(operand, NULL, 8));
            } else {
                snprintf(octalString, sizeof(octalString), "%ld", (unsigned long int) strtol(operand, NULL, 10));
            }
        }
        STRKOPIE(operand, octalString); 
    }
    unsigned long long dwValue = evaluateValue(operand, &errorFlag);
    // Negative Werte als 33-Bit-Wort (11 Oktalziffern) im Zweierkomplement ausgeben.
    // Falls die C8205 negative Zahlen anders darstellt, nur diese Zeile aendern.
    // Zulaessiger Bereich: -2^32 ... 2^33-1 (33-Bit-Wort, vorzeichenlos bzw. Zweierkomplement).
    if (errorFlag == 0) {
        long long dwWert = (long long)dwValue;
        if (dwWert < -4294967296LL || dwWert > 0x1FFFFFFFFLL) {
            errorFlag = 1;   // passt nicht in ein Maschinenwort
        } else if (dwWert < 0) {
            dwValue &= 0x1FFFFFFFFULL;
        }
    }

    if (errorFlag == 0 ) {
        if ( dwValue == 0) {
            snprintf(buffer, sizeof(buffer), "%04o: 0",z->pc);
            schreibeObjZeile(z->obj, buffer);

        } else {
            snprintf(buffer, sizeof(buffer), "%04o: 00 %011llo", z->pc,dwValue);
            schreibeObjZeile(z->obj, buffer);
        }
        fprintf(z->hilfs,"%s\n", line);
        copyAndIncrementLineElementsX(i,buffer); 
    } else {
        snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operand); // Fehlerausgabe
        copyAndIncrementLineElementsX (i,buffer);
        if (evaluateValueGrund != NULL) {
            // Symbolfehler (Doku 3.3): Grund an die Standardmeldung anhaengen
            char dwMeldung[512];
            snprintf(dwMeldung, sizeof(dwMeldung), " ist ungültig (%s)", evaluateValueGrund);
            outAdressError(operand, "Operand", dwMeldung);
        } else {
            outAdressError(operand, "Operand", " ist ungültig");
        }
        printHell = 1;
        is_error3=1;
    }
    z->pc++;
}

static void pass3Da(Pass3Zustand *z, int i, char *line, size_t lineGroesse, char *operand) {
    char buffer[512];
    int errorFlag = 0;
    int raAdr = 0;
    (void)errorFlag; (void)raAdr; (void)buffer;
    (void)lineGroesse;
  char adrMeldung[512];
  if (!pruefeAdressausdruck(operand, adrMeldung, sizeof(adrMeldung))) {
    snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operand); // Fehlerausgabe
    copyAndIncrementLineElementsX (i,buffer);
    outAdressError(operand, "Operand", adrMeldung);
    printHell = 1;
    is_error3=1;
    z->pc++;
  } else {
    // Frueher wurde hier eine reine Dezimalzahl in eine Oktalzeichenkette umgewandelt und danach von
    // evaluateAddress wieder als Dezimalzahl gelesen (da 10 ergab Adresse 12). evaluateAddress versteht
    // Dezimal- und Oktalzahlen selbst; die Umwandlung entfaellt.
    raAdr=z->relativ;
    unsigned int dwValue = evaluateAddress(operand, "", &errorFlag, &raAdr, "", z->pc, &absolutadresse );
    if (errorFlag == 0 && dwValue > 07777) {
        // Wertebereich der Adresse (negative Werte erscheinen hier als sehr grosse Zahl)
        snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operand); // Fehlerausgabe
        copyAndIncrementLineElementsX (i,buffer);
        outAdressError(operand, "Operand", "Der Adressausdruck liegt außerhalb des Bereichs 00000 bis 07777.");
        printHell = 1;
        is_error3=1;
    } else if (errorFlag == 0 ) {
        if ( absolutadresse == 0 ) flussMerkeVerweis((int)dwValue);   // -WARN=TOT: da-Wort verweist auf diese Adresse
        if ( absolutadresse != 0 ) { 
            snprintf(buffer, sizeof(buffer), "%04o: 00 %04o",z->pc,dwValue<<9);
            schreibeObjZeile(z->obj, buffer);
        } else { 
            snprintf(buffer, sizeof(buffer), "%04o: 01 %04o",z->pc,dwValue<<9);
            schreibeObjZeile(z->obj, buffer);
        }
        fprintf(z->hilfs,"%s\n", line);
        copyAndIncrementLineElementsX(i,buffer); 
    } else {
        printAdressError(operand, "Adresse (1)", " ist ungültig", line);
        printHell = 1;
        is_error3=1;
    }
    z->pc++;
  }
}

// db: Bereich ohne Initialisierung
static void pass3Db(Pass3Zustand *z, int i, char *line, size_t lineGroesse, char *operand) {
    char buffer[512];
    (void)lineGroesse;
    // Bereich ohne initialisierung definieren
    if (1) { /* operand ist ein Array, nie NULL */
        int byteCount;
        if (operand[0] == '0') {
            byteCount = strtol(operand, NULL, 8);
        } else {
            byteCount = strtol(operand, NULL, 10);
        }
        z->pc += byteCount;
        snprintf(buffer, sizeof(buffer), "%04o: 20 %04o", z->pc-byteCount,z->pc);
        schreibeObjZeile(z->obj, buffer);
        fprintf(z->hilfs,"%s\n",line);
        copyAndIncrementLineElementsX(i,buffer); 
    } else {
        // eigentlich ein fehlerfall, der in pass2 gemeldet wurde
    }
}

// dbn: Bereich auf Null
static void pass3Dbn(Pass3Zustand *z, int i, char *line, size_t lineGroesse, char *operand) {
    char buffer[512];
    (void)lineGroesse;
    // Bereich auf Null definieren
    if (1) { /* operand ist ein Array, nie NULL */
        snprintf(buffer, sizeof(buffer), "%04o: 00 0",z->pc);
        schreibeObjZeile(z->obj, buffer);
        fprintf(z->hilfs,"%s\n",line);
        copyAndIncrementLineElementsX(i,buffer); 
        int byteCount;
        if (operand[0] == '0') {
            byteCount = strtol(operand, NULL, 8);
        } else {
            byteCount = strtol(operand, NULL, 10);
        }
        // Folgeworte des Bereichs: eigene Schleifenvariable k (das aeussere i ist der
        // Index der Quelltextzeile) und aufsteigende Adressen.
        for (int k = 0; k < byteCount - 1; k++) {
            snprintf(buffer, sizeof(buffer), "%04o: 00 0", z->pc + k + 1);
            schreibeObjZeile(z->obj, buffer);
            fprintf(z->hilfs, "\n");
            copyAndIncrementLineElementsSpOnly(i,buffer); 
        }
        z->pc += byteCount;
    } else {
         // eigentlich ein Fehlerfall, der in pass2 gemeldet wurde
    }
}

// Ergebnis des letzten pass3Befehl fuer die Ablaufpruefungen (-WARN=SPR, -WARN=TOT)
static char befehlCode[8];
static int  befehlHatZiel, befehlZiel, befehlZielAbsolut;

// Normale Maschinenbefehle (Kennzeichen 01) einschliesslich Fehlerfaelle
static void pass3Befehl(Pass3Zustand *z, int i, char *line, char *operation, char *operand) {
    char buffer[512];
    int errorFlag = 0;
    int raAdr = 0;
    const char semikolon = ';';
    // Normale Anweisungen mit Kennzeichen "01"

    // operation --> operationCode (geprüft)
    char *operationCode = getOperationCode(operation);
    befehlCode[0] = '\0'; befehlHatZiel = 0; befehlZiel = -1; befehlZielAbsolut = 0;
    STRKOPIE(befehlCode, operationCode);
    if (istInDreua(operationCode)) {
        // Operationen, deren Adreßteil nicht verändert werden darf, z.B. 030
        if (1) {  // != NULL und beginnt nicht mit Semikolon
            raAdr=0;
            unsigned int address = evaluateAddress(operand, "", &errorFlag, &raAdr, "", z->pc, &absolutadresse);
            if (errorFlag == 0 ) {
                snprintf(buffer, sizeof(buffer), "%04o: 00 %04o %s", z->pc, address, operationCode);
                schreibeObjZeile(z->obj, buffer);

                fprintf(z->hilfs,"%s\n", line);
                copyAndIncrementLineElementsX(i,buffer); 
            } else {
                printAdressError(operand, "Adresse (2)", " ist ungültig", line);
                is_error3 = 1;
                printHell = 1;
            }
        } else {
            snprintf(buffer, sizeof(buffer), "%04o: 00 %s", z->pc, operationCode);
            schreibeObjZeile(z->obj, buffer);
            fprintf(z->hilfs,"%s\n", line);
            copyAndIncrementLineElementsX(i,buffer); 
        }
    } else if (strcmp(operationCode, "XXX") != 0)  { 
         if (operand[0] != semikolon) { // != NULL und beginnt nicht mit Semikolon
            raAdr=z->relativ;
            unsigned int address = evaluateAddress(operand, "", &errorFlag, &raAdr, "", z->pc, &absolutadresse);
            if (errorFlag == 0) {
                befehlHatZiel = 1; befehlZiel = (int)address; befehlZielAbsolut = (absolutadresse != 0);
                if ( absolutadresse != 0 ) { 
                    snprintf(buffer, sizeof(buffer), "%04o: 00 %04o %s", z->pc, address, operationCode);
                    schreibeObjZeile(z->obj, buffer);
                } else {
                    snprintf(buffer, sizeof(buffer), "%04o: 01 %04o %s", z->pc, address, operationCode);
                    schreibeObjZeile(z->obj, buffer);
                }
                fprintf(z->hilfs,"%s\n", line);
                copyAndIncrementLineElementsX(i,buffer); 
            } else {
                snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operationCode); // Fehlerausgabe
                copyAndIncrementLineElementsX (i,buffer);
                outAdressError(operand, "Adresse (3)", " ist ungültig");
                is_error3 = 1;
                printHell = 1;
            }
        } else {
            snprintf(buffer, sizeof(buffer), "%04o: 01 %s", z->pc, operationCode);
            schreibeObjZeile(z->obj, buffer);
            fprintf(z->hilfs,"%s\n", line);
            copyAndIncrementLineElementsX(i,buffer); 
        }
    } else {
        snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operationCode); // Fehlerausgabe
        copyAndIncrementLineElementsX (i,buffer);
        outAdressError(operation, "Operationscode", " ist ungültig");
        is_error3 = 1;
        printHell = 1;
    }
    z->pc++;
}

// dt (no_kbgb 0), dto (1), dtm (2): Text ausgeben und Befehlszaehler weiterschalten
static void pass3Text(Pass3Zustand *z, int i, char *line, char *operand, char *textkonst, int anzahlBackslashes, int no_kbgb) {
    textPC = z->pc;
    if (anzahlBackslashes != 2) {
        erzeugenText(operand, z->obj, z->hilfs, line, no_kbgb, i);
        z->pc += zaehleText(operand, no_kbgb);
    } else {
        erzeugenText(textkonst, z->obj, z->hilfs, line, no_kbgb, i);
        if (textkonst[0] != '\0') {
            z->pc += zaehleText(textkonst, no_kbgb);
        }
    }
}

void pass3(char *machineCodeFileName, char *hilfsFileName, char *dmpFileName, char *testFileName) {
    printf("Erzeuge Kennzeichen-Befehle in Objektdatei %s\n\n", machineCodeFileName);

    FILE *machineCodeFile = oeffneAusgabedatei(machineCodeFileName, "w");  //.obj
    FILE *hilfsFile = oeffneAusgabedatei(hilfsFileName, "w");
    FILE *dmpFile = oeffneAusgabedatei(dmpFileName, "w");  //.dmp

    if (absprAktiv) absprStart(machineCodeFile);
    line_ausgegeben=0;
    Pass3Zustand zst = { machineCodeFile, hilfsFile, 0, 0, "" };

    memset(belegtVonZeile, 0, sizeof(belegtVonZeile));
    flussZuruecksetzen();

    zFlag = 0; // Unterscheidung 2. Spalte -- 3. Spalte

    int maxWidth1 = 0, maxWidth2 = 0, maxWidth3 = 0;

    // Anwendung ohne direkte Änderung der Originalwerte
    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        const char *trimmed1 = getTrimmed(lineAsmAufgeloest[i].sp1);
        const char *trimmed2 = getTrimmed(lineAsmAufgeloest[i].sp2);
        const char *trimmed3 = getTrimmed(lineAsmAufgeloest[i].sp3);
        if (*trimmed1 != ';' && *trimmed1 != '#' && *trimmed1 != '$' &&
            *trimmed1 != '*' && *trimmed1 != '&') {
            int len1 = strlen(trimmed1) + 2;
            if (len1 > maxWidth1) maxWidth1 = len1;
        }
        int len2 = strlen(trimmed2) + 2;
        int len3 = strlen(trimmed3) + 2;
        if (len2 > maxWidth2) maxWidth2 = len2;
        if (len3 > maxWidth3) maxWidth3 = len3;
    }

    snprintf(zst.formatString, sizeof(zst.formatString), "%%-%ds %%-%ds %%-%ds %%s\n", maxWidth1, maxWidth2, maxWidth3);

    // für die c82asm - Ausgabe
    lineCountAsmAufgeloestX = 0;

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        char textkonst[1024]="";
        

        // übergehen
        if (  ((lineAsmAufgeloest[i].sp1[0] == ';') || (lineAsmAufgeloest[i].sp1[0] == '#') || (lineAsmAufgeloest[i].sp1[0] == '$')  ||
                (lineAsmAufgeloest[i].sp1[0] == '&') || (strstr(lineAsmAufgeloest[i].sp1, "***") != NULL)   ) ) {
            continue;
        } 
        // Leerzeile
        if (lineAsmAufgeloest[i].sp1[0] == '\0' && lineAsmAufgeloest[i].sp2[0] == '\0' &&
            lineAsmAufgeloest[i].sp3[0] == '\0' && lineAsmAufgeloest[i].sp4[0] == '\0') 
        {
            continue;
        }



        int pcVorher = zst.pc;   // fuer die Belegungspruefung

        char label[256];     
        char operation[256]; 
        char kommentar_p[256]; 
        char operand[256];
        char line[MAX_LINE_LENGTH];

        removeNewlines(lineAsmAufgeloest[i].sp1) ;
        removeNewlines(lineAsmAufgeloest[i].sp2) ;
        removeNewlines(lineAsmAufgeloest[i].sp3) ;
        removeNewlines(lineAsmAufgeloest[i].sp4) ;

        STRKOPIE(label, lineAsmAufgeloest[i].sp1 );
        STRKOPIE(operation, lineAsmAufgeloest[i].sp2 );
        STRKOPIE(operand, lineAsmAufgeloest[i].sp3 );
        STRKOPIE(kommentar_p, lineAsmAufgeloest[i].sp4 );

        int zaehleBackslaShes = zaehleBackslashes(lineAsmAufgeloest[i].sp3);

        if (zaehleBackslaShes == 2) {
            extractBackslashContent(operand,textkonst);
/**    
            char *start = strchr(operand, '\\');  
            char *end = strrchr(operand, '\\');

            if (start && end && start != end) {
                start++;  // Nach dem ersten Backslash beginnen
                size_t length = end - start;

                strncpy(operand, start, length);
                operand[length] = '\0';  // Null-Terminierung nicht vergessen!
                STRKOPIE(textkonst,operand);
            }
*/
        } 

        char *trimmed = label;
        while (*trimmed == ' ' || *trimmed == '\t') trimmed++; // Leerzeichen & Tabs entfernen
        if (*trimmed == ';' || *trimmed == '#' || *trimmed == '$' || *trimmed == '*'|| *trimmed == '&') {
            snprintf(line, sizeof(line), "%.1000s %.1000s %.1000s %.1000s", 
                    lineAsmAufgeloest[i].sp1, 
                    lineAsmAufgeloest[i].sp2, 
                    lineAsmAufgeloest[i].sp3, 
                    lineAsmAufgeloest[i].sp4);
        } else {
            snprintf(line, sizeof(line), zst.formatString, 
                    lineAsmAufgeloest[i].sp1, 
                    lineAsmAufgeloest[i].sp2, 
                    lineAsmAufgeloest[i].sp3, 
                    lineAsmAufgeloest[i].sp4);
        }


        line[strcspn(line, "\r")] = '\0';
        removeNewlines(line);
 
        if (strlen(operation) > 0) {
            if (strcmp(operation, "start") == 0) {
                pass3Start(&zst, i, line, sizeof(line));
            } else if (strstr(operation, "equ") != NULL) {
                pass3Equ(&zst, i, line, sizeof(line), operation, operand);
            } else if (strcmp(operation, "spa") == 0) {
                pass3Spa(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "abs") == 0) {
                pass3Abs(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "dw") == 0) {
                pass3Dw(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "da") == 0) {
                pass3Da(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "db") == 0) {
                pass3Db(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "dbn") == 0) {
                pass3Dbn(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "dt") == 0) {
                pass3Text(&zst, i, line, operand, textkonst, zaehleBackslaShes, 0);
            } else if (strcmp(operation, "dto") == 0) {
                pass3Text(&zst, i, line, operand, textkonst, zaehleBackslaShes, 1);
            } else if (strcmp(operation, "dtm") == 0) {
                pass3Text(&zst, i, line, operand, textkonst, zaehleBackslaShes, 2);
            } else if (strcmp(operation, "dz") == 0) {
                textPC = zst.pc;
                dzAuswertung(operand, zst.obj, zst.hilfs, line, i);
                zst.pc++;
            } else if (strcmp(operation, "end") == 0) {
                // nix zu tun.
            } else {
                pass3Befehl(&zst, i, line, operation, operand);
                if (zst.pc == pcVorher + 1) flussMerkeBefehl(pcVorher, befehlCode, befehlHatZiel, befehlZiel, befehlZielAbsolut, i);
            }
        }

        // Belegungspruefung: equ/spa/start setzen nur den Zaehler, abs/end/db belegen keine Zelle.
        if ( zst.pc > pcVorher
             && strstr(operation, "equ") == NULL
             && strcmp(operation, "spa") != 0
             && strcmp(operation, "start") != 0
             && strcmp(operation, "abs") != 0
             && strcmp(operation, "end") != 0
             && strcmp(operation, "db") != 0 ) {
            belegeAdressen(pcVorher, zst.pc, i);
        }
        // Ablaufpruefungen: Datenworte und reservierte Bereiche (db) vermerken; Befehle wurden oben vermerkt.
        if ( zst.pc > pcVorher
             && (strcmp(operation, "dw") == 0 || strcmp(operation, "da") == 0 || strcmp(operation, "dbn") == 0
                 || strcmp(operation, "dt") == 0 || strcmp(operation, "dto") == 0 || strcmp(operation, "dtm") == 0
                 || strcmp(operation, "dz") == 0 || strcmp(operation, "db") == 0) ) {
            flussMerkeDaten(pcVorher, zst.pc, operation, i);
        }

        printHell = 0;   
    }
    printFormattedAsmListingX(lineAsmAufgeloestX, lineCountAsmAufgeloestX, dmpFile);
    erzeugeTestDatei(lineAsmAufgeloestX, lineCountAsmAufgeloestX, testFileName);

    if (!absprAktiv) fprintf(machineCodeFile, "/\n");   // bei --ABSPR entfaellt das Endekennzeichen
    fclose(machineCodeFile);
    fclose(hilfsFile);
    if (dmpFile) fclose(dmpFile);

}
