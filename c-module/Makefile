# Linux:   make / make test        (gcc, pthread)
# Windows: mingw32-make (MinGW-w64)  -- NICHT getestet; fuer MSVC siehe build_msvc.bat
ifeq ($(OS),Windows_NT)
  EXE     = .exe
  LIB     = trommel.dll
  CFLAGS ?= -O2 -Wall -Wextra -std=gnu11 -DC8205_BUILD_DLL
  LDLIBS  = -lwinmm
  SHFLAGS = -shared
  RM      = del /Q
  RMDIR   = rmdir /S /Q
else
  EXE     =
  LIB     = libtrommel.so
  CFLAGS ?= -O2 -Wall -Wextra -pthread -std=gnu11 -fPIC -DC8205_BUILD_DLL
  LDLIBS  =
  SHFLAGS = -shared -pthread
  RM      = rm -f
  RMDIR   = rm -rf
endif
CC ?= gcc
AR ?= ar
OBJ = trommel.o bahnsperre.o unterbrechung.o
TEST = testframe_koinzidenz$(EXE)
STATIC = libtrommel.a
TEST_STATIC = testframe_koinzidenz_static$(EXE)

all: $(LIB) $(STATIC) $(TEST)

# Statische Bibliothek: wird beim Bauen eingebunden (nicht zur Laufzeit geladen). Fuer Python dient sie als Baustein des
# Erweiterungsmoduls c8205_trommel (python/setup.py bindet dieselben Quellen fest ein).
$(STATIC): $(OBJ)
	$(AR) rcs $@ $(OBJ)

$(TEST_STATIC): testframe_koinzidenz.c $(STATIC)
	$(CC) $(CFLAGS) -o $@ testframe_koinzidenz.c $(STATIC) $(LDLIBS)

test-static: $(TEST_STATIC)
	./$(TEST_STATIC)

# Tonmischer (tonmisch.c): Testrahmen ohne Python und ohne Audiogeraet, statisch gelinkt (Linux)
libtonmisch.a: tonmisch.c tonmisch.h
	$(CC) $(CFLAGS) -c tonmisch.c -o tonmisch.o
	$(AR) rcs $@ tonmisch.o
testframe_tonmisch$(EXE): testframe_tonmisch.c libtonmisch.a
	$(CC) $(CFLAGS) -static -o $@ testframe_tonmisch.c libtonmisch.a $(LDLIBS)
test-ton: testframe_tonmisch$(EXE)
	./testframe_tonmisch$(EXE)

# Python-Erweiterungsmodul (braucht Python-Entwicklungsdateien und setuptools)
pyext:
	cd python && python3 setup.py -q build_ext --inplace
pytest: pyext
	cd python && python3 -m unittest -v test_c8205_trommel

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

$(LIB): $(OBJ)
	$(CC) $(SHFLAGS) -o $@ $(OBJ) $(LDLIBS)

$(TEST): testframe_koinzidenz.c $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDLIBS)

test: $(TEST)
	./$(TEST)

# Die beiden uebrigen Rahmenprozesse (Wegwerf-Rahmen, schreiben 77777777777 an Adresse 1000 der Trommeldatei im AKTUELLEN Ordner).
# Sie laufen deshalb in einem Arbeitsordner rahmentest_tmp mit frisch erzeugter, leerer trommel.txt, nie auf einer echten Trommeldatei.
# Linux; Windows-Zweig nicht getestet.
RAHMEN = testframe$(EXE) testframe_trommel$(EXE)

testframe$(EXE): testframe.c $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDLIBS)

testframe_trommel$(EXE): testframe_trommel.c $(OBJ)
	$(CC) $(CFLAGS) -o $@ $^ $(LDLIBS)

test-rahmen: $(RAHMEN)
	-$(RMDIR) rahmentest_tmp
	mkdir rahmentest_tmp
	python3 -c "import sys; sys.stdout.write(''.join('%04o: %011o\\n' % (a, 0) for a in range(4096)))" > rahmentest_tmp/trommel.txt
	cd rahmentest_tmp && ../testframe$(EXE) && grep -q '^1000: 77777777777' trommel.txt
	cd rahmentest_tmp && ../testframe_trommel$(EXE) && grep -q '^1000: 77777777777' trommel.txt
	-$(RMDIR) rahmentest_tmp
	@echo "RAHMENPROZESSE BESTANDEN (testframe, testframe_trommel)"

# alle drei C-Testrahmen
test-alle: test test-rahmen test-ton

clean:
	$(RM) *.o libtonmisch.a testframe_tonmisch$(EXE) $(LIB) $(STATIC) $(TEST) $(TEST_STATIC) $(RAHMEN) trommel_test.txt
	-$(RMDIR) rahmentest_tmp
.PHONY: all test test-static test-rahmen test-ton test-alle pyext pytest clean
