// ca82_pass2.c - Pass 2: Adressen, Symboltabelle, Fehlermarken
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"


// ####################################




void sanitizeLabel(char *label) {
    if (label == NULL || strlen(label) == 0) {
        return; 
    }

    if (isspace(label[0])) {
        label[0] = '\0'; 
    }
}

void printLineIfNotPrinted(const char *line) {
    if (line_ausgegeben == 0) {
        printf("%s\n", line);
        line_ausgegeben = 1;
    }
}

void testeAdress(char *label, char *line) {
    char message[100];
    if (strlen(label) > MAX_SYMBOL_LENGTH) {
        printLineIfNotPrinted(line);
        is_error2=1;
        snprintf(message, sizeof(message), " ist länger als %d Zeichen.", MAX_LABEL_LENGTH);
        printLabelError(label, "Label", message, line);
        //char temp[sizeof(label)+1];
        memmove(label + 1, label, strlen(label) + 1);
        label[0] = ';';
    }
    if (isValidLabel(label) == false ) {
        printLineIfNotPrinted(line);
        is_error2=1;
        snprintf(message, sizeof(message), "   Label: \"%s\" enthält unzulässige Zeichen", label);
        printLabelError(label, "", message, line);
    }
    char *pos = strstr(line, label); // Finde das Label in der Zeile
    if (pos) {
        pos += strlen(label); // Springe hinter das Label
        
        // Prüfe, ob direkt danach ein Doppelpunkt steht
        if (*pos == ':') {
            pos++; // Überspringe den Doppelpunkt
            
            // Überspringe Leerzeichen und Tabs nach dem Doppelpunkt
            while (*pos == ' ' || *pos == '\t') {
                pos++;
            }
        
            // Prüfe, ob noch ein Substring folgt
            if (*pos == '\0') {
                printLineIfNotPrinted(line);
                is_error2 = 1; 
                snprintf(message, sizeof(message), "   Label: \"%s\" steht ohne Operation in der Zeile.", label);
                printLabelError(label, "", message, line);
            }
        }
    }
}


void extractBackslashContent(char *line, char *textkonst) {
    char *start = strchr(line, '\\');  // Finde ersten Backslash
    if (!start) return;  // Falls kein Backslash gefunden, nichts tun

    char *end = strchr(start + 1, '\\');  // Finde zweiten Backslash
    if (!end) return;  // Falls kein zweiter Backslash gefunden, nichts tun

    // Extrahiere den Inhalt zwischen den Backslashes
    size_t len = end - start + 1;
    strncpy(textkonst, start, len);
    textkonst[len] = '\0';

    // Entferne den extrahierten Teil aus `line`
    memmove(start, end + 1, strlen(end + 1) + 1);
}

int zaehleText(char operand[], int no_kbgb);

// Zustand eines Pass-2-Laufs, der von den Einzelfunktionen gelesen und veraendert wird
typedef struct {
    int i;                      // Index in lineAsmAufgeloestTemp; meldeFehlerP2 darf ihn weiterzaehlen
    unsigned int pc;            // Befehlszaehler
    unsigned int relativ;       // relative Adresse (equ/spa)
    int istStart;               // 1, sobald `start` gelesen wurde
    int fehlerP;                // Fehlerkennzeichen von evaluateAddress / sternadresseBearbeiten
    int raAdr;                  // Hilfswert fuer evaluateAddress
    char line[MAX_LINE_LENGTH]; // Zeilentext fuer Meldungen (in Pass 2 leer)
    char operation[256];
    char operand[256];
    char label[256];
    char textkonst[1024];       // \...\-Text, aus dem Operanden herausgeschnitten
} Pass2Zustand;

// Zeile unveraendert nach lineAsmAufgeloest uebernehmen
static void pass2KopiereZeile(int i) {
    pruefeZeilenfeld(lineCountAsmAufgeloest);
    STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp1, lineAsmAufgeloestTemp[i].sp1);
    STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp2, lineAsmAufgeloestTemp[i].sp2);
    STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp3, lineAsmAufgeloestTemp[i].sp3);
    STRKOPIE(lineAsmAufgeloest[lineCountAsmAufgeloest].sp4, lineAsmAufgeloestTemp[i].sp4);
    lineAsmAufgeloest[lineCountAsmAufgeloest].srcLine = lineAsmAufgeloestTemp[i].srcLine;
    lineCountAsmAufgeloest++;
}

