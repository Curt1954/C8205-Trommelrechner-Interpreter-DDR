// c82_austausch.c
#include "c82_austausch.h"
#include "ca82_protokoll.h"
#include "ca82_standards.h"
#include <string.h> // Für memset
#include <time.h>

// Globale Instanz der AustauschStruktur
AustauschStruktur austausch;


// Funktion zum Initialisieren der Struktur
void initializeAustausch() {
    // Speicher zurücksetzen
    memset(&austausch, 0, sizeof(AustauschStruktur));

    // 64-Bit-Register
    austausch.accumulator = 0;
    austausch.befehlsZaehler = 0;
    austausch.adressregister = 0;
    austausch.operationsregister = 0;
    austausch.befehlsregister = 0;
    austausch.zusatztrommeladresse = 0;

    // Status-Flags
    austausch.start_stop = 0;
    austausch.running = 1;

    // Schalter
    austausch.Schalter_BS = 0;
    austausch.Schalter_SP = 0;
    austausch.Schalter_SW = 0;
    austausch.Schalter_LS = 0;
    austausch.Schalter_K0 = 0;
    austausch.Schalter_K1 = 0;
    austausch.Schalter_K2 = 0;
    austausch.Schalter_K3 = 0;
    austausch.Schalter_K4 = 0;
    austausch.Schalter_K5 = 0;
    austausch.Schalter_K6 = 0;
    austausch.Schalter_K7 = 0;
    austausch.Schalter_T0 = 0;
    austausch.Schalter_T1 = 0;
    austausch.Schalter_T2 = 0;
    austausch.Schalter_T3 = 0;
    austausch.Schalter_HR = 0;
    austausch.Schalter_E = 0;
    austausch.Schalter_G = 0;
    austausch.Schalter_M = 0;
    austausch.Schalter_UE = 0;
    austausch.Schalter_TSW = 0;
    austausch.Schalter_ST = 0;

    // Flags
    austausch.flag_e = 0;
    austausch.flag_v1 = 0;
    austausch.flag_v2 = 0;
    austausch.flag_a = 0;
    austausch.flag_tt = 0;
    austausch.flag_sw = 0;
    austausch.flag_k0 = 0;
    austausch.flag_k1 = 0;
    austausch.flag_k2 = 0;
    austausch.flag_k3 = 0;
    austausch.flag_k4 = 0;
    austausch.flag_k5 = 0;
    austausch.flag_k6 = 0;
    austausch.flag_k7 = 0;
    austausch.flag_t0 = 0;
    austausch.flag_t1 = 0;
    austausch.flag_t2 = 0;
    austausch.flag_t3 = 0;
    austausch.flag_fe = 0;
    austausch.flag_bs = 0;
    austausch.flag_us = 0;
    austausch.flag_r = 0;
    austausch.flag_h = 0;
    austausch.flag_b = 0;
    austausch.flag_n = 0;
    austausch.flag_ue = 0;

    memset((void *)austausch.projektVerzeichnis, 0, sizeof(austausch.projektVerzeichnis));
    austausch.sz_start_from_nodejs = 0;

    austausch.LL1_Geraetefehler = 0;
    austausch.LL1_bereit = 0;
    austausch.LL1_Paritaetsfehler = 0;
    austausch.LL1_working = 0;
    austausch.LL2_Geraetefehler = 0;
    austausch.LL2_bereit = 0;
    austausch.LL2_Paritaetsfehler = 0;
    austausch.LL2_working = 0;
    austausch.LL3_Geraetefehler = 0;
    austausch.LL3_bereit = 0;
    austausch.LL3_Paritaetsfehler = 0;
    austausch.LL3_working = 0;
    austausch.LKS1_Geraetefehler = 0;
    austausch.LKS1_bereit = 0;
    austausch.LKS1_Paritaetsfehler = 0;
    austausch.LKS1_working = 0;
    austausch.SW1_Geraetefehler = 0;
    austausch.SW1_bereit = 0;
    austausch.SW1_Paritaetsfehler = 0;
    austausch.SW1_working = 0;
    austausch.SW2_Geraetefehler = 0;
    austausch.SW2_bereit = 0;
    austausch.SW2_Paritaetsfehler = 0;
    austausch.SW2_working = 0;

}

unsigned int getSz_start_from_nodejs() { return austausch.sz_start_from_nodejs; }
void setSz_start_from_nodejs(unsigned int value) { austausch.sz_start_from_nodejs = value; }

AustauschStruktur* getAustauschPointer() {
    return &austausch;
}

