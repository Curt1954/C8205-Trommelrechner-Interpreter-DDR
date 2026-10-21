// ca82_ausdruck.c - Auswertung von Werte- und Adressausdruecken
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"


// -------------------------------------------------------

// Grund des letzten Fehlers von evaluateValue (NULL = kein besonderer Grund, nur Syntax-/Bereichsfehler).
// Wird von Pass 3 an die Meldung "Operand ist ungueltig" angehaengt.
const char *evaluateValueGrund = NULL;

// Liefert 1 und setzt *wert und *absolut, wenn das Symbol in der Symboltabelle steht (sonst 0).
// *absolut = 1: Symbol wurde mit abs definiert (nicht verschieblich); sonst ist es eine Relativadresse
// (Marke, equ-Symbol, Literalsymbol).
static int sucheSymbolFuerWert(const char *name, long long *wert, int *absolut) {
    for (int i = 0; i < symbolCount; i++) {
        if (strcmp(symbolTable[i].symbol, name) == 0) {
            symbolTable[i].verwendet = 1;   // Verwendung in einem Ausdruck (-WARN=SYM)
            *wert = (long long)(symbolTable[i].address & ~BITMASK);
            *absolut = sucheInAbsTabelle(name) ? 1 : 0;
            return 1;
        }
    }
    return 0;
}

