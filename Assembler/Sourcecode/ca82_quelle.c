// ca82_quelle.c - Einlesen der Quelltextzeilen (Pragmas, Kommentare, Wiederholungsadressen)
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"



// Text-Anweisungen: Der Operand ist ein Text (Zeichenfolge, ggf. in \...\), kein Zahlen- oder
// Adressausdruck. Dort sind ';' und '#' (Doku 2, <sonderzeichen>) einfache Textzeichen, und ein
// fuehrendes '#' leitet kein Literal ein.
int istTextAnweisung(const char *operation) {
    return strcmp(operation, "dt") == 0 || strcmp(operation, "dto") == 0 || strcmp(operation, "dtm") == 0;
}

// Liefert die Position, an der der Operand endet: das erste ';' (Kommentarbeginn) bzw. das
// Zeilenende ab "rest". Bei dt, dto und dtm gilt (Doku 2, <kommentar>): "Innerhalb der \-Zeichen
// von dt wird ; nicht als Kommentar betrachtet." Steht vor dem ersten ';' ein '\' und gibt es
// dahinter ein schliessendes '\', so wird ein ';' dazwischen zum Text gerechnet, z. B.
//     dt  \ab;cd\   ; Kommentar      -> Text "ab;cd", Kommentar "; Kommentar"
// Ohne schliessendes '\' (oder bei einem ';' vor dem ersten '\') bleibt es beim ersten ';'.
// Die Auswahl der \...\-Grenzen entspricht extractBackslashContent(): erster bis zweiter '\'.
static char *findeOperandEnde(const char *operation, char *rest) {
    char *suchStart = rest;
    if (istTextAnweisung(operation)) {
        char *erstesEnde = strpbrk(rest, ";\n");
        char *b1 = strchr(rest, '\\');
        if (b1 && (!erstesEnde || b1 < erstesEnde)) {
            char *b2 = strchr(b1 + 1, '\\');
            if (b2) suchStart = b2 + 1;   // Kommentar frühestens hinter dem schliessenden '\'
        }
    }
    return strpbrk(suchStart, ";\n");
}

