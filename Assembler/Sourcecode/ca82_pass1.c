// ca82_pass1.c - Pass 1: Literale, equ/abs-Tabellen, Operandenpruefung
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"


// ----------------------------------------------------

int isKeywordMatch(const char *token) {
    static const char *keywords[] = {
        "start", "equ", "abs", "end", "dw", "da", "dt",
        "dto", "dtm", "dz", "dbn", "db", "equ10", "equ40", "equ100", "spa"
    };
    if (!token) return 1;  // Falls token NULL ist, nicht zutreffend

    // Schrittweise Prüfung der Schlüsselwörter
    int keyword_count = (int)(sizeof(keywords) / sizeof(keywords[0]));
    for (int i = 0; i < keyword_count; i++) {
        if (strcmp(token, keywords[i]) == 0) {
            return 0;  // Treffer
        }
    }
    return 1;  // Kein Treffer
}

int isValidSp3_keinLiteralEnthalten(const char *sp3) {
    if (!sp3 || sp3[0] == '\0') return 1; // Leer? Dann gültig

    const char *hashPos = strchr(sp3, '#'); // Sucht das erste `#`
    
    if (!hashPos) return 1; // Falls kein `#` existiert, ist es gültig

    // Prüft, ob vor `#` ein `;` oder `\` steht
    const char *ptr;
    for (ptr = sp3; ptr < hashPos; ptr++) {
        if (*ptr == ';' || *ptr == '\\') return 0; // Ungültig, wenn `#` danach kommt
    }

    return 1; // Falls kein `#` vor `;` oder `\` steht, ist es gültig
}


// Erzeugen der Literal-Definitionen am Programmende
void processLiteralEntry(lineElements lineAsmAufgeloestTemp_p[], int *lineCountAsmAufgeloestTemp_p, Literal literalTable_p[], int i) {
    char type[3]; // Platz für "dw" oder "da"

    if (literalTable_p[i].literalValue[0] == '#') {
        memmove(literalTable_p[i].literalValue, literalTable_p[i].literalValue + 1, strlen(literalTable_p[i].literalValue));
        STRKOPIE(type, "dw");
    } else if (literalTable_p[i].literalValue[0] == '@') {
        memmove(literalTable_p[i].literalValue, literalTable_p[i].literalValue + 1, strlen(literalTable_p[i].literalValue));
        STRKOPIE(type, "da");
    } else {
        STRKOPIE(type, "dw");
    }

    STRKOPIE(lineAsmAufgeloestTemp_p[*lineCountAsmAufgeloestTemp_p].sp1, literalTable_p[i].literalName);
    STRKOPIE(lineAsmAufgeloestTemp_p[*lineCountAsmAufgeloestTemp_p].sp2, type);
    STRKOPIE(lineAsmAufgeloestTemp_p[*lineCountAsmAufgeloestTemp_p].sp3, literalTable_p[i].literalValue);
    STRKOPIE(lineAsmAufgeloestTemp_p[*lineCountAsmAufgeloestTemp_p].sp4, "");
    (*lineCountAsmAufgeloestTemp_p)++;
}


// ----------------------------------------------------

// Prueft den Operanden von db/dbn gemaess Doku (<zahl> ::= <oktalzahl> | <dezimalzahl>):
//   oktalzahl   = fuehrende 0, nur Ziffern 0-7 ("0" allein ist zulaessig)
//   dezimalzahl = [+|-] Ziffer 1-9, danach Ziffern 0-9
// Alles andere (abc, 5x, 3+1, 09, #5, leer) ist ein Fehler; frueher wurde es stillschweigend als
// 0 oder als der gueltige Zahlenanfang gelesen und verschob alle folgenden Adressen.
// Rueckgabe 1 = gueltig (Anzahl in *wert), 0 = ungueltig (Text in meldung).
int pruefeDbOperand(const char *operation, const char *operand, long *wert, char *meldung, size_t groesse) {
    const char *p = (operand != NULL) ? operand : "";
    if (*p == '\0') {
        snprintf(meldung, groesse, "%s: Operand fehlt (erwartet wird eine Zahl).", operation);
        return 0;
    }
    int oktal = (p[0] == '0');
    const char *q = p;
    if (!oktal && (*q == '+' || *q == '-')) q++;
    int gueltig = (*q != '\0');
    if (oktal) {
        for (; *q; q++) if (*q < '0' || *q > '7') { gueltig = 0; break; }
    } else {
        if (*q < '1' || *q > '9') gueltig = 0;
        for (; gueltig && *q; q++) if (*q < '0' || *q > '9') gueltig = 0;
    }
    if (!gueltig) {
        snprintf(meldung, groesse,
                 "%s: Operand \"%s\" ist keine gültige Zahl (Oktalzahl mit führender 0 oder Dezimalzahl).",
                 operation, operand);
        return 0;
    }
    errno = 0;
    long v = strtol(p, NULL, oktal ? 8 : 10);
    if (v < 0) {
        snprintf(meldung, groesse, "%s: Operand \"%s\" darf nicht negativ sein.", operation, operand);
        return 0;
    }
    if (errno == ERANGE || v > 010000) {
        snprintf(meldung, groesse, "%s: Operand \"%s\" ist zu groß (die Trommel hat nur 010000 Speicherplätze).",
                 operation, operand);
        return 0;
    }
    *wert = v;
    return 1;
}

