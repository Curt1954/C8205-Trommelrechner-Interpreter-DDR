# Makefile des Zusatztrommelmoduls zt_modul (Projekt C8205Z).  Linux: make / make test       (gcc, pthread)
# Windows-Zweig wie plattform.h: NICHT uebersetzt, NICHT getestet.
# Der Simulator (c-module/) wird nicht veraendert; seine Quellen (trommel.c, plattform.h ...) werden von dort benutzt.
# SIM = Ordner c-module des Simulators (Vorgabe: ../../c-module, d. h. C8205Z liegt im Projektstamm des Simulators).
SIM     ?= ../../c-module
CC      ?= gcc
AR      ?= ar
CFLAGS  ?= -O2 -Wall -Wextra -Wshadow -pthread -std=gnu11 -fPIC -I$(SIM)
HTSRC    = $(SIM)/trommel.c $(SIM)/bahnsperre.c $(SIM)/unterbrechung.c

all: libztmodul.a testframe_zt

zt_modul.o: zt_modul.c zt_modul.h
	$(CC) $(CFLAGS) -c zt_modul.c -o $@

libztmodul.a: zt_modul.o
	$(AR) rcs $@ zt_modul.o

# Der Testrahmen bindet die Haupttrommel (trommel.c) ein: Test 6 koppelt die ZT an die echte HT.
testframe_zt: testframe_zt.c zt_modul.o $(HTSRC)
	$(CC) $(CFLAGS) -o $@ testframe_zt.c zt_modul.o $(HTSRC)

# Laeuft in einem Wegwerf-Ordner (Dateien zt_test_*.txt und ht_test.txt), nie in Trommel/.
test: testframe_zt
	-rm -rf rahmentest_zt
	mkdir rahmentest_zt
	cd rahmentest_zt && ../testframe_zt
	-rm -rf rahmentest_zt

clean:
	-rm -f *.o libztmodul.a testframe_zt
	-rm -rf rahmentest_zt
.PHONY: all test clean
