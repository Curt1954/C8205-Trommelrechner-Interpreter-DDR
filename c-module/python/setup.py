"""Baut das Python-Erweiterungsmodul c8205_trommel (C-Module statisch eingebunden, Limited API / abi3).
   python3 setup.py build_ext --inplace        (Linux)      -> c8205_trommel.abi3.so
   python  setup.py build_ext --inplace        (Windows)    -> c8205_trommel.pyd      (Visual Studio Build Tools oder MinGW-w64; NICHT getestet)
Voraussetzung: C-Compiler, Python-Entwicklungsdateien (Linux: z. B. python3-dev) und setuptools."""
import sys
from setuptools import setup, Extension

windows = sys.platform.startswith('win')
ext = Extension(
    'c8205_trommel',
    sources=['c8205_trommel_modul.c', '../trommel.c', '../bahnsperre.c', '../unterbrechung.c', '../tonmisch.c'],
    include_dirs=['..'],
    define_macros=[('Py_LIMITED_API', '0x03080000')],
    py_limited_api=True,
    extra_compile_args=[] if windows else ['-pthread', '-O2'],
    extra_link_args=[] if windows else ['-pthread'],
    libraries=['winmm'] if windows else [],
)
setup(name='c8205_trommel', version='0.2', ext_modules=[ext])
