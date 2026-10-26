"""Baut das Python-Erweiterungsmodul c8205_ztmodul (Zusatztrommeln, zt_modul.c statisch eingebunden, Limited API / abi3).
   python3 setup.py build_ext --inplace        (Linux)      -> c8205_ztmodul.abi3.so
   python  setup.py build_ext --inplace        (Windows)    -> c8205_ztmodul.pyd      (NICHT getestet)
Voraussetzung: C-Compiler, Python-Entwicklungsdateien, setuptools. plattform.h und c8205_api.h kommen aus c-module/ des Simulators
(Ordner SIM, Vorgabe ../../../c-module). trommel.c ist nicht enthalten (-DZT_OHNE_TROMMEL)."""
import os
import sys
from setuptools import setup, Extension

windows = sys.platform.startswith('win')
sim = os.environ.get('SIM', os.path.join('..', '..', '..', 'c-module'))
ext = Extension(
    'c8205_ztmodul',
    sources=['c8205_ztmodul.c', os.path.join('..', 'zt_modul.c')],
    include_dirs=['..', sim],
    define_macros=[('Py_LIMITED_API', '0x03080000'), ('ZT_OHNE_TROMMEL', '1')],
    py_limited_api=True,
    extra_compile_args=[] if windows else ['-pthread', '-O2'],
    extra_link_args=[] if windows else ['-pthread'],
    libraries=['winmm'] if windows else [],
)
setup(name='c8205_ztmodul', version='0.1', ext_modules=[ext])
