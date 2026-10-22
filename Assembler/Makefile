# Version 1.00-030
# Erzeugt und prueft den C8205-Assembler c82ass (aus dem Verzeichnis Assembler aufrufen).
#   make            Linux-Binary _Linux/c82ass erzeugen (mit -Wall -Wextra -Wshadow)
#   make test       Regressionstest (139 Programme, 54 Negativtests)
#   make pruefen    Gesamtpruefung mit -Werror und AddressSanitizer/UBSan (Regressionstest/pruefe_alles.sh)
#   make fuzz       Zufallstest (Regressionstest/fuzz.py) mit Sanitizer-Binary; FUZZ_N=Laeufe, FUZZ_SEED=Startwert
#   make clean      Binary entfernen
# Die Quelldatei-Liste steht nur hier; make_c82ass.sh und make_c82ass.bat bleiben fuer den Aufruf ohne make.
CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -Wshadow
SRC      = $(addprefix Sourcecode/, ca82_protokoll.c ca82_standards.c ca82_symbole.c ca82_berichte.c ca82_makros.c \
           ca82_zustand.c ca82_hilfen.c ca82_fehler.c ca82_quelle.c ca82_listing.c ca82_pass0.c ca82_pass1.c \
           ca82_pass2.c ca82_ausdruck.c ca82_codierung.c ca82_pass3.c ca82_fluss.c ca82_testdatei.c ca82_main.c)
HDR      = $(wildcard Sourcecode/*.h)

.PHONY: all test pruefen fuzz clean
all: _Linux/c82ass

_Linux/c82ass: $(SRC) $(HDR)
	mkdir -p _Linux
	$(CC) $(CFLAGS) --static -o $@ $(SRC)

test: _Linux/c82ass
	Regressionstest/regressionstest.sh

pruefen:
	Regressionstest/pruefe_alles.sh

FUZZ_N    ?= 500
FUZZ_SEED ?= 1
# Rueckgabecode 0 = keine Abstuerze/Sanitizer-Meldungen, 1 = Fund (Dateien in /tmp/c82fuzzwork/fund_*.asm)
fuzz:
	$(CC) -O1 -g -fsanitize=address,undefined -fno-sanitize-recover=undefined -fno-omit-frame-pointer -o /tmp/c82ass_asan $(SRC)
	C82ASS_ASAN=/tmp/c82ass_asan python3 Regressionstest/fuzz.py $(FUZZ_N) $(FUZZ_SEED)

clean:
	rm -f _Linux/c82ass