// Kommentar-, Pragma- und Fehlerzeilen sowie Leerzeilen belegen nichts und werden nur uebernommen
static int pass2IstKommentarOderLeer(const lineElements *e) {
    if ( e->sp1[0] == ';' || e->sp1[0] == '#' || e->sp1[0] == '$' || e->sp1[0] == '&' ||
         strstr(e->sp1, "***") != NULL ) {
        return 1;
    }
    return e->sp1[0] == '\0' && e->sp2[0] == '\0' && e->sp3[0] == '\0' && e->sp4[0] == '\0';
}

// Operation, Operand und Label der Zeile in den Zustand uebernehmen und das Label pruefen
static void pass2ZeileVorbereiten(Pass2Zustand *z) {
    char message[1024];

    z->textkonst[0] = '\0';
    // Zeile zuerst kopieren: extractBackslashContent schneidet den \...\-Text
    // aus sp3 heraus, Pass 3 braucht ihn aber noch in lineAsmAufgeloest.
    pass2KopiereZeile(z->i);
    extractBackslashContent(lineAsmAufgeloestTemp[z->i].sp3, z->textkonst);

    STRKOPIE(z->operation, lineAsmAufgeloestTemp[z->i].sp2);
    STRKOPIE(z->operand, lineAsmAufgeloestTemp[z->i].sp3);
    STRKOPIE(z->label, "");
    if ( isValidLabel(lineAsmAufgeloestTemp[z->i].sp1) )  {
        STRKOPIE(z->label, lineAsmAufgeloestTemp[z->i].sp1);
        if (strlen(z->label) > MAX_SYMBOL_LENGTH) {
            printLineIfNotPrinted(z->line);
            is_error2 = 1;
            snprintf(message, sizeof(message), "Label ist länger als %d Zeichen.", MAX_LABEL_LENGTH);
            MELDE_FEHLER_P2(z->i, message );
            memmove(z->label + 1, z->label, strlen(z->label) + 1);
            z->label[0] = ';';
            if ( strlen(z->operation) < 1 ) {
                is_error2 = 1;
                snprintf(message, sizeof(message), "Label: \"%s\" ohne `Operation`.", z->label);
                MELDE_FEHLER_P2(z->i, message );
            }
        }
    } else if ( lineAsmAufgeloestTemp[z->i].sp1[0] != '\0' ) {
        // Ein Label, das nicht gueltig ist (Ziffer am Anfang, Zeichen wie - . oder ae), wurde frueher
        // still verworfen und fehlte dann ohne Meldung in .sym und Symboltabelle.
        is_error2 = 1;
        snprintf(message, sizeof(message), "Label \"%s\" ist unzulaessig: erlaubt sind Buchstaben, Ziffern und _, das erste Zeichen ist keine Ziffer.", lineAsmAufgeloestTemp[z->i].sp1);
        MELDE_FEHLER_P2(z->i, message );
    }
}

// Marke allein auf der Zeile, oder Maschinenbefehl: Symbol eintragen und Befehlszaehler erhoehen
static void pass2Befehl(Pass2Zustand *z) {
    char message[1024];

    if ( z->pc > 0 && z->istStart == 0 ) {
        is_error2 = 1;
        MELDE_FEHLER_P2(z->i, "Operationscode `start` fehlt als erste Anweisung.");
    }

    if (z->operation[0] == '\0') {
        // Marke allein auf der Zeile (ohne Operation): Die Zeile belegt keinen Speicher.
        // Die Marke erhaelt die Adresse der naechsten Zeile, die Speicher belegt;
        // der Befehlszaehler wird NICHT erhoeht (sonst waeren alle folgenden Marken um 1 zu gross).
        if ( isValidLabel(lineAsmAufgeloestTemp[z->i].sp1) )  {
            if ( z->istStart == 0 ) {
                // Doku 3.7: Ein Label vor `start` ist ein Fehler.
                is_error2 = 1;
                snprintf(message, sizeof(message), "Ein Label: \"%s\" vor `start` ist nicht zulaessig.", lineAsmAufgeloestTemp[z->i].sp1);
                MELDE_FEHLER_P2(z->i, message );
            } else {
                addSymbol(lineAsmAufgeloestTemp[z->i].sp1, z->pc, z->relativ, lineAsmAufgeloestTemp[z->i].sp2, lineAsmAufgeloestTemp[z->i].sp3, 1, z->i);
            }
        }
    } else if (isKeywordMatch(z->operation) == 1  /* nicht gefunden */) {
        if ( isValidLabel(lineAsmAufgeloestTemp[z->i].sp1) )  {
            addSymbol(lineAsmAufgeloestTemp[z->i].sp1, z->pc, z->relativ, lineAsmAufgeloestTemp[z->i].sp2, lineAsmAufgeloestTemp[z->i].sp3, 1, z->i);
        }
        z->pc++;
    }
}

