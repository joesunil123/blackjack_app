
import math
from enum import Enum


class Action(Enum):
    STAND = 1
    HIT = 2
    SPLIT = 3
    DOUBLE = 4
    INSURANCE = 5

class GameState:
    def __init__(self, count_type, bet_strat, player_num, unit_bet, num_shoes):
        # Game parameters
        self.count_type = count_type
        self.bet_strat = bet_strat
        self.player_num = player_num
        self.num_shoes = num_shoes
        self.unit_bet = int(unit_bet)

        # Overall variables
        self.curr_winnings = 0
        self.curr_count = 0
        self.cards_seen = 0
        self.prev_win = False

        # Round variables
        self.curr_bet = 0
        self.player_value = 0
        self.dealer_value = 0
        self.is_soft = False

        # Basic Strategy tables
        self.hard_total = {
            8: {2: Action.HIT, 3: Action.HIT, 4:Action.HIT, 5: Action.HIT, 6: Action.HIT, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            9: {2: Action.HIT, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            10: {2: Action.DOUBLE, 3: Action.DOUBLE, 4:Action.DOUBLE, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.DOUBLE, 8: Action.DOUBLE, 9: Action.DOUBLE, 10: Action.HIT, 11: Action.HIT},
            11: {2: Action.DOUBLE, 3: Action.DOUBLE, 4:Action.DOUBLE, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.DOUBLE, 8: Action.DOUBLE, 9: Action.DOUBLE, 10: Action.DOUBLE, 11: Action.DOUBLE},
            12: {2: Action.HIT, 3: Action.HIT, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            13: {2: Action.STAND, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            14: {2: Action.STAND, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            15: {2: Action.STAND, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            16: {2: Action.STAND, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT}
        }

        self.soft_total = {
            2: {2: Action.HIT, 3: Action.HIT, 4:Action.HIT, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            3: {2: Action.HIT, 3: Action.HIT, 4:Action.HIT, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            4: {2: Action.HIT, 3: Action.HIT, 4:Action.DOUBLE, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            5: {2: Action.HIT, 3: Action.HIT, 4:Action.DOUBLE, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            6: {2: Action.HIT, 3: Action.DOUBLE, 4:Action.DOUBLE, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.HIT, 8: Action.HIT, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            7: {2: Action.DOUBLE, 3: Action.DOUBLE, 4:Action.DOUBLE, 5: Action.DOUBLE, 6: Action.DOUBLE, 7: Action.STAND, 8: Action.STAND, 9: Action.HIT, 10: Action.HIT, 11: Action.HIT},
            8: {2: Action.STAND, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.STAND, 8: Action.STAND, 9: Action.STAND, 10: Action.STAND, 11: Action.STAND},
            9: {2: Action.STAND, 3: Action.STAND, 4:Action.STAND, 5: Action.STAND, 6: Action.STAND, 7: Action.STAND, 8: Action.STAND, 9: Action.STAND, 10: Action.STAND, 11: Action.STAND},
        }


    # Modifying game state
    def reset(self):
        self.curr_winnings = 0
        self.curr_bet = 0
        self.curr_count = 0
        self.prev_win = None
        self.cards_seen = 0

    def game_end(self, is_win):
        if is_win:
            self.curr_winnings += self.curr_bet
        else:
            self.curr_winnings -= self.curr_bet
        
        self.prev_win = is_win

    def bet_amount(self, bet):
        self.curr_bet = bet

    def get_bet_amount(self):
        match self.bet_strat:
            case "martingale":
                if self.curr_winnings >= 0:
                    return self.unit_bet
                return self.unit_bet - self.curr_winnings
            case "rev_martinagle":
                if self.prev_win is None:
                    return self.unit_bet
                if self.prev_win:
                    return self.curr_bet * 2
                else:
                    return max(1.0, self.curr_bet/2)
            case "count-based":
                true_count = math.ceiling((self.num_shoes * 52 - self.cards_seen)//52)
                scale = max(1, true_count)
                return scale * self.unit_bet
            case _:
                return 0
    
    def get_action(self):
        match self.count_type:
            case "basic-strategy":
                if self.is_soft:
                    return self.soft_totals[self.player_value][self.dealer_value]
                else:
                    if self.player_value >= 17:
                        return Action.STAND
                    return self.hard_total[self.player_value][self.dealer_value]
            case "hi-lo":
                pass
            case "omega":
                pass
    
    





    