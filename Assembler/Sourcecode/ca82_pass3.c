// ca82_pass3.c - Pass 3: Erzeugung von .obj, .mqo und .dmp
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"
#include "ca82_fluss.h"
#include "ca82_berichte.h"


extern char inputFileName[1024];   // wird weiter unten definiert

// Sucht die erste Quelltextzeile, in der `token` als ganzes Wort (ausserhalb eines Kommentars) vorkommt.
// Rueckgabe: Zeilennummer ab 1 oder 0, wenn nicht gefunden (z. B. wenn der Fehler aus einer Makroexpansion stammt).
static int findeQuellzeileFuerToken(const char *token) {
    size_t tl = strlen(token);
    if (tl == 0) return 0;
    // Quelltext einschliesslich der mit $INCLUDE eingebundenen Dateien (fortlaufende Nummern, Doku 4.14)
    char zeile[2048];
    int nr = 0, gefunden = 0;
    while (!gefunden && nr < quellZeilenAnzahl()) {
        nr++;
        snprintf(zeile, sizeof(zeile), "%s", quellZeilenText(nr));
        char *kommentar_pos = strchr(zeile, ';');
        if (kommentar_pos) *kommentar_pos = '\0';
        for (char *p = zeile; (p = strstr(p, token)) != NULL; p++) {
            int vorne = (p == zeile) || !(isalnum((unsigned char)p[-1]) || p[-1] == '_');
            int hinten = !(isalnum((unsigned char)p[tl]) || p[tl] == '_');
            if (vorne && hinten) { gefunden = 1; break; }
        }
    }
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

// dwb (Doku 3.3.19): ein Datenwort aus einer Bitfolge. Der Operand besteht aus 1 bis 33 Ziffern 0 oder 1; die Folge
// ist immer dual (auch mit fuehrender 0) und steht rechtsbuendig im Wort: letzte Ziffer = z32, bei 33 Stellen
// erste Ziffer = z0. Kein Vorzeichen, kein Ausdruck, keine Hauptleitadresse. Objektzeile wie bei dw.
static void pass3Dwb(Pass3Zustand *z, int i, char *line, size_t lineGroesse, const char *operand) {
    char buffer[512];
    (void)lineGroesse;
    size_t n = strlen(operand);
    int gueltig = (n >= 1 && n <= 33 && strspn(operand, "01") == n);
    if (gueltig) {
        unsigned long long dwValue = 0;
        for (size_t k = 0; k < n; k++) dwValue = (dwValue << 1) | (unsigned long long)(operand[k] - '0');
        if (dwValue == 0) {
            snprintf(buffer, sizeof(buffer), "%04o: 0", z->pc);
        } else {
            snprintf(buffer, sizeof(buffer), "%04o: 00 %011llo", z->pc, dwValue);
        }
        schreibeObjZeile(z->obj, buffer);
        fprintf(z->hilfs, "%s\n", line);
        copyAndIncrementLineElementsX(i, buffer);
    } else {
        snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operand);   // Fehlerausgabe
        copyAndIncrementLineElementsX(i, buffer);
        outAdressError(operand, "Operand", " ist ungültig (dwb erwartet 1 bis 33 Ziffern 0 oder 1)");
        printHell = 1;
        is_error3 = 1;
    }
    z->pc++;
}

