'''
Created on Jul 11, 2023

@author: dwbzen
'''
from typing import List, Dict
import json
from game.careersObject import CareersObject

class TodoList(CareersObject):
    """A list of occupation(s) and degree(s) a player must complete
        in addtion to fulfilling their success formula, in order to win.
    """


    def __init__(self, occupation_names:List[str]=None, degree_names:List[str]=None):
        """
        Constructor
        """
        self._occupations = []
        self._degrees = []
        self._todos = {}
        if occupation_names is not None:
            for name in occupation_names:
                self._occupations.append( {"occupation_name" : name, "complete" : 0} )
            self._todos.update( {"occupations_todo" : self._occupations} )
        if degree_names is not None:
            for name in degree_names:
                self._degrees.append( {"degree_name" : name, "complete" : 0} )
                self._todos.update( {"degrees_todo" : self._degrees} )
        
    @property
    def todos(self) -> Dict:
        return self._todos
    
    @property
    def occupations(self) -> List[Dict]:
        return self._occupations
    
    @property
    def degrees(self)->List[Dict]:
        return self._degrees
    
    def set_completed(self, occupation_name:str=None, degree_name:str=None):
        """Sets the associated occupation/degree to complete (1)
            Arguments:
                occupation_name - the name of the occupation to complete. 
                degree_name - the names of the degree to complete.
            The occupation/degree does not need to be in the todo list
            Note that degree_name is case sensitive,
            That is it needs to be in the degreePrograms list in collegeDegrees.json.
        """
        if occupation_name is not None:
            for occupation in self._todos["occupations_todo"]:
                if occupation["occupation_name"]==occupation_name:
                    occupation["complete"] = 1
        
        if degree_name is not None:
            for degree in self._todos["degrees_todo"]:
                if degree["degree_name"]==degree_name:
                    degree["complete"] = 1
    
    def is_comlete(self) ->bool:
        """Returns True if all the todo items are complete, False otherwise
        """
        complete = True
        for occupation in self._todos["occupations_todo"]:
            complete &= occupation["complete"]
        for degree in self._todos["degrees_todo"]:
            complete &= degree["complete"]
        return complete
    
    def to_JSON(self) ->str:
        jstr = json.dumps(self._todos)
        return jstr
    
