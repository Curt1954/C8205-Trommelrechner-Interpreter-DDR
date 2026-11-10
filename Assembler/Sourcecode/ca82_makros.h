// ca82_makros.h - Version 1.03-009 (siehe ca82_version.h)
#ifndef CA82_MAKROS_H
#define CA82_MAKROS_H

#include "ca82_typen.h"

// ---- Daten des Makromoduls ----
extern macroDefinitionen *macros;
extern int macroCount;
extern int macroCapacity;
extern char recursiv_macro[128];

// ---- Vom Makromodul angebotene Funktionen ----
void erzeugeMacroArray(const char *macroFileName);
lineElements *loeseMacroAuf(macroDefinitionen *macros_p, int *macroCount_p, char *aktuellerOpCode,
                            char *aktuelleParameterZeile, int *lineCount, char *label);
void macroSprung1Aufloesen(lineElements **ergebnis, int *lineCount, char *mna, int seed, int meldeUngueltig);   // generische und lesbare lokale Labels <name>% (z. B. ML0001%, schleife%) eines Makroaufrufs ersetzen (seed = Nummer des Aufrufs)
int makroIstErzeugtesLabel(const char *name);   // 1, wenn c82ass das Label aus einem lesbaren lokalen Label <name>% erzeugt hat (Berichte: nicht als unbenutzt melden)
// Hook des Pass 0: loest eine Zeile auf, die ein Makroaufruf ist, samt aller verschachtelten Aufrufe (Rueckgabe malloc, *anzahl Zeilen);
// NULL, wenn die Zeile kein Makroaufruf ist. Das Makromodul ruft ihn fuer jede Zeile eines Makrorumpfs auf, damit verschachtelte Aufrufe in Quelltextreihenfolge aufgeloest werden.
extern lineElements *(*makroAufrufHook)(const lineElements *zeile, int *anzahl);
void quelltextDirektivenAuswerten(void);   // $-Direktiven ($IF, $REPT, $SET ...) im normalen Quelltext auswerten (Doku 4.1); nur wenn eine Zeile mit $ beginnt
void meldeZuVieleZeilen(int quellzeile);
void printAllMacros(void);
int sammleQuelltextMakros(void);          // Makrodefinitionen im Quelltext; Rueckgabe: Anzahl Fehler
int beginntMitSemikolon(const char *line);
int makroDateiSetzen(const char *pfad);   // Option -m; 0 = ok, -1 = Pfad zu lang
const char *makroDateiName(void);
int makroHerkunftFuerAufruf(const char *opcode, char *ziel, size_t n);   // Herkunft eines Makros fuer die Aufrufzeile im Listing (--makros)
void makroListeSichern(void);            // vor dem Freigeben der Makrotabelle: Liste fuer --makros sichern
void makroListeAusgeben(void);           // Makroliste (--makros) auf STDOUT und ins .log
int ladeProjektMakrodateien(void);        // Anweisungen ;#MACRODATEI1= bis ;#MACRODATEI9= im Quelltext; Rueckgabe: Anzahl Fehler
int makroSpecFehler(void);                // Zahl der Fehler in $SPEC-Zeilen der Makrodateien (ab 1.03-002, Doku 4.32); nach dem Laden der Makrodateien abfragen
int ladeMakroLokalSchalter(void);         // Anweisung ;#MAKROLOKAL=1 im Quelltext (ab 1.02-001, Doku 4.31); Rueckgabe: Anzahl Fehler
extern int optMakroUmordnen;               // 1 = Makro-Umordnung an (Doku 5.6, ca82_opt.c); gesetzt von ladeMakroUmordnenSchalter
#define MAKRO_UMORDNEN_VORGABE 1           // Vorgabe ohne ;#MAKROUMORDNEN: 1 = an (E4, Doku 5.6), 0 = aus
int ladeMakroUmordnenSchalter(void);       // Anweisung ;#MAKROUMORDNEN=YES/NO im Quelltext (ab 1.03-007, Doku 5.6); Rueckgabe: Anzahl Fehler
int ladeObjBefehle(void);                 // Anweisungen ;#PRECOMMAND=<Wert> und ;#POSTCOMMAND=<Wert> (ab 1.03-009, Doku 3.1e); Rueckgabe: Anzahl Fehler
void schreibeObjPre(FILE *f);              // alle PRECOMMAND als Lochbilder vor das erste Wort des .obj
void schreibeObjPost(FILE *f);             // alle POSTCOMMAND hinter das letzte Wort, vor das Endekennzeichen /

// Ort des aeussersten Makroaufrufs im Quelltext (fuer $NOTE und $DUMP, Doku 4.24) und Name der Quelldatei
extern int pass0AeussereZeile;
extern char inputFileName[1024];

// Zaehler der aufgeloesten Makros (Begrenzung seed_max)
extern int seed_value;
extern int seed_max;

// ---- Vom Makromodul benoetigte Daten und Funktionen des Hauptprogramms (ca82ass.c) ----
extern lineElements linesAsm[PROGRAMMZEILEN];
extern int lineCountAsm;
extern int is_error;
extern int is_error0;

void copyLineElements(lineElements *output, lineElements *ergebnis, int i);
void processLine(char *line, lineElements linesAsm_p[], int *lineCount);
void verarbeiteZeile_wdhl_adr_e(char *tempLine);
int verarbeiteZeile_wdhl(char *tempLine, char *loe, char *resu, char *opcode, char *anzahl, char *adresse);
int berechneOperand(const char *operand_str);

#endif