// löst eine Stringzeile in die .SPx-Struktur auf und gibt diese zurück.
void processLine(char *line, lineElements linesAsm_p[], int *lineCount) {
    int posIndex = 0;

    // Aktuelle Zeile initialisieren
    resetParsedLinesArrays(linesAsm_p, *lineCount);
    trimLeadingSpaces(line);

    while (*line) {

        if ((posIndex == 0) && ((*line == ';') || (*line == '#') || (*line == '$')  || (*line == '&') )) {
            STRKOPIE(linesAsm_p[*lineCount].sp1, line);
            removeNewlines(linesAsm_p[*lineCount].sp1);
            trimWhitespace(linesAsm_p[*lineCount].sp1);
            (*lineCount)++;
            return;
        }

        if ((*line != ' ') && (*line != '\t') && (*line != ';') && (*line != '#')  && (*line != '$')  && (*line != '&') && (posIndex == 0)) {
            char *colonPos = strchr(line, ':');
            if (colonPos) {
                int labelLength = colonPos - line + 1;  // +1, um `:` einzuschließen
                strncpy(linesAsm_p[*lineCount].sp1, line, labelLength);
                linesAsm_p[*lineCount].sp1[labelLength] = '\0'; // Nullterminierung
                removeNewlines(linesAsm_p[*lineCount].sp1);
                trimWhitespace(linesAsm_p[*lineCount].sp1);
                line = colonPos + 1;
                posIndex = labelLength;  // Kein `+1`, da `:` bereits enthalten ist
            }
        }

        while (*line && isspace((unsigned char)*line)) line++;

        char *nextSpace = strpbrk(line, " \t\n");
        if (nextSpace) {
            if ((*line == ';') && (posIndex > 0)) {
                STRKOPIE(linesAsm_p[*lineCount].sp4, line);
                removeNewlines(linesAsm_p[*lineCount].sp4);
                trimWhitespace(linesAsm_p[*lineCount].sp4);
                (*lineCount)++;
                return;
            }

            while (*line && isspace((unsigned char)*line)) { line++; posIndex++; }
            char *nextSpace_in = strpbrk(line, " \t\n;");
            int wordLength = nextSpace_in ? (int)(nextSpace_in - line) : (int)strlen(line);

            strncpy(linesAsm_p[*lineCount].sp2, line, wordLength);
            linesAsm_p[*lineCount].sp2[wordLength] = '\0';
            removeNewlines(linesAsm_p[*lineCount].sp2);
            trimWhitespace(linesAsm_p[*lineCount].sp2);

            posIndex += wordLength;
            line += wordLength; 

            while (*line && isspace((unsigned char)*line)) { line++; posIndex++; }

            char *restEnd = findeOperandEnde(linesAsm_p[*lineCount].sp2, line);
            int restLength = restEnd ? (int)(restEnd - line) : (int)strlen(line);
            strncpy(linesAsm_p[*lineCount].sp3, line, restLength);
            linesAsm_p[*lineCount].sp3[restLength] = '\0';
            removeNewlines(linesAsm_p[*lineCount].sp3);
            trimWhitespace(linesAsm_p[*lineCount].sp3);
            posIndex += restLength;
            line += restLength;
            removeNewlines(line);
            if (strlen(line) == 0) {
                (*lineCount)++;
                return;
            }
        }

        if ((*line == ';') && (posIndex > 0)) {
            STRKOPIE(linesAsm_p[*lineCount].sp4, line);
            removeNewlines(linesAsm_p[*lineCount].sp4);
            trimWhitespace(linesAsm_p[*lineCount].sp4);
            (*lineCount)++;
            return;
        }

        // nur Operationscode angegeben
        if (( strlen(line) > 0) ) {
            STRKOPIE(linesAsm_p[*lineCount].sp2, line);
            removeNewlines(linesAsm_p[*lineCount].sp2);
            trimWhitespace(linesAsm_p[*lineCount].sp2);
            (*lineCount)++;
            return;
        }

//        if (*line == '\n' || *line == '\0') {
            (*lineCount)++;
            return;
//        }
    }

    (*lineCount)++;
}

// Pragma   ;#; LEITADRESSE xx
//   - steht als Kommentarzeile im Quelltext und muss VOR `start` stehen,
//   - darf keinmal oder genau einmal vorkommen (Standard ohne Pragma: 01),
//   - xx ist zweistellig und liegt zwischen 00 und 09.
// Wirkung: Alle Befehle und Konstanten, die im Objektcode (.obj) bisher mit dem Kennzeichen 01 erzeugt
// wurden, erhalten stattdessen den Wert xx (siehe schreibeObjZeile).
// Bei xx = 00 entfaellt ausserdem die Kennzeichenzeile "21 0000 <zahl>" des start-Operanden (siehe pass3).
// Liefert 1, wenn die Zeile ein LEITADRESSE-Pragma ist (auch ein fehlerhaftes), sonst 0.
static int verarbeiteLeitadressePragma(const char *zeile, int zeilennr, int startGesehen) {
    const char *p = zeile;
    while (*p == ' ' || *p == '\t') p++;
    if (strncmp(p, ";#;", 3) != 0) return 0;
    p += 3;
    while (*p == ' ' || *p == '\t') p++;

    char wort[32];
    size_t n = 0;
    while (isalnum((unsigned char)*p) || *p == '_') {
        if (n < sizeof(wort) - 1) wort[n++] = *p;
        p++;
    }
    wort[n] = '\0';
    if (!gleichOhneGrossKlein(wort, "LEITADRESSE")) return 0;   // anderes ";#;"-Kommentar: bleibt Kommentar

    while (*p == ' ' || *p == '\t') p++;

    if (startGesehen) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Das Pragma LEITADRESSE muss vor `start` stehen.", zeilennr);
        is_error = 1;
        return 1;
    }
    if (leitadressePragmaGesetzt) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Das Pragma LEITADRESSE darf nur einmal vorkommen.", zeilennr);
        is_error = 1;
        return 1;
    }
    leitadressePragmaGesetzt = 1;

    // Wert: genau zwei Ziffern 00 ... 09; danach nur noch Leerraum oder ein Kommentar (;).
    int wertOk = isdigit((unsigned char)p[0]) && isdigit((unsigned char)p[1])
                 && (p[2] == '\0' || p[2] == ' ' || p[2] == '\t' || p[2] == ';' || p[2] == '\r' || p[2] == '\n');
    int wert = wertOk ? (p[0] - '0') * 10 + (p[1] - '0') : 0;
    if (!wertOk || wert < 0 || wert > 9) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Das Pragma LEITADRESSE erwartet einen zweistelligen Wert von 00 bis 09 (z. B. ;#; LEITADRESSE 02).", zeilennr);
        is_error = 1;
        return 1;
    }
    leitadresseKennzeichen = wert;
    return 1;
}

