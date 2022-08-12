'''
Created on Aug 9, 2022

@author: don_bacon
'''

from enum import Enum

class ActionType(Enum):
    """Action types referenced on Opportunity cards, occupation and border squares

    """
    EXTRA_TURN = 1          # player gets an extra turn
    LEAVE_UNEMPLOYMENT = 2  # player can leave unemployment without penalty
    COLLECT_EXPERIENCE = 3  # collect experience card from other players
    DRAW_EXPERIENCE = 4     # draw 1 or more experience card(s) from the deck
    DRAW_OPPORTUNITY = 5    # "opportunity"
    LOSE_TURN = 6            # "loseTurn"
    CASH_LOSS = 7            # "cashLoss"  percent or amount
    SALARY_INCREASE = 8        # "salaryIncrease" money amount
    SALARY_DIE_ROLL = 9        # "salary_dieRoll" amount x roll of 1 die
    BONUS_AMOUNT = 10        # "bonus_amount"  cash bonus amount
    SALARY_CUT = 11            # "salaryCut" by percent or amount
    BONUS_DIE_ROLL = 12        # cash amount x roll of 1 die "bonus_dieRoll"
    CALL_IN_FAVORS = 13        # "favors"
    CASH_LOSS_OR_UNEMPLOYMENT = 14        # cash loss amount or go to unemployment "cashLossOrUnemployment"
    EXIT_OCCUPATION = 15    # "occupationExit"
    ENTER_OCCUPATION = 16   # "enterOccupation"
    CASH_LOSS_DICE_ROLL = 17    # "cashLossRoll" salary, %salary, cash or %cash, 1 or 2 dice
    TRAVEL = 18                # "travel_shortcut" or "travel_border" next_square = number or name
    OCCUPATION_EXIT = 19    # "occupationExit"  raise salary if College or give Experience cards
    PAY_TAX = 20            # "payTax" as %salary depending on salary    
    
    def describe(self):
        # self is the member here
        return self.name, self.value
    