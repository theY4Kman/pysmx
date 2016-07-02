import sys
import os
import shutil

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

SPVM_PATH = os.path.abspath(os.path.dirname(__file__))
_rel = lambda *p: os.path.join(SPVM_PATH, *p)


# clean previous build
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if (name.startswith("spvm") and not(name.endswith(".pyx") or name.endswith(".pxd"))):
            os.remove(os.path.join(root, name))
    for name in dirs:
        if (name == "build"):
            shutil.rmtree(name)

# build "myext.so" python extension to be added to "PYTHONPATH" afterwards...
setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension("spvm",
                  sources=["spvm.pyx"],
                  libraries=["sourcepawn.jit.x86", 'python27'],
                  library_dirs=[_rel('vendor'), 'C:\Python27\libs'],
                  language="c++",
             )
        ]
)
