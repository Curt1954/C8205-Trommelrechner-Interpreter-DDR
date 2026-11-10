#!/usr/bin/env python3
"""hschl_variante.py -- gemeinsame Quelle der Tests hschl, hschl_voll, hschl_rand, hschl_ziffer, hschl_leer, hschl_zulang (Projektmakro HSCHL, Projekt ZT-Loader).

Seit 01.11.2026 (Auftrag Inhaber) legt HSCHL den Streifen als TYP 10 ab (Eingaben zu je 2 Worten, Aufgabenstellung 5a und 7a), gelesen mit dem Makro TYP10EINGABE.
Die .asm der Tests sind bis auf Streifen, Dokumentationszeile und Sollwerte gleich; sie werden von gen/<name>_gen.py (asm_und_test.sh fuehrt sie selbst aus)
mit erzeuge() geschrieben und nie von Hand geaendert. Die Teststreifen erzeugt streifen.py (gleicher Ordner) aus den Texten unten.

Die Sollwerte kommen aus einem Python-Modell der Regeln in C8205Z/zt/ZT-Repository_Aufgabenstellung.md 7a (unabhaengig vom Makro und von der Kodetabelle, aus der streifen.py die Lochbilder liest).
Schreibweise der Streifentexte: 0 bis 9 und + (Kennzeichen oder Ziffern), . und : (Ende der Eingabe), Leertaste ' ', WRZL 'W', Buchstabe 'a' (wird uebergangen),
Um. GB 'G', Um. KB 'K', Streifenende '/'.
"""
import os

HIER = os.path.dirname(os.path.abspath(__file__))

# Eingabeadresse (Kodetabelle R 300) je Zeichen; hier unabhaengig von der Kodetabelle noch einmal angegeben (Aufgabenstellung 5 und 6c)
EA = {'0': 0o00, '1': 0o01, '2': 0o02, '3': 0o03, '4': 0o04, '5': 0o05, '6': 0o06, '7': 0o07, '8': 0o10, '9': 0o11,
      ':': 0o15, '+': 0o20, '.': 0o33, ' ': 0o12, 'W': 0o32, 'a': 0o21, 'G': 0o37, 'K': 0o57, '/': 0o61}

MASKE33 = (1 << 33) - 1


def modell(text):
    """Liest den Streifentext nach den Regeln von 7a; liefert die Worte (Wort 1, Wort 2, Wort 1, ...) der fertigen Eingaben bis zum Zeichen /."""
    worte = []
    kz = []
    w1 = 0
    for c in text:
        if c == '/':
            break                                     # Streifenende: die begonnene Eingabe wird verworfen
        if c in '.:':
            if len(kz) == 0:
                w2 = 0
            elif len(kz) == 1:
                w2 = EA[kz[0]] << 6                   # ein einzelnes Kennzeichen steht in Kennzeichen 1 (z21 bis z26)
            else:
                w2 = (EA[kz[0]] << 6) | EA[kz[1]]
            worte += [w1, w2]
            kz, w1 = [], 0
        elif c in '0123456789+':
            if len(kz) < 2:
                kz.append(c)                          # die ersten zwei Zeichen sind Kennzeichen
            elif c in '01234567':
                w1 = ((w1 << 3) | int(c)) & MASKE33   # Oktalziffer, die letzten 11 bleiben
        # alles andere (Leertaste, WRZL, Buchstaben, Um. GB, Um. KB): wirkungslos uebergangen
    return worte


def o11(x):
    return '%011o' % x


# Die Eingaben des Hauptfalls (17 Eingaben = 34 Worte = 16 Eingaben einer vollen Spur + 1)
E_HAUPT = [
    '+0771234567012:',          # 1: Beispiel 1 aus 7a (12 Ziffern, die letzten 11 bleiben)
    '+0123:',                   # 2: Beispiel 2 aus 7a (Vornullen)
    '2.',                       # 3: Beispiel 3 aus 7a (Punkt vor dem 2. Kennzeichen)
    '2 1a8W9+5:',               # 4: Leertaste, Buchstabe, 8, WRZL, 9 und + im Ziffernteil werden uebergangen: Kennzeichen 2 1, Ziffer 5
    'G33.',                     # 5: Um. GB wird uebergangen (nur KBGB), Kennzeichen 3 3, keine Ziffern
    'K7.',                      # 6: Um. KB, ein einzelnes Kennzeichen 7
    '89.',                      # 7: 8 und 9 als Kennzeichen (gueltig)
    '00' + '7' * 11 + ':',      # 8: 11 Siebenen: z0 gesetzt
] + ['34%o7%o.' % (k, k) for k in range(9, 18)]   # 9 bis 17: Kennzeichen 3 4, Ziffern 7 und k (zweimal)


