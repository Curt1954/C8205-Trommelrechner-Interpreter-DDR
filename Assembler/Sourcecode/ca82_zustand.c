// ca82_zustand.c - Globale Zustandsvariablen des Assemblers (Zeilenfelder, Fehlerkennzeichen, Dateinamen)
// Teil des C8205-Assemblers c82ass, Version siehe ca82_version.h
#include "ca82_intern.h"



char fehlertext[4096];


lineElements linesAsm[PROGRAMMZEILEN];  //2 MB
int lineCountAsm = 0; 


lineElements lineAsmAufgeloest[PROGRAMMZEILEN];
int lineCountAsmAufgeloest = 0; 

lineElements lineAsmAufgeloestTemp[PROGRAMMZEILEN];
int lineCountAsmAufgeloestTemp = 0; 


lineElementsX lineAsmAufgeloestX[PROGRAMMZEILEN];
int lineCountAsmAufgeloestX = 0; 


// ------------------------------
int is_error  = 0;
int is_error0 = 0;
int is_error1 = 0;
int is_error2 = 0;
int is_error3 = 0;
int is_error_abs = 0;
int printHell = 0;

// Pragma ";#; LEITADRESSE xx": Kennzeichen, das im Objektcode (.obj) und im Listing (STDOUT, .dmp) anstelle von 01 ausgegeben wird.
// Standard 01, erlaubt sind 00 bis 09.
// Wert 00: Der Code wird so ausgegeben, wie ihn der Assembler erzeugt hat, mit dem Kennzeichen 00 statt 01
// (bereits absolut codiertes Programm). Die Kennzeichenzeile "21 0000 <zahl>" fuer den Operanden von `start`
// (Hauptleitadresse, "Leitbefehl") wird dann nicht in den Objektcode und nicht in das Listing geschrieben.
int leitadresseKennzeichen = 1;
int leitadressePragmaGesetzt = 0;   // 1, wenn das Pragma im Quelltext angegeben war

unsigned int absolutadresse;



int line_ausgegeben=0;



// ############################################


unsigned int startAdresse = 0;

char inputFileName[1024] = "";
