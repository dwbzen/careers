'''
Created on Aug 12, 2022

@author: don_bacon
'''
import random, math
from datetime import datetime
from game.successFormula import SuccessFormula


class GameUtils(object):
    """
    General purpose routines.
    """

    def __init__(self, params):
        pass
    
    @staticmethod
    def shuffle(size:int) -> list:
        return random.sample(list(range(0, size)), size)
    
    
    @staticmethod
    def get_random_formula(total_points) -> SuccessFormula:
        cash = random.randint(1, total_points)
        hearts = random.randint(1, 100-cash)
        stars = random.randint(1,100-(cash+hearts))
        return SuccessFormula(stars, hearts, cash)
    
    @staticmethod
    def roll(number_of_dice):
        return random.choices(population=[1,2,3,4,5,6],k=number_of_dice)
    
    @staticmethod
    def get_datetime() -> str:
        """Returns - now formatted as a string, for example: 20220911_120545
        """
        now = datetime.today()
        return '{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    @staticmethod
    def time_since(base_date:datetime=datetime(2000, 1, 1, 0, 0),  end_date=None, what='seconds') -> int:
        """Gets the number of seconds or days that has passed since a given base date/datetime
            Arguments:
                base_date : the base date, default is 12:00 AM 2000-01-01
                what : 'seconds' or 'days'
            Returns:
                The seconds or days since the base date to now, truncated to an integer
        """
        end_date = datetime.now() if end_date is None else end_date
        delta = end_date-base_date
        if what=='seconds':
            return math.trunc(delta.total_seconds())
        else:   # assume days
            return delta.days
        