#!/bin/sh
# Version 1.00-026
# Erzeugt den C8205-Assembler fuer Linux (aus dem Verzeichnis Assembler aufrufen).
# Die Warnungen (-Wall -Wextra -Wshadow) sind eingeschaltet; der Quelltext uebersetzt ohne Warnung.
mkdir -p ./_Linux
gcc -O2 -Wall -Wextra -Wshadow --static -o ./_Linux/c82ass ./Sourcecode/ca82_protokoll.c ./Sourcecode/ca82_standards.c ./Sourcecode/ca82_symbole.c ./Sourcecode/ca82_berichte.c ./Sourcecode/ca82_makros.c ./Sourcecode/ca82_zustand.c ./Sourcecode/ca82_hilfen.c ./Sourcecode/ca82_fehler.c ./Sourcecode/ca82_quelle.c ./Sourcecode/ca82_listing.c ./Sourcecode/ca82_pass0.c ./Sourcecode/ca82_pass1.c ./Sourcecode/ca82_pass2.c ./Sourcecode/ca82_ausdruck.c ./Sourcecode/ca82_codierung.c ./Sourcecode/ca82_pass3.c ./Sourcecode/ca82_fluss.c ./Sourcecode/ca82_testdatei.c ./Sourcecode/ca82_main.c
