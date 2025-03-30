
import math
from enum import Enum
from collections import deque

# Constants
MAX_DISPLAY_WINNINGS = 10

class Action(Enum):
    STAND = 1
    HIT = 2
    SPLIT = 3
    DOUBLE = 4
    INSURANCE = 5

class Outcome(Enum):
    WIN = 1
    PUSH = 2
    LOSE = 3
    BJ = 4

class GameState:
    def __init__(self):
        # Input parameters
        self.counting_technique = ""
        self.betting_strategy = ""
        self.player_pos = 0
        self.num_shoes = 0
        self.unit_bet = 0

        # Display parameters
        self.profits = deque()
        self.curr_bet = 0

        # Intermediate data
        self.curr_count = 0
        self.cards_seen = 0
        self.prev_result = Outcome.WIN

        # Player + Dealer info
        self.curr_hands = []
        self.dealer_hand = []

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

    def place_bet(self, new_bet):
        self.curr_bet = new_bet
    
    def round_outcome(self, outcome: Outcome):
        self.curr_hands = []
        prev_profit = 0 if not self.profits else self.profits[-1]
        self.prev_result = outcome
        match outcome:
            case Outcome.WIN:
                self.profits.append(prev_profit + self.curr_bet)
            case Outcome.PUSH:
                self.profits.append(prev_profit)
            case Outcome.LOSE:
                self.profits.append(prev_profit-self.curr_bet)
            case Outcome.BJ:
                self.profits.append(prev_profit + self.curr_bet * 1.5)
            case _:
                # Dummy case
                self.profits.append(0)
        
        if len(self.profits) > MAX_DISPLAY_WINNINGS:
            self.profits.popleft()

    # Resetting game state to start
    def start(self, counting_technique, betting_strategy, player_pos, num_shoes, unit_bet):
        self.counting_technique = counting_technique
        self.betting_strategy = betting_strategy
        self.player_pos = player_pos
        self.num_shoes = num_shoes
        self.unit_bet = unit_bet
        
        self.profits = deque()
        self.curr_winnings = 0
        self.curr_bet = self.unit_bet
        self.cards_seen = 0
        self.prev_result = Outcome.PUSH

        #TODO: Dummy for now: Needs to be updated when integration occurs
        self.curr_hands = [{"A": 1, "2": 2}, {"10": 2}]
        self.dealer_hand = [{"3": 1, "A": 3}]
    
    def get_betting_mode(self):
        temp = self.betting_strategy.split("-")
        res = ""
        for word in temp:
            res += word
            res += " "
        return res.title()

    def get_winnings(self):
        if not self.profits:
            return [0]
        return self.profits.copy()
    
    def get_current_bet(self):
        return self.curr_bet

    def get_optimal_bet(self):
        decks_used = math.floor(self.cards_seen/52)
        true_count = math.floor(self.curr_count/(self.num_shoes-decks_used))

        match self.betting_strategy:
            case "martingale":
                match self.prev_result:
                    case Outcome.PUSH:
                        return self.curr_bet
                    case Outcome.LOSE:
                        return self.curr_bet * 2
                    case _ :
                        return self.unit_bet
            case "reverse-martingale":
                match self.prev_result:
                    case Outcome.PUSH:
                        return self.curr_bet
                    case Outcome.LOSE:
                        return max(self.curr_bet // 2, self.unit_bet//2)
                    case _ :
                        return self.curr_bet * 2
            case _:
                scale = max(1, true_count)
                return scale * self.unit_bet

    def get_curr_hand(self, hand):
        num_aces = 0
        total_rest = 0
        for key, val in hand.items():
            if key == "A":
                num_aces = val
            elif key == "J" or key == "Q" or key == "K":
                total_rest += val * 10
            else:
                total_rest += val * int(key)

        hand = []
        for i in range(num_aces+1):
            temp = i * 1 + (num_aces-i)*11
            temp += total_rest

            if temp <= 21:
                hand.append(temp)
        
        return hand

    def get_optimal_play(self):
        dealer_hand = self.get_curr_hand(self.dealer_hand)
        player_hands = []
        for hand in self.curr_hands:
            temp = hand.copy()
            player_hands.append(self.get_curr_hand(temp))




    