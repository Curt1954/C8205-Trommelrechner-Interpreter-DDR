// ca82_berichte.h - Version 1.00-030 (siehe ca82_version.h)
// Aufrufhilfe, Versionszeile und Berichte nach dem Lauf: -WARN=SYM (unbenutzte Symbole), --xref (Querverweisliste).
#ifndef CA82_BERICHTE_H
#define CA82_BERICHTE_H

extern int warnSym;     // 1 = Aufruf mit -WARN=SYM
extern int xrefAktiv;   // 1 = Aufruf mit --xref

void printUsage(const char *programName);
void greetings(void);
void verarbeiteWarnOptionen(int argc, char *argv[]);
void pruefeUnbenutzteSymbole(void);   // nach fehlerfreiem Pass 3
void erzeugeQuerverweisliste(void);   // nach fehlerfreiem Pass 3
void xrefMerkeMakroOperand(int quellzeile, const char *operand);   // Pass 0: Operand einer Makroexpansion (nur mit --xref)

#endif