// Getter- und Setter-Funktionen für 64-Bit-Register
uint64_t getAccumulator() { return austausch.accumulator; }
void setAccumulator(uint64_t value) {
    uint64_t mask = 0x1FFFFFFFF; // 33-Bit Maske (Oktal: 77777777777)
    austausch.accumulator = value & mask;
}

uint64_t getBefehlsZaehler() { return austausch.befehlsZaehler; }
void setBefehlsZaehler(uint64_t value) { austausch.befehlsZaehler = value; }

uint64_t getAdressRegister() { return austausch.adressregister; }
void setAdressRegister(uint64_t value) { austausch.adressregister = value; }

uint64_t getOperationsRegister() { return austausch.operationsregister; }
void setOperationsRegister(uint64_t value) { austausch.operationsregister = value; }

uint64_t getBefehlsRegister() { return austausch.befehlsregister; }
void setBefehlsRegister(uint64_t value) { austausch.befehlsregister = value; }

uint64_t getZusatztrommelAdresse()  { return austausch.zusatztrommeladresse; }
void setZusatztrommelAdresse(uint64_t value)  { austausch.zusatztrommeladresse = value; }

// Getter- und Setter-Funktionen für Status-Flags
unsigned int getStartStop() { return austausch.start_stop; }
void setStartStop(unsigned int value) { austausch.start_stop = value; }

unsigned int getRunning() { return austausch.running; }
void setRunning(unsigned int value) { austausch.running = value; }

// Getter- und Setter-Funktionen für Schalter
unsigned int getSchalterBS() { return austausch.Schalter_BS; }
void setSchalterBS(unsigned int value) { austausch.Schalter_BS = value; }

unsigned int getSchalterSP() { return austausch.Schalter_SP; }
void setSchalterSP(unsigned int value) { austausch.Schalter_SP = value; }

unsigned int getSchalterSW() { return austausch.Schalter_SW; }
void setSchalterSW(unsigned int value) { austausch.Schalter_SW = value; }

unsigned int getSchalterLS() { return austausch.Schalter_LS; }
void setSchalterLS(unsigned int value) { austausch.Schalter_LS = value; }

unsigned int getSchalterK0() { return austausch.Schalter_K0; }
void setSchalterK0(unsigned int value) { austausch.Schalter_K0 = value; }

unsigned int getSchalterK1() { return austausch.Schalter_K1; }
void setSchalterK1(unsigned int value) { austausch.Schalter_K1 = value; }

unsigned int getSchalterK2() { return austausch.Schalter_K2; }
void setSchalterK2(unsigned int value) { austausch.Schalter_K2 = value; }

unsigned int getSchalterK3() { return austausch.Schalter_K3; }
void setSchalterK3(unsigned int value) { austausch.Schalter_K3 = value; }

unsigned int getSchalterK4() { return austausch.Schalter_K4; }
void setSchalterK4(unsigned int value) { austausch.Schalter_K4 = value; }

unsigned int getSchalterK5() { return austausch.Schalter_K5; }
void setSchalterK5(unsigned int value) { austausch.Schalter_K5 = value; }

unsigned int getSchalterK6() { return austausch.Schalter_K6; }
void setSchalterK6(unsigned int value) { austausch.Schalter_K6 = value; }

unsigned int getSchalterK7() { return austausch.Schalter_K7; }
void setSchalterK7(unsigned int value) { austausch.Schalter_K7 = value; }

unsigned int getSchalterT0() { return austausch.Schalter_T0; }
void setSchalterT0(unsigned int value) { austausch.Schalter_T0 = value; }

unsigned int getSchalterT1() { return austausch.Schalter_T1; }
void setSchalterT1(unsigned int value) { austausch.Schalter_T1 = value; }

unsigned int getSchalterT2() { return austausch.Schalter_T2; }
void setSchalterT2(unsigned int value) { austausch.Schalter_T2 = value; }

unsigned int getSchalterT3() { return austausch.Schalter_T3; }
void setSchalterT3(unsigned int value) { austausch.Schalter_T3 = value; }

unsigned int getSchalterHR() { return austausch.Schalter_HR; }
void setSchalterHR(unsigned int value) { austausch.Schalter_HR = value; }

unsigned int getSchalterE() { return austausch.Schalter_E; }
void setSchalterE(unsigned int value) { austausch.Schalter_E = value; }

unsigned int getSchalterG() { return austausch.Schalter_G; }
void setSchalterG(unsigned int value) { austausch.Schalter_G = value; }