// start: Startadresse lesen, Befehlszaehler auf 0
static void pass2Start(Pass2Zustand *z) {
    if ( z->istStart > 0 ) {
        is_error2 = 1;
        MELDE_FEHLER_P2(z->i, "Operationscode `start` darf nur einmal vorkommen.");
    }
    z->istStart = 1;
    z->pc = 0;
    if (strlen(z->label) > 0) {
        char message[1024];
        // Doku 3.7: Ein Label vor `start` ist ein Fehler (frueher nur still verworfen).
        is_error2 = 1;
        snprintf(message, sizeof(message), "Ein Label: \"%s\" vor `start` ist nicht zulaessig.", z->label);
        MELDE_FEHLER_P2(z->i, message );
    }
    if (!strchr(z->operand, ';')) {
        z->raAdr = z->relativ;
        startAdresse = evaluateAddress(z->operand, "", &z->fehlerP, &z->raAdr, z->label, z->pc, &absolutadresse);
        PRINT_MSG("Startadresse: %04o",startAdresse);
        if (( absolutadresse != 0 ) || (z->fehlerP != 0 ))  {
            is_error2 = 1;
            MELDE_FEHLER_P2(z->i, "Operand hinter `start` ist keine Konstante.");
        }
    }
}

// equ, equ10, equ40, equ100: setzt den Befehlszaehler
static void pass2Equ(Pass2Zustand *z) {
    unsigned int address = 0;
    z->raAdr = z->relativ;
    if (z->operand[0] == '*') {
        address = sternadresseBearbeiten(z->operand, z->line, &z->fehlerP, z->pc) ;
        if (strcmp(z->operation, "equ100") == 0) {
            address = (address + 0100 - 1) & ~(0100 - 1); // Aufrunden auf nächste 0100
        } else if (strcmp(z->operation, "equ40") == 0) {
            address = (address + 0040 - 1) & ~(0040 - 1); // Aufrunden auf nächste 0040
        } else if (strcmp(z->operation, "equ10") == 0) {
            address = (address + 0010 - 1) & ~(0010 - 1); // Aufrunden auf nächste 0010
        }
    } else {
        address = evaluateAddress(z->operand, "", &z->fehlerP, &z->raAdr, z->label, z->pc, &absolutadresse);
        if ( z->fehlerP != 0) { is_error2 = 1; printHell = 1; }
    }
    z->pc = address;
    if ( isValidLabel(z->label) ) {
        addSymbol(z->label, address, z->relativ, z->operation, z->operand, 2, z->i);
    }
    z->relativ = z->pc;
}

// spa: wie equ, aber der Wert ist der Befehlszaehler mit ersetzten rechten beiden Oktalziffern.
// Das Label erhaelt die so berechnete Adresse (wie bei equ *).
static void pass2Spa(Pass2Zustand *z) {
    char message[1024];
    long spaWert = 0;
    if ( pruefeSpaOperand(z->operand, &spaWert, message, sizeof(message)) ) {
        unsigned int address = spaAdresse(z->pc, spaWert);
        z->pc = address;
        if ( isValidLabel(z->label) ) {
            addSymbol(z->label, address, z->relativ, z->operation, z->operand, 15, z->i);
        }
        z->relativ = z->pc;
    } else {
        is_error2 = 1;
        MELDE_FEHLER_P2(z->i, message );
    }
}

// abs: Symbol mit konstantem Wert (nicht verschieblich)
static void pass2Abs(Pass2Zustand *z) {
    char message[1024];
    z->raAdr = z->relativ;
    unsigned int address = evaluateAddress(z->operand, "", &z->fehlerP, &z->raAdr, z->label, z->pc, &absolutadresse);
    if (( absolutadresse != 0 ) || (z->fehlerP != 0 ))  {
        is_error2 = 1;
        snprintf(message, sizeof(message), "Operand: \"%s\" ist keine Konstante.", z->operand);
        MELDE_FEHLER_P2(z->i, message );
    }
    if ( isValidLabel(z->label) ) {
        addSymbol(z->label, address, z->relativ, z->operation, z->operand, 3, z->i);
    }
    z->relativ = z->pc;
}

// db, dbn: Bytefolge; nr ist die Kennung des Symbols (4 = db, 5 = dbn)
static void pass2Db(Pass2Zustand *z, int nr) {
    char message[1024];
    long byteCount = 0;
    if ( isValidLabel(z->label) ) {
        addSymbol(z->label, z->pc, z->relativ, z->operation, z->operand, nr, z->i);
    }
    if ( pruefeDbOperand(z->operation, z->operand, &byteCount, message, sizeof(message)) ) {
        z->pc += (unsigned int)byteCount;
    } else {
        is_error2 = 1;
        MELDE_FEHLER_P2(z->i, message );
    }
}

