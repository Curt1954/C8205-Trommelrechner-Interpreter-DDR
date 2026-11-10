# mk_dot.py - erzeugt haupt.dot, jn.dot, zi.dot und hs.dot (Flussdiagramm zil.asm, Elemente mit laufender Nummer); Aenderungen des Ablaufs hier
import itertools
NL=chr(92)+'n'
n=itertools.count(1)
import textwrap
def wrap(label,w,ind=''):
    out=[]
    for ln in label.split('\\n'):
        out+=textwrap.wrap(ln,w,subsequent_indent=ind,break_long_words=False) or ['']
    return '\\n'.join(out)
def node(name,label,kind,num):
    label=wrap(label,50,'       ')
    st={'start':'shape=oval, fillcolor="#e8e8e8"','end':'shape=oval, fillcolor="#f4cccc"',
       'box':'shape=box','up':'shape=box, style="filled,rounded", fillcolor="#dbe9f7"',
       'out':'shape=box, style="filled,rounded", fillcolor="#e2f0d9"','dec':'shape=diamond, fillcolor="#fff2cc"',
       'wait':'shape=box, style="filled,dashed", fillcolor="#f2f2f2"','ans':'shape=box, fillcolor="#e2f0d9"','out_hw':'shape=box, style="filled,rounded", fillcolor="#fce4d6"'}[kind]
    return f' {name} [{st}, label="{label}", xlabel=<<font color="#c00000" point-size="12"><b>{num}</b></font>>];\n'
def build(title,nodes,edges,legend,start):
    global n
    out='digraph G {\n graph [rankdir=TB, fontname="Helvetica", labelloc=t, fontsize=16, nodesep=0.6, ranksep=0.45, forcelabels=true,\n   label="%s"];\n'%title
    out+=' node [fontname="Helvetica", fontsize=11, style=filled, fillcolor="#ffffff", color="#333333"];\n edge [fontname="Helvetica", fontsize=10];\n'
    for t in nodes:
        lab=t[1]; par=None
        if t[2]=='up' and (NL+'Ein:') in lab:   # Parameter in gestrichelt gekoppeltes Ergaenzungskaestchen rechts
            i=lab.index(NL+'Ein:'); par=lab[i+len(NL):]; lab=lab[:i]
        out+=node(t[0],lab,t[2],t[3] if len(t)>3 else next(n))   # 4. Eintrag = feste Nummer (z. B. 11a), zaehlt nicht mit
        if par:
            out+=' %s_p [shape=box, style="filled,dashed", fillcolor="#f7fbff", fontsize=10, label="%s"];\n'%(t[0],wrap(par,44,'      '))
            out+=' %s->%s_p [style=dashed, arrowhead=none, constraint=false];\n {rank=same; %s; %s_p}\n'%(t[0],t[0],t[0],t[0])   # 4. Eintrag = feste Nummer (z. B. 11a), zaehlt nicht mit
    for e in edges: out+=' '+e+';\n'
    out+=' leg [shape=note, fillcolor="#fafafa", fontsize=9, label="%s"];\n %s->leg [style=invis];\n}\n'%(wrap(legend,60),start)
    return out