// dwh (Doku 3.3.19a): ein Datenwort aus 1 bis 8 Hexadezimalziffern 0-9, A-F oder a-f (Gross-/Kleinschreibung gleich). Jede
// Ziffer sind 4 Bit; die Folge steht rechtsbuendig im Wort (letzte Ziffer = z29 bis z32), z0 bleibt 0. Kein Vorzeichen,
// kein Praefix, kein Ausdruck, keine Hauptleitadresse. Objektzeile wie bei dw und dwb.
static void pass3Dwh(Pass3Zustand *z, int i, char *line, size_t lineGroesse, const char *operand) {
    char buffer[512];
    (void)lineGroesse;
    size_t n = strlen(operand);
    int gueltig = (n >= 1 && n <= 8 && strspn(operand, "0123456789abcdefABCDEF") == n);
    if (gueltig) {
        unsigned long long dwValue = 0;
        for (size_t k = 0; k < n; k++) {
            int c = (unsigned char)operand[k];
            int d = (c >= '0' && c <= '9') ? c - '0' : (c >= 'a' && c <= 'f') ? c - 'a' + 10 : c - 'A' + 10;
            dwValue = (dwValue << 4) | (unsigned long long)d;
        }
        if (dwValue == 0) {
            snprintf(buffer, sizeof(buffer), "%04o: 0", z->pc);
        } else {
            snprintf(buffer, sizeof(buffer), "%04o: 00 %011llo", z->pc, dwValue);
        }
        schreibeObjZeile(z->obj, buffer);
        fprintf(z->hilfs, "%s\n", line);
        copyAndIncrementLineElementsX(i, buffer);
    } else {
        snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operand);   // Fehlerausgabe
        copyAndIncrementLineElementsX(i, buffer);
        outAdressError(operand, "Operand", " ist ungültig (dwh erwartet 1 bis 8 Hexadezimalziffern 0-9 und A-F)");
        printHell = 1;
        is_error3 = 1;
    }
    z->pc++;
}

// ---- dwf und dwg (Doku 3.3.20, 3.3.21): Dezimalzahl exakt in ein Maschinenwort umrechnen ----
// Der Operand wird nicht in Gleitkommaarithmetik gelesen, sondern als Bruch D / 10^k (D = alle Ziffern als grosse
// Ganzzahl, k = Zahl der Stellen nach dem Punkt, bei dwg mal 10^E) mit einer kleinen Ganzzahlrechnung auf 32-Bit-Teilen
// umgerechnet; so entsteht keine Zwischenrundung, und die Mitte zwischen zwei Woertern wird genau erkannt.
#define GZ_TEILE 1400                      // 1400 * 32 Bit; reicht fuer 10^999 mal einen Operanden von 256 Stellen mit Reserve
typedef struct { unsigned int w[GZ_TEILE]; int n; } GrosseZahl;   // w[0] niedrigster Teil, n = Zahl der benutzten Teile (0 = Null)

static void gzNull(GrosseZahl *a) { a->n = 0; }

// a := a * m + d; Rueckgabe 1 bei Ueberlauf der Tabelle
static int gzMulAdd(GrosseZahl *a, unsigned int m, unsigned int d) {
    unsigned long long uebertrag = d;
    for (int i = 0; i < a->n; i++) {
        unsigned long long p = (unsigned long long)a->w[i] * m + uebertrag;
        a->w[i] = (unsigned int)(p & 0xFFFFFFFFULL);
        uebertrag = p >> 32;
    }
    if (uebertrag != 0) {
        if (a->n >= GZ_TEILE) return 1;
        a->w[a->n++] = (unsigned int)uebertrag;
    }
    return 0;
}

// Anzahl der Bits (0 bei Null)
static int gzBits(const GrosseZahl *a) {
    if (a->n == 0) return 0;
    unsigned int h = a->w[a->n - 1];
    int b = 0;
    while (h != 0) { b++; h >>= 1; }
    return (a->n - 1) * 32 + b;
}

// a := a << bits; Rueckgabe 1 bei Ueberlauf der Tabelle
static int gzShl(GrosseZahl *a, int bits) {
    if (a->n == 0 || bits <= 0) return 0;
    int teile = bits / 32, rest = bits % 32;
    if (a->n + teile + 1 > GZ_TEILE) return 1;
    unsigned int neu[GZ_TEILE];
    int n = a->n + teile + 1;
    for (int i = 0; i < n; i++) neu[i] = 0;
    for (int i = 0; i < a->n; i++) {
        unsigned long long v = (unsigned long long)a->w[i] << rest;
        neu[i + teile] |= (unsigned int)(v & 0xFFFFFFFFULL);
        neu[i + teile + 1] |= (unsigned int)(v >> 32);
    }
    while (n > 0 && neu[n - 1] == 0) n--;
    for (int i = 0; i < n; i++) a->w[i] = neu[i];
    a->n = n;
    return 0;
}