// Wertet den <werteausdruck> von dw aus (Doku 3.3).
//   Zahlen:    Oktalzahl (fuehrende 0) oder Dezimalzahl.
//   Symbole:   abs-Symbole sind erlaubt. Relative Symbole (Marken, equ-Symbole) sind nur erlaubt, wenn sich ihre
//              Verschiebung aufhebt: paarweise Differenzen symbolischer Adressen, auch mehrfach (a-b+c-d),
//              sind absolut und zulaessig.
//              Eine einzelne symbolische Adresse (Ergebnis relativ) ist nicht zulaessig; Adressen schreibt man mit da.
//   Rechnen:   * und / vor + und -, links nach rechts. Relative Symbole duerfen nicht multipliziert oder dividiert werden.
// Jedes Symbol wird mit seinem Verschiebungsgrad gefuehrt: abs-Symbole und Zahlen 0, relative Symbole +1;
// bei + addieren, bei - subtrahieren sich die Grade. Das Ergebnis ist nur bei Grad 0 absolut.
long long int evaluateValue(char *operand, int *errorFlag) {
    long long values[512];     // vorzeichenbehaftet, damit Subtraktion und negative Werte stimmen
    int       grade[512];      // Verschiebungsgrad je Wert (0 = absolut)
    char operators[512];
    int valueIndex = 0, operatorIndex = 0;

    *errorFlag = 0; // Standardmäßig kein Fehler
    evaluateValueGrund = NULL;

    char *currentPos = operand;

    while (*currentPos != '\0') {
        while (*currentPos == ' ') currentPos++;

        char tempToken[512];
        int tokenLength = 0;

        // Extrahiere Zahl oder Symbol bis zum Operator
        while (*currentPos != '\0' && !strchr("+-*/", *currentPos)) {
            if (!(isalnum((unsigned char)*currentPos) || *currentPos == '_') || tokenLength >= (int)sizeof(tempToken) - 1) {
                *errorFlag = 1;
                return 0;
            }
            tempToken[tokenLength++] = *currentPos;
            currentPos++;
        }
        tempToken[tokenLength] = '\0';

        // Fuehrendes Vorzeichen (-5, +5): als 0-5 bzw. 0+5 auswerten
        if (tokenLength == 0 && valueIndex == 0 && *currentPos != '\0' && strchr("+-", *currentPos)) {
            grade[valueIndex] = 0;
            values[valueIndex++] = 0;
        }

        if (tokenLength > 0) {
            long long value = 0;
            int grad = 0;
            if (isdigit((unsigned char)tempToken[0])) {
                // Zahl: nur Ziffern
                char *endPtr;
                if (tempToken[0] == '0') {
                    value = strtol(tempToken, &endPtr, 8);
                } else {
                    value = strtol(tempToken, &endPtr, 10);
                }
                if (*endPtr != '\0') {
                    *errorFlag = 1; // Nicht konvertierbarer Wert
                    return 0;
                }
            } else {
                // Symbol
                int absolut = 0;
                if (!sucheSymbolFuerWert(tempToken, &value, &absolut)) {
                    evaluateValueGrund = "Symbol nicht definiert";
                    *errorFlag = 1;
                    return 0;
                }
                grad = absolut ? 0 : 1;
            }
            grade[valueIndex] = grad;
            values[valueIndex++] = value; // Speichere den konvertierten Wert
        }

        // Speichere den Operator
        if (*currentPos != '\0' && strchr("+-*/", *currentPos)) {
            operators[operatorIndex++] = *currentPos;
            currentPos++;
        }
    }

    // Jeder Operator braucht einen rechten Operanden (z. B. "5-" ist ungueltig)
    if (operatorIndex >= valueIndex) {
        *errorFlag = 1;
        return 0;
    }

    // Multiplikation und Division zuerst ausführen
    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '*' || operators[i] == '/') {
            long long leftValue = values[i];
            long long rightValue = values[i + 1];

            // Eine relative Adresse darf nicht multipliziert oder dividiert werden.
            if (grade[i] != 0 || grade[i + 1] != 0) {
                evaluateValueGrund = "symbolische Adresse in * oder /";
                *errorFlag = 1;
                return 0;
            }

            if (operators[i] == '*') {
                if (__builtin_mul_overflow(leftValue, rightValue, &values[i])) {
                    evaluateValueGrund = "Ueberlauf bei der Multiplikation";
                    *errorFlag = 1; // Ueberlauf
                    return 0;
                }
            } else if (operators[i] == '/') {
                if (rightValue == 0) {
                    evaluateValueGrund = "Division durch 0";
                    *errorFlag = 1; // Division durch Null ist unzulässig
                    return 0;
                }
                values[i] = leftValue / rightValue;
            }

            // Werte und Operatoren verschieben
            for (int j = i + 1; j < valueIndex - 1; j++) {
                values[j] = values[j + 1];
                grade[j] = grade[j + 1];
            }
            valueIndex--;
            for (int j = i; j < operatorIndex - 1; j++) {
                operators[j] = operators[j + 1];
            }
            operatorIndex--;
            i--;
        }
    }

    // Addition und Subtraktion ausführen
    long long totalValue = values[0];
    int totalGrad = grade[0];
    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '+') {
            if (__builtin_add_overflow(totalValue, values[i + 1], &totalValue)) { *errorFlag = 1; return 0; }
            totalGrad += grade[i + 1];
        } else if (operators[i] == '-') {
            if (__builtin_sub_overflow(totalValue, values[i + 1], &totalValue)) { *errorFlag = 1; return 0; }
            totalGrad -= grade[i + 1];
        }
    }

    // Ergebnis relativ (z. B. eine einzelne symbolische Adresse, "a+1", "a+b"): nicht zulaessig.
    if (totalGrad != 0) {
        evaluateValueGrund = "Ergebnis ist relativ; Adressen mit da schreiben, erlaubt sind nur paarweise Differenzen von Adressen";
        *errorFlag = 1;
        return 0;
    }

    return totalValue;
}


// ############################


// Prüfung auf nummerisch
int isValidToken(const char *tempToken) {
    for (int i = 0; tempToken[i] != '\0'; i++) {
        if (!(tempToken[i] == '-' || (tempToken[i] >= '0' && tempToken[i] <= '9'))) {
            return 0; // Ungültiges Zeichen gefunden
        }
    }
    return 1; // Alle Zeichen sind gültig
}