// Blockkommentar: Eine Zeile, die ab Spalte 1 genau ``` enthaelt (danach nur Leerraum), eroeffnet bzw.
// beendet einen Blockkommentar. Alles dazwischen (und die beiden ```-Zeilen selbst) wird wie ein
// Kommentar ueberlesen und erzeugt keine Programmzeile.
static int istBlockkommentarGrenze(const char *s) {
    if (strncmp(s, "```", 3) != 0) return 0;
    for (s += 3; *s; s++) {
        if (*s != ' ' && *s != '\t' && *s != '\r' && *s != '\n') return 0;
    }
    return 1;
}

void ladeAssemblerZeilen(const char *inputFileName_p) {
    FILE *inputFile = fopen(inputFileName_p, "r");
    if (!inputFile) {
        fprintf(stderr, "Fehler: Datei '%s' konnte nicht geöffnet werden!\n", inputFileName_p);
        exit(RC_FEHLER); // Programm beenden, falls Datei nicht geöffnet werden konnte
    }

    char line[1024];
    int zeilennr = 0;
    int vorigeZeileOffen = 0;   // 1 = vorige fgets-Teilzeile hatte kein Zeilenende (Zeile laenger als Puffer)
    int startGesehen = 0;       // 1, sobald die Anweisung `start` gelesen wurde (Pragma LEITADRESSE muss davor stehen)
    int imBlockkommentar = 0;   // 1 = zwischen zwei ```-Zeilen
    int blockkommentarStart = 0; // Quelltextzeile, in der der offene Blockkommentar begann
    while (fgets(line, sizeof(line), inputFile)) {
        int hatZeilenende = (strchr(line, '\n') != NULL);

        if (vorigeZeileOffen) {            // Rest einer bereits gemeldeten, zu langen Zeile ueberspringen
            vorigeZeileOffen = !hatZeilenende;
            continue;
        }
        if (zeilennr == 0 && (unsigned char)line[0] == 0xEF && (unsigned char)line[1] == 0xBB && (unsigned char)line[2] == 0xBF) {
            memmove(line, line + 3, strlen(line + 3) + 1);   // UTF-8-Bytefolgemarke (BOM, z. B. aus dem Windows-Editor) ueberspringen
        }
        zeilennr++;

        // Blockkommentar (```-Zeilen und alles dazwischen) - auch zu lange Zeilen darin sind kein Fehler
        int istGrenze = istBlockkommentarGrenze(line);
        if (istGrenze || imBlockkommentar) {
            if (!hatZeilenende && !feof(inputFile)) vorigeZeileOffen = 1;
            if (istGrenze) {
                imBlockkommentar = !imBlockkommentar;
                if (imBlockkommentar) blockkommentarStart = zeilennr;
            }
            continue;
        }

        if (*line == '\0' || strcmp(line, "\n") == 0) {
            continue;
        }

        removeNewlines(line);

        // Die internen Zeilenpuffer (elementType) fassen nur MAX_QUELLZEILE Zeichen (Bytes).
        // Laengere Zeilen wuerden einen Pufferueberlauf (Absturz) ausloesen -> sauber melden.
        size_t laenge = strlen(line);
        if (laenge > 0 && line[laenge - 1] == '\r') {
            line[--laenge] = '\0';
        }
        if (!hatZeilenende && !feof(inputFile)) {
            vorigeZeileOffen = 1;
            laenge = MAX_QUELLZEILE + 1;   // laenger als der Lesepuffer, also sicher zu lang
        }
        if (laenge > MAX_QUELLZEILE) {
            PRINT_FEHLER("Zeile %d der Quelldatei ist zu lang (mehr als %d Zeichen); bitte kuerzen oder umbrechen.", zeilennr, MAX_QUELLZEILE);
            is_error = 1;
            continue;
        }
        if (lineCountAsm >= ZEILEN_GRENZE) {
            meldeZuVieleZeilen(zeilennr);
            is_error = 1;
            break;
        }
        verarbeiteLeitadressePragma(line, zeilennr, startGesehen);   // vor processLine: line wird dort veraendert
        int zeilenVorher = lineCountAsm;
        {
            int vorher = lineCountAsm;
            processLine(line, linesAsm, &lineCountAsm);
            for (int k = vorher; k < lineCountAsm; k++) linesAsm[k].srcLine = zeilennr;
        }
        if (lineCountAsm > zeilenVorher && gleichOhneGrossKlein(linesAsm[lineCountAsm - 1].sp2, "start")) {
            startGesehen = 1;
        }
    }
    fclose(inputFile); 

    if (imBlockkommentar) {
        PRINT_FEHLER("Zeile %d der Quelldatei: Der Blockkommentar (```) wird bis zum Dateiende nicht geschlossen.", blockkommentarStart);
        is_error = 1;
    }

    //printAssemblerzeilenArray() ;
}