def haupt_text():
    return ''.join(E_HAUPT) + 'W/'      # nach der letzten Eingabe noch ein WRZL, dann das Streifenende


E_ZIFFER = ['89.', '0898 97.', '+8.']     # 8 und 9 als Kennzeichen (gueltig) und im Ziffernteil (uebergangen); kein Fehler mehr
E_ZIL = ['+0771234567012:W', '2 1 123.W', '2.W']   # Streifen des Prototyps zil (ZTD-Platzhalter): 3 Eingaben, 6 Sektoren


def streifentexte():
    """{Dateiname: Streifentext} fuer Test-virtuelleGeraete/Leser1/ (erzeugt streifen.py)."""
    return {
        'hschl.txt': haupt_text(),
        'hschl_voll.txt': ''.join(E_HAUPT[:16]) + '/',            # genau 16 Eingaben = 32 Worte = eine volle Spur, dann /
        'hschl_rand.txt': ''.join(E_HAUPT[:16]) + '215/',         # 16 Eingaben, dann eine 17. Eingabe, die vor ihrem Ende von / abgebrochen wird (verworfen)
        'hschl_ziffer.txt': ''.join(E_ZIFFER) + '/',
        'hschl_leer.txt': '/',                                    # keine Eingabe
        'hschl_zulang.txt': ''.join('12%o.' % k for k in range(1, 2049)) + '/',   # 2048 Eingaben = 4096 Sektoren
        'hschl_zil.txt': ''.join(E_ZIL) + '/',
    }


def zt_spur(o, spur, ws, erste, text):
    """ZT-Pruefzeilen fuer die Worte ws (Index erste..) auf Spur 'spur' der Trommel o (Zelle = spur * 040 + Index in der Spur)."""
    z = []
    for i, w in enumerate(ws):
        z.append('%d-%04o: %s   # %s %d' % (o, spur * 32 + i, o11(w), text, erste + i))
    return z