// r := a * b (r darf nicht a oder b sein); Rueckgabe 1 bei Ueberlauf der Tabelle
static int gzMul(GrosseZahl *r, const GrosseZahl *a, const GrosseZahl *b) {
    gzNull(r);
    if (a->n == 0 || b->n == 0) return 0;
    if (a->n + b->n > GZ_TEILE) return 1;
    for (int i = 0; i < a->n + b->n; i++) r->w[i] = 0;
    for (int i = 0; i < a->n; i++) {
        unsigned long long uebertrag = 0;
        for (int j = 0; j < b->n; j++) {
            unsigned long long p = (unsigned long long)a->w[i] * b->w[j] + r->w[i + j] + uebertrag;
            r->w[i + j] = (unsigned int)(p & 0xFFFFFFFFULL);
            uebertrag = p >> 32;
        }
        r->w[i + b->n] = (unsigned int)uebertrag;
    }
    r->n = a->n + b->n;
    while (r->n > 0 && r->w[r->n - 1] == 0) r->n--;
    return 0;
}

// -1, 0, 1 wie strcmp
static int gzVergleich(const GrosseZahl *a, const GrosseZahl *b) {
    if (a->n != b->n) return a->n < b->n ? -1 : 1;
    for (int i = a->n - 1; i >= 0; i--) {
        if (a->w[i] != b->w[i]) return a->w[i] < b->w[i] ? -1 : 1;
    }
    return 0;
}

// a := a - b (Voraussetzung a >= b)
static void gzSub(GrosseZahl *a, const GrosseZahl *b) {
    long long borgen = 0;
    for (int i = 0; i < a->n; i++) {
        long long d = (long long)a->w[i] - (i < b->n ? (long long)b->w[i] : 0LL) - borgen;
        if (d < 0) { d += 4294967296LL; borgen = 1; } else borgen = 0;
        a->w[i] = (unsigned int)d;
    }
    while (a->n > 0 && a->w[a->n - 1] == 0) a->n--;
}

// 10^p
static int gzZehnerpotenz(GrosseZahl *a, int p) {
    gzNull(a);
    a->w[0] = 1; a->n = 1;
    for (int i = 0; i < p; i++) if (gzMulAdd(a, 10, 0)) return 1;
    return 0;
}

// q := Quotient n / t auf ganze Zahl gerundet (genau in der Mitte nach oben, also weg von 0); q muss unter 2^maxBits liegen.
// Rueckgabe 0 = ok, 1 = Quotient zu gross oder Tabellenueberlauf.
static int gzTeileGerundet(const GrosseZahl *n, const GrosseZahl *t, int maxBits, unsigned long long *q) {
    GrosseZahl rest = *n;
    unsigned long long erg = 0;
    for (int bit = maxBits - 1; bit >= 0; bit--) {
        GrosseZahl tb = *t;
        if (gzShl(&tb, bit)) return 1;
        if (gzVergleich(&rest, &tb) >= 0) { gzSub(&rest, &tb); erg |= 1ULL << bit; }
    }
    if (gzVergleich(&rest, t) >= 0) return 1;   // Quotient haette mehr als maxBits Bits
    if (gzShl(&rest, 1)) return 1;
    if (gzVergleich(&rest, t) >= 0) erg++;      // 2 * Rest >= Teiler: aufrunden
    *q = erg;
    return 0;
}

// Zerlegt den Operanden von dwf (mitExponent = 0) oder dwg (mitExponent = 1) nach Doku 3.3.20/3.3.21:
// [+|-] Ziffern [. Ziffern] [E [+|-] 1 bis 3 Ziffern]. Rueckgabe 0 = ok, sonst 1.
static int dezimalZerlegen(const char *s, int mitExponent, int *negativ, GrosseZahl *d, int *nachkomma, int *zehnerExp) {
    *negativ = 0; *nachkomma = 0; *zehnerExp = 0;
    gzNull(d);
    if (*s == '+' || *s == '-') { *negativ = (*s == '-'); s++; }
    int stellen = 0;
    while (*s >= '0' && *s <= '9') { if (gzMulAdd(d, 10, (unsigned int)(*s - '0'))) return 1; s++; stellen++; }
    if (stellen == 0) return 1;
    if (*s == '.') {
        s++;
        int nach = 0;
        while (*s >= '0' && *s <= '9') { if (gzMulAdd(d, 10, (unsigned int)(*s - '0'))) return 1; s++; nach++; }
        if (nach == 0) return 1;
        *nachkomma = nach;
    }
    if (mitExponent && (*s == 'E' || *s == 'e')) {
        s++;
        int expNegativ = 0, ziffern = 0, wert = 0;
        if (*s == '+' || *s == '-') { expNegativ = (*s == '-'); s++; }
        while (*s >= '0' && *s <= '9') { wert = wert * 10 + (*s - '0'); s++; ziffern++; if (ziffern > 3) return 1; }
        if (ziffern == 0) return 1;
        *zehnerExp = expNegativ ? -wert : wert;
    }
    return *s != '\0';
}