// ------------------------------








// ######################################################

const int trommel_sektor_map[32] = {
    0, 015, 032, 07, 024, 01, 016, 033, 010, 025, 02,
    017, 034, 011, 026, 03, 020, 035, 012, 027, 04, 021,
    036, 013, 030, 05, 022, 037, 014, 031, 06, 023
};

unsigned int berechneWiederholAdr(int anzahl, unsigned int basisAdr ) {
    int x = 31 - anzahl - 1;
    unsigned int sektor = trommel_sektor_map[x] + basisAdr;

    return sektor;
}

int berechneOperand(const char *operand_str) {
    int zahl1, zahl2;
    char op;

    // Versuch, einen mathematischen Ausdruck zu parsen: z.B. "9-1" oder "-5+3"
    if (sscanf(operand_str, "%d %c %d", &zahl1, &op, &zahl2) == 3) {
        switch (op) {
            case '+': return zahl1 + zahl2;
            case '-': return zahl1 - zahl2;
            case '*': return zahl1 * zahl2;
            case '/': return zahl2 != 0 ? zahl1 / zahl2 : 0; // Division durch 0 vermeiden
            default: fprintf(stderr, "Fehler: Unbekannter Operator '%c'\n", op); return 0;
        }
    }

    // Falls kein Operator gefunden wurde, einfach die Zahl konvertieren
    return strtol(operand_str, NULL, 10);
}