unsigned int sternadresseBearbeiten(char *xoperand, char *line, int *errorFlag, unsigned int programCounter) {
    if (!xoperand) {
        printAdressError(xoperand, "Operand", "Ungültige Sternadresse", line);
        *errorFlag = -1;
        return 0;
    }

    unsigned int result = programCounter; // Setze die Sternadresse

    char operand[1024];
    STRKOPIE(operand, xoperand);
    char *expr = operand + 1; // Ignoriere das erste '*'
    char *token = strtok(expr, "+-*/");
    char lastOperator = '+'; // Standardmäßig Addition
    unsigned int value;

    while (token) {
        if (isdigit(token[0])) {
            if (token[0] == '0') {
               value = strtoul(token, NULL, 8);
            } else {  
               value = strtoul(token, NULL, 10);
            }
            switch (lastOperator) {
                case '+': result += value; break;
                case '-': result -= value; break;
                case '*': result *= value; break;
                case '/': if (value != 0) result /= value; else {
                              printAdressError(token, "Operand", "Division durch Null", line);
                              *errorFlag = -1;
                              return 0;
                          }
                          break;
            }
        } else {
            int symbolValue = getSymbolAddress(token);
            if (symbolValue == -1) {
                printAdressError(token, "Operand", "Ungültiges Symbol", line);
                *errorFlag = -1;
                return 0;
            }
            switch (lastOperator) {
                case '+': result += symbolValue; break;
                case '-': result -= symbolValue; break;
                case '*': result *= symbolValue; break;
                case '/': if (symbolValue != 0) result /= symbolValue; else {
                              printAdressError(token, "Operand", "Division durch Null", line);
                              *errorFlag = -1;
                              return 0;
                          }
                          break;
            }
        }

        char *operatorToken = strtok(NULL, "+-*/");
        if (operatorToken) {
            lastOperator = expr[token + strlen(token) - operand];
            token = strtok(NULL, "+-*/");
        } else {
            token = NULL;
        }
    }

    return result;
}

unsigned int evaluateAddress(char *operand, char *line, int *errorFlag, int *raAdr, char *label, unsigned int programCounter, unsigned int *absolutadresse_p) {
    unsigned int values[MAX_LINE_LENGTH];
    values[0] = 0;
    char operators[MAX_LINE_LENGTH];
    int valueIndex = 0, operatorIndex = 0, symbolCount_p = 0;

    *errorFlag = 0;      // Standardmäßig kein Fehler
    *raAdr = 0;          // Standardmäßig keine relativAdresse
    *absolutadresse_p = 0; // Standartmäßig relativ

    char *endPtr;    
    char *currentPos = operand;
    unsigned int totalValue=0;

    if (*currentPos == '*') {
       totalValue = sternadresseBearbeiten(operand, line, errorFlag, programCounter) ;
       return totalValue; 
    }

    // currentPos == operand
    while (*currentPos != '\0') {
        while (*currentPos == ' ') currentPos++;

        char tempToken[MAX_LINE_LENGTH];
        int tokenLength = 0;

        while (*currentPos != '\0' && !strchr("+-*/", *currentPos)) {
            tempToken[tokenLength++] = *currentPos;
            currentPos++;
        }
        tempToken[tokenLength] = '\0';

        if (tokenLength > 0) {
            unsigned int value = 0;
            if (isSymbol(tempToken)) {
                symbolCount_p++;

                //testeAdress(tempToken, line);
                if ( sucheInAbsTabelle(tempToken) ) { 
                   *absolutadresse_p = 1;
                }
                value = getSymbolAddress(tempToken);
                if ((int)value == -1) {
                    printAdressError(operand, "Operand", " Ungültiges Symbol", line);
                    *errorFlag = -1; // Fehler: Ungültiges Symbol
                    return 0;
                }

                // Relativadresse für das Symbol finden
                for (int i = 0; i < symbolCount_p; i++) {
                    if (strcmp(symbolTable[i].symbol, tempToken) == 0) {
                        *raAdr = symbolTable[i].relativAdresse;
                        break;
                    }
                }

            } else if (!isValidToken(tempToken) && (strcmp(tempToken, label) == 0)) { 
                value = programCounter;

            } else {
                if (tempToken[0] == '0') {
                            value = strtol(tempToken, &endPtr, 8);
                } else { 
                            value = strtol(tempToken, &endPtr, 10);
                }
                if (*endPtr != '\0') {
                    *errorFlag = -2; 
                    return 0;
                }
            }
            values[valueIndex++] = value;
        }

        if (*currentPos != '\0' && strchr("+-*/", *currentPos)) {
            operators[operatorIndex++] = *currentPos;
            currentPos++;
        }
    }

    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '*' || operators[i] == '/') {
            unsigned int leftValue = values[i];
            unsigned int rightValue = values[i + 1];

            if (operators[i] == '*') {
                values[i] = leftValue * rightValue;
            } else if (operators[i] == '/') {
                if (rightValue == 0) {
                    printAdressError(operand, "Operand", " Division durch Null", line);
                    *errorFlag = -4; // Fehler: Division durch Null
                    return 0;
                }
                values[i] = leftValue / rightValue;
            }

            for (int j = i + 1; j < valueIndex - 1; j++) {
                values[j] = values[j + 1];
            }
            valueIndex--;
            for (int j = i; j < operatorIndex - 1; j++) {
                operators[j] = operators[j + 1];
            }
            operatorIndex--;
            i--;
        }
    }

    totalValue = values[0];

    for (int i = 0; i < operatorIndex; i++) {
        if (operators[i] == '+') {
            totalValue += values[i + 1];
        } else if (operators[i] == '-') {
            totalValue -= values[i + 1];
        }
    }

    return totalValue; 
}