// spa (Definition Absolute Sektoradresse):  [<symbol>] spa <oktalzahl> | <dezimalzahl>   (00 ... 77 oktal)
// Prueft den Operanden: oktalzahl = fuehrende 0, nur Ziffern 0-7; dezimalzahl = [+] Ziffer 1-9, danach
// Ziffern 0-9. Der Wert muss im Bereich 0 ... 077 (= 63 dezimal) liegen, weil er die rechten beiden
// Oktalziffern der Adresse ersetzt. Symbole und Ausdruecke sind nicht zulaessig.
// Rueckgabe 1 = gueltig (Wert in *wert), 0 = ungueltig (Text in meldung).
int pruefeSpaOperand(const char *operand, long *wert, char *meldung, size_t groesse) {
    const char *p = (operand != NULL) ? operand : "";
    if (*p == '\0') {
        snprintf(meldung, groesse, "spa: Operand fehlt (erwartet wird eine Zahl von 00 bis 77 oktal).");
        return 0;
    }
    int oktal = (p[0] == '0');
    const char *q = p;
    if (!oktal && *q == '+') q++;
    int gueltig = (*q != '\0');
    if (oktal) {
        for (; *q; q++) if (*q < '0' || *q > '7') { gueltig = 0; break; }
    } else {
        if (*q < '1' || *q > '9') gueltig = 0;
        for (; gueltig && *q; q++) if (*q < '0' || *q > '9') gueltig = 0;
    }
    if (!gueltig) {
        snprintf(meldung, groesse,
                 "spa: Operand \"%s\" ist keine gültige Zahl (Oktalzahl mit führender 0 oder Dezimalzahl).",
                 operand);
        return 0;
    }
    errno = 0;
    long v = strtol(p, NULL, oktal ? 8 : 10);
    if (errno == ERANGE || v < 0 || v > 077) {
        snprintf(meldung, groesse,
                 "spa: Operand \"%s\" liegt außerhalb des Bereichs 00 bis 77 oktal (0 bis 63 dezimal).",
                 operand);
        return 0;
    }
    *wert = v;
    return 1;
}

// spa verhaelt sich wie ein equ mit einer Adresse, bei der die rechten beiden Oktalziffern des aktuellen
// Befehlszaehlers durch den Operanden ersetzt sind (Beispiel: Zaehler 0256, spa 020 ==> equ 0220).
// Der Wert kann dabei kleiner sein als der Zaehler (0277 ==> 0220); der Zaehler wird dann zurueckgesetzt.
unsigned int spaAdresse(unsigned int befehlszaehler, long wert) {
    return (befehlszaehler & ~077u) | ((unsigned int)wert & 077u);
}

// Baut aus den Zeilenelementen den Text der Quellzeile fuer Fehlermeldungen (Pass 1 hat keine
// fertige Zeile; frueher erschien dort "in Zeile: ``").
static void baueMeldeZeile(char *ziel, size_t groesse, const lineElements *z) {
    ziel[0] = '\0';
    const char *teile[3] = { z->sp1, z->sp2, z->sp3 };
    for (int k = 0; k < 3; k++) {
        if (teile[k][0] == '\0') continue;
        if (ziel[0] != '\0') strncat(ziel, " ", groesse - strlen(ziel) - 1);
        strncat(ziel, teile[k], groesse - strlen(ziel) - 1);
    }
}

// Kommentar-, Pragma- und Fehlerzeilen (beginnen mit ; # $ & oder enthalten ***) werden nur uebernommen.
static int pass1IstUebergehbar(const lineElements *z) {
    return (z->sp1[0] == ';') || (z->sp1[0] == '#') || (z->sp1[0] == '$') ||
           (z->sp1[0] == '&') || (strstr(z->sp1, "***") != NULL);
}

static int pass1IstLeerzeile(const lineElements *z) {
    return z->sp1[0] == '\0' && z->sp2[0] == '\0' && z->sp3[0] == '\0' && z->sp4[0] == '\0';
}

