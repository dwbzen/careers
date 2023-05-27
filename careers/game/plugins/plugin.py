'''
Created on May 23, 2023

@author: don_bacon
'''

class Plugin(object):
    '''
    Interface and abstract base module for all plugin modules.
    Plug-ins are found in the game.plugins package, extend this Plugin class, and follow the following naming convention for plug-in discovery.
    The module name careers_{plugin_name} applies to all game editions (Hi-Tech, UK, JazzAge etc.)
    Modules that apply to a specific edition only are named careers_{plugin_name}{_edition_name}
    edition_name for each edition are in  resources/editions.json
    
    Edition rules plug-in modules are named: careers_{edition_name}_Rules_. Each edition has a rules plug-in.
    edition_name == "All" if the plug-in applies to all editions.
    '''


    def __init__(self, edition_name):
        '''
        Constructor
        '''
        self.name_template = "careers_{_edition_name}_{plugin_name}"
        self.edition = edition_name    # the edition that created this plug-in instance
    
    