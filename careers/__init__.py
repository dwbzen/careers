
from __future__ import absolute_import

import sys
minPythonVersion = (3, 9)
minPythonVersionStr = '.'.join([str(x) for x in minPythonVersion])

import sys  
from pathlib import Path  
file = Path(__file__). resolve()  
package_root_directory = file.parents [1]  
sys.path.append(str(package_root_directory))  
sys.path.append(str(package_root_directory) + "\\careers")  

del sys
del minPythonVersion
del minPythonVersionStr

__author__ = "Donald Bacon"
__version__ = "0.0.1"


# this defines what  is loaded when importing __all__
# put these in alphabetical order FIRST dirs then modules
# but: base must come first; in some cases other modules depend on
# definitions in base


__all__ = [
    # sub folders
    'game',
    'server',
    # individual modules
    # KEEP ALPHABETICAL unless necessary for load reasons, if so
    # put a note.  Keep one letter per line.
    'environment'
]

# -----------------------------------------------------------------------------
# this brings all of our own __all__ names into the dwbzen package namespace
# pylint: disable=wildcard-import
# 
from careers.environment import Environment
import game
import server