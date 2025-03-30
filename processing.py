
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
    DOUBLE = 5

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
        self.curr_round_profit = 0
        self.curr_round_cards_seen = 0
        self.curr_round_count_change = 0
        self.doubled_hands = set()

        # Player + Dealer info
        self.curr_hands = []
        self.dealer_hand = {}

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
        self.curr_count = 0
        self.cards_seen = 0
        self.prev_result = Outcome.PUSH
        self.curr_round_profit = 0
        self.curr_round_cards_seen = 0
        self.curr_round_count_change = 0
        self.doubled_hands = set()

        self.curr_hands = []
        self.dealer_hand = {}
    
    # Updating game state
    def place_bet(self, new_bet):
        self.curr_bet = new_bet
        self.curr_round_profit = 0
        self.curr_round_cards_seen = 0
        self.curr_round_count_change = 0
        self.doubled_hands = set()

        #TODO: Currently is random information but needs to be updated to not have this be called
        dummy_data = [{"id": "dealer", "hands": [{"3": 1, "A": 3}]},
                      {"id": "1", "hands": [{"A": 1, "2": 2}]},
                      {"id": "2", "hands": [{"10": 2}, {"A": 1, "7": 1}]},
                      {"id": "3", "hands": [{"A": 1, "2": 2}]},
                      {"id": "4", "hands": [{"A": 3, "2": 2}]},
                      {"id": "5", "hands": [{"10": 1, "3": 1, "4": 1}]}]
        
        self.update_hands(dummy_data)
        
    def hand_outcome(self, outcome: Outcome, id):
        if outcome == Outcome.DOUBLE:
            self.doubled_hands.add(id)
            return False
        
        net_bet = self.curr_bet
        if id in self.doubled_hands:
            net_bet *= 2

        del self.curr_hands[id]
        self.doubled_hands.remove(id)
        
        match outcome:
            case Outcome.WIN:
                self.curr_round_profit += net_bet
            case Outcome.PUSH:
                self.curr_round_profit += 0
            case Outcome.LOSE:
                self.curr_round_profit -= net_bet
            case Outcome.BJ:
                self.curr_round_profit += net_bet * 1.5
            case _:
                # Dummy case
                self.curr_round_profit += net_bet

        if not self.curr_hands:
            prev_profit = 0 if not self.profits else self.profits[-1]
            self.profits.append(prev_profit + self.curr_round_profit)
            self.cards_seen += self.curr_round_cards_seen
            self.curr_count += self.curr_round_count_change
            
            if self.cards_seen >= self.num_shoes * 52:
                self.cards_seen = 0
                self.curr_count = 0

        if len(self.profits) > MAX_DISPLAY_WINNINGS:
            self.profits.popleft()

        return not self.curr_hands
    
    def update_hands(self, data):
        temp_seen = 0
        temp_change = 0

        for player_data in data:
            if player_data["id"] == "dealer":
                self.dealer_hand = player_data["hands"][0]
            if player_data["id"] == str(self.player_pos):
                self.curr_hands = player_data["hands"]
            
            (num_cards, count_change) = self.process_hand(player_data["hands"])
            temp_seen += num_cards
            temp_change += count_change

        self.curr_round_cards_seen = temp_seen
        self.curr_round_count_change = temp_change

    def process_hand(self, hands):
        cards_seen = 0
        count_change = 0

        for hand in hands:
            for key, val in hand.items():
                cards_seen += val
                match self.counting_technique:
                    case "hi-lo":
                        if key in {"2", "3", "4", "5", "6"}:
                            count_change += val
                        elif key in {"10", "J", "Q", "K", "A"}:
                            count_change -= val
                    case "omega-ii":
                        if key in {"2", "3", "7"}:
                            count_change += val
                        elif key in {"4", "5", "6"}:
                            count_change += val * 2
                        elif key == "9":
                            count_change -= val
                        elif key in {"10", "J", "Q", "K"}:
                            count_change -= val * 2
                    case _:
                        continue

        return (cards_seen, count_change)
    
    # Getting game state
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
        return self.curr_bet * (len(self.curr_hands) + len(self.doubled_hands))

    def get_optimal_bet(self):
        decks_used = math.floor(self.cards_seen/52)
        true_count = math.floor(self.curr_count/(self.num_shoes-decks_used))

        match self.betting_strategy:
            case "martingale":
                if self.curr_round_profit < 0:
                    return -self.curr_round_profit * 2
                elif self.curr_round_profit == 0:
                    return self.curr_bet
                else:
                    return self.unit_bet
                
            case "reverse-martingale":
                if self.curr_round_profit < 0:
                    return max(self.curr_bet // 2, self.unit_bet//2)
                elif self.curr_round_profit == 0:
                    return self.curr_bet
                else:
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

        if num_aces == 0:
            return (total_rest, None)
        
        soft_total = total_rest + num_aces
        hard_total = soft_total + 10

        if hard_total <= 21:
            return (hard_total, soft_total)
        return (soft_total, None)
    
    def get_dealer_hands(self):
        (hard, soft) = self.get_curr_hand(self.dealer_hand)
        if soft is None:
            return f"Hard: {hard}"
        return f"Hard: {hard}, Soft: {soft}"
    
    def get_player_hands(self):
        hands = []
        for i in range(len(self.curr_hands)):
            temp = self.curr_hands[i]
            (hard, soft) = self.get_curr_hand(temp)
            if soft is None:
                hands.append({"id": i+1, "hand": f"Hard: {hard}"})
            else:
                hands.append({"id": i+1, "hand": f"Hard: {hard}, Soft: {soft}"})
        return hands

    def get_optimal_play(self):
        dealer = 0
        dealer_card = ""
        for key in self.dealer_hand:
            # This should only run once techniquely
            dealer_card = key
            if key == "A":
                dealer = 11
            else:
                dealer = int(key)

        player_play = []
        for i in range(len(self.curr_hands)):
            temp = self.curr_hands[i].copy()
            (hard, soft) = self.get_curr_hand(temp)


            #TODO: Needs to case base on the counting technique
            if hard >= 17:
                player_play.append(Action.STAND)
            elif soft is not None:
                player_play.append(self.soft_total[soft][dealer])
            else:
                player_play.append(self.hard_total[soft][dealer])

        return (player_play, dealer_card)




    