// dt, dto, dtm: Text; nr ist die Kennung des Symbols (6, 7, 8), kbgb die Betriebsart fuer zaehleText
static void pass2Text(Pass2Zustand *z, int nr, int kbgb) {
    if ( isValidLabel(z->label) ) {
        addSymbol(z->label, z->pc, z->relativ, z->operation, z->operand, nr, z->i);
    }
    if (z->textkonst[0] != '\0') {
        z->pc += zaehleText(z->textkonst, kbgb);
    } else {
        z->pc += zaehleText(z->operand, kbgb);
    }
}

// dz: ein Wort
static void pass2Dz(Pass2Zustand *z) {
    if ( isValidLabel(z->label) ) {
        addSymbol(z->label, z->pc, z->relativ, z->operation, z->operand, 9, z->i);
    }
    z->pc++;
}

// dw (istDa = 0) und da (istDa = 1): ein Wort. Der Operand von dw darf Symbole enthalten (Doku 3.3),
// auch spaeter definierte; er wird erst in Pass 3 ausgewertet, wenn alle Symbole bekannt sind.
// Deshalb hier kein "spaetes Symbol" (BITMASK), das den Operanden in resolveSymbols() durch eine
// Zahl ersetzt haette (ohne Pruefung auf relative Adressen, und nur bei dw-Zeilen mit Marke).
// Verschiebungsgrad eines <adressausdruck> von da (und von @-Literalen): Zahlen und abs-Symbole haben den Grad 0,
// relative Symbole (Marken, equ-Symbole, Literalsymbole) +1; bei + addieren, bei - subtrahieren sich die Grade.
// Regel fuer da: Das Ergebnis muss eine relative Adresse sein (Grad >= 1). Konstante Ausdruecke (Grad 0, z. B. "5"
// oder "absx") und paarweise Differenzen relativer Adressen (z. B. "a-b") sind unzulaessig; es muss mindestens
// ein relativer Adressanteil uebrig bleiben, z. B. "(a-b)+c" geschrieben als "a-b+c". Die Pruefung arbeitet auf dem
// Quelltext des Operanden (Pass 2); ob ein Symbol definiert ist, prueft evaluateAddress/Pass 3. abs-Symbole sind
// nach Pass 1 bekannt, auch bei Vorwaertsreferenzen.
// Rueckgabe: 0 = Grad in *grad gesetzt, -1 = relatives Symbol in * oder / (kein Adressanteil mehr bestimmbar).
static int adressausdruckGrad(const char *operand, int *grad) {
    int gesamt = 0;
    int vorzeichen = 1;          // Vorzeichen des aktuellen Summanden
    int termGrad = 0;            // Grad der Faktoren des aktuellen Summanden
    int faktoren = 0;            // Anzahl der Faktoren des aktuellen Summanden
    int relativeFaktoren = 0;
    const char *p = operand;
    for (;;) {
        char token[MAX_LINE_LENGTH];
        int n = 0;
        while (*p && !strchr("+-*/", *p)) {
            if (n < (int)sizeof(token) - 1) token[n++] = *p;
            p++;
        }
        while (n > 0 && (token[n - 1] == ' ' || token[n - 1] == '\t')) n--;
        token[n] = '\0';
        const char *t = token;
        while (*t == ' ' || *t == '\t') t++;
        int g = 0;
        if (*t != '\0' && !isdigit((unsigned char)*t) && !sucheInAbsTabelle(t)) g = 1;
        faktoren++;
        if (g) { relativeFaktoren++; termGrad = 1; }
        if (*p == '*' || *p == '/') {      // Faktor weiter im selben Summanden
            p++;
            continue;
        }
        if (faktoren > 1 && relativeFaktoren > 0) return -1;   // Adresse multipliziert/dividiert
        gesamt += vorzeichen * termGrad;
        termGrad = 0; faktoren = 0; relativeFaktoren = 0;
        if (*p == '\0') break;
        vorzeichen = (*p == '-') ? -1 : 1;
        p++;
    }
    *grad = gesamt;
    return 0;
}

