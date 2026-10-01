#ifndef C82_AUSTAUSCH_H
#define C82_AUSTAUSCH_H

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <stdbool.h>


typedef struct {
    volatile uint64_t accumulator;
    volatile uint64_t befehlsZaehler;
    volatile uint64_t adressregister;
    volatile uint64_t operationsregister;
    volatile uint64_t befehlsregister;
    volatile uint64_t zusatztrommeladresse;

    volatile unsigned int start_stop;
    volatile unsigned int running;

    volatile unsigned int Schalter_BS;
    volatile unsigned int Schalter_SP; //bedingter Sprung
    volatile unsigned int Schalter_SW;
    volatile unsigned int Schalter_LS;
    volatile unsigned int Schalter_K0;
    volatile unsigned int Schalter_K1;
    volatile unsigned int Schalter_K2;
    volatile unsigned int Schalter_K3;
    volatile unsigned int Schalter_K4;
    volatile unsigned int Schalter_K5;
    volatile unsigned int Schalter_K6;
    volatile unsigned int Schalter_K7;
    volatile unsigned int Schalter_T0;
    volatile unsigned int Schalter_T1;
    volatile unsigned int Schalter_T2;
    volatile unsigned int Schalter_T3;
    volatile unsigned int Schalter_HR;
    volatile unsigned int Schalter_E;
    volatile unsigned int Schalter_G;
    volatile unsigned int Schalter_M;
    volatile unsigned int Schalter_UE;
    volatile unsigned int Schalter_TSW;
    volatile unsigned int Schalter_ST;

    volatile unsigned int flag_e;
    volatile unsigned int flag_v1;
    volatile unsigned int flag_v2;
    volatile unsigned int flag_a;
    volatile unsigned int flag_tt;
    volatile unsigned int flag_sw;
    volatile unsigned int flag_k0;
    volatile unsigned int flag_k1;
    volatile unsigned int flag_k2;
    volatile unsigned int flag_k3;
    volatile unsigned int flag_k4;
    volatile unsigned int flag_k5;
    volatile unsigned int flag_k6;
    volatile unsigned int flag_k7;
    volatile unsigned int flag_t0;
    volatile unsigned int flag_t1;
    volatile unsigned int flag_t2;
    volatile unsigned int flag_t3;
    volatile unsigned int flag_fe;
    volatile unsigned int flag_bs;
    volatile unsigned int flag_us;
    volatile unsigned int flag_r;
    volatile unsigned int flag_h;
    volatile unsigned int flag_b;
    volatile unsigned int flag_n;
    volatile unsigned int flag_ue;

    volatile char projektVerzeichnis[256];
    volatile unsigned int sz_start_from_nodejs;

    volatile unsigned int LL1_Geraetefehler;
    volatile unsigned int LL1_bereit;
    volatile unsigned int LL1_Paritaetsfehler;
    volatile unsigned int LL1_working;
    volatile unsigned int LL2_Geraetefehler;
    volatile unsigned int LL2_bereit;
    volatile unsigned int LL2_Paritaetsfehler;
    volatile unsigned int LL2_working;
    volatile unsigned int LL3_Geraetefehler;
    volatile unsigned int LL3_bereit;
    volatile unsigned int LL3_Paritaetsfehler;
    volatile unsigned int LL3_working;
    volatile unsigned int LKS1_Geraetefehler;
    volatile unsigned int LKS1_bereit;
    volatile unsigned int LKS1_Paritaetsfehler;
    volatile unsigned int LKS1_working;
    volatile unsigned int SW1_Geraetefehler;
    volatile unsigned int SW1_bereit;
    volatile unsigned int SW1_Paritaetsfehler;
    volatile unsigned int SW1_working;
    volatile unsigned int SW2_Geraetefehler;
    volatile unsigned int SW2_bereit;
    volatile unsigned int SW2_Paritaetsfehler;
    volatile unsigned int SW2_working;

} AustauschStruktur;

// Globale Instanz der AustauschStruktur
extern AustauschStruktur austausch;

extern void executeProgram(unsigned int startAddress);