// dwf: gebrochene Festkommazahl. wort = x * 2^32, gerundet, bei negativem x im Zweierkomplement (33 Bit).
// Rueckgabe 0 = ok, 1 = Aufbau des Operanden falsch, 2 = Zahlenbereich.
static int dezimalZuFestkomma(const char *operand, unsigned long long *wort) {
    int neg, k, e10;
    GrosseZahl d, t;
    if (dezimalZerlegen(operand, 0, &neg, &d, &k, &e10)) return 1;
    if (d.n == 0) { *wort = 0; return 0; }
    if (gzZehnerpotenz(&t, k) || gzShl(&d, 32)) return 2;
    unsigned long long q;
    if (gzTeileGerundet(&d, &t, 40, &q)) return 2;
    if (q == 0) { *wort = 0; return 0; }
    if (neg ? q > (1ULL << 32) : q > 0xFFFFFFFFULL) return 2;
    *wort = neg ? ((1ULL << 33) - q) : q;
    return 0;
}

// dwg: Gleitkommazahl in der internen Darstellung: z0 Vorzeichen, z1..z6 Exponent e' = e + 32, z7..z32 Mantisse (26 Bit,
// das erste Bit ist 1). Rueckgabe 0 = ok, 1 = Aufbau falsch, 2 = Betrag zu gross (e' > 63), 3 = Betrag zu klein (e' < 0).
static int dezimalZuGleitkomma(const char *operand, unsigned long long *wort) {
    int neg, k, e10;
    GrosseZahl d, a, b;
    if (dezimalZerlegen(operand, 1, &neg, &d, &k, &e10)) return 1;
    if (d.n == 0) { *wort = 0; return 0; }
    int p = e10 - k;                         // Wert = D * 10^p
    a = d;
    gzNull(&b); b.w[0] = 1; b.n = 1;
    if (p >= 0) {
        GrosseZahl z, prod;
        if (gzZehnerpotenz(&z, p) || gzMul(&prod, &d, &z)) return 2;   // Betrag viel zu gross
        a = prod;
    } else if (gzZehnerpotenz(&b, -p)) {
        return 3;                                                        // Betrag viel zu klein
    }
    // e mit 2^(e-1) <= a/b < 2^e
    int l = gzBits(&a) - gzBits(&b);
    GrosseZahl x = a, y = b;
    if (l >= 0) { if (gzShl(&y, l)) return 2; } else { if (gzShl(&x, -l)) return 3; }
    int e = (gzVergleich(&x, &y) >= 0 ? l : l - 1) + 1;
    if (e > 40) return 2;
    if (e < -80) return 3;
    int s = 26 - e;                          // Mantisse M = a/b * 2^s, 2^25 <= M < 2^26 vor dem Runden
    if (s >= 0) { if (gzShl(&a, s)) return 2; } else { if (gzShl(&b, -s)) return 3; }
    unsigned long long m;
    if (gzTeileGerundet(&a, &b, 27, &m)) return 2;
    if (m == (1ULL << 26)) { m = 1ULL << 25; e++; }   // Rundung ergab 1: Mantisse 0,5, Exponent um 1 groesser
    int eg = e + 32;
    if (eg > 63) return 2;
    if (eg < 0) return 3;
    *wort = ((unsigned long long)(neg ? 1 : 0) << 32) | ((unsigned long long)eg << 26) | m;
    return 0;
}