KOPF = """; {name}.asm - ERZEUGT von gen/{name}_gen.py (Quelle gen/hschl_variante.py; nicht von Hand aendern). Test des Makros HSCHL (ZIL Element 15, Ablage als Typ 10). Variante: {var}
; Empfehlung (001): kleinste Startzelle 0040 (0002 bis 0037 gehoeren dem KEP), groesste Startzelle 4000, Ausrichtung auf eine 040-Grenze (Tabellen und Spurpuffer legen equ100/equ40 selbst).
; Ablauf: K1 (Lochbandleser 1) anwaehlen, KBGB := 1, R1 = Spurpuffer Programmcode (spufpc), R2 = Trommel 0, R3 = Spur 127 (0177), UP hschl aufrufen, danach die Abweichung von R1 und R3 festhalten (dif1, dif3), Halt.
;   Der Fehlerausgang des Makros (Parameter fe_lang) traegt die Fehlerart 2 (mehr als 4095 Sektoren) in die Zelle fehlart ein und haelt. Das UP eingabe (Makro TYP10EINGABE) liest die Eingaben, sein Endeausgang ist die Marke hs_ende in HSCHL.
;   Der Streifen liegt in Leser 1 (Datei {streifen}). Die ZT beginnen leer (#ZTROMMEL=LEER). KBGB steht vor dem Aufruf auf 1 und muss danach 1 sein (der Streifen kann Um. GB und Um. KB enthalten).
;#MACRODATEI1=../../macro_zt_loader.macro
;#ZTROMMEL=LEER
;#DOK-0001 {name}: Projektmakro HSCHL: {dok}
;#SPEI-0001 0001-0004
;#PROT STUFE=2
; --leser1 Test-virtuelleGeraete/Leser1/{streifen}

r1:             abs     07773                ; Register 1: Adresse des Spurpuffers Programmcode (Adressfeld)
r2:             abs     07776                ; Register 2: Trommelnummer, nach dem Lauf Sektoranzahl
r3:             abs     07774                ; Register 3: Spurnummer der ersten Zielspur
kbgb:           abs     07775                ; KBGB, globale KB/GB-Zelle

                start                        ; Zaehlung beginnt bei 0000
                000     haupt                ; Zelle 0000: Sprung zum Hauptprogramm
dif1:           dw      0                    ; Zelle 0001: R1 - apc nach dem Aufruf (0, wenn R1 unveraendert)
dif3:           dw      0                    ; Zelle 0002: R3 - 0177 nach dem Aufruf (0, wenn R3 unveraendert)
fehlart:        dw      0                    ; Zelle 0003: Fehlerart (0 kein Fehler, 2 zu lang), vom Fehlerausgang gesetzt
apc:            da      spufpc               ; Zelle 0004: Adresse des Spurpuffers Programmcode (Adressfeld)

haupt:          ANWAHL  K1                   ; Lochbandleser 1 anwaehlen (Kanal K1)
                211     #1                   ; AC := 1
                240     kbgb                 ; KBGB := 1 (GB); der Lauf darf es nicht aendern
                211     apc                  ; AC := Adresse des Spurpuffers
                240     r1                   ; R1 := Spurpuffer Programmcode
                241     r2                   ; R2 := 0 (Trommel 0), AC := 0
                211     #0177                ; AC := 127
                240     r3                   ; R3 := Spur 127 der Trommel 0 (die zweite Spur liegt dann auf Trommel 1, Spur 0)
                025     hschl                ; UP hschl: Streifen lesen, auf die ZT schreiben, R2 := Sektoranzahl
                211     r1                   ; AC := R1
                220     apc                  ; minus Soll: 0, wenn R1 unveraendert
                240     dif1                 ; dif1 := Abweichung von R1
                211     r3                   ; AC := R3
                220     #0177                ; minus Soll: 0, wenn R3 unveraendert
                240     dif3                 ; dif3 := Abweichung von R3
                020     0                    ; Halt (normales Ende)
fe_lang:        211     #2                   ; Fehlerausgang zu lang: AC := 2
                240     fehlart              ; fehlart := 2
                020     0                    ; Halt (Fehler zu lang)

; ---- UP hschl: Hauptschleife Ls nach ZT (Projektmakro HSCHL). R1 = Spurpuffer Programmcode, R2 = Trommel, R3 = Spur der ersten Zielspur; Fehlerausgang fe_lang, UP eingabe, Streifenende hs_ende
hschl:          HSCHL   fe_lang eingabe ende ; Unterprogramm (Makro); setzt die Marke hs_ende

; ---- UP eingabe: eine Typ-10-Eingabe lesen (Projektmakro TYP10EINGABE), Endeausgang hs_ende
eingabe:        TYP10EINGABE hs_ende         ; Unterprogramm (Makro)

; ---- Spurpuffer Programmcode (auf einer 040-Grenze, 1 Spur = 32 Zellen)
                equ40   *                    ; Spurgrenze
spufpc:         db      040                  ; Spurpuffer Programmcode: 32 Zellen
schluss:        end

"""


def umbruch(text):
    """Bricht Kommentarzeilen ueber 240 Zeichen um (der Assembler erlaubt hoechstens 255)."""
    import textwrap
    aus = []
    for z in text.split('\n'):
        if len(z) > 240 and z.startswith(';'):
            teile = textwrap.wrap(z[1:].strip(), width=200)
            aus.append('; ' + teile[0])
            aus += [';     ' + x for x in teile[1:]]
        else:
            aus.append(z)
    return '\n'.join(aus)


def erzeuge(name, var, dok, streifen, soll_text, pruefe, ordner):
    text = KOPF.format(name=name, var=var, dok=dok, streifen=streifen)
    text += soll_text.rstrip('\n') + '\n;#PRUEFE-START\n' + '\n'.join('; ' + p for p in pruefe) + '\n;#PRUEFE-ENDE\n'
    text = umbruch(text)
    with open(os.path.join(ordner, name + '.asm'), 'w', encoding='utf8', newline='\n') as f:
        f.write(text)