// Meldet Operanden, die an dieser Stelle kein Literal sein duerfen (dt, dw, spa) bzw. kein Text sind.
static void pass1PruefeLiteralOperand(int i) {
    char line[MAX_LINE_LENGTH]={0};

    // dt/dto/dtm: Ein Operand, der mit '#' beginnt, ist KEIN Text, sondern die Schreibweise eines
    // Literals (Doku 2, <literal> ::= #<werteausdruck>). Soll ein Text mit '#' am Anfang ausgegeben
    // werden, muss er in \...\ stehen (dt \#ab\). Ein '#' innerhalb des Textes (dt a#b) bleibt Text.
    if ( istTextAnweisung(lineAsmAufgeloest[i].sp2) && lineAsmAufgeloest[i].sp3[0] == '#' ) {
        baueMeldeZeile(line, sizeof(line), &lineAsmAufgeloest[i]);
        printAdressError(lineAsmAufgeloest[i].sp3, "Operand", "beginnt mit # und ist daher kein Text; Text mit # braucht \\...\\", line);
        MELDE_FEHLER_P1("Operand %s ist kein Text (beginnt mit #); Text mit # muss in \\...\\ stehen.", lineAsmAufgeloest[i].sp3);
        is_error1 = 1;
    }

    // dw: Der Operand ist ein <werteausdruck> (Doku 3.3.3). Ein Literal (#... oder @...) ist eine
    // relative Adresse und damit kein zulaessiger Operand von dw; Adressen schreibt man mit da.
    // Zulaessig bleiben paarweise Differenzen von Adressen, auch mehrere (dw ende-anfang, dw a-b+c-d,
    // auch mit Literalsymbolen wie dw l0002-l0001); ein einzelnes Literalsymbol (dw l0001) meldet
    // Pass 3 als relativ.
    if ( strcmp(lineAsmAufgeloest[i].sp2, "dw") == 0 &&
         (lineAsmAufgeloest[i].sp3[0] == '#' || lineAsmAufgeloest[i].sp3[0] == '@') ) {
        baueMeldeZeile(line, sizeof(line), &lineAsmAufgeloest[i]);
        printAdressError(lineAsmAufgeloest[i].sp3, "Operand", "ist ein Literal und damit eine relative Adresse; dw erwartet einen <werteausdruck> (Adressen mit da schreiben)", line);
        MELDE_FEHLER_P1("Operand %s ist bei dw nicht zulaessig: ein Literal ist eine relative Adresse (Adressen mit da schreiben).", lineAsmAufgeloest[i].sp3);
        is_error1 = 1;
    }

    // spa: Der Operand ist eine Zahl von 00 bis 77 oktal. Ein Literal (#... oder @...) ist eine Adresse
    // bzw. ein Wort im Literalbereich und damit kein zulaessiger Operand.
    if ( strcmp(lineAsmAufgeloest[i].sp2, "spa") == 0 &&
         (lineAsmAufgeloest[i].sp3[0] == '#' || lineAsmAufgeloest[i].sp3[0] == '@') ) {
        baueMeldeZeile(line, sizeof(line), &lineAsmAufgeloest[i]);
        printAdressError(lineAsmAufgeloest[i].sp3, "Operand", "ist ein Literal; spa erwartet eine Zahl von 00 bis 77 oktal", line);
        MELDE_FEHLER_P1("Operand %s ist bei spa nicht zulaessig: erwartet wird eine Zahl von 00 bis 77 oktal.", lineAsmAufgeloest[i].sp3);
        is_error1 = 1;
    }
}