//#ifdef __cplusplus
void loeschAc();

extern unsigned int getSz_start_from_nodejs();
extern void setSz_start_from_nodejs(unsigned int value);


// Deklarationen der Getter und Setter für 64-Bit-Register
extern uint64_t getAccumulator();
extern void setAccumulator(uint64_t value);

extern uint64_t getBefehlsZaehler();
extern void setBefehlsZaehler(uint64_t value);

extern uint64_t getAdressRegister();
extern void setAdressRegister(uint64_t value);

extern uint64_t getOperationsRegister();
extern void setOperationsRegister(uint64_t value);

extern uint64_t getBefehlsRegister();
extern void setBefehlsRegister(uint64_t value);

extern uint64_t getZusatztrommelAdresse();
extern void setZusatztrommelAdresse(uint64_t value);

// Deklarationen der Getter und Setter für Status-Flags
extern unsigned int getStartStop();
extern void setStartStop(unsigned int value);

extern unsigned int getRunning();
extern void setRunning(unsigned int value);

// Deklarationen der Getter und Setter für Schalter
extern unsigned int getSchalterBS();
extern void setSchalterBS(unsigned int value);

extern unsigned int getSchalterSP();
extern void setSchalterSP(unsigned int value);

extern unsigned int getSchalterSW();
extern void setSchalterSW(unsigned int value);

extern unsigned int getSchalterLS();
extern void setSchalterLS(unsigned int value);

extern unsigned int getSchalterK0();
extern void setSchalterK0(unsigned int value);

extern unsigned int getSchalterK1();
extern void setSchalterK1(unsigned int value);

extern unsigned int getSchalterK2();
extern void setSchalterK2(unsigned int value);

extern unsigned int getSchalterK3();
extern void setSchalterK3(unsigned int value);

extern unsigned int getSchalterK4();
extern void setSchalterK4(unsigned int value);

extern unsigned int getSchalterK5();
extern void setSchalterK5(unsigned int value);

extern unsigned int getSchalterK6();
extern void setSchalterK6(unsigned int value);

extern unsigned int getSchalterK7();
extern void setSchalterK7(unsigned int value);

extern unsigned int getSchalterT0();
extern void setSchalterT0(unsigned int value);

extern unsigned int getSchalterT1();
extern void setSchalterT1(unsigned int value);

extern unsigned int getSchalterT2();
extern void setSchalterT2(unsigned int value);

extern unsigned int getSchalterT3();
extern void setSchalterT3(unsigned int value);

extern unsigned int getSchalterHR();
extern void setSchalterHR(unsigned int value);

extern unsigned int getSchalterE();
extern void setSchalterE(unsigned int value);

extern unsigned int getSchalterG();
extern void setSchalterG(unsigned int value);

extern unsigned int getSchalterM();
extern void setSchalterM(unsigned int value);

extern unsigned int getSchalterUE();
extern void setSchalterUE(unsigned int value);

extern unsigned int getSchalterTSW();
extern void setSchalterTSW(unsigned int value);

extern unsigned int getSchalterST();
extern void setSchalterST(unsigned int value);

// Deklarationen der Getter und Setter für Flags
extern unsigned int getFlagE();
extern void setFlagE(unsigned int value);

extern unsigned int getFlagV1();
extern void setFlagV1(unsigned int value);

extern unsigned int getFlagV2();
extern void setFlagV2(unsigned int value);

extern unsigned int getFlagA();
extern void setFlagA(unsigned int value);

extern unsigned int getFlagTT();
extern void setFlagTT(unsigned int value);

extern unsigned int getFlagSW();
extern void setFlagSW(unsigned int value);

extern unsigned int getFlagK0();
extern void setFlagK0(unsigned int value);

extern unsigned int getFlagK1();
extern void setFlagK1(unsigned int value);

extern unsigned int getFlagK2();
extern void setFlagK2(unsigned int value);

extern unsigned int getFlagK3();
extern void setFlagK3(unsigned int value);

extern unsigned int getFlagK4();
extern void setFlagK4(unsigned int value);