H=[('start','Start\\nZelle 0000: Sprung nach haupt','start'),
('kb','Hauptprogramm setzt die globale Zelle KBGB := 0 (KB)\\nKBGB = Zelle 7775 (Arbeitsspur 77xx), gilt für das ganze Projekt;\\nalle HP und UP benutzen sie','box','1a'),
('zs','Hauptprogramm gibt vor der ersten Ausgabe eine Zeilenschaltung aus\\nK2 anwählen (Schreibwerk), WRZL (danach K0 angewählt)','out','1b'),
('repo','UP repo  (Platzhalter, meldet „UP Repository pruefen“)\\nEin:  R1 = Adresse SPUF-00 (Spurpuffer Spur 0 von ZT 0)\\nAus: R2 = 1 (Repository vorhanden) oder 0 (keines)\\nWirkung: liest Spur 0 von ZT 0 nach SPUF-00 und prüft das Repository-Kennzeichen (Zelle 0 = 52525252525)','up'),
('d1','R2 = 0 ?','dec'),
('m1','Ausschrift\\n„Repository gefunden“','out'),
('m2','Ausschrift\\n„Zusatztrommel loeschen [J/N]“','out'),
('jn','UP jneingabe  (siehe Seite 2)\\nEin:  K0 angewählt (SW-Eingabe)\\nAus: R2 = 1 (J) oder 0 (N); nur Großbuchstabe zählt','up'),
('d2','R2 = 1 ?','dec'),
('zn','Hauptprogramm gibt nach der Antwort N eine Zeilenschaltung aus (vor „Programmende“)\\nK2 anwählen (Schreibwerk), WRZL (danach K0 angewählt)','out','7b'),
('m3','Ausschrift\\n„Programmende“','out'),
('s2','status := 2\\n(Weg Nein)','box'),
('zj','Hauptprogramm gibt nach der Antwort J eine Zeilenschaltung aus (vor „UP Zusatztrommeln initialisieren“)\\nK2 anwählen (Schreibwerk), WRZL (danach K0 angewählt)','out','7a'),
('zi','UP ztinit  (siehe Seite 3; im Prototyp noch Platzhalter, meldet „UP Zusatztrommeln initialisieren“)\\nEin:  R1 = Adresse SPUF-00 (Spurpuffer Spur 0 von ZT 0, auf Spurgrenze; wie bei repo)\\nAus: – (SPUF-00 enthält danach Spur 0 wie auf ZT 0 geschrieben; ZT 0 bleibt angewählt)\\nWirkung: löscht alle vier Trommeln (513 Ausgaben, rund 44 s, keine Meldung), legt Spur 0 von ZT 0 an: Zelle 0 = Repository-Kennzeichen 52525252525, Repository-Kopf (Zelle 16) = 1, höchste Programm-ID (Zelle 17) = 0, letzte belegte Trommel (Zelle 18) = 0, letzte belegte Spur (Zelle 19) = 48 (60 oktal; Länge des größten Programmverzeichnisses in ganzen Spuren, fester Wert)','up'),
('s3','status := 3\\n(Weg Ja)','box'),
('pv','Hauptprogramm bereitet den Spurpuffer „Namensverzeichnis“ (SPUF-PN) vor: Bereich (2 Spuren) auf Spurgrenze legen und löschen (alle Wörter 0 = leere Einträge); ebenso liegt der Puffer „Programmcode“ (1 Spur = 32 Zellen) auf einer Spurgrenze','box','11a'),
('k1','Hauptprogramm wählt K1 an (Lochbandleser 1)','box','14a'),
('a1','Ausschrift\\n„Lochband mit ZTD in Leser 1 einlegen“','out'),
('a2','UP „Programmname eintragen“  (allgemeines UP, Projektmakro; später nachnutzbar)\\nEin:  R1 = Adresse SPUF-PN (Spurgrenze),\\n       R2 = Adresse der Zelle des kat5-Namens „ztd“ (Wort 1),\\n       R3 = Adresse SPUF-00 (Spurgrenze)\\nAus: –\\nWirkung: ermittelt aus SPUF-00 (Zellen 17 bis 19) die Lage des neuen Eintrags (ID = Zähler + 1; Eintrag ab SPUF-PN + 2 · (ID − 1)) und den nächsten freien Platz (Spur nach der letzten belegten); danach Zähler (Zelle 17 in SPUF-00) := ID; trägt ein: Wort 1 = Name; Wort 2 nur die Bitfelder Typ z1–z2 = 10, ID z3–z11, Trommel z12–z13, Spur z14–z20, alle übrigen Bits von Wort 2 bleiben unverändert\\nVERMERK: Hier müsste die Prüfung auf doppelte Namen stehen (Aufgabenstellung 4.4); nicht programmiert, Speicherbedarf offen','up'),
('a3','UP „neuanlage Programm“\\nEin:  R1 = Adresse SPUF-PN (2 Spuren),\\n       R2 = Trommelnummer, R3 = Spurnummer (Zahlen, der ersten Spur)\\nAus: –\\nWirkung: schreibt SPUF-PN (Programmnamen-Puffer) auf die Zusatztrommel (Trommel/Spur aus der Übergabe; Verzeichnis: Trommel 0, Spur 1 und 2); Länge noch 0, SPUF-PN wird in Element 16 noch einmal geschrieben','up'),
('a4','UP „Hauptschleife Ls nach ZT“  (hschl, Makro HSCHL; siehe Seite 4)\\nEin:  R1 = Adresse Puffer „Programmcode“ (1 Spur),\\n       R2 = Trommelnummer, R3 = Spurnummer (Zahlen, der ersten Zielspur;\\n       ZTD: Trommel 0, Spur 33)\\nAus: R2 = Sektoranzahl = 2 · Zahl der Eingaben (R1, R3 und KBGB unverändert)\\nDer Streifen wird als Typ 10 abgelegt (Eingaben zu je 2 Worten, gelesen mit dem UP eingabe = Makro TYP10EINGABE).\\nFehler im Lochstreifen (mehr als 4095 Sektoren): das UP springt auf den Fehlerausgang fe_lang des Hauptprogramms: Ausschrift auf dem SW („lochstreifen zu lang“) und Halt; keine Fehlerrückgabe','up'),
('a5','Sektoranzahl in SPUF-PN eintragen (Wort 2 = Zelle 1 des Eintrags, nur Länge z21–z32; übrige Bits bleiben)\\nSPUF-PN (2 Spuren) noch einmal auf ZT schreiben (erstes Mal in Element 14, dort Länge 0)\\nUP neuanl: R1 = SPUF-PN, R2 = 0, R3 = 1 (ZT 0 Spur 1 und 2; ZT 0 bleibt angewählt)','box'),
('a6','SPUF-00 auf ZT 0, Spur 0 schreiben\\nAnwahl ZT 0 (5100 030), Ausgabe 601 mit Spur 0 und Adresse SPUF-00 (Zähler in Zelle 17 = 1; Zellen 18/19 nicht nachgeführt)','box'),
('a7','Ausschrift\\n„ZTD geladen mit Programm-ID 1“','out'),
('m0','Ausschrift\\n„Kein Repository gefunden“','out'),
('s1','status := 1\\n(Weg kein Repository)','box'),
('halt','Halt (ende)\\nalle Wege enden hier','end')]
HE=['start->kb->zs->repo->d1','d1->m1 [label=" nein (R2 = 1)"]','d1->m0 [label=" ja (R2 = 0)"]','m1->m2->jn->d2',
'd2->zj [label=" ja (J)"]','zj->zi','d2->zn [label=" nein (N)"]','zn->m3','m3->s2->halt','zi->s3->pv->a2->a3->a1->k1->a4->a5','a5->a6->a7->halt','m0->s1->halt']
h=build('ZIL (Initialloader der Zusatztrommeln) – Ablauf des Hauptprogramms haupt (zil.asm)\\nSeite 1 von 4; rote Nummer = laufende Nummer des Elements',H,HE,
'Legende:  Wort 2 eines Verzeichniseintrags entsteht nacheinander (jedes Element ändert nur seine Bitfelder): leer (alles 0, ztinit und Element 11a), Element 13 = Typ z1–z2, ID z3–z11, Trommel z12–z13, Spur z14–z20, Element 16 = Länge z21–z32.   Element 14 schreibt SPUF-PN auf die ZT (Länge 0), Element 16 schreibt es nach Eintragen der Länge nochmals.   SPUF-00 = Spurpuffer Spur 0 von ZT 0, SPUF-PN = 2-Spur-Puffer Namensverzeichnis (IDs 1 bis 32)   blau = Unterprogramm (025), gestrichelt rechts daneben seine Parameter (Ein/Aus/Wirkung)   grün = Ausschrift auf Schreibwerk K2, eigene Zeile (Makro MELDUNG)   gelb = Verzweigung\\nEin/Aus = Aufruf- bzw. Rückgabeparameter; Register gelten nur für die Dauer des UP-Aufrufs.   status = Zelle 0001, nur für den Test.   KBGB = globale Zelle 7775 (0 = KB, 1 = GB): Jedes Element, das KB/GB ändert, führt sie nach (ein UP muss dafür dtm nicht verwenden).   Alle Elemente sind als Prototyp in zil.asm umgesetzt (die blauen UP außer jneingabe als Platzhalter, die nur ihren Namen melden). Elemente 15a/15b und die Zelle lsfehl sind gestrichen (Fehler im Lochstreifen meldet hschl selbst); im Prototyp zil.asm noch nicht nachgeführt.','halt')
open('haupt.dot','w').write(h)
J=[('a','UP jneingabe (Aufruf 025)\\nEin:  K0 angewählt\\nAus: R2 = 1 (J) oder 0 (N)','start'),
('rd','lesen:  Befehl 011 tab\\nZeichen von K0 lesen, AC := Tabellenwert','box'),
('tz','Art des Zeichens\\n(Tabelle, 64 Zellen)','dec'),
('st','Steuerzeichen:\\nUm. GB: KBGB := 1   Um. KB: KBGB := 0\\nSprungzeichen (Leertaste, :, WRZL, Punkt, …): ohne Wirkung','box'),
('w','zeich := Tabellenwert\\n(1 = j, 2 = n, sonst 0)','box'),
('k0','KBGB = 0 ?\\n(Kleinschreibung)','dec'),
('wl','Zeichen zählt nicht:\\nzurück zu lesen','wait'),
('d1','zeich = 1 ?','dec'),('d2','zeich = 2 ?','dec'),
('aj','antj:  R2 := 1  (Ja)','ans'),('an','antn:  R2 := 0  (Nein)','ans'),
('ret','Rückkehr zum Aufrufer','end')]
JE=['a->rd->tz','tz->st [label=" Steuerzeichen"]','tz->w [label=" alle übrigen"]','w->k0','k0->wl [label=" ja (KB)"]','wl->rd [constraint=false]','st->rd [constraint=false]',
'k0->d1 [label=" nein (GB)"]','d1->aj [label=" ja"]','d1->d2 [label=" nein"]','d2->an [label=" ja"]','d2->wl [label=" nein: anderes\\nZeichen"]','aj->ret','an->ret']
open('jn.dot','w').write(build('UP jneingabe – Antwort J oder N lesen (zil.asm)\\nSeite 2 von 4; Nummern setzen die von Seite 1 fort',J,JE,
'Nur ein großgeschriebenes J oder N zählt (Um. GB, dann j bzw. n). Kleines j/n und alle anderen Zeichen werden übergangen,\\nweil auf Ja eine Löschung folgt. KBGB = globale Zelle 7775 (0 = KB, 1 = GB), vom Hauptprogramm nach dem Start auf KB gesetzt.','a'))

