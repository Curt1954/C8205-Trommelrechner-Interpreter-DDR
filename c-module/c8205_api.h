/* c8205_api.h — Exportmakro fuer die gemeinsame Bibliothek (Linux: .so, Windows: .dll).
 * Unter Windows werden Funktionen und Variablen nur exportiert, wenn die Bibliothek mit
 * -DC8205_BUILD_DLL gebaut wird (Makefile bzw. build_msvc.bat). Python (ctypes) laedt
 * dann trommel.dll bzw. libtrommel.so. */
#ifndef C8205_API_H
#define C8205_API_H
#if defined(_WIN32) && defined(C8205_BUILD_DLL)
#define C8205_API __declspec(dllexport)
#else
#define C8205_API
#endif
#endif