// da: Adresswort
static void pass2DwDa(Pass2Zustand *z, int istDa) {
    char message[1024];
    z->raAdr = z->relativ;

    if (z->operand[0] == '*') {
        z->relativ = sternadresseBearbeiten(z->operand, z->line, &z->fehlerP, z->pc) ;
    } else {
        z->relativ = evaluateAddress(z->operand, z->line, &z->fehlerP, &z->raAdr, z->label, z->pc, &absolutadresse);
        if (( z->fehlerP != -2 ) && ( z->fehlerP != 0 )) {
            snprintf(message, sizeof(message), "Operand: \"%s\" hat eine ungültige Konstante.", z->operand);
            MELDE_FEHLER_P2(z->i, message );
        } else if ( isValidLabel(z->label) ) {
            if ( z->fehlerP == -2 ) {
                // Wert noch nicht bekannt
                if (istDa) {
                    addSymbol(z->label, z->pc | 010000000000, z->relativ, z->operation, z->operand, 12, z->i);
                } else {
                    addSymbol(z->label, z->pc, z->relativ, z->operation, z->operand, 10, z->i);
                }
            } else {
                addSymbol(z->label, z->pc, z->relativ, z->operation, z->operand, istDa ? 13 : 11, z->i);
            }
        }
        // da muss eine relative Adresse ergeben (Doku 3.3.4): keine Konstante, keine reine Differenz (a-b).
        if (istDa && z->operand[0] != '*' && z->fehlerP != -1) {
            int grad = 0;
            int rc = adressausdruckGrad(z->operand, &grad);
            if (rc != 0 || grad < 1) {
                snprintf(message, sizeof(message), rc != 0
                    ? "Operand: \"%s\" ist bei da nicht zulässig: eine Adresse darf nicht multipliziert oder dividiert werden."
                    : "Operand: \"%s\" ist bei da nicht zulässig: da verlangt eine relative Adresse; Konstanten und paarweise Differenzen von Adressen (a-b) sind unzulässig, mindestens ein Adressanteil muss übrig bleiben.",
                    z->operand);
                is_error2 = 1;
                MELDE_FEHLER_P2(z->i, message);
            }
        }
    }
    z->pc++;
}

// end: Marke an der Endadresse
static void pass2Ende(Pass2Zustand *z) {
    if ( isValidLabel(z->label)) {
        addSymbol(z->label, z->pc, z->relativ, z->operation, z->operand, 14, z->i);
    }
}

// Der Programmzaehler zeigt auf die NAECHSTE freie Zelle. Nach einem Wort auf Zelle 7777
// steht er daher auf 010000 (= 8 * 1024); das ist noch zulaessig. Ein Fehler liegt erst vor,
// wenn ein Wort auf Zelle 010000 oder darueber abgelegt werden muesste.
static void pass2PruefeUeberlauf(Pass2Zustand *z) {
    static int ueberlaufGemeldet = 0;   // nur die erste Zeile melden, nicht jede weitere
    if ( z->pc + startAdresse > 010000 ) {
        is_error2 = 1;
        if (!ueberlaufGemeldet) {
            ueberlaufGemeldet = 1;
            MELDE_FEHLER_P2(z->i, "Programmzählerüberlauf über 7777 (weitere Zeilen werden nicht einzeln gemeldet).");
        }
    }
}

// Das Kommentarfeld `orig_operation` in der Symboltabelle ergänzen
//
// BUGFIX (siehe Analyse): Die ursprüngliche Implementierung suchte `orig_operation`
// (z.B. "a" oder "b") per strstr() als reinen Teilstring in der Operanden-Spalte und
// ersetzte den ERSTEN Treffer - unabhängig davon, ob dieser Treffer tatsächlich ein
// eigenständiges Symbol war oder nur zufällig als Teilzeichenkette in einem längeren
// Bezeichner vorkam. Dadurch wurden z.B. "adr_a" (enthält "a"), "adr_b" (enthält "a"
// UND "b") und "beginn" (beginnt mit "b") fälschlich beschädigt, sobald Symbole mit
// kurzen, einbuchstabigen Namen ("a", "b") aufgelöst wurden - mit der Folge, dass die
// betroffenen Operanden in der .dmp-Datei korrupt waren und Pass 3 "Adresse ist
// ungültig"-Fehler meldete.
//
// Fix: Ein Treffer zählt nur dann als Symbol-Treffer, wenn das Zeichen davor und das
// Zeichen danach kein weiterer Bezeichner-Bestandteil (alphanumerisch oder '_') ist -
// also eine echte Wortgrenze vorliegt. Andernfalls wird die Suche hinter dem (falschen)
// Treffer fortgesetzt.
static void pass2ErsetzeOrigOperation(const char *orig_operation, unsigned int result) {
    // Suche der `orig_operation` in `lineAsmAufgeloest` und ersetzen durch `result`
    char line_in[1024];
    size_t opLen = strlen(orig_operation);
    if (opLen == 0) {
        return; // nichts zu ersetzen
    }
    for (int i = 0; i < lineCountAsmAufgeloest; i++) {
        STRKOPIE(line_in, lineAsmAufgeloest[i].sp3);

        char *searchStart = line_in;
        char *pos;
        while ((pos = strstr(searchStart, orig_operation)) != NULL) {
            char before = (pos == line_in) ? '\0' : *(pos - 1);
            char after  = *(pos + opLen);
            int grenzeDavor  = (pos == line_in) || !(isalnum((unsigned char)before) || before == '_');
            int grenzeDanach = !(isalnum((unsigned char)after) || after == '_');

            if (grenzeDavor && grenzeDanach) {
                char newLine[1024];
                int offset = pos - line_in;

                strncpy(newLine, line_in, offset);
                newLine[offset] = '\0';

                char resultStr[256];
                snprintf(resultStr, sizeof(resultStr), "%012o", result);
                STRANHANG(newLine, resultStr);
                STRANHANG(newLine, pos + opLen);

                STRKOPIE(line_in, newLine);
                STRKOPIE(lineAsmAufgeloest[i].sp3, line_in);
                break; // ein echter Treffer pro Zeile genügt
            }

            // Kein echtes Wortgrenzen-Match - hinter diesem Fundort weitersuchen
            searchStart = pos + 1;
        }
    }
}

