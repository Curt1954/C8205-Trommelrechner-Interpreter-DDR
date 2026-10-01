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
1;   -;              Konnektor;        B; 2(1)
2;   1 2 3 4 5 6 7 8 9;  Phasenzuordnung;  Beginn Phase I; 3(1)
3;   1;              Anweisung;        $ANWEISUNG-001; 4(1)
4;   1;              Test;             $ANWEISUNG-002; 5(1 falsch) | 8(1 wahr)
5;   1 2;            Test;             $ANWEISUNG-003; 6(1 falsch) | 8(2 wahr)
6;   1 2;            Anweisung;        $ANWEISUNG-004; 5(2)
7;   -;              Konnektor;        1; 6(2)
8;   1 2;            Phasenzuordnung;  Beginn Phase II; 9(1)
9;   1;              Anweisung;        $ANWEISUNG-005; 10(1)
10;  1;              Test;             $ANWEISUNG-006; 11(1 falsch) | 37(1 wahr)
11;  1;              Anweisung;        $ANWEISUNG-007; 12(1)
12;  1;              Test;             $ANWEISUNG-008; 15(1 falsch) | 13(1 wahr)
13;  1;              Test;             $ANWEISUNG-009; 15(2 falsch) | 14(1 wahr)
14;  1;              Anweisung;        $ANWEISUNG-010; 15(3)
15;  1 2 3 4;        Phasenzuordnung;  Beginn Phase III; 16(1)
16;  1;              Anweisung;        $ANWEISUNG-001; 17(1)
17;  1;              Test;             $ANWEISUNG-011; 19(1 falsch) | 18(1 wahr)
18;  1;              Anweisung;        $ANWEISUNG-012; 19(2)
19;  1 2;            Test;             $ANWEISUNG-013; 20(1 falsch) | 40(1 wahr)
20;  1;              Test;             $ANWEISUNG-043; 21(1 falsch) | 42(1 wahr)
21;  1;              Test;             $ANWEISUNG-015; 22(1 falsch) | 48(1 wahr)
22;  1;              Test;             $ANWEISUNG-016; 24(1 falsch) | 39(1 wahr)
23;  1;              Anweisung;        $ANWEISUNG-017; 2(2)
24;  1;              Test;             $ANWEISUNG-018; 25(1 falsch) | 55(1 wahr)
25;  1;              Test;             $ANWEISUNG-019; 26(1 falsch) | 56(1 wahr)
26;  1 2 3;          Test;             $ANWEISUNG-003; 27(1 falsch) | 28(1 wahr)
27;  1;              Anweisung;        $ANWEISUNG-004; 26(2)
28;  1;              Test;             $ANWEISUNG-020; 31(1 falsch) | 30(1 wahr)
29;  -;              Konnektor;        2; 57(1)
30;  1;              Anweisung;        $ANWEISUNG-030; ---
31;  1;              Phasenzuordnung;  Beginn Phase IV; 32(1)
32;  1 2;            Anweisung;        $ANWEISUNG-021; 33(1)
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
43;  1;              Test;             $ANWEISUNG-031; 44(1 falsch) | 45(2 wahr)
44;  1;              Test;             $ANWEISUNG-020; 47(1 falsch) | 46(1 wahr)
45;  1 2;            Anweisung;        $ANWEISUNG-030; ---
46;  1;              Anweisung;        $ANWEISUNG-030; ---
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
57;  1 2 3;          Test;             $ANWEISUNG-003; 64(1 falsch) | 65(1 wahr)
58;  1;              Anweisung;        $ANWEISUNG-030; ---
59;  1;              Test;             $ANWEISUNG-036; 60(1 falsch) | 61(1 wahr)
60;  1;              Anweisung;        $ANWEISUNG-004; 2(6)
61;  1;              Phasenzuordnung;  Beginn Phase IV; 62(1)
62;  1;              Anweisung;        $ANWEISUNG-022; 63(1)
63;  1;              Konnektor;        1; verbindet mit Konnektor 1 in Knoten 7
64;  1;              Anweisung;        $ANWEISUNG-004; 57(3)
65;  1;              Test;             $ANWEISUNG-020; 67(1 falsch) | 66(1 wahr)
66;  1;              Anweisung;        $ANWEISUNG-030; ---
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
# in beiden Zellen Vorrang. Der Merker "X-Abbruch aufgetreten" wird nur gesetzt, wenn der Abbruch durch die
# X-Bedingung erfolgt (Knoten 78).
73;  1;              Test;             $ANWEISUNG-042; 36(1 falsch) | 74(1 wahr)
74;  1;              Anweisung;        $ANWEISUNG-025; 75(1)
75;  1;              Anweisung;        $ANWEISUNG-021; 76(1)
76;  1;              Anweisung;        $ANWEISUNG-022; 77(1)
77;  1;              Test;             $ANWEISUNG-024; 78(1 falsch) | 2(9 wahr)
78;  1;              Anweisung;        $ANWEISUNG-044; 2(8)