void verarbeiteZeile_wdhl_adr_e(char *tempLine) {
    char *start = strstr(tempLine, "!$wdhl_adr_e");

    // Suche nach dem Operand (erste Zahl nach !#wdhl")
    start += 12; // Springt hinter "!#wdhl_adr_e"
    while (*start == ' ') start++; // Ignoriere Leerzeichen

    char operand_str[MAX_LINE_LENGTH];
    sscanf(start, "%s", operand_str);

    // Berechne den Wert des Operanden
    //int operand_value = strtol(operand_str, NULL, 10) - 1; // `9-1` → `8`
    int operand_value = berechneOperand(operand_str);
    unsigned int sektor_address = berechneWiederholAdr(operand_value, 07700);

    // Erstelle die neue Zeile mit der oktalen Sektoradresse (mit Vornull)
    char neueZeile[MAX_LINE_LENGTH];
    snprintf(neueZeile, sizeof(neueZeile), "     !$wdhl_adr_e   %05o     ; %d mal Linksverschiebung", sektor_address, operand_value);
    strkopiere(tempLine, MACRO_PARAMETER_LAENGE, neueZeile);

    char *pos = strstr(tempLine, "!$wdhl_adr_e");
    if (pos != NULL) {
        // Länge des zu ersetzenden Substrings ermitteln
        size_t lenAlt = strlen("!$wdhl_adr_e");
        size_t lenNeu = strlen("644");

        // Verschiebt den restlichen Text nach links, falls nötig
        memmove(pos + lenNeu, pos + lenAlt, strlen(pos + lenAlt) + 1);
        memcpy(pos, "644", lenNeu);
    }
}

int verarbeiteZeile_wdhl(char *tempLine, char *loe, char *resu, char *opcode, char *anzahl, char *adresse) {
    char op[32]={0};
    int rc = 0 ;

    int berechneOpString(char *opStr, char *rStr, char *loe_p, char *result) {
        (void)rStr;
        int rc_in = 0;
        char *OPCODE[]              = { "KON", "ADD", "SUB", "BADD" };
        int OP_Table[]              = { 060, 061, 062, 063 };
        int R_Zuordnung[]           = { 04, 02, 06, 0 };
        int R_Zuordnung_Loe[]       = { 05, 03, 07, 01 };

        int opNum = -1, rNum = -1;

        for (size_t i = 0; i < sizeof(OPCODE) / sizeof(OPCODE[0]); i++) {
            if (strcmp(opStr, OPCODE[i]) == 0) {
                opNum = OP_Table[i];
                break;
            }
        }

        if ( opNum == -1 ) { return -1; }

        // R-Zuordnung basierend auf LOE (JA vs NE)
        int *R_Table = (strcmp(loe_p, "JA") == 0) ? R_Zuordnung_Loe : R_Zuordnung;
        for (size_t i = 0; i < sizeof(OPCODE) / sizeof(OPCODE[0]); i++) {
            if (strcmp(opStr, OPCODE[i]) == 0) {
                rNum = R_Table[i];
                break;
            }
        }

        if ( rNum == -1 ) { return -1; }

        // Falls beide Werte gefunden wurden, erstelle den Ziffernstring
        if (opNum != -1 && rNum != -1) {
            snprintf(result, 10, "%o%o", opNum, rNum);
        } else {
            strkopiere(result, 32, "Macro gen. Op-Code Mismatch ??"); // Fehlerfall
            rc_in = -1;
        }

        return rc_in;
    }

    rc = berechneOpString(opcode, resu, loe, op);
    if ( (rc == -1 ) || ( rc == -2 ) ) { return rc; }

    unsigned int basis_adr;
    if ( adresse[0] == '0' ) {
       basis_adr = strtol(adresse, NULL, 8);
    } else { 
       basis_adr = strtol(adresse, NULL, 10);
    }

    int anz = berechneOperand(anzahl);
    unsigned int sektor_address = berechneWiederholAdr(anz, basis_adr);

    char neueZeile[MAX_LINE_LENGTH];
    snprintf(neueZeile, sizeof(neueZeile), "     !#wdhl   %05o     ; %d mal Linksverschiebung", (unsigned int)  sektor_address, anz);
    strkopiere(tempLine, MACRO_PARAMETER_LAENGE, neueZeile);

    char *pos = strstr(tempLine, "!#wdhl");
    if (pos != NULL) {
        memmove(pos + 3, pos + 6, strlen(pos + 6) + 1);
        memcpy(pos, op, 3);
    }
    if ( (rc == -3 )  ) { return rc; }
    return 0;
}