Z=[('a','UP ztinit (Aufruf 025)\\nEin:  R1 = Adresse SPUF-00 (auf Spurgrenze, bleibt unverändert)\\nAus: – ; ZT 0 am Ende angewählt','start'),
('z1','Nullpuffer: Befehl 441 <SPUF-00>, alle 32 Zellen von SPUF-00 := 0\\nlaufende Spur g := 0  (g = 128 · d + s, 0 bis 511)','box'),
('z3','Trommel anwählen (bei jeder Spur): d = g div 128 (Bit 7 und 8 von g)\\nAnwahlbefehl := 05100030 + d · 0100000  (5k00 030, k = d + 1), ausführen','box'),
('z4','Ausgabe:  Wort := s · 2^26 + R1 + 601  (s = g mod 128; s um 26 Stellen\\nnach links geschoben, kein Überlauf), ausführen  (zzz0 bbbb 601)\\nSPUF-00 (lauter Nullen) → Spur s der Trommel d, rund 85 ms\\n(erste Ausgabe: Spur 0 von ZT 0)','out_hw'),
('z5','g := g + 1','box'),
('d1','g = 512 ?','dec'),
('z7','SPUF-00 aufbauen (Spur 0 von ZT 0), die übrigen Zellen bleiben 0:\\nZelle 0 := 52525252525 (Repository-Kennzeichen)\\nZelle 16 := 1 (Repository-Kopf)   Zelle 17 := 0 (Zähler)\\nZelle 18 := 0 (letzte belegte Trommel)   Zelle 19 := 40 oktal (letzte belegte Spur, 32 dezimal)','box'),
('z8','Anwahl ZT 0 (030 05100 ausführen)\\nAusgabebefehl := 601 + R1 · 01000  (zzz0 = 0000)','box'),
('z9','Ausgabe:  Ausgabebefehl ausführen\\nSPUF-00 → Spur 0 von ZT 0 (die 513. Ausgabe)','out_hw'),
('ret','Rückkehr zum Aufrufer\\n(ZT 0 angewählt, KBGB und Kanäle unverändert)','end')]
ZE=['a->z1->z3->z4->z5->d1','d1->z3 [label=" nein: nächste Spur"]','d1->z7 [label=" ja (alle 512 Spuren)"]','z7->z8->z9->ret']
open('zi.dot','w').write(build('UP ztinit – alle Zusatztrommeln löschen und Spur 0 von ZT 0 anlegen (Spezifikation, ZT-Repository_Aufgabenstellung.md 6a)\\nSeite 3 von 4; Nummern setzen die von Seite 2 fort',Z,ZE,
'g = laufende Spur (Arbeitszelle des UP, Aufgabenstellung 6a); eine Schleife über alle 512 Spuren, kein getrennter Trommel- und Spurzähler. Das Löschen beginnt mit Spur 0 von ZT 0\\n(ein Abbruch hinterlässt kein halb gelöschtes Repository); Spur 0 wird zuletzt neu geschrieben. Das Spurfeld zzz0 = s · 040 entsteht durch Schieben, nicht durch Addieren\\nvon 0400000000 (ab Spur 64 wäre das Wort negativ: Überlauf). Befehlswörter: Anwahl 5k00 030 (k = d + 1) = 05100030 + d · 0100000; Ausgabe zzz0 bbbb 601.\\n513 Ausgaben ≈ 43,9 s; im TEST-Interpreter sind alle Zeiten 0.','a'))