// Ersetzt ein Literal im Operanden (#... oder @...) durch ein Literalsymbol l<nnnn> und traegt es in die
// Literaltabelle ein.
// Nicht bei dt/dto/dtm: Dort ist der Operand ein Text; ein '#' innerhalb des Textes ist ein
// Textzeichen, ein fuehrendes '#' wird in pass1PruefeLiteralOperand als Fehler gemeldet (dt # schrieb frueher
// "l0001"), ein '@' wird von der Zeichenpruefung in Pass 3 gemeldet.
// Nicht bei dw und spa: Ein Literal als Operand wird in pass1PruefeLiteralOperand als Fehler gemeldet.
static void pass1LiteralErsetzen(int i, unsigned int relativAdresse) {
    if ( istTextAnweisung(lineAsmAufgeloest[i].sp2) ||
         strcmp(lineAsmAufgeloest[i].sp2, "dw") == 0 ||
         strcmp(lineAsmAufgeloest[i].sp2, "spa") == 0 ||
         !(lineAsmAufgeloest[i].sp3[0] == '#' || lineAsmAufgeloest[i].sp3[0] == '@')) {
        return;
    }
    char oldName[256]="";
    char literalValue[256];
    char literalName[50];
    if (lineAsmAufgeloest[i].sp3[1] == '0' && strchr(lineAsmAufgeloest[i].sp3, '+') == NULL && strchr(lineAsmAufgeloest[i].sp3, '-') == NULL) {
        //oktal
        snprintf(literalValue, sizeof(literalValue), "%012lo", (unsigned long int) strtol(lineAsmAufgeloest[i].sp3 + 1, NULL, 8));
    } else {
        // dezimal
        strncpy(literalValue, lineAsmAufgeloest[i].sp3, sizeof(literalValue) - 1);
        literalValue[sizeof(literalValue) - 1] = '\0';
    }
    snprintf(literalName, sizeof(literalName), "l%04d", literalCount+1);

    STRKOPIE(oldName , addLiteral(literalName, literalValue, relativAdresse+1));
    if (oldName[0] == '\0') {
       STRKOPIE(oldName, literalName) ;
    }
    if (oldName[0] != '\0') {
        STRKOPIE(lineAsmAufgeloest[i].sp3, oldName);
    }
}

// equ, equ10, equ40, equ100: Definition in die equ-Tabelle, Zeile uebernehmen.
static void pass1Equ(int i) {
    appendToEquTable(lineAsmAufgeloest[i].sp1, lineAsmAufgeloest[i].sp3);
    copyAndIncrementLineElements(i);
    if (strcmp(lineAsmAufgeloest[i].sp3, "") == 0) {
        MELDE_FEHLER_P1("Operand %s fehlt bei equ", lineAsmAufgeloest[i].sp3);
        is_error1 = 1;
    }
}

// abs: Definition in die abs-Tabelle, Zeile uebernehmen.
static void pass1Abs(int i) {
    int rc = appendToAbsTable(lineAsmAufgeloest[i].sp1, lineAsmAufgeloest[i].sp3);
    copyAndIncrementLineElements(i);
    if (strcmp(lineAsmAufgeloest[i].sp3, "") == 0) {
        MELDE_FEHLER_P1("Operand %s fehlt bei abs", lineAsmAufgeloest[i].sp3);
        is_error1 = 1;
    }
    if ( rc == -1 ) {
        MELDE_FEHLER_P1("abs Definition %s existiert schon mit anderem Wert.",lineAsmAufgeloest[i].sp1);
        is_error1 = 1;
    } else if (rc != 0 ) {
        MELDE_FEHLER_P1("abs Definition %s kann nicht aufgenommen werden. Tabelle voll.",lineAsmAufgeloest[i].sp1);
        is_error1 = 1;
    }
}

// Sonstige Assembleranweisungen (start, end, dw, da, dt, dz, db, ... ) und oktale Operationscodes: Zeile
// uebernehmen; ein #-Literal ist nur dort erlaubt, wo es in pass1LiteralErsetzen ersetzt wurde.
static void pass1Sonstige(int i) {
    char line[MAX_LINE_LENGTH]={0};
    if ( isKeywordMatch(lineAsmAufgeloest[i].sp2) == 0 ) {
        if (!( (strstr(lineAsmAufgeloest[i].sp2, "equ") != NULL) ||  (strstr(lineAsmAufgeloest[i].sp2, "abs") != NULL) )) {
           copyAndIncrementLineElements(i);
        }
        // Text-Anweisungen ausgenommen: Ein '#' im dt-Text (z. B. dt \a#b\) ist ein Sonderzeichen.
        if (!istTextAnweisung(lineAsmAufgeloest[i].sp2) &&
            !isValidSp3_keinLiteralEnthalten(lineAsmAufgeloest[i].sp3)) {
            baueMeldeZeile(line, sizeof(line), &lineAsmAufgeloest[i]);
            printAdressError(lineAsmAufgeloest[i].sp3, "Operand", "darf kein #-Literal sein", line);
            MELDE_FEHLER_P1("Operand %s darf kein #-Literal enthalten.",lineAsmAufgeloest[i].sp3);
            is_error1 = 1;
        }
    } else {
        // oktale Operationscodes
        copyAndIncrementLineElements(i);
    }
}