static int pass2IstZahl(const char *token) {
    for (int i = 0; token[i] != '\0'; i++) {
        if (!isdigit((unsigned char)token[i])) {
            return 0; // Nicht numerisch
        }
    }
    return 1; // Numerisch
}

// Adresse des Symbols, -1 wenn nicht gefunden
static int pass2SymbolAdresse(const char *token) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, token) == 0) {
            symbolTable[i].verwendet = 1;  // Verwendung in einem Ausdruck (-WARN=SYM)
            return symbolTable[i].address; // Rückgabe der Adresse des Symbols
        }
    }
    return -1; // Symbol nicht gefunden
}

// Fuegt hinter der Zeile pos von lineAsmAufgeloest eine Fehlermarke ein (pos < 0: am Ende). Der Fehler
// erscheint damit im Listing und auf STDERR bei der Quellzeile, in der das Symbol definiert ist.
static void pass2FehlermarkeNachZeile(int pos, const char *text) {
    pruefeZeilenfeld(lineCountAsmAufgeloest);
    is_error2 = 1;
    if (pos < 0 || pos >= lineCountAsmAufgeloest) {
        pos = lineCountAsmAufgeloest - 1;
    }
    int ziel = pos + 1;
    memmove(&lineAsmAufgeloest[ziel + 1], &lineAsmAufgeloest[ziel],
            (size_t)(lineCountAsmAufgeloest - ziel) * sizeof(lineElements));
    char fehlertext_p[2048];
    snprintf(fehlertext_p, sizeof(fehlertext_p), ";%s*** (2) Fehler%s: %s\n", _violett, _normal, text);
    STRKOPIE(lineAsmAufgeloest[ziel].sp1, fehlertext_p);
    STRKOPIE(lineAsmAufgeloest[ziel].sp2, "");
    STRKOPIE(lineAsmAufgeloest[ziel].sp3, "");
    STRKOPIE(lineAsmAufgeloest[ziel].sp4, "");
    lineAsmAufgeloest[ziel].srcLine = 0;
    lineCountAsmAufgeloest++;
    for (int k = 0; k < symbolCount; k++) {
        if (symbolTable[k].aufgeloestIndex >= ziel) symbolTable[k].aufgeloestIndex++;
    }
}

// späte symbole auflösen
static void pass2LoeseSpaeteSymbole(void) {
    char message[1024];
    for (int i = 0; i < symbolCount; i++) {
        if (symbolTable[i].address & BITMASK) {

            char *expr = symbolTable[i].orig_operation;
            int result = 0;
            int value = 0;
            char lastOp = '+';

            while (*expr) {
                // Überspringe Leerzeichen
                while (*expr && isspace((unsigned char)*expr)) expr++;

                // Wenn Operator gefunden, speichern
                if (*expr == '+' || *expr == '-' || *expr == '*' || *expr == '/') {
                    lastOp = *expr;
                    expr++;
                    continue;
                }

                // Extrahiere nächstes Token (Symbol oder Zahl)
                char token[50] = {0};  // Buffer für Token
                int j = 0;
                while (*expr && !isspace((unsigned char)*expr) && *expr != '+' && *expr != '-' && *expr != '*' && *expr != '/') {
                    if (j < (int)sizeof(token) - 1) token[j++] = *expr;   // zu lange Namen abschneiden statt Puffer zu ueberschreiben
                    expr++;
                }
                token[j] = '\0';  // Null-terminieren

                // Prüfe Token: Zahl oder Symbol
                if (pass2IstZahl(token)) {
                    value = atoi(token);
                } else if (isSymbol(token) && (value = pass2SymbolAdresse(token)) != -1) {
                    // Symbol gefunden, value ist seine Adresse
                } else {
                    // Das Symbol ist nirgends definiert (frueher blieb der Wert 0, ohne jede Meldung,
                    // und der Lauf endete ohne Fehler)
                    value = 0;
                    snprintf(message, sizeof(message), "Symbol '%s' ist nicht definiert.", token);
                    pass2FehlermarkeNachZeile(symbolTable[i].aufgeloestIndex, message);
                }

                // Berechnung basierend auf vorherigem Operator
                switch (lastOp) {
                    case '+': result += value; break;
                    case '-': result -= value; break;
                    case '*': result *= value; break;
                    case '/': result /= (value == 0 ? 1 : value); break;
                }
            }

            pass2ErsetzeOrigOperation(symbolTable[i].orig_operation, result);
            snprintf(symbolTable[i].orig_operation, sizeof(symbolTable[i].orig_operation), "%012o", result);
            symbolTable[i].address &= ~BITMASK;
        }
    }
}