// Prueft den <adressausdruck> von da (und von @-Literalen, die als da-Zeile erzeugt werden) gemaess
// Doku 3.2 (<adressausdruck>): kein Vorzeichen (negative Adressen gibt es nicht), keine fehlenden
// Operanden (z. B. "5-" oder "x+*2"). Die Zahl der Symbole ist nicht begrenzt (die Doku nennt seit der
// erneuerten .odt keine Obergrenze mehr, vgl. 3.3.9: Ausdruck mit abs-Symbol). Der Wertebereich
// 00000 bis 07777 wird nach der Auswertung geprueft. Eine Sternadresse (*) wird von sternadresseBearbeiten geprueft.
// Rueckgabe 1 = in Ordnung, 0 = Fehler (Text in meldung).
int pruefeAdressausdruck(const char *operand, char *meldung, size_t groesse) {
    const char *p = (operand != NULL) ? operand : "";
    while (*p == ' ' || *p == '\t') p++;
    if (*p == '\0') {
        snprintf(meldung, groesse, "Adressausdruck fehlt.");
        return 0;
    }
    if (*p == '*') return 1;
    if (*p == '-' || *p == '+') {
        snprintf(meldung, groesse, "Der Adressausdruck darf nicht mit einem Vorzeichen beginnen (Adressen sind 00000 bis 07777).");
        return 0;
    }
    for (;;) {
        char token[MAX_LINE_LENGTH];
        int n = 0;
        while (*p && !strchr("+-*/", *p)) {
            if (n < (int)sizeof(token) - 1) token[n++] = *p;
            p++;
        }
        while (n > 0 && (token[n - 1] == ' ' || token[n - 1] == '\t')) n--;   // Leerraum am Ende entfernen
        token[n] = '\0';
        if (n == 0) {
            snprintf(meldung, groesse, "Im Adressausdruck fehlt ein Operand (zwei Operatoren hintereinander oder Operator am Ende).");
            return 0;
        }
        if (*p == '\0') break;
        p++;                       // Operator ueberspringen
        if (*p == '\0') {
            snprintf(meldung, groesse, "Im Adressausdruck fehlt ein Operand (zwei Operatoren hintereinander oder Operator am Ende).");
            return 0;
        }
    }
    return 1;
}