// Literal-, equ- und abs-Tabelle in die .log-Datei schreiben.
static void pass1SchreibeLog(FILE *symbolLog) {
    if ( literalCount > 0 ) {
        fprintf(symbolLog, "Literaltabelle\n\n");
        fprintf(symbolLog, "Symbol                             | RelAddr | Literalwert\n");
        fprintf(symbolLog, "-----------------------------------| ------- | -----------\n");
        for (int i = 0; i < literalCount; i++) {
            fprintf(symbolLog,"%-35s|  %04o   | %s\n", literalTable[i].literalName, literalTable[i].relativAdresse, literalTable[i].literalValue);
        }
    }

    if ( equ_fuellstand > 0 ) {
        fprintf(symbolLog, "\n\n");

        fprintf(symbolLog, "EQU-Definitionen\n\n");
        fprintf(symbolLog, "Symbol                             |   Wert  \n");
        fprintf(symbolLog, "-----------------------------------| --------\n");

        for (int i = 0; i < equ_fuellstand; i++) {
            fprintf(symbolLog,"%-35s|  %s\n", equ_tabelle[i].key, equ_tabelle[i].value);
        }
    }

    if ( abs_fuellstand > 0 ) {
        fprintf(symbolLog, "\n\n");

        fprintf(symbolLog, "ABS-Definitionen\n\n");
        fprintf(symbolLog, "Symbol                             |   Wert  \n");
        fprintf(symbolLog, "-----------------------------------| --------\n");

        for (int i = 0; i < abs_fuellstand; i++) {
            fprintf(symbolLog,"%-35s|  %s\n", abs_tabelle[i].key, abs_tabelle[i].value);
        }
    }

    fprintf(symbolLog, "\n\n");
}

// Haengt alle Literaldefinitionen (l0001 dw/da ...) an lineAsmAufgeloestTemp an.
static void pass1HaengeLiteraleAn(void) {
    for (int i = 0; i < literalCount; i++) {
        processLiteralEntry( lineAsmAufgeloestTemp, &lineCountAsmAufgeloestTemp, literalTable, i);
    }
}

void pass1(char *symbolLogFile) {
    printf("Löse Literale auf \n");

    FILE *symbolLog = oeffneAusgabedatei(symbolLogFile, "w");  // .log
    int end_war=0;
    unsigned int relativAdresse = 0000;

    for (int i = 0; i < lineCountAsmAufgeloest; i++) {

        // Kommentare u. a. und Leerzeilen unveraendert uebernehmen
        if ( pass1IstUebergehbar(&lineAsmAufgeloest[i]) || pass1IstLeerzeile(&lineAsmAufgeloest[i]) ) {
            copyAndIncrementLineElements(i);
            continue;
        }

        pass1PruefeLiteralOperand(i);
        pass1LiteralErsetzen(i, relativAdresse);

        if (strstr(lineAsmAufgeloest[i].sp2, "equ") != NULL) {
            pass1Equ(i);
        }
        if ( strcmp(lineAsmAufgeloest[i].sp2, "abs") == 0 ) {
            pass1Abs(i);
        }
        pass1Sonstige(i);

        // end
        // Die Literale werden einmalig hinter dem ersten end ausgegeben. end_war wird beim Erkennen von end
        // gesetzt und die Schleife nicht verlassen: Zeilen hinter end (abs, equ) werden weiter ausgewertet,
        // auch wenn das Programm Literale enthaelt. Die Warnung "end fehlt" erscheint nur, wenn wirklich
        // kein end vorhanden ist.
        if ( strcmp(lineAsmAufgeloest[i].sp2, "end") == 0 && end_war == 0 ) {
            end_war=1;
            pass1HaengeLiteraleAn();
        }
    }

    if ( end_war == 0 ) {
        // es gab kein end im quellcode
        pass1HaengeLiteraleAn();
        MELDE_WARNUNG_P1("end - Anweisung %s fehlt.","");
    }

    pass1SchreibeLog(symbolLog);
    fclose(symbolLog);

    if (is_error1 != 0) {
       is_error2 = 1;
    }
}

const char* addLiteral(char *literalName, char *literalValue, unsigned int relativAdresse) {
    if (literalCount >= MAX_LITERALS) {
        MELDE_FEHLER_P1("Literal-Tabelle ist voll. Literal '%s' konnte nicht hinzugefügt werden.", literalName);
        is_error  = 1;
        return ""; 
    }

    if (isLiteralInTable( literalName) == 1 ) { return ""; }  // Literal schon vorhanden
    static char oldName[256];
    strcpy (oldName, getLiteralNameByValue(literalValue) );
    if ( strlen(oldName) > 0 ) { return (strlen(oldName) > 0) ? oldName : ""; }

    STRKOPIE(literalTable[literalCount].literalName, literalName);
    STRKOPIE(literalTable[literalCount].literalValue, literalValue);
    literalTable[literalCount].relativAdresse = relativAdresse;
    literalCount++;

    return "";
}
