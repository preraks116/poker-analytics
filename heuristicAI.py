from pypokerengine.players import BasePokerPlayer
import helper
import itertools
from deuces import Card
import deuces as d
import numpy as np

suits = ['s', 'h', 'd', 'c']
vals = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

def normalize(narray):
    return [x/sum(x) for x in narray]

class HeuristicPlayer(BasePokerPlayer):
    def __init__(self, def_prob, agg=1):
        """
        Input: Various hyperparameters that govern play
            Aggression: How aggressively the bot bids
            Default Prob: Default probability
            ity of folding, calling, raising or bluffing at
                          the buckets:
                          - RR <= 0.7 (struggling hand)
                          - 0.7 < R <= 0.9 (bad hand)
                          - 0.9 < R <= 1.1 (average hand)
                          - 1.1 < R <= 1.3 (good hand)
                          - 1.3 <= R (excellent hand)
            Example:  [
                [0.6, 0.2, 0.0, 0.2], # Bad hand play
                [0.4, 0.4, 0.1, 0.1], # Average hand play
                [0.1, 0.7, 0.2, 0.0], # Decent hand play
                [0.0, 0.6, 0.4, 0.0], # Good hand play
                [0.0, 0.3, 0.7, 0.0] # Excellent hand play
            ]
        """
        self.aggression = agg
        self.default_prob = def_prob
        self.vals = ['s', 'h', 'd', 'c']
        self.suits = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    # def one_look_hp(self, your_hand, board_cards, no_of_other_hands, sim=10000):
    #     evaluator = d.Evaluator()
    #     # Hand potential array, each index represents ahead, tied, and behind.
    #     HP = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    #     # Initialize HPTotal to 0.
    #     HPTotal = [0, 0, 0]

    #     my_hand = [d.Card.new(card) for card in your_hand]
    #     hand_strength = evaluator.evaluate(board_cards, my_hand)

    def hp_1(self, your_hand, board_cards):
        # Hand potential array, each index represents ahead, tied, and behind.
        HP = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        # Initialize HPTotal to 0.
        HPTotal = [0, 0, 0]
        evaluator = d.Evaluator()
        board = [d.Card.new(card) for card in board_cards]

        d.Card.print_pretty_cards(board)
        my_hand = [d.Card.new(card) for card in your_hand]
        
        ourrank = evaluator.evaluate(board, my_hand)

        deck = d.Deck()

        for card in board + my_hand:
            deck.cards.remove(card)

        for oppcards in itertools.combinations(deck.cards, 2):
            oppcards = list(oppcards)

            # Remove the cards from the deck.
            for card in oppcards:
                deck.cards.remove(card)

            opprank = evaluator.evaluate(board, oppcards)
            if ourrank < opprank:
                index = 0 #ahead
            elif ourrank == opprank:
                index = 1 #tied
            else:
                index = 2 #behind
            
            # All possiblities of next card
            for next_card in deck.cards:
                HPTotal[index] += 1
                updated_board = board + [next_card]
                ourbest = evaluator.evaluate(updated_board, my_hand)
                oppbest = evaluator.evaluate(updated_board, oppcards)
                
                if ourbest < oppbest:
                    HP[index][0] += 1
                elif ourbest == oppbest:
                    HP[index][1] += 1
                else:
                    HP[index][2] += 1
            
            # Readd the cards to the deck.
            for card in oppcards:
                deck.cards.append(card)
            
        # if the last two row of HP is all 0, then Ppot = 0
        if HP[2][0] == 0 and HP[2][1] == 0 and HP[2][2] == 0 and HP[1][0] == 0 and HP[1][1] == 0 and HP[1][2] == 0:
            Ppot = 0
        else:
            Ppot = (HP[2][0] + HP[2][1]/2 + HP[1][0]/2) / (HPTotal[2] + HPTotal[1])
        
        # Npot = (HP[0][2] + HP[1][2]/2 + HP[0][1]/2) / (HPTotal[0] + HPTotal[1])

        return Ppot

    def hp_2(self, your_hand, board_cards):
        # Hand potential array, each index represents ahead, tied, and behind.
        HP = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        # Initialize HPTotal to 0.
        HPTotal = [0, 0, 0]

        evaluator = d.Evaluator()
        board = [d.Card.new(card) for card in board_cards]
        my_hand = [d.Card.new(card) for card in your_hand]
        ourrank = evaluator.evaluate(board, my_hand)

        deck = d.Deck()

        for card in board + my_hand:
            deck.cards.remove(card)

        for oppcards in itertools.combinations(deck.cards, 2):
            oppcards = list(oppcards)

            # Remove the cards from the deck.
            for card in oppcards:
                deck.cards.remove(card)
            
            opprank = evaluator.evaluate(board, oppcards)
            if ourrank < opprank:
                index = 0 #ahead
            elif ourrank == opprank:
                index = 1 #tied
            else:
                index = 2 #behind

            # All possiblities of the next 2 cards (turn and river)
            for next_cards in itertools.combinations(deck.cards, 2):
                next_cards = list(next_cards)
                HPTotal[index] += 1
                updated_board = board + next_cards
                ourbest = evaluator.evaluate(updated_board, my_hand)
                oppbest = evaluator.evaluate(updated_board, oppcards)
                
                if ourbest < oppbest:
                    HP[index][0] += 1
                elif ourbest == oppbest:
                    HP[index][1] += 1
                else:
                    HP[index][2] += 1
            
            # Readd the cards to the deck.
            for card in oppcards:
                deck.cards.append(card)

        # if the last two row of HP is all 0, then Ppot = 0
        if HP[2][0] == 0 and HP[2][1] == 0 and HP[2][2] == 0 and HP[1][0] == 0 and HP[1][1] == 0 and HP[1][2] == 0:
            Ppot = 0
        else:
            Ppot = (HP[2][0] + HP[2][1]/2 + HP[1][0]/2) / (HPTotal[2] + HPTotal[1])
        
        Npot = (HP[0][2] + HP[1][2]/2 + HP[0][1]/2) / (HPTotal[0] + HPTotal[1])

        return Ppot, Npot

    def hse_1(self, your_hand, board_cards, players_still_in):
        if len(board_cards) == 0: #Pre-flop, compute with lookup table
            if your_hand[0][1] == your_hand[1][1]: #suited
                return helper.preflop([your_hand[0][0] + your_hand[1][0] + 's', your_hand[1][0] + your_hand[0][0] + 's'], players_still_in+1)
            else: #unsuited
                return helper.preflop([your_hand[0][0] + your_hand[1][0] + 'o', your_hand[1][0] + your_hand[0][0] + 'o'], players_still_in+1)
        wins = 0
        losses = 0
        ties = 0

        my_hand = [d.Card.new(card) for card in your_hand]
        board = [d.Card.new(card) for card in board_cards]
        
        deck = d.Deck()
        evaluator = d.Evaluator()

        for card in board + my_hand: 
            deck.cards.remove(card)

        hero_score = evaluator.evaluate(board, my_hand)
        # for all possible starting hands the opponent could have
        for i in range(len(deck.cards)):
            for j in range(i + 1, len(deck.cards)):
                villain_hand = [deck.cards[i], deck.cards[j]]

                # evaluate the hand
                villain_score = evaluator.evaluate(board, villain_hand)

                if hero_score < villain_score:
                    wins += 1
                elif hero_score > villain_score:
                    losses += 1
                else:
                    ties += 1
        hse = (wins + ties / 2) / (wins + losses + ties)
        return hse 

    def hse(self, your_hand, board_cards, no_of_other_hands, sim=10000):
        if len(board_cards) == 0: #Pre-flop, compute with lookup table
            if your_hand[0][1] == your_hand[1][1]: #suited
                return helper.preflop([your_hand[0][0] + your_hand[1][0] + 's', your_hand[1][0] + your_hand[0][0] + 's'], no_of_other_hands+1)
            else: #unsuited
                return helper.preflop([your_hand[0][0] + your_hand[1][0] + 'o', your_hand[1][0] + your_hand[0][0] + 'o'], no_of_other_hands+1)
        else:
            possible_cards = [a+b for a in vals for b in suits]
            for card in your_hand:
                possible_cards.remove(card)
            for card in board_cards:
                possible_cards.remove(card)

            wins = 0
            num_cards = 5 - len(board_cards) + 2 * no_of_other_hands
            evaluator = d.Evaluator()

            my_hand = [d.Card.new(card) for card in your_hand]
            
            for i in range(sim): #10,000 MC simulations
                generated_cards = np.random.choice(possible_cards, num_cards, replace=False)
                counter = 0
                
                board = [d.Card.new(card) for card in board_cards]
                hand_strength = evaluator.evaluate(board, my_hand)
                while len(board) < 5:
                    board.append(d.Card.new(generated_cards[counter]))
                    counter += 1
                best_strength = 1e10 #some random large number
                no_best_hands = 1 #number of hands that are at best_strength
                for j in range(no_of_other_hands):
                    new_hand = [d.Card.new(generated_cards[counter]), d.Card.new(generated_cards[counter+1])]
                    counter += 2
                    new_strength = evaluator.evaluate(board, new_hand)
                    if new_strength < best_strength:
                        best_strength = new_strength
                        no_best_hands = 1 #reset
                    elif new_strength == best_strength:
                        no_best_hands += 1 #add one more
                if best_strength > hand_strength:
                    wins += 1
                elif best_strength == hand_strength:
                    wins += 1/no_best_hands

            return wins/sim
        
    def declare_action(self, valid_actions, hole_card, round_state):
        your_hand = helper.pp_to_array(hole_card)
        # d.Card.print_pretty_cards(helper.pp_to_deuces(your_hand))
        board_cards = helper.pp_to_array(round_state['community_card'])
        player_no = round_state['next_player'] #your position
        
        players_still_in = 0
        for player in round_state['seats']:
            if player['state'] == "participating":
                players_still_in += 1
        
        pot = round_state['pot']['main']['amount']
        if len(round_state['pot']) == 2:
            for sidepot in round_state['pot']['side']:
                pot += sidepot['amount'] #can always assume you are in sidepot, else you have no choices anyways.
            
        min_bet = valid_actions[1]['amount']
        stack = round_state['seats'][player_no]
        min_raise = valid_actions[2]['amount']['min']
        max_raise = valid_actions[2]['amount']['max']

       
        if min_bet == 0: #when we are first to act
            hse = self.hse(your_hand, board_cards, players_still_in)
            hse_1 = self.hse_1(your_hand, board_cards, players_still_in)
            # ppot, npot = self.hp_1(your_hand, board_cards)
            ppot = 0
            if len(board_cards) > 0 and len(board_cards) < 5:
                ppot = self.hp_1(your_hand, board_cards)
                ehs = hse_1 + (1-hse)*ppot
            else:
                ehs = hse
            rr = hse * (players_still_in+1)
            rr2 = ehs * (players_still_in+1)
            # rr2 = ppot/(1-ppot) * (pot + min_bet) / (min_bet + pot + min_raise)
            # rr3 = (1+ppot)*hse - npot*(1-hse)
            print("------- AI LOG --------")
            print("hse: ", hse_1)
            print("ppot: ", ppot)
            print("RR: ", rr2/10)
            # print("rr3: ", rr3)
            print("-----------------------")
            # prob = self.default_prob[np.argmin(abs(np.array([0.6, 0.8, 1.0, 1.2, 1.4]) - rr))]
            prob = self.default_prob[np.argmin(abs(np.array([0.6, 0.8, 1.0, 1.2, 1.4]) - rr2))]

            prob[1] = prob[0] + prob[1]
            prob[0] = 0 #we don't ever want to fold when we don't have to!!
            
        else:
            # Use heuristic to decide optimal move.
            wp = self.hse(your_hand, board_cards, players_still_in-1)
            hse_1 = self.hse_1(your_hand, board_cards, players_still_in-1)
            pot_odds = min_bet/(pot+min_bet)
            # ppot, npot = self.hp_1(your_hand, board_cards)
            rr = wp/pot_odds # our main heuristic, expected rate of return
            ppot = 0
            if len(board_cards) > 0 and len(board_cards) < 5:
                ppot = self.hp_1(your_hand, board_cards)
                ehs = hse_1 + (1-hse_1)*ppot
            else:
                ehs = hse_1
            
            rr2 = ehs/pot_odds
            # rr2 = (1+ppot)*rr - npot*(1-rr) # our second heuristic, expected rate of return
            # print("------- AI LOG --------")
            # print("wp: ", wp)
            # print("pot_odds: ", pot_odds)
            # print("ppot: ", ppot)
            # print("npot: ", npot)
            # print("rr: ", rr)
            # print("rr2: ", rr2)
            # print("-----------------------")

            # prob = self.default_prob[np.argmin(abs(np.array([0.6, 0.8, 1.0, 1.2, 1.4]) - rr))]
            prob = self.default_prob[np.argmin(abs(np.array([0.6, 0.8, 1.0, 1.2, 1.4]) - rr2))]

            ## We should adjust this probability with our rr!!!

        move = np.random.choice(['fold', 'call', 'raise', 'bluff'], p=prob)
        if move == "raise":
            raise_amount = pot / 3 * self.aggression
            ## We should adjust this raise with our rr!!!
            raise_amount = int(max(min(raise_amount, max_raise), min_raise))
            if len(valid_actions) == 3: #is possible to raise, i.e. have enough money to raise
                return ("raise", raise_amount)
            else:
                return ("call", min_bet)
        elif move == "bluff":
            raise_amount = pot / 2 * self.aggression
            ## We should adjust this raise with our rr!!!
            raise_amount = int(max(min(raise_amount, max_raise), min_raise))
            if len(valid_actions) == 3: #is possible to raise, i.e. have enough money to raise
                return ("raise", raise_amount)
            else:
                return ("call", min_bet)
        elif move == "call":
            return (move, min_bet)
        else:
            return (move, 0)

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        print("------- AI LOG --------")
        d.Card.print_pretty_cards(helper.pp_to_deuces(hole_card))
        print("-----------------------")
        pass

    def receive_street_start_message(self, street, round_state):
        print("------- AI LOG --------")
        board = helper.pp_to_deuces(round_state['community_card'])
        print("Board cards: ")
        d.Card.print_pretty_cards(board)
        print("-----------------------")
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        # print("------- AI LOG --------")
        # print(hand_info[0]["hand"]["hand"]["strength"]) 
        # print(hand_info[1]["hand"]["hand"]["strength"]) 
        # print("-----------------------")
        pass

def setup_ai():
    init_def_prob = [
        [0.6, 0.2, 0.0, 0.2],
        [0.4, 0.4, 0.1, 0.1],
        [0.1, 0.7, 0.2, 0.0],
        [0.0, 0.6, 0.4, 0.0],
        [0.0, 0.3, 0.7, 0.0]
    ]
    return HeuristicPlayer(init_def_prob)