// dwf und dwg: ein Datenwort aus einer Dezimalzahl. Objektzeile wie bei dw und dwb. Fehler (Aufbau oder Zahlenbereich) meldet
// Pass 3 als ungueltigen Operanden; die Meldungszeile nennt den Operanden.
static void pass3Zahlwort(Pass3Zustand *z, int i, char *line, const char *operand, int istDwg) {
    char buffer[512];
    unsigned long long wort = 0;
    int rc = istDwg ? dezimalZuGleitkomma(operand, &wort) : dezimalZuFestkomma(operand, &wort);
    if (rc == 0) {
        flussZahlwortIstNull = (wort == 0);
        if (wort == 0) {
            snprintf(buffer, sizeof(buffer), "%04o: 0", z->pc);
        } else {
            snprintf(buffer, sizeof(buffer), "%04o: 00 %011llo", z->pc, wort);
        }
        schreibeObjZeile(z->obj, buffer);
        fprintf(z->hilfs, "%s\n", line);
        copyAndIncrementLineElementsX(i, buffer);
    } else {
        char *grund;
        if (rc == 1) {
            grund = istDwg ? " ist ungültig (dwg erwartet [+|-]Ziffern[.Ziffern][E[+|-]1 bis 3 Ziffern])"
                           : " ist ungültig (dwf erwartet [+|-]Ziffern[.Ziffern])";
        } else if (!istDwg) {
            grund = " ist ungültig (dwf: Zahlenbereich -1 bis 1-2^-32 überschritten)";
        } else if (rc == 2) {
            grund = " ist ungültig (dwg: Betrag größer als 2^31-2^5)";
        } else {
            grund = " ist ungültig (dwg: Betrag ungleich 0 kleiner als 2^-33)";
        }
        snprintf(buffer, sizeof(buffer), "%04o: %sEE%s %04o %s   ", z->pc, _violett, _normal, 0, operand);   // Fehlerausgabe
        copyAndIncrementLineElementsX(i, buffer);
        outAdressError(operand, "Operand", grund);
        printHell = 1;
        is_error3 = 1;
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

// kat4: komprimierten Text ausgeben (4 Zeichen je Wort) und Befehlszaehler weiterschalten
static void pass3Kat4(Pass3Zustand *z, char *line, char *operand, char *textkonst, int anzahlBackslashes, int i) {
    const char *text = (anzahlBackslashes != 2) ? operand : textkonst;
    textPC = z->pc;
    erzeugenKat4(text, z->obj, z->hilfs, line, i);
    z->pc += zaehleKat4(text);
}

// kat5: komprimierten Text ausgeben (5 Zeichen je Wort) und Befehlszaehler weiterschalten
static void pass3Kat5(Pass3Zustand *z, char *line, char *operand, char *textkonst, int anzahlBackslashes, int i) {
    const char *text = (anzahlBackslashes != 2) ? operand : textkonst;
    textPC = z->pc;
    erzeugenKat5(text, z->obj, z->hilfs, line, i);
    z->pc += zaehleKat5(text);
}

// kat6: komprimierten Text im Eingabecode ausgeben (5 Zeichen je Wort, Stoppbit) und Befehlszaehler weiterschalten
static void pass3Kat6(Pass3Zustand *z, char *line, char *operand, char *textkonst, int anzahlBackslashes, int i) {
    const char *text = (anzahlBackslashes != 2) ? operand : textkonst;
    textPC = z->pc;
    erzeugenKat6(text, z->obj, z->hilfs, line, i);
    z->pc += zaehleKat6(text);
}

void pass3(char *machineCodeFileName, char *hilfsFileName, char *dmpFileName, char *testFileName) {
    printf("Erzeuge Kennzeichen-Befehle in Objektdatei %s\n\n", machineCodeFileName);

    FILE *machineCodeFile = oeffneAusgabedatei(machineCodeFileName, "w");  //.obj
    FILE *hilfsFile = oeffneAusgabedatei(hilfsFileName, "w");
    FILE *dmpFile = oeffneAusgabedatei(dmpFileName, "w");  //.dmp

    if (absprAktiv) absprStart(machineCodeFile);
    if (!absprAktiv) schreibeObjPre(machineCodeFile);   // ;#PRECOMMAND: vor dem ersten Wort (ab 1.03-009)
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
        

        // --makros: Herkunft je Makroaufruf als Kommentarzeile ins Listing (steht in sp4 der ";+++"-Zeile)
        if (makrolisteAktiv && strncmp(lineAsmAufgeloest[i].sp1, ";+++ ", 5) == 0 &&
            strncmp(lineAsmAufgeloest[i].sp4, ";+++ Makro ", 11) == 0) {
            pruefeZeilenfeld(lineCountAsmAufgeloestX);
            lineAsmAufgeloestX[lineCountAsmAufgeloestX].adrValid = 0;
            STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp0, "");
            STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp1, lineAsmAufgeloest[i].sp4);
            STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp2, "");
            STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp3, "");
            STRKOPIE(lineAsmAufgeloestX[lineCountAsmAufgeloestX].sp4, "");
            lineCountAsmAufgeloestX++;
            continue;
        }
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
            } else if (strcmp(operation, "dwb") == 0) {
                pass3Dwb(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "dwh") == 0) {
                pass3Dwh(&zst, i, line, sizeof(line), operand);
            } else if (strcmp(operation, "dwf") == 0) {
                pass3Zahlwort(&zst, i, line, operand, 0);
            } else if (strcmp(operation, "dwg") == 0) {
                pass3Zahlwort(&zst, i, line, operand, 1);
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
            } else if (strcmp(operation, "kat4") == 0) {
                pass3Kat4(&zst, line, operand, textkonst, zaehleBackslaShes, i);
            } else if (strcmp(operation, "kat5") == 0) {
                pass3Kat5(&zst, line, operand, textkonst, zaehleBackslaShes, i);
            } else if (strcmp(operation, "kat6") == 0) {
                pass3Kat6(&zst, line, operand, textkonst, zaehleBackslaShes, i);
            } else if (strcmp(operation, "dz") == 0) {
                textPC = zst.pc;
                dzAuswertung(operand, zst.obj, zst.hilfs, line, i);
                zst.pc++;
            } else if (strcmp(operation, "end") == 0 || strcmp(operation, "begin") == 0 || strcmp(operation, "bend") == 0) {
                // nix zu tun (begin/bend erzeugen weder Code noch belegen sie Speicher).
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
             && strcmp(operation, "begin") != 0
             && strcmp(operation, "bend") != 0
             && strcmp(operation, "db") != 0 ) {
            belegeAdressen(pcVorher, zst.pc, i);
        }
        // Ablaufpruefungen: Datenworte und reservierte Bereiche (db) vermerken; Befehle wurden oben vermerkt.
        if ( zst.pc > pcVorher
             && (strcmp(operation, "dw") == 0 || strcmp(operation, "dwb") == 0 || strcmp(operation, "dwh") == 0 || strcmp(operation, "dwf") == 0 || strcmp(operation, "dwg") == 0 || strcmp(operation, "da") == 0 || strcmp(operation, "dbn") == 0
                 || strcmp(operation, "dt") == 0 || strcmp(operation, "dto") == 0 || strcmp(operation, "dtm") == 0 || strcmp(operation, "kat4") == 0 || strcmp(operation, "kat5") == 0 || strcmp(operation, "kat6") == 0
                 || strcmp(operation, "dz") == 0 || strcmp(operation, "db") == 0) ) {
            flussMerkeDaten(pcVorher, zst.pc, operation, i);
        }

        printHell = 0;   
    }
    printFormattedAsmListingX(lineAsmAufgeloestX, lineCountAsmAufgeloestX, dmpFile);
    erzeugeTestDatei(lineAsmAufgeloestX, lineCountAsmAufgeloestX, testFileName);

    if (!absprAktiv) schreibeObjPost(machineCodeFile);   // ;#POSTCOMMAND: hinter dem letzten Wort, vor dem Endekennzeichen
    if (!absprAktiv) schreibeLochbilder(machineCodeFile, "/");   // bei --ABSPR entfaellt das Endekennzeichen
    fclose(machineCodeFile);
    fclose(hilfsFile);
    if (dmpFile) fclose(dmpFile);

}
