#!/usr/bin/env python3
# Aufruf siehe Regressionstest/LIESMICH.md (Abschnitt Zufallstest)
# Mutations-Fuzzer: veraendert vorhandene .asm zufaellig und sucht Abstuerze / ASan / UBSan-Meldungen.
import os, sys, random, subprocess, shutil, glob, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.environ.get("C82ASS_ASAN", "/tmp/c82ass_asan")
WORK = "/tmp/c82fuzzwork"
N = int(sys.argv[1]) if len(sys.argv) > 1 else 500
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
random.seed(SEED)

quellen = [f for f in glob.glob(ROOT + "/**/*.asm", recursive=True)
           if "/Regressionstest/" not in f and "/Sourcecode/" not in f and "/Dokumentation/" not in f]
quellen = [f for f in quellen if os.path.getsize(f) < 20000]
negativ = glob.glob(ROOT + "/Regressionstest/negativ/*.asm")
quellen += negativ

TOKEN = ["ubxx", "100", "0", "-1", "99999", "#5", "dw", "dt", "dtm", "dto", "da", "equ", "start", "ende", "end",
         "MACRO", "MEND", "WDHL", "TEST", "KB", "GB", "$PR1", "$", "#", ";", ":", ",", "'", '"', "(", ")", "a-b", "5/0",
         "*", "+", "-", "/", "%", "<<", ">>", "&", "|", "^", "~", "\x00", "\xff", "\t", "\r", "ö", "9999999999999",
         "-9999999999999", "0x", "0b", "1e9", "label:", "L1", "L1:", "org", "pragma", "#leitadresse", "10", "7777", "8000"]

def mutiere(daten: bytes) -> bytes:
    zeilen = daten.split(b"\n")
    for _ in range(random.randint(1, 6)):
        art = random.randint(0, 11)
        if not zeilen:
            zeilen = [b""]
        i = random.randrange(len(zeilen))
        if art == 0:      # Zeile loeschen
            del zeilen[i]
        elif art == 1:    # Zeile duplizieren (viele Male)
            zeilen[i:i] = [zeilen[i]] * random.choice([1, 2, 10, 100, 3000])
        elif art == 2:    # Byte kippen
            z = bytearray(zeilen[i])
            if z:
                z[random.randrange(len(z))] = random.randrange(256)
            zeilen[i] = bytes(z)
        elif art == 3:    # Token einfuegen
            t = random.choice(TOKEN).encode("latin-1", "replace")
            z = zeilen[i]
            p = random.randint(0, len(z))
            zeilen[i] = z[:p] + b" " + t + b" " + z[p:]
        elif art == 4:    # Zeile abschneiden
            z = zeilen[i]
            zeilen[i] = z[:random.randint(0, len(z))]
        elif art == 5:    # Zeilen tauschen
            j = random.randrange(len(zeilen))
            zeilen[i], zeilen[j] = zeilen[j], zeilen[i]
        elif art == 6:    # sehr lange Zeile
            zeilen[i] = zeilen[i] + b" " + b"A" * random.choice([100, 300, 1000, 5000, 70000])
        elif art == 7:    # Token ersetzen
            w = zeilen[i].split(b" ")
            if w:
                w[random.randrange(len(w))] = random.choice(TOKEN).encode("latin-1", "replace")
            zeilen[i] = b" ".join(w)
        elif art == 8:    # Datei kuerzen
            zeilen = zeilen[:random.randint(0, len(zeilen))]
        elif art == 9:    # BOM / CRLF
            zeilen[i] = b"\xef\xbb\xbf" + zeilen[i] if random.random() < 0.5 else zeilen[i] + b"\r"
        elif art == 10:   # Zeile in anderes Stueck der Datei kopieren
            j = random.randrange(len(zeilen))
            zeilen.insert(j, zeilen[i])
        elif art == 11:   # langes Symbol
            zeilen[i] = b"S" * random.choice([30, 64, 200, 1000]) + b": " + zeilen[i]
    return b"\n".join(zeilen)

shutil.rmtree(WORK, ignore_errors=True)
os.makedirs(WORK + "/w", exist_ok=True)
shutil.copy(ROOT + "/Sourcecode/c82ass.makros", WORK + "/c82ass.makros")
os.makedirs(WORK + "/Sourcecode", exist_ok=True)
shutil.copy(ROOT + "/Sourcecode/c82ass.makros", WORK + "/Sourcecode/c82ass.makros")

gefunden = {}
for n in range(N):
    quelle = random.choice(quellen)
    daten = mutiere(open(quelle, "rb").read())
    name = "f.asm"
    open(f"{WORK}/w/{name}", "wb").write(daten)
    for e in ("obj", "mqo", "sym", "dmp", "test", "log"):
        try: os.remove(f"{WORK}/w/f.{e}")
        except FileNotFoundError: pass
    try:
        p = subprocess.run([BIN, "--no-color", "-p", "w", "-s", name], cwd=WORK, capture_output=True, timeout=20,
                           env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0:abort_on_error=0", "UBSAN_OPTIONS": "print_stacktrace=1"})
        rc = p.returncode
        err = p.stderr.decode("latin-1", "replace")
        out = p.stdout.decode("latin-1", "replace")
    except subprocess.TimeoutExpired:
        rc, err, out = "TIMEOUT", "", ""
    problem = None
    if rc == "TIMEOUT":
        problem = "TIMEOUT"
    elif rc not in (0, 16):
        problem = f"rc={rc}"
    if "AddressSanitizer" in err or "runtime error" in err:
        problem = (problem or "") + " SAN"
    if problem:
        # Signatur: erste Stack-Zeile mit ca82
        sig = problem
        for zeile in err.splitlines():
            if "runtime error" in zeile or "ERROR: AddressSanitizer" in zeile:
                sig += " " + zeile.strip()[:140]
                break
        for zeile in err.splitlines():
            if " in " in zeile and "ca82" in zeile:
                sig += " | " + zeile.strip().split(" in ", 1)[1][:120]
                break
        h = hashlib.md5(sig.encode()).hexdigest()[:8]
        if h not in gefunden:
            gefunden[h] = sig
            open(f"{WORK}/fund_{h}.asm", "wb").write(daten)
            open(f"{WORK}/fund_{h}.txt", "w").write(sig + "\n\n" + err[:4000])
            print(f"[{n}] NEU {h}: {sig}", flush=True)
print(f"fertig: {N} Laeufe, {len(gefunden)} verschiedene Probleme")
sys.exit(1 if gefunden else 0)