unsigned int getSchalterM() { return austausch.Schalter_M; }
void setSchalterM(unsigned int value) { austausch.Schalter_M = value; }

unsigned int getSchalterUE() { return austausch.Schalter_UE; }
void setSchalterUE(unsigned int value) { austausch.Schalter_UE = value; }

unsigned int getSchalterTSW() { return austausch.Schalter_TSW; }
void setSchalterTSW(unsigned int value) { austausch.Schalter_TSW = value; }

unsigned int getSchalterST() { return austausch.Schalter_ST; }
void setSchalterST(unsigned int value) { austausch.Schalter_ST = value; }

// Getter- und Setter-Funktionen für Flags
unsigned int getFlagE() { return austausch.flag_e; }
void setFlagE(unsigned int value) { austausch.flag_e = value; }

unsigned int getFlagV1() { return austausch.flag_v1; }
void setFlagV1(unsigned int value) { austausch.flag_v1 = value; }

unsigned int getFlagV2() { return austausch.flag_v2; }
void setFlagV2(unsigned int value) { austausch.flag_v2 = value; }

unsigned int getFlagA() { return austausch.flag_a; }
void setFlagA(unsigned int value) { austausch.flag_a = value; }

unsigned int getFlagTT() { return austausch.flag_tt; }
void setFlagTT(unsigned int value) { austausch.flag_tt = value; }

unsigned int getFlagSW() { return austausch.flag_sw; }
void setFlagSW(unsigned int value) { austausch.flag_sw = value; }

unsigned int getFlagK0() { return austausch.flag_k0; }
void setFlagK0(unsigned int value) { austausch.flag_k0 = value; }

unsigned int getFlagK1() { return austausch.flag_k1; }
void setFlagK1(unsigned int value) { austausch.flag_k1 = value; }

unsigned int getFlagK2() { return austausch.flag_k2; }
void setFlagK2(unsigned int value) { austausch.flag_k2 = value; }

unsigned int getFlagK3() { return austausch.flag_k3; }
void setFlagK3(unsigned int value) { austausch.flag_k3 = value; }

unsigned int getFlagK4() { return austausch.flag_k4; }
void setFlagK4(unsigned int value) { austausch.flag_k4 = value; }

unsigned int getFlagK5() { return austausch.flag_k5; }
void setFlagK5(unsigned int value) { austausch.flag_k5 = value; }

unsigned int getFlagK6() { return austausch.flag_k6; }
void setFlagK6(unsigned int value) { austausch.flag_k6 = value; }

unsigned int getFlagK7() { return austausch.flag_k7; }
void setFlagK7(unsigned int value) { austausch.flag_k7 = value; }

unsigned int getFlagT0() { return austausch.flag_t0; }
void setFlagT0(unsigned int value) { austausch.flag_t0 = value; }

unsigned int getFlagT1() { return austausch.flag_t1; }
void setFlagT1(unsigned int value) { austausch.flag_t1 = value; }

unsigned int getFlagT2() { return austausch.flag_t2; }
void setFlagT2(unsigned int value) { austausch.flag_t2 = value; }

unsigned int getFlagT3() { return austausch.flag_t3; }
void setFlagT3(unsigned int value) { austausch.flag_t3 = value; }

unsigned int getFlagFE() { return austausch.flag_fe; }
void setFlagFE(unsigned int value) { austausch.flag_fe = value; }

unsigned int getFlagBS() { return austausch.flag_bs; }
void setFlagBS(unsigned int value) { austausch.flag_bs = value; }

unsigned int getFlagUS() { return austausch.flag_us; }
void setFlagUS(unsigned int value) { austausch.flag_us = value; }

unsigned int getFlagR() { return austausch.flag_r; }
void setFlagR(unsigned int value) { austausch.flag_r = value; }

unsigned int getFlagH() { return austausch.flag_h; }
void setFlagH(unsigned int value) { austausch.flag_h = value; }

unsigned int getFlagB() { return austausch.flag_b; }
void setFlagB(unsigned int value) { austausch.flag_b = value; }

unsigned int getFlagN() { return austausch.flag_n; }
void setFlagN(unsigned int value) { austausch.flag_n = value; }

unsigned int getFlagUE() { return austausch.flag_ue; }
void setFlagUE(unsigned int value) { austausch.flag_ue = value; }


// Getter und Setter für LL1
unsigned int getLL1_Geraetefehler() { return austausch.LL1_Geraetefehler; }
void setLL1_Geraetefehler(unsigned int value) { austausch.LL1_Geraetefehler = value; }