S=[('a','UP hschl (Makro HSCHL, Aufruf 025)\\nEin:  R1 = Adresse Puffer Programmcode (1 Spur, auf Spurgrenze), R2 = Trommel d, R3 = Spur s der ersten Zielspur (Zahlen); K1 angewählt\\nAus: R2 = Sektoranzahl (R1, R3 und KBGB unverändert); Fehler: kein Rücksprung','start'),
('i1','Anfang:  Adresse des Puffers (R1) und KBGB merken\\np := 128 · d + s  (laufende Zielspur)\\nSektorzähler := 0     Ende-Merker := 0  (Streifen läuft noch)','box'),
('i2','neue Spur im Puffer:  Zeiger := Adresse des Puffers\\nBefehl 441 <Puffer>:  alle 32 Zellen des Puffers := 0  (Rest der letzten Spur bleibt 0)','box'),
('rd','Eingabe lesen:  R1 := Zeiger\\nUP eingabe (Makro TYP10EINGABE, Aufruf 025): liest eine Eingabe bis einschließlich . oder :  vom Leser 1 (K1)\\nund legt Wort 1 (Daten) und Wort 2 (Kennzeichen) in die 2 Zellen ab Zeiger;  Um. KB / Um. GB führen KBGB nach','box'),
('ds','„/“ (Streifenende) gelesen ?\\n(TYP10EINGABE springt dann nach hs_ende;\\neine begonnene Eingabe wird verworfen)','dec'),
('sp','Eingabe fertig:  Sektorzähler := Sektorzähler + 2','box'),
('dl','Sektorzähler ≥ 4096 ?\\n(mehr als 4095 Sektoren = 2048 Eingaben)','dec'),
('f2','Fehlerausgang fe_lang des Hauptprogramms\\nAusschrift „lochstreifen zu lang“, Halt','end'),
('zg','Zeiger := Zeiger + 2 Zellen','box'),
('dp','Zeiger = Puffer + 32 Zellen ?\\n(Puffer voll: 16 Eingaben)','dec'),
('en','Streifenende:  Ende-Merker := -1','box'),
('de','Zeiger = Puffer ?\\n(keine Eingabe mehr im Puffer)','dec'),
('wr','Spur schreiben:  Anwahl 5k00 030  (k = d + 1,  d = Bit 7 und 8 von p)\\nAusgabe:  Wort := s · 2^26 + Puffer + 601  (s = Bit 0 bis 6 von p), ausführen\\nPuffer → Spur s der Trommel d;   p := p + 1  (Übertrag Spur 127 → Spur 0 der nächsten Trommel)','out_hw'),
('dm','Ende-Merker < 0 ?','dec'),
('ret','R2 := Sektorzähler;  R1 := Adresse des Puffers;  KBGB zurückgestellt\\nRückkehr zum Aufrufer  (K1 und die letzte Trommel bleiben angewählt)','end')]
SE=['a->i1->i2->rd->ds','ds->en [label=\" ja\"]','ds->sp [label=\" nein\"]','sp->dl','dl->f2 [label=\" ja\"]','dl->zg [label=\" nein\"]','zg->dp',
'dp->wr [label=\" ja\"]','dp->rd [label=\" nein: nächste Eingabe\", constraint=false]','en->de','de->ret [label=\" ja: nichts zu schreiben\"]','de->wr [label=\" nein: letzte Spur\"]',
'wr->dm','dm->ret [label=\" ja\"]','dm->i2 [label=\" nein: nächste Spur\", constraint=false]']
open('hs.dot','w').write(build('UP hschl – Lochstreifen aus Leser 1 als Typ 10 lesen und spurweise auf die ZT schreiben (Makro HSCHL, ZT-Repository_Aufgabenstellung.md 6c und 7a)\\nSeite 4 von 4; Nummern setzen die von Seite 3 fort',S,SE,
'Eine Eingabe = 2 Zellen (Typ 10, Aufgabenstellung 5a und 7a): Wort 1 = Datenwert, Wort 2 = Kennzeichen; ein Puffer (1 Spur = 32 Zellen) fasst 16 Eingaben. „/“ beendet den Streifen. p = 128 · d + s ist der laufende Spurzähler (Arbeitszelle).\\nAnwahl 5k00 030 = 05100030 + d · 0100000 (wie NEUANL), je Spur; der Puffer wird je Spur mit 441 gelöscht. Der Fehlerausgang ist ein Parameter des Makros (Sprungziel im Hauptprogramm); 8 und 9 sind kein Fehler mehr.\\nR1 wird je Eingabe auf die Pufferstelle gesetzt und am Ende zurückgestellt, KBGB ebenfalls (der Streifen kann Um. KB / Um. GB enthalten).','a'))
