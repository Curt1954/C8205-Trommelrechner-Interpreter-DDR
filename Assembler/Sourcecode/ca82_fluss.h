// ca82_fluss.h - Version 1.00-030 (siehe ca82_version.h)
// Ablaufpruefungen nach Pass 3: -WARN=SPR (Sprungziel ist kein Befehl) und -WARN=TOT (nicht erreichbarer Code).
#ifndef CA82_FLUSS_H
#define CA82_FLUSS_H

extern int warnSpr;   // 1 = Aufruf mit -WARN=SPR
extern int warnTot;   // 1 = Aufruf mit -WARN=TOT

// Von Pass 3 aufgerufen: merkt sich, was an welcher Trommeladresse steht.
void flussZuruecksetzen(void);
void flussMerkeBefehl(int adresse, const char *opcode, int hatZiel, int ziel, int zielAbsolut, int zeile);
void flussMerkeDaten(int von, int bis, const char *operation, int zeile);
void flussMerkeVerweis(int adresse);   // ein da-Wort enthaelt diese (relative) Adresse

// Nach fehlerfreiem Pass 3 aufgerufen (main).
void pruefeSprungziele(void);
void pruefeToterCode(void);

#endif
