
from threading import Lock
import sys

class Environment(object):
    _environ = None
    _lock = Lock()
    
    def __init__(self, package_name=None):
        """Initialize the running Environment by setting global environment variables
        
        """
        self.name = package_name
        self.resource_base = '/Compile/careers/resources'
        self.package_name = package_name
        self.resources = {}
        self.resources['game'] = self.resource_base + '/game'
        self.resources['server'] = self.resource_base + '/server'
        self.items = {}
        
    def __repr__(self):
        return '<Environment>'
    
    
    def get_resource_folder(self, package=None):
        if package is None:
            return self.resource_base
        if package in self.resources:
            return self.resources[package]
        else:
            print(f'Invalid package {package}', file=sys.stderr)
            return None

    def add_item(self, key, value):
        self.items[key] = value
    
    def get_items(self):
        return self.items
    
    def get_item(self, key):
        return self.items[key]

    @staticmethod
    def get_environment():
        env = None
        Environment._lock.acquire()
        if Environment._environ is not None:
            env = Environment._environ
        else:
            Environment._environ = Environment('dwbzen')
            env = Environment._environ
        Environment._lock.release()
        return env