extern unsigned int getFlagK5();
extern void setFlagK5(unsigned int value);

extern unsigned int getFlagK6();
extern void setFlagK6(unsigned int value);

extern unsigned int getFlagK7();
extern void setFlagK7(unsigned int value);

extern unsigned int getFlagT0();
extern void setFlagT0(unsigned int value);

extern unsigned int getFlagT1();
extern void setFlagT1(unsigned int value);

extern unsigned int getFlagT2();
extern void setFlagT2(unsigned int value);

extern unsigned int getFlagT3();
extern void setFlagT3(unsigned int value);

extern unsigned int getFlagFE();
extern void setFlagFE(unsigned int value);

extern unsigned int getFlagBS();
extern void setFlagBS(unsigned int value);

extern unsigned int getFlagUS();
extern void setFlagUS(unsigned int value);

extern unsigned int getFlagR();
extern void setFlagR(unsigned int value);

extern unsigned int getFlagH();
extern void setFlagH(unsigned int value);

extern unsigned int getFlagB();
extern void setFlagB(unsigned int value);

extern unsigned int getFlagN();
extern void setFlagN(unsigned int value);

extern unsigned int getFlagUE();
extern void setFlagUE(unsigned int value);



// Externe Definitionen für LL1
extern unsigned int getLL1_Geraetefehler();
extern void setLL1_Geraetefehler(unsigned int value);

extern unsigned int getLL1_bereit();
extern void setLL1_bereit(unsigned int value);

extern unsigned int getLL1_Paritaetsfehler();
extern void setLL1_Paritaetsfehler(unsigned int value);

extern unsigned int getLL1_working();
extern void setLL1_working(unsigned int value);

// Externe Definitionen für LL2
extern unsigned int getLL2_Geraetefehler();
extern void setLL2_Geraetefehler(unsigned int value);

extern unsigned int getLL2_bereit();
extern void setLL2_bereit(unsigned int value);

extern unsigned int getLL2_Paritaetsfehler();
extern void setLL2_Paritaetsfehler(unsigned int value);

extern unsigned int getLL2_working();
extern void setLL2_working(unsigned int value);

// Externe Definitionen für LL3
extern unsigned int getLL3_Geraetefehler();
extern void setLL3_Geraetefehler(unsigned int value);

extern unsigned int getLL3_bereit();
extern void setLL3_bereit(unsigned int value);

extern unsigned int getLL3_Paritaetsfehler();
extern void setLL3_Paritaetsfehler(unsigned int value);

extern unsigned int getLL3_working();
extern void setLL3_working(unsigned int value);

// Externe Definitionen für Lks1
extern unsigned int getLKS1_Geraetefehler();
extern void setLKS1_Geraetefehler(unsigned int value);

extern unsigned int getLKS1_bereit();
extern void setLKS1_bereit(unsigned int value);

extern unsigned int getLKS1_Paritaetsfehler();
extern void setLKS1_Paritaetsfehler(unsigned int value);

extern unsigned int getLKS1_working();
extern void setLKS1_working(unsigned int value);


// Externe Definitionen für SW1
extern unsigned int getSW1_Geraetefehler();
extern void setSW1_Geraetefehler(unsigned int value);

extern unsigned int getSW1_bereit();
extern void setSW1_bereit(unsigned int value);

extern unsigned int getSW1_Paritaetsfehler();
extern void setSW1_Paritaetsfehler(unsigned int value);

extern unsigned int getSW1_working();
extern void setSW1_working(unsigned int value);

// Externe Definitionen für SW2 bis SW5
extern unsigned int getSW2_Geraetefehler();
extern void setSW2_Geraetefehler(unsigned int value);

extern unsigned int getSW2_bereit();
extern void setSW2_bereit(unsigned int value);

extern unsigned int getSW2_Paritaetsfehler();
extern void setSW2_Paritaetsfehler(unsigned int value);

extern unsigned int getSW2_working();
extern void setSW2_working(unsigned int value);

//#endif

extern bool running;

#endif // C82_AUSTAUSCH_H

