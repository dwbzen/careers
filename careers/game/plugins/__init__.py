'''
Created on May 23, 2023

@author: don_bacon

Plugin modules provide the means for extending the game functionality  
and/or adding edition-specific rules implementations.

Plugin implementations are loaded by CareersGame and invoked as needed by the CareersGameEngine.

The module naming convention for rules is: <edition-name><Rules>_Plugin>.py,
the plug-in module name(s) are specified in the editions.json file as 
for example "hiTechRules_Plugin"
For extensions: <edition-name><entension-name>_Plugin>.py,
for example "hiTechRandomizer_Plugin.py"

A plugin can be mandatory or optional.
'''

from __future__ import absolute_import  # multi-line and relative/absolute imports

from .__version__ import __title__, __description__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__


__all__ = [
    "careers_All_Randomizer",
    "careers_HiTech_Rules",
    "plugin"
]

from game.plugins.plugin import Plugin
from game.plugins.careers_All_Randomizer import Careers_Randomizer
from game.plugins.careers_HiTech_Rules import Careers_HiTech_Rules