unsigned int getLL1_bereit() { return austausch.LL1_bereit; }
void setLL1_bereit(unsigned int value) { austausch.LL1_bereit = value; }

unsigned int getLL1_Paritaetsfehler() { return austausch.LL1_Paritaetsfehler; }
void setLL1_Paritaetsfehler(unsigned int value) { austausch.LL1_Paritaetsfehler = value; }

unsigned int getLL1_working() { return austausch.LL1_working; }
void setLL1_working(unsigned int value) { austausch.LL1_working = value; }

// Getter und Setter für LL2
unsigned int getLL2_Geraetefehler() { return austausch.LL2_Geraetefehler; }
void setLL2_Geraetefehler(unsigned int value) { austausch.LL2_Geraetefehler = value; }

unsigned int getLL2_bereit() { return austausch.LL2_bereit; }
void setLL2_bereit(unsigned int value) { austausch.LL2_bereit = value; }

unsigned int getLL2_Paritaetsfehler() { return austausch.LL2_Paritaetsfehler; }
void setLL2_Paritaetsfehler(unsigned int value) { austausch.LL2_Paritaetsfehler = value; }

unsigned int getLL2_working() { return austausch.LL2_working; }
void setLL2_working(unsigned int value) { austausch.LL2_working = value; }

// Getter und Setter für LL3
unsigned int getLL3_Geraetefehler() { return austausch.LL3_Geraetefehler; }
void setLL3_Geraetefehler(unsigned int value) { austausch.LL3_Geraetefehler = value; }

unsigned int getLL3_bereit() { return austausch.LL3_bereit; }
void setLL3_bereit(unsigned int value) { austausch.LL3_bereit = value; }

unsigned int getLL3_Paritaetsfehler() { return austausch.LL3_Paritaetsfehler; }
void setLL3_Paritaetsfehler(unsigned int value) { austausch.LL3_Paritaetsfehler = value; }

unsigned int getLL3_working() { return austausch.LL3_working; }
void setLL3_working(unsigned int value) { austausch.LL3_working = value; }

// Getter und Setter für LKS1
unsigned int getLKS1_Geraetefehler() { return austausch.LL3_Geraetefehler; }
void setLKS1_Geraetefehler(unsigned int value) { austausch.LKS1_Geraetefehler = value; }

unsigned int getLKS1_bereit() { return austausch.LL3_bereit; }
void setLKS1_bereit(unsigned int value) { austausch.LKS1_bereit = value; }

unsigned int getLKS1_Paritaetsfehler() { return austausch.LL3_Paritaetsfehler; }
void setLKS1_Paritaetsfehler(unsigned int value) { austausch.LKS1_Paritaetsfehler = value; }

unsigned int getLKS1_working() { return austausch.LL3_working; }
void setLKS1_working(unsigned int value) { austausch.LKS1_working = value; }



// Getter und Setter für SW1
unsigned int getSW1_Geraetefehler() { return austausch.SW1_Geraetefehler; }
void setSW1_Geraetefehler(unsigned int value) { austausch.SW1_Geraetefehler = value; }

unsigned int getSW1_bereit() { return austausch.SW1_bereit; }
void setSW1_bereit(unsigned int value) { austausch.SW1_bereit = value; }

unsigned int getSW1_Paritaetsfehler() { return austausch.SW1_Paritaetsfehler; }
void setSW1_Paritaetsfehler(unsigned int value) { austausch.SW1_Paritaetsfehler = value; }

unsigned int getSW1_working() { return austausch.SW1_working; }
void setSW1_working(unsigned int value) { austausch.SW1_working = value; }

// Getter und Setter für SW2 bis SW5
unsigned int getSW2_Geraetefehler() { return austausch.SW2_Geraetefehler; }
void setSW2_Geraetefehler(unsigned int value) { austausch.SW2_Geraetefehler = value; }

unsigned int getSW2_bereit() { return austausch.SW2_bereit; }
void setSW3_bereit(unsigned int value) { austausch.SW2_bereit = value; }

unsigned int getSW2_Paritaetsfehler() { return austausch.SW2_Paritaetsfehler; }
void setSW4_Paritaetsfehler(unsigned int value) { austausch.SW2_Paritaetsfehler = value; }

unsigned int getSW2_working() { return austausch.SW2_working; }
void setSW5_working(unsigned int value) { austausch.SW2_working = value; }

// Globale Variablen für die Steuerung
bool running = true;