// Symboltabelle und Adresstabelle in das .log
static void pass2SchreibeSymbolLog(FILE *symbolLog) {
    fprintf(symbolLog, "Symboltabelle\n\n");
    fprintf(symbolLog, "Symbol                             | RelAddr |    Adresse      | original Operation\n");
    fprintf(symbolLog, "-----------------------------------| ------- | --------------- | ----------------\n");
    bubbleSortBySymbol(symbolTable, symbolCount);
    for (int i = 0; i < symbolCount; i++) {
        fprintf(symbolLog, "%-34s |   %04o  |  %012o   | %s\n", symbolTable[i].symbol, symbolTable[i].relativAdresse, symbolTable[i].address, symbolTable[i].orig_operation);
    }

    fprintf(symbolLog, "\n\n");
    fprintf(symbolLog, "Adresstabelle\n\n");
    fprintf(symbolLog, "Symbol                             | RelAddr |    Adresse\n");
    fprintf(symbolLog, "-----------------------------------| ------- | ---------------\n");
    bubbleSortByAddress(symbolTable, symbolCount);
    for (int i = 0; i < symbolCount; i++) {
        fprintf(symbolLog, "%-34s |   %04o  | %012o\n", symbolTable[i].symbol, symbolTable[i].relativAdresse, symbolTable[i].address);
    }
}

// Symbole in die .sym-Datei (Symbol,Adresse)
static void pass2SchreibeSymDatei(FILE *symFile) {
    for (int i = 0; i < symbolCount; i++) {
        fprintf(symFile, "%s,%04o\n", symbolTable[i].symbol, symbolTable[i].address);
    }
}

void pass2(char *symbolLogFile, char *symFileName) {
    printf("Löse Symbole auf nach %s und %s\n", symbolLogFile, symFileName);

    FILE *symbolLog = oeffneAusgabedatei(symbolLogFile, "a");
    FILE *symFile = oeffneAusgabedatei(symFileName, "w+");

    // lineAsmAufgeloest wird dynamisch vergrößert
    lineCountAsmAufgeloest = 0;
    line_ausgegeben = 0;

    Pass2Zustand z;
    memset(&z, 0, sizeof(z));

    for (z.i = 0; z.i < lineCountAsmAufgeloestTemp; z.i++) {

        if ( pass2IstKommentarOderLeer(&lineAsmAufgeloestTemp[z.i]) ) {
            pass2KopiereZeile(z.i);
            continue;
        }

        pass2ZeileVorbereiten(&z);
        pass2Befehl(&z);

        // Die Anweisungen schliessen sich nicht aus: der Operationsname steht in z.operation
        if (strcmp(z.operation, "start") == 0)  pass2Start(&z);
        if (strstr(z.operation, "equ") != NULL) pass2Equ(&z);
        if (strcmp(z.operation, "spa") == 0)    pass2Spa(&z);
        if (strcmp(z.operation, "abs") == 0)    pass2Abs(&z);
        if (strcmp(z.operation, "db") == 0)     pass2Db(&z, 4);
        if (strcmp(z.operation, "dbn") == 0)    pass2Db(&z, 5);

        if ( (strcmp(z.operation, "dt") == 0 || strcmp(z.operation, "dto") == 0 || strcmp(z.operation, "dtm") == 0)
             && z.textkonst[0] == '\0' && z.operand[0] == '\0' ) {
            char message[1024];
            snprintf(message, sizeof(message), "%s ohne Text: es wird kein Wort erzeugt.", z.operation);
            meldeWarnungOrt(lineAsmAufgeloestTemp[z.i].srcLine, message);
        }

        if (strcmp(z.operation, "dt") == 0)     pass2Text(&z, 6, 0);
        if (strcmp(z.operation, "dto") == 0)    pass2Text(&z, 7, 1);
        if (strcmp(z.operation, "dtm") == 0)    pass2Text(&z, 8, 2);
        if (strcmp(z.operation, "dz") == 0)     pass2Dz(&z);
        if (strcmp(z.operation, "dw") == 0)     pass2DwDa(&z, 0);
        if (strcmp(z.operation, "da") == 0)     pass2DwDa(&z, 1);
        if (strcmp(z.operation, "end") == 0)    pass2Ende(&z);

        line_ausgegeben = 0;
        pass2PruefeUeberlauf(&z);
    }

    pass2LoeseSpaeteSymbole();

    // Der Operand von dw ist ein <werteausdruck> (Doku 3.3.3); Symbole darin, auch Literalsymbole
    // (l0001), bleiben stehen und werden in Pass 3 nach den Regeln von Doku 3.3.3 ausgewertet
    // (evaluateValue): eine einzelne Adresse ist relativ und damit ein Fehler, paarweise Differenzen
    // von Adressen (auch mehrfach) sind zulaessig.

    if (symbolLog) {
        pass2SchreibeSymbolLog(symbolLog);
        fclose(symbolLog);
    } else {
        fprintf(stderr, "Fehler: Datei %s kann nicht geschrieben werden.\n", symbolLogFile);
        is_error2 = 1;
    }
    if (symFile) {
        pass2SchreibeSymDatei(symFile);
        fclose(symFile);
    } else {
        fprintf(stderr, "Fehler: Datei %s kann nicht geschrieben werden.\n", symFileName);
        is_error2 = 1;
    }

    if (is_error2 != 0) {
       printFormattedAsmListing(lineAsmAufgeloest, lineCountAsmAufgeloest);
    }
}


