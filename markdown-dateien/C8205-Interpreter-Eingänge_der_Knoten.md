# ** Knotendefinition **
#
# Zeilenformat:
# Knotennummer; Eingänge...; Typ; Text; Ausgänge
#
# Ausgänge: bei Anweisungen und Phasenzuordnungen  Knoten(Eingang)
#           bei Tests  Knoten(Eingang falsch) | Knoten(Eingang wahr)
#
# Lesart z.b. für: 5; 1 2; Test; Koinzidenz; 6(1 falsch) | 8(2 wahr)
#     Knoten 5 hat die Eingänge 1 und 2;
#              ist ein Test;
#              Testbedingung ist "Koinzidenz" erreicht ?
#              hat den Ausgang zu Knoten 6 auf dessen Eingang 1 im FALSE-Zweig
#              hat den Ausgang zu Knoten 8 auf dessen Eingang 2 im WAHR-Zweig
#
# Lesart z.b. für: 12; 1; Test; Sprung bedingt; 15(1 falsch) | 13(1 wahr)
#     Knoten 12 hat den Eingang 1;
#              ist ein Test;
#              Testbedingung ist "ist BAZ ein bedingter Sprung" ?
#              hat den Ausgang zu Knoten 15 auf dessen Eingang 1 im FALSE-Zweig
#              hat den Ausgang zu Knoten 13 auf dessen Eingang 1 im WAHR-Zweig
#
# Typen (Knotentypen): Es gibt die vier Typen Konnektor, Phasenzuordnung, Anweisung und Test.
#
# Konnektoren:
#     Konnektoren verbinden sich AUCH, wenn Ein- und/oder Ausgang fehlt.
#     Die Verbindung entsteht allein über die gleiche Konnektornummer;
#     der Text "verbindet mit ..." ist nur ein Kommentar.
#     Es können Mehrfachverbindungen entstehen, ohne daß die Zahl der Ein- und
#     Ausgänge davon berührt wird. Sie wächst implizit mit.
# Ausnahme:
#     Konnektor B ist extern und hat in dieser Tabelle kein Gegenstück.
#     Er kennzeichnet den Eintritt in den Ablauf von außerhalb her.
#
# Sonstiges:
#     Mehrere gleichzeitige Anweisungen in einem Knoten-Text werden mit && getrennt.
#     Klarstellung zu "gleichzeitig": Beide durch && verbundenen Anweisungen werden mit den
#     Registerwerten ausgewertet, die unmittelbar VOR dem Knoten galten - nicht nacheinander mit
#     dem durch die erste Teilanweisung ggf. bereits neu gesetzten Wert. Beispiel ANWEISUNG-001
#     "<AR>:=<BZ> && <BZ>:=<AR>+1": das neue <BZ> ergibt sich aus dem ALTEN <AR> (also <AR>+1 mit
#     dem Wert von vor dem Knoten), nicht aus dem im selben Knoten gerade erst neu gesetzten <AR>.
#     Bestätigt durch die Phase-III-Zeile in Datei "C8205-Interpreter-Überblick_und_Gesamtaufbau.md", Abschnitt 4:
#     "<AR>:=<BZ>=ADR, gleichzeitig <BZ>:=<AR>+1=BADR+1" - nur mit dieser Lesart ergibt sich dort
#     BADR+1 (alter AR-Wert + 1) statt ADR+1 (neuer AR-Wert + 1).
#     --- im Ausgangsfeld bedeutet Endknoten ohne Ausgang.
#     - im Eingangsfeld bedeutet: kein Eingang.
#     Im Textfeld kann statt des Klartextes eine Variable $ANWEISUNG-nnn stehen.
#     Sie wird in der gesonderten Tabelle "Variablentabelle T2" aufgelöst.
#
# Ergänzung 03.10.2026: Informationszustand an den Phasengrenzen und Wartezeiten W1/W2
# (Quelle: Programmieranleitung, Abschnitt 2.2 "Befehlsschleife", Seitenabbild).
# Bezeichnungen: b = Adresse des abzuarbeitenden Befehls, a = sein Adreßteil, ω = sein Operationsteil,
# ω* = Operationsteil nach einer eventuellen Umstellung in Phase II, R₋₁ = Resultat des vorigen Befehls, R = Resultat dieses Befehls.
#     Eintritt in Phase I     BZ=b                  OR=ω₋₁   AC=R₋₁   (= Ende Phase IV des vorigen Befehls)
#     Eintritt in Phase II    AR=b                  OR=ω₋₁   AC=R₋₁   (BZ in der Quelle nicht angegeben)
#     Eintritt in Phase III   BZ=a    AR=b          OR=ω     AC=R₋₁   (bei Umstellung in Phase II bereits ω*)
#     Eintritt in Phase IV    BZ=b+1  AR=a          OR=ω*    AC=R₋₁ bzw. gelöscht (L=1)
#     Ende Phase IV           BZ=b+1  AR=a          OR=ω*    AC=R
# W1 = Wartezeit zwischen Phase I und Phase II (Knoten 5/6, Sektornummer von b).
# W2 = Wartezeit zwischen Phase III und Phase IV (Knoten 26/27 und 57/64, Sektornummer von a).
# Für die interpretative Abarbeitung gilt Wartezeit=0 (ANWEISUNG-004).
# Hinweis zu Phase I: Nach der oben beschriebenen Lesart (Registerwerte VOR dem Knoten) ergibt ANWEISUNG-001 in Knoten 3 für BZ
# den alten AR-Wert + 1, nicht b+1. Das ist folgenlos, weil Phase II (Knoten 11 bzw. 37) den BZ neu setzt. Die Quelle gibt den
# BZ nach Phase I nicht an.
# Stopp: Ein programmierter Stopp erfolgt am Ende der Phase III (Knoten 45 und 79). Die Fortsetzung hängt nach der Quelle von der
# Bedienung ab und ist im Knotenautomaten nicht abgebildet (Endzustände ohne Ausgang). Einstiegsknoten der Tasten: s. Ergänzung
# 04.10.2026 (2) am Dateiende.
# Überlauf: Definition, Setzbedingungen und Löschen beim Überlaufsprung siehe ANWEISUNG-020 und -010 in "C8205-Interpreter-Beschreibung_der_Knoten.md".
# Der Überlauf wird auch nach Ausgabe-Halt und Anwahl getestet (Knoten 80/81, Ergänzung 04.10.2026 am Dateiende).
#
1;   -;              Konnektor;        B; 2(1)
# Zustand bei Eintritt in Phase I: BZ=b, OR=ω₋₁, AC=R₋₁ (Ende Phase IV des vorigen Befehls).
2;   1 2 3 4 5 6 7 8;  Phasenzuordnung;  Beginn Phase I; 3(1)
3;   1;              Anweisung;        $ANWEISUNG-001; 4(1)
4;   1;              Test;             $ANWEISUNG-002; 5(1 falsch) | 8(1 wahr)
# Knoten 5/6: Wartezeit W1 (Koinzidenz vor Phase II, Sektornummer von b).
5;   1 2;            Test;             $ANWEISUNG-003; 6(1 falsch) | 8(2 wahr)
6;   1 2;            Anweisung;        $ANWEISUNG-004; 5(2)
7;   -;              Konnektor;        1; 6(2)
# Zustand bei Eintritt in Phase II: AR=b, OR=ω₋₁, AC=R₋₁.
8;   1 2;            Phasenzuordnung;  Beginn Phase II; 9(1)
9;   1;              Anweisung;        $ANWEISUNG-005; 10(1)
10;  1;              Test;             $ANWEISUNG-006; 11(1 falsch) | 37(1 wahr)
11;  1;              Anweisung;        $ANWEISUNG-007; 12(1)
12;  1;              Test;             $ANWEISUNG-008; 15(1 falsch) | 13(1 wahr)
13;  1;              Test;             $ANWEISUNG-009; 15(2 falsch) | 14(1 wahr)
14;  1;              Anweisung;        $ANWEISUNG-010; 15(3)
# Zustand bei Eintritt in Phase III: BZ=a, AR=b, OR=ω (bei Umstellung in Phase II bereits ω*), AC=R₋₁.
15;  1 2 3 4;        Phasenzuordnung;  Beginn Phase III; 16(1)
16;  1;              Anweisung;        $ANWEISUNG-001; 17(1)
17;  1;              Test;             $ANWEISUNG-011; 19(1 falsch) | 18(1 wahr)
18;  1;              Anweisung;        $ANWEISUNG-012; 19(2)
19;  1 2;            Test;             $ANWEISUNG-013; 20(1 falsch) | 40(1 wahr)
20;  1;              Test;             $ANWEISUNG-043; 21(1 falsch) | 42(1 wahr)
21;  1;              Test;             $ANWEISUNG-015; 22(1 falsch) | 48(1 wahr)
22;  1;              Test;             $ANWEISUNG-016; 24(1 falsch) | 39(1 wahr)
23;  1;              Anweisung;        $ANWEISUNG-017; 80(1)
24;  1;              Test;             $ANWEISUNG-018; 25(1 falsch) | 55(1 wahr)
25;  1;              Test;             $ANWEISUNG-019; 26(1 falsch) | 56(1 wahr)
# Knoten 26/27: Wartezeit W2 (Koinzidenz vor Phase IV, Sektornummer von a).
26;  1 2 3;          Test;             $ANWEISUNG-003; 27(1 falsch) | 28(1 wahr)
27;  1;              Anweisung;        $ANWEISUNG-004; 26(2)
28;  1;              Test;             $ANWEISUNG-020; 31(1 falsch) | 30(1 wahr)
29;  -;              Konnektor;        2; 57(1)
# Ergänzung 03.10.2026: Knoten 30 ist der Halt wegen Überlauf (Test in Knoten 28) und wurde bei der Änderung vom 02.10.2026
# übersehen. Jetzt ANWEISUNG-046 wie in den Knoten 46, 58 und 66 (vorher ANWEISUNG-030, das Flag US setzt).
30;  1;              Anweisung;        $ANWEISUNG-046; ---
# Zustand bei Eintritt in Phase IV: BZ=b+1, AR=a, OR=ω*, AC=R₋₁ bzw. gelöscht (L=1). Gilt auch für die Knoten 61 und 67.
31;  1;              Phasenzuordnung;  Beginn Phase IV; 32(1)
32;  1 2;            Anweisung;        $ANWEISUNG-021; 33(1)
# Knoten 33: Keine Resultatbehandlung für den Leer-Befehl (B=1, A=6, Z=4 bis 7, z. B. 164), siehe ANWEISUNG-022.
33;  1;              Anweisung;        $ANWEISUNG-022; 34(1)
34;  1;              Test;             $ANWEISUNG-023; 2(3 falsch) | 35(1 wahr)
35;  1;              Test;             $ANWEISUNG-024; 73(1 falsch) | 2(4 wahr)
36;  1;              Anweisung;        $ANWEISUNG-025; 32(2)
37;  1;              Anweisung;        $ANWEISUNG-026; 38(1)
38;  1;              Anweisung;        $ANWEISUNG-027; 15(4)
39;  1;              Anweisung;        $ANWEISUNG-028; 23(1)
40;  1;              Anweisung;        $ANWEISUNG-029; 41(1)
41;  1;              Konnektor;        4; verbindet mit Konnektor 4 in Knoten 54
42;  1;              Test;             $ANWEISUNG-014; 43(1 falsch) | 45(1 wahr)
43;  1;              Test;             $ANWEISUNG-031; 44(1 falsch) | 79(1 wahr)
44;  1;              Test;             $ANWEISUNG-020; 47(1 falsch) | 46(1 wahr)
45;  1;              Anweisung;        $ANWEISUNG-030; ---
46;  1;              Anweisung;        $ANWEISUNG-046; ---
47;  1;              Anweisung;        $ANWEISUNG-004; 2(5)
48;  1;              Anweisung;        $ANWEISUNG-032; 49(1)
49;  1;              Anweisung;        $ANWEISUNG-033; 50(1)
50;  1;              Test;             $ANWEISUNG-034; 71(1 falsch) | 51(1 wahr)
51;  1;              Konnektor;        2; verbindet mit Konnektor 2 in Knoten 29
52;  1;              Konnektor;        3; verbindet mit Konnektor 3 in Knoten 72
53;  1;              Konnektor;        4; verbindet mit Konnektor 4 in Knoten 54
54;  -;              Konnektor;        4; 55(2)
55;  1 2;            Test;             $ANWEISUNG-020; 59(1 falsch) | 58(1 wahr)
56;  1;              Anweisung;        $ANWEISUNG-035; 57(2)
# Knoten 57/64: Wartezeit W2 (markierter Einzelbefehl, Koinzidenz vor Phase IV, Sektornummer von a).
57;  1 2 3;          Test;             $ANWEISUNG-003; 64(1 falsch) | 65(1 wahr)
58;  1;              Anweisung;        $ANWEISUNG-046; ---
59;  1;              Test;             $ANWEISUNG-036; 60(1 falsch) | 61(1 wahr)
# Knoten 60: nicht erfüllter bedingter Sprung, nach einer Wortzeit folgt Phase I (Programmieranleitung 2.2.3).
60;  1;              Anweisung;        $ANWEISUNG-004; 2(6)
61;  1;              Phasenzuordnung;  Beginn Phase IV; 62(1)
62;  1;              Anweisung;        $ANWEISUNG-022; 63(1)
63;  1;              Konnektor;        1; verbindet mit Konnektor 1 in Knoten 7
64;  1;              Anweisung;        $ANWEISUNG-004; 57(3)
65;  1;              Test;             $ANWEISUNG-020; 67(1 falsch) | 66(1 wahr)
66;  1;              Anweisung;        $ANWEISUNG-046; ---
67;  1;              Phasenzuordnung;  Beginn Phase IV; 68(1)
68;  1;              Anweisung;        $ANWEISUNG-021; 69(1)
69;  1;              Anweisung;        $ANWEISUNG-037; 70(1)
70;  1;              Anweisung;        $ANWEISUNG-022; 2(7)
71;  1;              Test;             $ANWEISUNG-038; 53(1 falsch) | 52(1 wahr)
72;  -;              Konnektor;        3; 26(3)
#
# Ergänzung 28.09.2026: X-Abbruch der verkürzten Gruppen-/Wiederholungsbefehle (B=5, B=7), Befehlsliste 4.1.6.
# Ist nach Operation und Resultatbehandlung einer Zelle der AC negativ (ANWEISUNG-042), werden Operation und
# Resultatbehandlung noch mit genau einer weiteren Zelle ausgeführt (der negative AC wird also noch verarbeitet,
# z. B. gespeichert), danach erfolgt der Abbruch. Die normale Abbruchbedingung (ANWEISUNG-024 = 040 ODER 041) hat
# Vorrang vor der X-Bedingung: sie wird an Knoten 35 VOR dem Erreichen von Knoten 73 geprüft, sodass eine Zelle,
# die beide Bedingungen gleichzeitig erfüllt, bereits an Knoten 35 (wahr) abgeht, ohne dass Knoten 73 je erreicht
# wird. Der Merker "X-Abbruch aufgetreten" wird nur gesetzt, wenn der Abbruch durch die X-Bedingung erfolgt
# (Knoten 78).
# Korrektur 04.10.2026: Die Zusatzzelle (Knoten 74-76) hatte bisher einen eigenen, zweiten Test der normalen
# Abbruchbedingung (ehem. Knoten 77), der bei "wahr" den Merker NICHT setzte. Das entspricht nicht Abb. 10 der
# Originaldokumentation (Befehlsliste.md 4.1.6, Bildabgleich): Dort hat der x-Bedingung-Zweig (i:=2) nach
# "Ausführung der Operation"/"Resultatbehandlung" KEINEN weiteren Test, sondern geht unbedingt in den schnellen
# Ausgang (Beginn Phase I/II ohne Koinzidenz-Wartezeit). Knoten 77 ist daher ersatzlos gestrichen; Knoten 76
# führt jetzt direkt zu Knoten 78. Der Eingang "9" an Knoten 2 (ehemals Knoten 77 wahr) entfällt entsprechend.
73;  1;              Test;             $ANWEISUNG-042; 36(1 falsch) | 74(1 wahr)
74;  1;              Anweisung;        $ANWEISUNG-025; 75(1)
75;  1;              Anweisung;        $ANWEISUNG-021; 76(1)
76;  1;              Anweisung;        $ANWEISUNG-022; 78(1)
78;  1;              Anweisung;        $ANWEISUNG-044; 2(8)
#
# Ergänzung 02.10.2026: Trennung der Stopp-Zustände nach der Originaldokumentation (Lampen US, BS, FÜ).
# Unbedingter Stopp (Knoten 45, ANWEISUNG-030): Flag US:=1. Bedingter Stopp bei gesetztem Schalter BS (neuer Knoten 79,
# ANWEISUNG-045, vorher gemeinsam mit dem unbedingten Stopp in Knoten 45): Flag BS:=1. Halt wegen Überlauf (Knoten 46, 58, 66,
# ANWEISUNG-046, vorher ANWEISUNG-030): weder US noch BS, angezeigt wird nur das Flag FÜ, das bereits gesetzt ist.
79;  1;              Anweisung;        $ANWEISUNG-045; ---
#
# Ergänzung 04.10.2026: Überlauftest nach Ausgabe-Halt und Anwahl (Originaldokumentation 4.3.2.5, Abb. 21).
# Nach der Anwahl bzw. der Zeichenausgabe (Knoten 23, erreicht von Knoten 22 über 39) folgt vor Phase I der Test "Überlauf vorhanden"
# (ANWEISUNG-020): Bei vorhandenem Überlauf Halt wegen Überlauf (Knoten 81, ANWEISUNG-046), sonst Phase I. Phase IV läuft bei diesen
# Befehlen nicht ab, deshalb gibt es keine Resultatbehandlung. Vorher führte Knoten 23 direkt zu Phase I.
# Zwei Angaben der Abb. 21 sind nicht als Knoten abgebildet: (1) Von der Löschanweisung bis zum Beginn der Phase I vergehen mindestens
# zwei Wortzeiten (interpretativ Wartezeit=0, ANWEISUNG-004). (2) Die Umstellung der Operation nach Phase III in Überlaufsprung oder
# Vergleichersprung 3 ist für die Wirkung bedeutungslos, weil die Sprungbedingung nur in Phase II ausgewertet wird. Einzelheiten:
# Befehlsliste, Ausgabe-/Anwahl-Befehl.
80;  1;              Test;             $ANWEISUNG-020; 2(2 falsch) | 81(1 wahr)
81;  1;              Anweisung;        $ANWEISUNG-046; ---
#
# Ergänzung 04.10.2026 (2): Fortsetzung nach einem Stopp (Originaldokumentation 4.3.2.3, Abb. 19).
# Der Stopp erfolgt am Ende der Phase III, also VOR der Wartezeit W2 (Knoten 45 und 79 liegen vor den Knoten 26/27).
# Die Fortsetzung durch die Tasten ist im Knotenautomaten nicht als eigene Knoten abgebildet. Die Tastenfolge (Interpreter) stellt
# den BR auf und wählt den Einstiegsknoten:
#     ST, Ue, E ohne M          -> Knoten 19 (B=2, z. B. 26Z oder 240: Knoten 26/27 Wartezeit W2, 28 Überlauftest, 31 Phase IV)
#     M ohne E, BR = Sprung mit Rückkehrabsicht (B=0/1, A=2, Z>=4: 025, 027, 125, 127)
#                               -> Knoten 54 (Konnektor 4): Phase III gilt als abgelaufen, die Sprungoperation (Knoten 40,
#                                  ANWEISUNG-029) und die Löschanweisung entfallen. Die Umstellung auf A=0 wird beim Eintritt
#                                  vorweggenommen. Weg: 54, 55 (Überlauftest), 59, 61, 62 (nur Resultatbehandlung), 63, 7, 6, 5 (W1), 8 (Phase II).
#     M ohne E, anderer BR      -> Knoten 19 (z. B. bedingter Sprung mit Rückkehrabsicht 065/067: Knoten 24, 55, 60, Phase I)
# Die Knotentabelle selbst bleibt unverändert.