// HINWEIS (Bereinigung): Die Parameter hießen zuvor in der Deklaration "operand, operation",
// wurden aber von ALLEN Aufrufstellen konsequent in der Reihenfolge "operation, operand" befüllt.
// Funktional war das unproblematisch (der frühere Parameter "operand" wurde im Funktionskörper
// gar nicht benutzt), aber irreführend. Hier an die tatsächliche Verwendung angepasst:
// "operation" ist der Mnemonic/die Anweisung (z. B. "da", "dw"), "operand" ist der Adressausdruck
// (z. B. "a", "zvektor"), der bei vorwärtsreferenzierten Symbolen später von resolveSymbols()
// ausgewertet und für orig_operation benötigt wird.
void addSymbol(char *symbol, int address, int relativAdresse, char *operation, char *operand, int nr, int i) {
    char message[1024];
    strtok(symbol, ":"); // Entfernt ':' am Ende

    if (symbolCount >= MAX_SYMBOLS) {
        snprintf(message, sizeof(message), "(%i): Symbol-Tabelle ist voll. Symbol '%s' konnte nicht hinzugefügt werden.\n", nr, symbol);
        MELDE_FEHLER_P2(i, message );
        is_error2 = 1; 
        return;
    }

    for (int i_p = 0; i_p < symbolCount; i_p++) {
        if (strcmp(symbolTable[i_p].symbol, symbol) == 0) {
            if ( strcmp(operation, "abs") == 0 ) {
                return;  
            }
            snprintf(message, sizeof(message), "(%i): Symbol existiert bereits. Symbol '%s' konnte nicht hinzugefügt werden.\n", nr, symbol);
            MELDE_FEHLER_P2(i_p, message );
            is_error2 = 1; 
            return;
        }
    }

    unsigned int  relAdr =  isLiteralInTableRelativAdresse( symbol) ;
    if (relAdr != (unsigned int)-1) {
       symbolTable[symbolCount].relativAdresse = relAdr;
    } else { 
       symbolTable[symbolCount].relativAdresse = relativAdresse;
    }

    STRKOPIE(symbolTable[symbolCount].symbol, symbol);
    symbolTable[symbolCount].address = address;
    symbolTable[symbolCount].verwendet = 0;
    symbolTable[symbolCount].aufgeloestIndex = lineCountAsmAufgeloest - 1;   // die Zeile wurde vor addSymbol uebernommen
    if ( strstr(operand,";") != 0) {
       STRKOPIE(symbolTable[symbolCount].orig_operation , "");
    } else {
       STRKOPIE(symbolTable[symbolCount].orig_operation , operand);
    }
    symbolCount++;
    //snprintf(message, sizeof(message), "(%i): Symbol '%s' hinzugefügt.",nr, symbol);
    //MELDE_MSG_P2("%s", message );
}
